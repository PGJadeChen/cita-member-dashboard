import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import nzGeoJson from "./gadm41_NZL_2.json"; 
import { MapProps } from "../../model/types";

const NZCityMap: React.FC<MapProps> = ({ data }) => {
    const svgRef = useRef<SVGSVGElement | null>(null);

    useEffect(() => {
        const container = svgRef.current.parentElement;
        const width = container.offsetWidth; 
        const height = 800; 

        const projection = d3
            .geoMercator()
            .center([172, -41]) 
            .scale(2000) 
            .translate([width / 2, height / 2]);

        const pathGenerator = d3.geoPath().projection(projection);
        const svg = d3.select(svgRef.current).attr("width", width).attr("height", height);

        svg.selectAll("*").remove();

        const tooltip = d3
            .select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0)
            .style("position", "absolute")
            .style("background-color", "white")
            .style("border", "1px solid #ddd")
            .style("padding", "10px");

        const provinceDataMap = new Map(data.map((province) => [province.name, province]));

        const customColorScheme = d3
            .scaleQuantile()
            .domain([0, d3.max(data.map((d) => d.value))])
            .range(["#0088FE", "#00C49F", "#FFBB28", "#FF8042"]); 

        svg.selectAll("path")
            .data(nzGeoJson.features)
            .enter()
            .append("path")
            .attr("d", pathGenerator)
            .attr("fill", (d) => {
                const regionName = d.properties.NAME_1; 
                const province = provinceDataMap.get(regionName);
                return province ? customColorScheme(province.value) : "#ccc"; 
            })
            .attr("stroke", "#000")
            .attr("stroke-width", 0.5)
            .on("mouseover", (event, d) => {
                const regionName = d.properties.NAME_1;
                const province = provinceDataMap.get(regionName);

                if (province) {
                    const cityList = province.children.map((city) => `<li>${city.name}: ${city.value}</li>`).join("");
                    const tooltipContent = `
                        <strong>${regionName}</strong>(${province.value})<br>
                        <ul>${cityList}</ul>
                    `;

                    tooltip.transition().duration(200).style("opacity", 0.9);
                    tooltip
                        .html(tooltipContent)
                        .style("left", event.pageX + 10 + "px")
                        .style("top", event.pageY - 30 + "px");
                }
            })
            .on("mousemove", (event) => {
                tooltip.style("left", event.pageX + 10 + "px").style("top", event.pageY - 30 + "px");
            })
            .on("mouseout", () => {
                tooltip.transition().duration(300).style("opacity", 0);
            });

        const resizeHandler = () => {
            const newWidth = container.offsetWidth;
            projection.translate([newWidth / 2, height / 2]);
            svg.attr("width", newWidth);
            svg.selectAll("path").attr("d", pathGenerator);
        };
        window.addEventListener("resize", resizeHandler);

        return () => {
            window.removeEventListener("resize", resizeHandler); 
        };
    }, [data]);

    return (
        <div>
            <svg ref={svgRef} />
        </div>
    );
};

export default NZCityMap;
