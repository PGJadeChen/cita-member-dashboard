import React from "react";
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    LabelList,
} from "recharts";
import { RegionDistribution } from "../../model/types";

// Helper function to decode HTML entities like &#039; to an apostrophe
const decodeHtmlEntities = (str: string) => {
    const parser = new DOMParser();
    const decodedString = parser.parseFromString(`<!doctype html><body>${str}`, "text/html").body.textContent;
    return decodedString || str; // Fallback to the original string if decoding fails
};

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

const RegionDistributionChart: React.FC<{ data: RegionDistribution | null }> = ({ data }) => {
    if (!data || (!Array.isArray(data.mainRegions) && !Array.isArray(data.otherRegions))) {
        return (
            <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Region Distribution</h2>
                <p>No data available for Region Distribution</p>
            </div>
        );
    }

    // Decode HTML entities in region names
    const mainRegionsData = data.mainRegions.map((region) => ({
        ...region,
        region: decodeHtmlEntities(region.region), // Decode region name
    }));

    const otherRegionsData = data.otherRegions
        .filter((region) => region.region !== "Unknown")
        .map((region) => ({
            ...region,
            region: decodeHtmlEntities(region.region), // Decode region name
        }))
        .sort((a, b) => b.memberCount - a.memberCount);

    const CustomizedPieLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, region }: any) => {
        const RADIAN = Math.PI / 180;
        const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);

        return (
            <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central">
                <tspan x={x} dy="-0.5em">
                    {region} {/* Decoded region name */}
                </tspan>
                <tspan x={x} dy="1.2em">{`${(percent * 100).toFixed(0)}%`}</tspan>
            </text>
        );
    };

    const CustomizedBarLabel = (props: any) => {
        const { x, y, width, value } = props;
        return (
            <text x={x + width + 5} y={y + 15} fill="#666" textAnchor="start" fontSize={12}>
                {value}
            </text>
        );
    };

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const regionName = payload[0].payload.region; // Access region from payload
            return (
                <div className="bg-white border border-gray-300 p-2 shadow-md">
                    <p className="font-semibold">{regionName}</p> {/* Display region name */}
                    <p>{`Number of Members: ${payload[0].value}`}</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="backdrop-blur-lg bg-white/50 shadow rounded-lg p-6">
            <div className="flex flex-col md:flex-row justify-around items-stretch gap-8">
                <div className="w-full md:w-1/3 flex flex-col">
                    <h3 className="text-lg font-semibold mb-2 text-center">Main Regions</h3>
                    <div className="flex-grow" style={{ minHeight: "400px" }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={mainRegionsData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={<CustomizedPieLabel />}
                                    outerRadius={150}
                                    fill="#8884d8"
                                    dataKey="memberCount"
                                >
                                    {mainRegionsData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} /> {/* Use CustomTooltip */}
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
                <div className="w-full md:w-2/3 flex flex-col">
                    <h3 className="text-lg font-semibold mb-2 text-center">Other Regions</h3>
                    <div className="flex-grow" style={{ minHeight: "400px" }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={otherRegionsData}
                                layout="vertical"
                                margin={{
                                    top: 5,
                                    right: 0,
                                    left: 50,
                                    bottom: 5,
                                }}
                            >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" />
                                <YAxis
                                    dataKey="region"
                                    type="category"
                                    width={100}
                                    tick={{ fontSize: 12 }}
                                    interval={0} // Ensure all labels are shown
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Bar dataKey="memberCount" fill="#8884d8">
                                    <LabelList content={<CustomizedBarLabel />} />
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegionDistributionChart;
