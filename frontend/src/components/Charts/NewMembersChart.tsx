import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface NewMembersChartProps {
    data: { Month: string; Count: number }[];
}

const NewMembersChart: React.FC<NewMembersChartProps> = ({ data }) => {
    return (
        <div className="backdrop-blur-lg bg-white/50  shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-center">New Members per Month</h2>
            <ResponsiveContainer width="100%" height={400}>
                <LineChart
                    data={data}
                    margin={{
                        top: 10,
                        right: 0,
                        bottom: 30, // Increased bottom margin to accommodate rotated labels
                        left: 0,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="Month"
                        tickFormatter={(tick) => {
                            const date = new Date(`${tick}-01`);
                            return date.toLocaleDateString("en-US", {
                                year: "numeric",
                                month: "short",
                            });
                        }}
                        interval={0} // Ensures that every month is displayed
                        tick={{ angle: -45, textAnchor: "end", fontSize: 12 }} // Rotating labels by -45 degrees
                    />
                    <YAxis />
                    <Tooltip formatter={(value: number) => [`${value}`, "New Members"]} />
                    <Line type="monotone" dataKey="Count" stroke="#3366cc" strokeWidth={2} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default NewMembersChart;
