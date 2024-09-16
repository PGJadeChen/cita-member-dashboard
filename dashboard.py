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
    "primary": "#003366",
    "secondary": "#FF9900",
    "accent": "#66CCCC",
    "background": "#F0F2F6",
    "text": "#333333",
}

# 自定义CSS
st.markdown(
    """
<style>
    .stApp {
        background-color: #F0F2F6;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .card h2 {
        color: #003366;
        margin-top: 0;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #003366;
    }
    /* 新增：确保图表容器内的所有内容都被包裹 */
    .card-content {
        overflow: hidden;
    }
</style>
""",
    unsafe_allow_html=True,
)


def create_card(title, content):
    card = st.container()
    with card:
        st.markdown(
            f'<div class="card"><h2>{title}</h2><div class="card-content">',
            unsafe_allow_html=True,
        )
        content()
        st.markdown("</div></div>", unsafe_allow_html=True)


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


# 加载数据
@st.cache_data
def load_data():
    members = pd.read_csv("./data/members.csv")
    members = members[
        members["Member ID"].notna()
        & members["Member ID"].str.startswith("CITANZ-", na=False)
    ]
    members = deduplicate_regions(members, "Region")

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


# 加载新西兰的 geojson 文件
@st.cache_data
def load_geojson():
    with open("./gadm41_NZL_2.json") as f:
        nz_geojson = json.load(f)
    return nz_geojson


