import React from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface MembershipStatusProps {
    data: Record<string, number>;
}

// 保持与 RegionDistributionChart 一致的颜色
const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

const MembershipStatus: React.FC<MembershipStatusProps> = ({ data }) => {
    // 将对象数据转换为适合 recharts 的格式
    const chartData = Object.entries(data).map(([name, value]) => ({
        name,
        value,
    }));

    // 自定义饼图标签，确保和 RegionDistributionChart 一致
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
            <h2 className="text-xl font-semibold mb-4 text-center">Membership Status</h2>
            <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        outerRadius={140}
                        fill="#8884d8"
                        dataKey="value"
                        label={<CustomizedPieLabel />}
                        labelLine={false} // 隐藏饼图外的连接线，风格一致
                    >
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip formatter={(value: number, name: string) => [`${value}`, `${name}`]} />
                    <Legend />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default MembershipStatus;
