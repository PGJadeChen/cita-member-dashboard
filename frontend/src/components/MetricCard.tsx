import React from "react";
import { MetricCardProps } from "../model/types";

const MetricCard: React.FC<MetricCardProps> = ({ title, value }) => {
    return (
        <div className="backdrop-blur-lg bg-white/50 overflow-hidden transform hover:scale-105 transition-transform duration-300 rounded-xl">
            <div className="px-6 py-5 sm:p-6 flex flex-col items-center justify-center h-full">
                <dt className="text-lg font-medium tracking-widest uppercase">{title}</dt>
                <dd className="mt-2 text-4xl font-bold font-georgia tracking-wide">{value}</dd>
            </div>
        </div>
    );
};

export default MetricCard;
