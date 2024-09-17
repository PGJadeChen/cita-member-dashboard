import { useMemo } from "react";
import ReactECharts from "echarts-for-react";

const MemberActivityChart = ({ data }) => {
    const options = useMemo(() => {
        const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);

        const formattedData = data.map((item) => [item.Hour, item.DayOfWeek, item.Count]);
        const maxCount = Math.max(...data.map((item) => item.Count));

        return {
            tooltip: {
                position: "top",
                formatter: function (params) {
                    return `Day: ${days[params.value[1]]}<br>Hour: ${params.value[0]}:00<br>Count: ${params.value[2]}`;
                },
            },
            grid: {
                height: "80%",
                top: "7%",
                right: "8%",
                left: "8%",
            },
            xAxis: {
                type: "category",
                data: hours,
                splitArea: {
                    show: true,
                },
                axisLabel: {
                    rotate: 45,
                    fontSize: 12,
                },
            },
            yAxis: {
                type: "category",
                data: days,
                splitArea: {
                    show: true,
                },
            },
            visualMap: {
                min: 0,
                max: maxCount,
                calculable: true,
                orient: "vertical",
                right: "2%",
                top: "center",
                dimension: 2,
                inRange: {
                    color: ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"],
                },
            },
            series: [
                {
                    name: "Member Activity",
                    type: "heatmap",
                    data: formattedData,
                    label: {
                        show: false,
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: "rgba(0, 0, 0, 0.5)",
                        },
                    },
                    itemStyle: {
                        borderColor: "#fff",
                        borderWidth: 1,
                    },
                },
            ],
        };
    }, [data]);

    return (
        <div className="backdrop-blur-lg bg-white/50 shadow rounded-lg p-6 w-full">
            <h2 className="text-xl font-semibold mb-4 text-center">Member Activity Heatmap</h2>
            <ReactECharts option={options} style={{ height: "400px" }} />
        </div>
    );
};

export default MemberActivityChart;
