import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface RenewalFunnelProps {
    data: Record<string, number>;
}

// Using consistent colors across charts
const COLORS = ["#0088FE", "#FF8042"];

const RenewalFunnelChart: React.FC<RenewalFunnelProps> = ({ data }) => {
    // Convert object data into a format compatible with recharts
    const chartData = Object.entries(data).map(([name, value]) => ({
        name,
        value,
    }));

    // Custom pie chart label, ensuring consistency with other charts
    const CustomizedPieLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }: any) => {
        const RADIAN = Math.PI / 180;
        const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);

        return (
            <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central">
                <tspan x={x} dy="-0.5em">
                    {name}
                </tspan>
                <tspan x={x} dy="1.2em">{`${(percent * 100).toFixed(0)}%`}</tspan>
            </text>
        );
    };

    return (
        <div className="backdrop-blur-lg bg-white/50  shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-center">Renewal Funnel</h2>
            <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50} // Space in the middle
                        outerRadius={140}
                        fill="#8884d8"
                        dataKey="value"
                        label={<CustomizedPieLabel />}
                        labelLine={false} // Hide default lines to keep style consistent
                    >
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => [`${value}`, "Count"]} />
                    {/* Add the legend below the pie chart */}
                    <Legend
                        layout="horizontal"
                        verticalAlign="bottom"
                        align="center"
                        formatter={(value, entry) => `${entry.payload.name}`} // Show the name in the legend
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RenewalFunnelChart;
