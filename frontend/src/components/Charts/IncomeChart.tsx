import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { IncomeData } from "../../model/types";

interface IncomeChartProps {
    data: IncomeData[];
}

const IncomeChart: React.FC<IncomeChartProps> = ({ data }) => {
    if (data.length === 0) {
        return (
            <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Income Trend</h2>
                <p>No income data available</p>
            </div>
        );
    }

    const formatDate = (month: string) => {
        // Append "-01" to make it a full date (YYYY-MM-DD) for parsing
        return new Date(`${month}-01`);
    };

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Income Trend</h2>
            <ResponsiveContainer width="100%" height={400}>
                <LineChart data={data} margin={{ top: 20, right: 30, bottom: 50, left: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="Month" // Using the correct key for month
                        tickFormatter={(tick) => {
                            const date = formatDate(tick); // Parse the date correctly
                            return !isNaN(date.getTime())
                                ? date.toLocaleDateString("en-US", {
                                      year: "numeric",
                                      month: "short",
                                  })
                                : "Invalid Date";
                        }}
                    />
                    <YAxis tickFormatter={(value) => `$${value}`} />
                    <Tooltip
                        formatter={(value: number) => [`$${value}`, "Amount"]}
                        labelFormatter={(label: string) => {
                            const date = formatDate(label); // Parse the date correctly
                            return !isNaN(date.getTime())
                                ? date.toLocaleDateString("en-US", {
                                      year: "numeric",
                                      month: "short",
                                  })
                                : "Invalid Date";
                        }}
                    />
                    <Line
                        type="monotone"
                        dataKey="Amount" // Using the correct key for amount
                        stroke="#8884d8"
                        strokeWidth={2}
                        dot={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default IncomeChart;
