import React, { useState, useEffect } from "react";
import MetricCard from "./MetricCard";
import RegionDistributionChart from "./Charts/RegionDistributionChart";
import MembershipStatusChart from "./Charts/MembershipStatusChart";
import PaymentDistribution from "./Charts/PaymentDistribution";
import RenewalFunnelChart from "./Charts/RenewalFunnelChart";
import IncomeChart from "./Charts/IncomeChart";
import NZCityMap from "./Charts/NZCityMap";
import MemberActivityChart from "./Charts/MemberActivityChart";
import NewMembersChart from "./Charts/NewMembersChart";
import { fetchFromAPI } from "../utils/api";
import {
    KeyMetrics,
    RegionDistribution,
    MembershipStatus,
    MembershipType,
    RenewalStatus,
    IncomeData,
    CityDistribution,
    ActivityData,
    NewMembersData,
    RegionData,
} from "../model/types";

// 数据转换函数
const convertKeyMetrics = (data: any): KeyMetrics => ({
    totalMembers: data.total_members,
    activeMembers: data.active_members,
    newMembersThisMonth: data.new_members_this_month,
});

const convertRegionDistribution = (data: any): RegionDistribution => ({
    mainRegions: data.main_regions.map(
        (r: any): RegionData => ({
            region: r.Region,
            memberCount: r["Number of Members"],
            name: r.Region,
            value: r["Number of Members"],
        })
    ),
    otherRegions: data.other_regions.map(
        (r: any): RegionData => ({
            region: r.Region,
            memberCount: r["Number of Members"],
            name: r.Region,
            value: r["Number of Members"],
        })
    ),
});

const Dashboard: React.FC = () => {
    const [keyMetrics, setKeyMetrics] = useState<KeyMetrics | null>(null);
    const [regionData, setRegionData] = useState<RegionDistribution | null>(null);
    const [membershipStatus, setMembershipStatus] = useState<MembershipStatus | null>(null);
    const [membershipType, setMembershipType] = useState<MembershipType | null>(null);
    const [renewalStatus, setRenewalStatus] = useState<RenewalStatus | null>(null);
    const [incomeTrend, setIncomeTrend] = useState<IncomeData[] | null>(null);
    const [cityDistribution, setCityDistribution] = useState<CityDistribution[] | null>(null);
    const [activityHeatmap, setActivityHeatmap] = useState<ActivityData[] | null>(null);
    const [newMembers, setNewMembers] = useState<NewMembersData[] | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [
                    keyMetricsData,
                    regionDistributionData,
                    membershipStatusData,
                    membershipTypeData,
                    renewalStatusData,
                    incomeTrendData,
                    activityHeatmapData,
                    nzCityDistributionData,
                    newMembersData,
                ] = await Promise.all([
                    fetchFromAPI<any>("/api/key_metrics"),
                    fetchFromAPI<any>("/api/region_distribution"),
                    fetchFromAPI<MembershipStatus>("/api/membership_status"),
                    fetchFromAPI<MembershipType>("/api/payment_distribution"),
                    fetchFromAPI<RenewalStatus>("/api/renewal_funnel"),
                    fetchFromAPI<IncomeData[]>("/api/income_trend"),
                    fetchFromAPI<ActivityData[]>("/api/activity_heatmap"),
                    fetchFromAPI<CityDistribution[]>("/api/nz_city_distribution"),
                    fetchFromAPI<NewMembersData[]>("/api/new_members"),
                ]);

                setKeyMetrics(convertKeyMetrics(keyMetricsData));
                setRegionData(convertRegionDistribution(regionDistributionData));
                setMembershipStatus(membershipStatusData);
                setMembershipType(membershipTypeData);
                setRenewalStatus(renewalStatusData);
                setIncomeTrend(incomeTrendData);
                setActivityHeatmap(activityHeatmapData);
                setCityDistribution(nzCityDistributionData);
                setNewMembers(newMembersData);
            } catch (error) {
                console.error("Failed to fetch data:", error);
                setError("An error occurred while fetching data. Please try again later.");
            }
        };

        fetchData();
    }, []);

    if (error) return <div className="text-red-500 text-center py-4">{error}</div>;
    if (!keyMetrics) return <div className="text-center py-4">Loading...</div>;

    return (
        <div className="w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
            {/* Metrics Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 w-full">
                <MetricCard title="Total Members" value={keyMetrics.totalMembers} />
                <MetricCard title="Active Members" value={keyMetrics.activeMembers} />
                <MetricCard title="New Members This Month" value={keyMetrics.newMembersThisMonth} />
            </div>

            {/* Region Distribution */}
            <div className="backdrop-blur-lg bg-white/10 shadow-xl rounded-lg p-6 w-full">
                <RegionDistributionChart data={regionData} />
            </div>

            {/* Membership Status, Membership Type, and Renewal Funnel */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full">
                <div className="shadow-xl rounded-lg p-4 backdrop-blur-lg bg-white/10">
                    <MembershipStatusChart data={membershipStatus} />
                </div>
                <div className="shadow-xl rounded-lg p-4 backdrop-blur-lg bg-white/10">
                    <RenewalFunnelChart data={renewalStatus} />
                </div>
                <div className="shadow-xl rounded-lg p-4 backdrop-blur-lg bg-white/10">
                    <PaymentDistribution data={membershipType} />
                </div>
            </div>

            {/* Member Activity Heatmap */}
            <div className="backdrop-blur-lg bg-white/10 shadow-xl rounded-lg p-6 w-full">
                <MemberActivityChart data={activityHeatmap} />
            </div>

            {/* New Members Chart */}
            <div className="backdrop-blur-lg bg-white/10 shadow-xl rounded-lg p-6 w-full">
                <NewMembersChart data={newMembers} />
            </div>

            {/* NZ City Map */}
            <div className="backdrop-blur-lg bg-white/10 shadow-xl rounded-lg w-full">
                <div className="text-center text-xl font-bold pt-6">Member Geographical Distribution</div>
                <NZCityMap data={cityDistribution} />
            </div>
        </div>
    );
};

export default Dashboard;
