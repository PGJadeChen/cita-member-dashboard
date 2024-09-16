import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
from pypinyin import lazy_pinyin
import re
from datetime import datetime

# 设置页面配置
chinese_font = "SimHei"
st.set_page_config(page_title="CITANZ Membership Dashboard", layout="wide")

# 定义颜色方案
COLOR_SCHEME = {
    "primary": "#3366cc",  # A soft blue as the primary color
    "secondary": "#dc3912",  # A muted red for contrast and highlights
    "accent": "#ff9900",  # A soft orange for accents
    "background": "#f9f9f9",  # A light grey for background
    "text": "#333333",  # A dark grey for text
    "neutral": "#909090",  # A medium grey for less important elements
}

# 自定义CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {COLOR_SCHEME["background"]};
    }}
    .card {{
        background-color: white;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }}
    .card h2 {{
        color: {COLOR_SCHEME["primary"]};
        margin-top: 0;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
    }}
    .metric-value {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {COLOR_SCHEME["primary"]};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# 定义统一的图表样式
def apply_common_style(fig, title):
    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(family=chinese_font, size=20, color=COLOR_SCHEME["primary"]),
        },
        font=dict(family=chinese_font, color=COLOR_SCHEME["text"]),
        plot_bgcolor=COLOR_SCHEME["background"],
        paper_bgcolor=COLOR_SCHEME["background"],
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1),
    )
    fig.update_xaxes(gridcolor=COLOR_SCHEME["neutral"], gridwidth=0.5)
    fig.update_yaxes(gridcolor=COLOR_SCHEME["neutral"], gridwidth=0.5)
    return fig


nz_regions_cities = {
    "Northland": (-35.7317, 174.3242),
    "Auckland": (-36.8485, 174.7633),
    "Waikato": (-37.7870, 175.2793),
    "Bay of Plenty": (-37.6878, 176.1651),
    "Gisborne": (-38.6623, 178.0176),
    "Hawke's Bay": (-39.4928, 176.9120),
    "Taranaki": (-39.0556, 174.0752),
    "Manawatu-Whanganui": (-40.3523, 175.6082),
    "Wellington": (-41.2865, 174.7762),
    "Tasman": (-41.2706, 173.2840),
    "Nelson": (-41.2706, 173.2840),
    "Marlborough": (-41.5134, 173.9611),
    "West Coast": (-42.4504, 171.2108),
    "Canterbury": (-43.5321, 172.6362),
    "Otago": (-45.8788, 170.5028),
    "Southland": (-46.4132, 168.3538),
    # 主要城市
    "Hamilton": (-37.7870, 175.2793),
    "Tauranga": (-37.6878, 176.1651),
    "Napier-Hastings": (-39.4928, 176.9120),
    "Palmerston North": (-40.3523, 175.6082),
    "Christchurch": (-43.5321, 172.6362),
    "Dunedin": (-45.8788, 170.5028),
    "Invercargill": (-46.4132, 168.3538),
    "Queenstown": (-45.0312, 168.6626),
}


def to_pinyin(text):
    if pd.isna(text):
        return ""
    return "".join(lazy_pinyin(str(text)))


