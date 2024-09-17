import pandas as pd
from pypinyin import lazy_pinyin
import numpy as np
from datetime import datetime


def to_pinyin(text):
    return "".join(lazy_pinyin(text))


def normalize_name(pinyin):
    return pinyin.lower().replace(" ", "")


def load_and_preprocess_data():
    members = pd.read_csv("./data/members.csv")
    members = members[
        members["Member ID"].notna()
        & members["Member ID"].str.startswith("CITANZ-", na=False)
    ]

    payments = pd.read_csv("./data/payments.csv")

    # Process date columns
    date_columns = {
        "Expiry date": "%d/%m/%Y",
        "Last Payment Date": "%d/%m/%Y %H:%M",
        "Date Signed up": "%b %d, %Y, %I:%M %p",
        "Last logged in": "%b %d, %Y, %I:%M %p",
    }

    for col, format in date_columns.items():
        members[col] = pd.to_datetime(members[col], format=format, errors="coerce")

    payments["Paid at"] = pd.to_datetime(
        payments["Paid at"], format="%b %d, %Y, %I:%M %p", errors="coerce"
    )
    payments["Amount"] = (
        payments["Amount"].replace(r"[$,]", "", regex=True).astype(float)
    )

    return members, payments


def calculate_key_metrics(members):
    total_members = len(members)
    active_members = len(members[members["Expiry date"] > datetime.now()])
    current_month = datetime.now().strftime("%Y-%m")
    new_members_this_month = len(
        members[members["Date Signed up"].dt.to_period("M") == current_month]
    )
    return total_members, active_members, new_members_this_month


def process_regions(df, region_column):
    processed_df = df.copy()

    processed_df[region_column] = (
        processed_df[region_column].fillna("Unknown").astype(str)
    )

    processed_df["pinyin"] = processed_df[region_column].apply(to_pinyin)
    processed_df["normalized_name"] = processed_df["pinyin"].apply(normalize_name)

    grouped = (
        processed_df.groupby("normalized_name")
        .agg(
            {
                region_column: "first",
                "Member ID": "count",
            }
        )
        .reset_index()
    )

    grouped = grouped.sort_values("Member ID", ascending=False)

    grouped = grouped.rename(columns={"Member ID": "Number of Members"})

    main_regions = ["Auckland", "Wellington", "Canterbury"]

    main_regions_normalized = [
        normalize_name(to_pinyin(region)) for region in main_regions
    ]

    main_region_data = grouped[
        grouped["normalized_name"].isin(main_regions_normalized)
    ].to_dict("records")
    other_region_data = grouped[
        ~grouped["normalized_name"].isin(main_regions_normalized)
    ].to_dict("records")

    for data in main_region_data + other_region_data:
        data["Region"] = data.pop(region_column)

    return main_region_data, other_region_data


def calculate_membership_status(members):
    expiry_status = (
        members["Expiry date"]
        .dropna()
        .apply(lambda x: "Active" if x > datetime.now() else "Expired")
        .value_counts()
    )
    return expiry_status.to_dict()


def calculate_payment_distribution(payments):
    amount_dist = payments["Amount"].value_counts().reset_index()
    amount_dist.columns = ["Amount", "Count"]
    return amount_dist.to_dict("records")


def calculate_renewal_funnel(members):
    renewal_status = members["Last Payment Date"].notna().value_counts()
    return {
        "Renewed": int(renewal_status[True]),
        "Not Renewed": int(renewal_status[False]),
    }


def calculate_income_trend(payments):
    payments["Month"] = payments["Paid at"].dt.to_period("M").astype(str)
    monthly_income = payments.groupby("Month")["Amount"].sum().reset_index()
    return monthly_income.to_dict("records")


def calculate_activity_heatmap(members):
    members["DayOfWeek"] = members["Last logged in"].dt.dayofweek
    members["Hour"] = members["Last logged in"].dt.hour
    activity_counts = (
        members.groupby(["DayOfWeek", "Hour"]).size().reset_index(name="Count")
    )
    return activity_counts.to_dict("records")


def calculate_nz_distribution(members):
    # Fill NA values
    members["Region"] = members["Region"].fillna("Unknown")
    members["City"] = members["City"].fillna("Unknown")

    # Calculate region counts
    region_counts = members["Region"].value_counts().reset_index()
    region_counts.columns = ["name", "value"]

    # Calculate city counts within each region
    result = []
    for _, region in region_counts.iterrows():
        region_data = {
            "name": region["name"],
            "value": int(region["value"]),
            "children": [],
        }

        if region["name"] != "Unknown":
            city_counts = (
                members[members["Region"] == region["name"]]["City"]
                .value_counts()
                .reset_index()
            )
            city_counts.columns = ["name", "value"]

            for _, city in city_counts.iterrows():
                region_data["children"].append(
                    {"name": city["name"], "value": int(city["value"])}
                )

        result.append(region_data)

    return result


def calculate_new_members(members):
    members["Sign Up Month"] = members["Date Signed up"].dt.to_period("M").astype(str)
    new_members = members.groupby("Sign Up Month")["Member ID"].count().reset_index()
    new_members.columns = ["Month", "Count"]
    return new_members.to_dict("records")