# 处理数据
def preprocess_data(members, payments):
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

    payments["Paid at"] = pd.to_datetime(
        payments["Paid at"], format="%b %d, %Y, %I:%M %p", errors="coerce"
    )
    payments["Amount"] = (
        payments["Amount"].replace("[\$,]", "", regex=True).astype(float)
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

    # 创建环形图
    fig = px.pie(
        values=expiry_status.values,
        names=expiry_status.index,
        title="Membership Status",
        hole=0.4,
        color_discrete_sequence=[COLOR_SCHEME["primary"], COLOR_SCHEME["secondary"]],
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(title_font_size=20, title_x=0.5)
    return fig


# 收入趋势图
def plot_income_trend(payments):
    payments["Month"] = (
        payments["Paid at"].dt.to_period("M").astype(str)
    )  # 将 Period 转换为字符串
    monthly_income = payments.groupby("Month")["Amount"].sum().reset_index()
    fig = px.line(monthly_income, x="Month", y="Amount", title="Monthly Charge Trend")
    fig.update_xaxes(nticks=20)
    fig.update_layout(
        font=dict(family=chinese_font),
        title_font=dict(family=chinese_font),
        title_font_size=20,
        title_x=0.5,
    )
    return fig


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

    # 创建主要地区的饼图
    fig1 = px.pie(
        main_region_data,
        values="Member ID",
        names=region_column,
        title="Main Regions Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig1.update_traces(textposition="inside", textinfo="percent+label")
    fig1.update_layout(title_font_size=20, title_x=0.5)

    # 创建其他地区的条形图
    fig2 = px.bar(
        other_region_data,
        x=region_column,
        y="Member ID",
        title="Other Regions Distribution",
        color_discrete_sequence=[COLOR_SCHEME["accent"]],
    )
    fig2.update_layout(xaxis_tickangle=-45, title_font_size=20, title_x=0.5)

    return fig1, fig2


# 使用 Plotly 绘制会员活跃度热力图
def plot_member_activity_heatmap(members):
    # 提取星期和小时
    members["Last logged in date"] = pd.to_datetime(
        members["Last logged in"], format="%b %d, %Y, %I:%M %p", errors="coerce"
    )
    members["DayOfWeek"] = members[
        "Last logged in date"
    ].dt.dayofweek  # 星期几 (0: Monday, 6: Sunday)
    members["Hour"] = members["Last logged in date"].dt.hour  # 登录的小时

    # 统计每个时间段的活跃度
    activity_heatmap = members.pivot_table(
        index="DayOfWeek",
        columns="Hour",
        values="Member ID",
        aggfunc="count",
        fill_value=0,
    )

    # 使用 Plotly 绘制热力图
    fig = px.imshow(
        activity_heatmap,
        labels=dict(x="Hour of Day", y="Day of Week", color="Login Count"),
        x=activity_heatmap.columns,
        y=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
        color_continuous_scale="YlGnBu",
        aspect="auto",
    )

    fig.update_layout(
        title="Member Activity Heatmap (Days vs Hours)",
        font=dict(family=chinese_font),
        title_font=dict(family=chinese_font),
        title_font_size=20,
        height=500,
        title_x=0.5,
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

    fig.update_layout(
        font=dict(family=chinese_font),
        title_font=dict(family=chinese_font),
        annotations=[
            dict(text="Renewal", x=0.5, y=0.5, font_size=20, showarrow=False)
        ],  # 环形图中心的文本
    )

    return fig  # 返回图表对象而不是直接显示它


# 每月新会员注册柱状图
def plot_new_members(members):
    members["Sign Up Month"] = (
        members["Date Signed up"].dt.to_period("M").astype(str)
    )  # 转换为字符串
    new_members = members.groupby("Sign Up Month")["Member ID"].count().reset_index()
    fig = px.bar(
        new_members, x="Sign Up Month", y="Member ID", title="New Members per Month"
    )
    fig.update_xaxes(nticks=20)
    fig.update_layout(
        font=dict(family=chinese_font),
        title_font=dict(family=chinese_font),
        title_font_size=20,
        title_x=0.5,
    )
    return fig


# 会员缴费金额分布饼图
def plot_payment_amount_distribution(payments):
    amount_dist = payments["Amount"].value_counts().reset_index()
    amount_dist.columns = ["Amount", "Count"]

    fig = px.pie(
        values=amount_dist["Count"],
        names=amount_dist["Amount"],
        title="Membership Type",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        font=dict(family=chinese_font),
        title_font=dict(family=chinese_font),
        title_font_size=20,
        title_x=0.5,
    )
    return fig


# 新西兰城市分布气泡地图
def plot_nz_city_map(members):
    # members["Region"] = members["Region"].fillna("Unknown")
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

    # members["Matched_Region"] = members["Region"].apply(match_location)
    members["Matched_City"] = members["City"].apply(match_location)

    # region_counts = members[members["Matched_Region"] != "Unknown"][
    #     "Matched_Region"
    # ].value_counts()
    city_counts = members[members["Matched_City"] != "Unknown"][
        "Matched_City"
    ].value_counts()

    # 定义气泡大小缩放函数
    def scale_bubble_size(count, min_size=10, max_size=100):
        return np.clip(np.log(count) * 5, min_size, max_size)

    fig_map = go.Figure()

    # 添加 Region 数据
    # fig_map.add_trace(
    #     go.Scattermapbox(
    #         lat=[nz_regions_cities[region][0] for region in region_counts.index],
    #         lon=[nz_regions_cities[region][1] for region in region_counts.index],
    #         mode="markers",
    #         marker=go.scattermapbox.Marker(
    #             size=scale_bubble_size(region_counts.values), color="blue", opacity=0.6
    #         ),
    #         text=[f"{region}: {count}" for region, count in region_counts.items()],
    #         hoverinfo="text",
    #         name="Regions",
    #     )
    # )

    # 添加 City 数据
    fig_map.add_trace(
        go.Scattermapbox(
            lat=[nz_regions_cities[city][0] for city in city_counts.index],
            lon=[nz_regions_cities[city][1] for city in city_counts.index],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=scale_bubble_size(city_counts.values), color="red", opacity=0.5
            ),
            text=[f"{city}: {count}" for city, count in city_counts.items()],
            hoverinfo="text",
            name="Cities",
        )
    )

    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox=dict(center=dict(lat=-41.0, lon=174.0), zoom=4.2),
        showlegend=False,
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig_map


def dashboard_layout():
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 2rem;'>Cita Membership Dashboard</h1>",
        unsafe_allow_html=True,
    )

    members, payments = load_data()
    members, payments = preprocess_data(members, payments)

    # 计算并展示关键指标
    total_members, active_members, new_members_this_month = calculate_key_metrics(
        members
    )

    # 关键指标卡片居中展示
    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card("Total Members", total_members)
    with col2:
        display_metric_card("Active Members", active_members)
    with col3:
        display_metric_card("New Members This Month", new_members_this_month)

    # 会员分布
    def membership_distribution_content():
        fig1, fig2 = process_and_visualize_regions(members, "Region")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.plotly_chart(fig2, use_container_width=True)

    create_card("Membership Distribution", membership_distribution_content)

    # 会员状态
    def membership_status_content():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(plot_membership_status(members), use_container_width=True)
        with col2:
            st.plotly_chart(
                plot_payment_amount_distribution(payments), use_container_width=True
            )
        with col3:
            st.plotly_chart(plot_renewal_funnel(members), use_container_width=True)

    create_card("Membership Status", membership_status_content)

    # 财务分析
    def financial_analysis_content():
        income_trend_fig = plot_income_trend(payments)
        st.plotly_chart(income_trend_fig, use_container_width=True)

    create_card("Financial Analysis", financial_analysis_content)

    # 会员活动和地理分布
    def activity_and_distribution_content():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("<h3>Geographical Distribution</h3>", unsafe_allow_html=True)
            nz_map_fig = plot_nz_city_map(members)
            if nz_map_fig is not None:
                st.plotly_chart(nz_map_fig, use_container_width=True)
            else:
                st.write("No data available for New Zealand map.")
        with col2:
            st.markdown("<h3>Member Activity Heatmap</h3>", unsafe_allow_html=True)
            activity_heatmap_fig = plot_member_activity_heatmap(members)
            st.plotly_chart(activity_heatmap_fig, use_container_width=True)

    create_card(
        "Member Activity and Geographical Distribution",
        activity_and_distribution_content,
    )

    # 新会员注册趋势
    def new_member_trend_content():
        new_members_fig = plot_new_members(members)
        st.plotly_chart(new_members_fig, use_container_width=True)

    create_card("New Member Registration Trend", new_member_trend_content)


# 运行 Dashboard
if __name__ == "__main__":
    dashboard_layout()