def normalize_name(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def deduplicate_regions(df, region_column):
    # 创建一个新的DataFrame来存储处理后的数据
    processed_df = df.copy()

    # 确保region_column中的所有值都是字符串
    processed_df[region_column] = processed_df[region_column].astype(str)

    # 添加拼音列和规范化名称列
    processed_df["pinyin"] = processed_df[region_column].apply(to_pinyin)
    processed_df["normalized_name"] = processed_df["pinyin"].apply(normalize_name)

    # 根据规范化名称分组并合并
    grouped = (
        processed_df.groupby("normalized_name")
        .agg(
            {
                region_column: "first",  # 保留第一个出现的原始名称
                "Member ID": "count",  # 计算每个地区的成员数量
            }
        )
        .reset_index()
    )

    # 按计数降序排序
    grouped = grouped.sort_values("Member ID", ascending=False)

    # 重命名列
    grouped = grouped.rename(columns={"Member ID": "Count"})

    # 合并回原始DataFrame
    result = pd.merge(
        df, grouped[[region_column, "Count"]], on=region_column, how="left"
    )

    return result


# 加载新西兰的 geojson 文件
@st.cache_data
def load_geojson():
    with open("./gadm41_NZL_2.json") as f:
        nz_geojson = json.load(f)
    return nz_geojson


# 加载和处理数据
@st.cache_data
def load_and_preprocess_data():
    members = pd.read_csv("./data/members.csv")
    members = members[
        members["Member ID"].notna()
        & members["Member ID"].str.startswith("CITANZ-", na=False)
    ]

    payments = pd.read_csv("./data/payments.csv")

    # 处理日期格式
    members["Expiry date"] = pd.to_datetime(
        members["Expiry date"], format="%d/%m/%Y", errors="coerce"
    )
    members["Last Payment Date"] = pd.to_datetime(
        members["Last Payment Date"], format="%d/%m/%Y %H:%M", errors="coerce"
    )
    members["Date Signed up"] = pd.to_datetime(
        members["Date Signed up"], format="%b %d, %Y, %I:%M %p", errors="coerce"
    )
    members["Last logged in"] = pd.to_datetime(
        members["Last logged in"], format="%b %d, %Y, %I:%M %p", errors="coerce"
    )

    payments["Paid at"] = pd.to_datetime(
        payments["Paid at"], format="%b %d, %Y, %I:%M %p", errors="coerce"
    )
    payments["Amount"] = (
        payments["Amount"].replace(r"[$,]", "", regex=True).astype(float)
    )

    return members, payments


# 计算关键指标
def calculate_key_metrics(members):
    total_members = len(members)  # 会员总数量
    active_members = members[members["Expiry date"] > datetime.now()]  # 活跃会员数量
    current_month = datetime.now().strftime("%Y-%m")  # 获取当前月份
    new_members_this_month = len(
        members[members["Date Signed up"].dt.to_period("M") == current_month]
    )  # 当月新增会员数量
    return total_members, len(active_members), new_members_this_month


# 卡片样式
def display_metric_card(label, value):
    st.markdown(
        f"""
        <div class="card" style="text-align: center;">
            <h3>{label}</h3>
            <p class="metric-value" style="font-family: Georgia, serif;">{value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# 会员状态饼图
def plot_membership_status(members):
    expiry_status = (
        members["Expiry date"]
        .dropna()
        .apply(lambda x: "Active" if x > datetime.now() else "Expired")
        .value_counts()
    )

    fig = px.pie(
        values=expiry_status.values,
        names=expiry_status.index,
        title="Membership Status",
        hole=0.4,
        color_discrete_sequence=[COLOR_SCHEME["primary"], COLOR_SCHEME["secondary"]],
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return apply_common_style(fig, "Membership Status")


# 收入趋势图
def plot_income_trend(payments):
    payments["Month"] = payments["Paid at"].dt.to_period("M").astype(str)
    monthly_income = payments.groupby("Month")["Amount"].sum().reset_index()
    fig = px.line(
        monthly_income,
        x="Month",
        y="Amount",
        title="Monthly Charge Trend",
        line_shape="spline",
        render_mode="svg",
    )
    fig.update_traces(line_color=COLOR_SCHEME["primary"])
    fig.update_xaxes(
        dtick="M1", tickformat="%b %Y", tickangle=-45, ticklabelmode="period"
    )
    return apply_common_style(fig, "Monthly Charge Trend")


def process_and_visualize_regions(df, region_column):
    # 过滤数据
    df = df[
        df["Member ID"].notna() & df["Member ID"].str.startswith("CITANZ-", na=False)
    ]

    # 创建一个新的DataFrame来存储处理后的数据
    processed_df = df.copy()

    # 确保region_column中的所有值都是字符串
    processed_df[region_column] = (
        processed_df[region_column].fillna("Unknown").astype(str)
    )

    # 添加拼音列和规范化名称列
    processed_df["pinyin"] = processed_df[region_column].apply(to_pinyin)
    processed_df["normalized_name"] = processed_df["pinyin"].apply(normalize_name)

    # 根据规范化名称分组并合并
    grouped = (
        processed_df.groupby("normalized_name")
        .agg(
            {
                region_column: "first",  # 保留第一个出现的原始名称
                "Member ID": "count",  # 计算每个地区的成员数量
            }
        )
        .reset_index()
    )

    # 按计数降序排序
    grouped = grouped.sort_values("Member ID", ascending=False)

    # 分离主要地区和其他地区
    main_regions = ["Auckland", "Wellington", "Canterbury"]
    main_region_data = grouped[grouped[region_column].isin(main_regions)]
    other_region_data = grouped[~grouped[region_column].isin(main_regions)]

    # Create pie chart for main regions
    fig1 = px.pie(
        main_region_data,
        values="Member ID",
        names=region_column,
        title="Main Regions Distribution",
        color_discrete_sequence=[
            COLOR_SCHEME["primary"],
            COLOR_SCHEME["secondary"],
            COLOR_SCHEME["accent"],
        ],
    )
    fig1.update_traces(textposition="inside", textinfo="percent+label")
    fig1 = apply_common_style(fig1, "Main Regions Distribution")

    # Create bar chart for other regions
    fig2 = px.bar(
        other_region_data,
        x=region_column,
        y="Member ID",
        title="Other Regions Distribution",
        color_discrete_sequence=[COLOR_SCHEME["primary"]],
    )
    fig2 = apply_common_style(fig2, "Other Regions Distribution")
    fig2.update_layout(xaxis_tickangle=-45)
    return fig1, fig2


# 使用 Plotly 绘制会员活跃度热力图
def plot_member_activity_heatmap(members):
    members["Last logged in date"] = pd.to_datetime(
        members["Last logged in"], format="%b %d, %Y, %I:%M %p", errors="coerce"
    )
    members["DayOfWeek"] = members["Last logged in date"].dt.dayofweek
    members["Hour"] = members["Last logged in date"].dt.hour
    members["Date"] = members["Last logged in date"].dt.date

    # Create a complete index for all day and hour combinations
    all_days = range(7)
    all_hours = list(range(24))
    index = pd.MultiIndex.from_product(
        [all_days, all_hours], names=["DayOfWeek", "Hour"]
    )

    # Count the occurrences and reindex to include all combinations
    activity_counts = (
        members.groupby(["DayOfWeek", "Hour"]).size().reindex(index, fill_value=0)
    )

    # Reshape to create the heatmap data
    activity_heatmap = activity_counts.unstack(level="Hour")

    # Create hover text
    hover_text = [
        [
            f"Day: {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day]}<br>"
            f"Hour: {hour:02d}:00<br>"
            f"Count: {activity_heatmap.iloc[day, hour]}"
            for hour in all_hours
        ]
        for day in all_days
    ]

    fig = px.imshow(
        activity_heatmap,
        labels=dict(x="Hour of Day", y="Day of Week", color="Login Count"),
        x=all_hours,
        y=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
        color_continuous_scale=[
            [0, COLOR_SCHEME["background"]],
            [1, COLOR_SCHEME["primary"]],
        ],
        aspect="auto",
    )

    fig.update_traces(hovertemplate="%{text}", text=hover_text)

    fig = apply_common_style(fig, "Member Activity Heatmap (Days vs Hours)")
    fig.update_layout(height=500)

    # Update x-axis to show 24-hour format
    fig.update_xaxes(
        tickvals=list(range(24)), ticktext=[f"{h:02d}:00" for h in range(24)]
    )

    return fig


# 会员续费情况环形图
def plot_renewal_funnel(members):
    renewal_status = members["Last Payment Date"].notna().value_counts()

    # 创建环形图
    fig = px.pie(
        values=renewal_status.values,
        names=["Renewed", "Not Renewed"],
        title="Membership Status(Renewed vs Not Renewed)",
        hole=0.4,  # 设置 hole 参数以创建环形图
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")

    fig = apply_common_style(fig, "Membership Status (Renewed vs Not Renewed)")
    fig.add_annotation(text="Renewal", x=0.5, y=0.5, font_size=20, showarrow=False)
    return fig


# 每月新会员注册柱状图
def plot_new_members(members):
    members["Sign Up Month"] = members["Date Signed up"].dt.to_period("M").astype(str)
    new_members = members.groupby("Sign Up Month")["Member ID"].count().reset_index()
    fig = px.bar(
        new_members, x="Sign Up Month", y="Member ID", title="New Members per Month"
    )
    fig.update_xaxes(
        dtick="M1", tickformat="%b %Y", tickangle=-45, ticklabelmode="period"
    )
    return apply_common_style(fig, "New Members per Month")


# 会员缴费金额分布饼图
def plot_payment_amount_distribution(payments):
    amount_dist = payments["Amount"].value_counts().reset_index()
    amount_dist.columns = ["Amount", "Count"]

    fig = px.pie(values=amount_dist["Count"], names=amount_dist["Amount"])
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return apply_common_style(fig, "Membership Type")


# 新西兰城市分布气泡地图
def plot_nz_city_map(members):
    members["City"] = members["City"].fillna("Unknown")

    # 创建一个地区和城市名称映射字典
    location_mapping = {
        name: [
            name.lower(),
            name.replace(" ", "").lower(),
            name.replace("-", " ").lower(),
        ]
        for name in nz_regions_cities.keys()
    }

    def match_location(location):
        location_lower = location.lower().replace(" ", "")
        for name, aliases in location_mapping.items():
            if any(alias in location_lower for alias in aliases):
                return name
        return "Unknown"

    members["Matched_City"] = members["City"].apply(match_location)
    city_counts = members[members["Matched_City"] != "Unknown"][
        "Matched_City"
    ].value_counts()

    # 定义气泡大小缩放函数
    def scale_bubble_size(count, min_size=10, max_size=100):
        return np.clip(np.log(count) * 5, min_size, max_size)

    fig_map = go.Figure()

    # 添加 City 数据
    fig_map.add_trace(
        go.Scattermapbox(
            lat=[nz_regions_cities[city][0] for city in city_counts.index],
            lon=[nz_regions_cities[city][1] for city in city_counts.index],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=scale_bubble_size(city_counts.values),
                color=COLOR_SCHEME["primary"],  # Changed to primary color (blue)
                opacity=0.7,
            ),
            text=[f"{city}: {count}" for city, count in city_counts.items()],
            hoverinfo="text",
            name="Cities",
        )
    )

    fig_map = apply_common_style(fig_map, "New Zealand City Distribution")
    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox=dict(center=dict(lat=-41.0, lon=174.0), zoom=4),
        showlegend=False,
        height=500,
    )
    return fig_map


def dashboard_layout():
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 2rem;'>Cita Membership Dashboard</h1>",
        unsafe_allow_html=True,
    )

    members, payments = load_and_preprocess_data()

    # 计算关键指标
    total_members, active_members, new_members_this_month = calculate_key_metrics(
        members
    )

    # 关键指标
    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card("Total Members", total_members)
    with col2:
        display_metric_card("Active Members", active_members)
    with col3:
        display_metric_card("New Members This Month", new_members_this_month)

    # 会员分布
    fig1, fig2 = process_and_visualize_regions(members, "Region")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    # 会员状态
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(plot_membership_status(members), use_container_width=True)
    with col2:
        st.plotly_chart(
            plot_payment_amount_distribution(payments), use_container_width=True
        )
    with col3:
        st.plotly_chart(plot_renewal_funnel(members), use_container_width=True)

    # 会员充值分析
    income_trend_fig = plot_income_trend(payments)
    st.plotly_chart(income_trend_fig, use_container_width=True)

    # 会员活动和地理分布
    col1, col2 = st.columns([1, 2])
    with col1:
        nz_map_fig = plot_nz_city_map(members)
        if nz_map_fig is not None:
            st.plotly_chart(nz_map_fig, use_container_width=True)
        else:
            st.write("No data available for New Zealand map.")
    with col2:
        activity_heatmap_fig = plot_member_activity_heatmap(members)
        st.plotly_chart(activity_heatmap_fig, use_container_width=True)

    # 新会员注册趋势
    new_members_fig = plot_new_members(members)
    st.plotly_chart(new_members_fig, use_container_width=True)


# 运行 Dashboard
if __name__ == "__main__":
    dashboard_layout()
