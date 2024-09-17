import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface PaymentDistributionProps {
    data: { Amount: number; Count: number }[];
}

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#FF0000", "#AA00FF"];

const PaymentDistribution: React.FC<PaymentDistributionProps> = ({ data }) => {
    // Custom label for the pie chart slices
    const CustomizedPieLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, Amount }: any) => {
        const RADIAN = Math.PI / 180;
        const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);

        return (
            <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central">
                <tspan x={x} dy="-0.5em">{`$${Amount}`}</tspan>
                <tspan x={x} dy="1.2em">{`${(percent * 100).toFixed(0)}%`}</tspan>
            </text>
        );
    };

    return (
        <div className="backdrop-blur-lg bg-white/50  shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-center">Payment Distribution</h2>
            <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        outerRadius={140}
                        fill="#8884d8"
                        dataKey="Count"
                        nameKey="Amount"  // This ensures the Amount is linked in the legend
                        label={<CustomizedPieLabel />}
                        labelLine={false} // Hide default connection lines
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip
                        formatter={(value: number, name: string, props) => [
                            `Count: ${value}`,
                            `Amount: $${props.payload.Amount}`,
                        ]}
                    />
                    {/* Adding the custom legend */}
                    <Legend
                        layout="horizontal"
                        verticalAlign="bottom"
                        align="center"
                        formatter={(value, entry) => `$${entry.payload.Amount}`} // Display Amount in the legend
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PaymentDistribution;
