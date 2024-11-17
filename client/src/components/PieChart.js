import { useRef, useEffect} from "react";
import * as d3 from "d3";

export default function PieChart({data}){

    const svgRef = useRef();

    useEffect(() => {

        // Setup svg

        const width = 400;
        const height = 400;
        const radius = width / 2;

        // Only use top, left margins to offset by radius
        const MARGIN = { top: 200, bottom: -200, left: 200 };

        const svg = d3.select(svgRef.current)
            .attr('width', width)
            .attr('height', height)
            .style('margin-top', MARGIN.top)
            .style('margin-bottom', MARGIN.bottom)
            .style('margin-left', MARGIN.left)
            .style('overflow', 'visible')
            .style('overflow-y', 'visible')

        // Format data for pie chart
        const formattedData = d3.pie().value(d => d.y)(data);
        const arcGenerator = d3.arc().innerRadius(0).outerRadius(radius);

        // Color scheme
        const color = d3.scaleOrdinal().range(d3.schemeBlues[9])

        // Add corresponding colors for data to plot
        svg.selectAll()
        .data(formattedData)
        .join('path')
        .attr('d', arcGenerator)
        .attr('fill', (d, i) => color(i))

        // Add corresponding text for data to plot
        svg.selectAll()
        .data(formattedData)
        .join('text')
        .text(d => `${d.data.x} (${typeof d.data.y === 'string' ? parseFloat(d.data.y).toFixed(2) : d.data.y.toFixed(2) }%)`)
        .attr('transform', d => `translate(${arcGenerator.centroid(d)})`)
        .style('text-anchor', 'middle')
        .style('font-weight', 'bold')

    }, [data])

    return(
        <div className="pt-4 pb-2">
            <svg ref={svgRef}></svg>
        </div>
    );
}