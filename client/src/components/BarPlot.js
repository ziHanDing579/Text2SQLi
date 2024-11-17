import { useRef, useEffect} from "react";
import * as d3 from "d3";

export default function BarPlot({data}){

    const svgRef = useRef();

    useEffect(() => {

        // Setup svg

        const width = 640;
        const height = 400;

        const MARGIN = { top: 30, right: 30, bottom: 50, left: 30 };

        const boundsWidth = width - MARGIN.right - MARGIN.left;
        const boundsHeight = height - MARGIN.top - MARGIN.bottom;


        const svg = d3.select(svgRef.current)
            .attr('width', boundsWidth)
            .attr('height', boundsHeight + MARGIN.top)
            .style('margin-top', MARGIN.top)
            .style('margin-left', MARGIN.left)
            .style('overflow', 'visible')
            .style('overflow-y', 'visible')

        // Setup scaling


        // Get max Y for top range of axis
        const max = d3.max(data, (d) => typeof d.y === 'string' ? parseFloat(d.y) : d.y);
        console.log(`yMax: ${max}`)
        const yScale = d3
            .scaleLinear()
            .domain([0, max || boundsHeight])
            .range([boundsHeight, 0]);

        // Get max (categorical) x
        const xMax = d3.max(data, (d) => d.x);
        console.log(`xMax: ${xMax}`)
        const xScale = d3
            .scaleBand()
            .domain(data.map(d => d.x))
            .range([0, boundsWidth])
            .padding(0.3);

        // Set axes

        const xAxis = d3.axisBottom(xScale)
        .ticks(data.length)

        const yAxis = d3.axisLeft(yScale);

        svg.append('g')
        .call(xAxis)
        .attr("transform", `translate(0, ${boundsHeight})`)

        svg.append('g')
        .call(yAxis)

        // Setup data
        svg.selectAll('.bar')
        .data(data)
        .join('rect')
        .attr('x', (d => xScale(d.x)))
        .attr('y', (d => yScale(d.y)))
        .attr('width', xScale.bandwidth())
        .attr('height', (d =>  d.y === null ? 0 : boundsHeight - yScale(d.y)))
        .attr('stroke', '#818cf8')
        .attr('fill', '#818cf8')
    }, [data])

    return(
        <div className="py-2">
            <svg ref={svgRef}></svg>
        </div>
    );
}