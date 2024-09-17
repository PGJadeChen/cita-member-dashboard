from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from data_processing import (
    load_and_preprocess_data,
    calculate_key_metrics,
    process_regions,
    calculate_membership_status,
    calculate_payment_distribution,
    calculate_renewal_funnel,
    calculate_income_trend,
    calculate_activity_heatmap,
    calculate_nz_distribution,
    calculate_new_members,
)

app = Flask(__name__)
CORS(app)

# Load data
members, payments = load_and_preprocess_data()


@app.route("/api/key_metrics")
def key_metrics():
    total_members, active_members, new_members_this_month = calculate_key_metrics(
        members
    )
    return jsonify(
        {
            "total_members": total_members,
            "active_members": active_members,
            "new_members_this_month": new_members_this_month,
        }
    )


@app.route("/api/region_distribution")
def region_distribution():
    main_regions, other_regions = process_regions(members, "Region")
    return jsonify({"main_regions": main_regions, "other_regions": other_regions})


@app.route("/api/membership_status")
def membership_status():
    status = calculate_membership_status(members)
    return jsonify(status)


@app.route("/api/payment_distribution")
def payment_distribution():
    distribution = calculate_payment_distribution(payments)
    return jsonify(distribution)


@app.route("/api/renewal_funnel")
def renewal_funnel():
    funnel = calculate_renewal_funnel(members)
    return jsonify(funnel)


@app.route("/api/income_trend")
def income_trend():
    trend = calculate_income_trend(payments)
    return jsonify(trend)


@app.route("/api/activity_heatmap")
def activity_heatmap():
    heatmap = calculate_activity_heatmap(members)
    return jsonify(heatmap)


@app.route("/api/nz_city_distribution")
def nz_city_distribution():
    distribution = calculate_nz_distribution(members)
    return jsonify(distribution)


@app.route("/api/new_members")
def new_members():
    new_members_data = calculate_new_members(members)
    return jsonify(new_members_data)


if __name__ == "__main__":
    app.run(debug=True)
