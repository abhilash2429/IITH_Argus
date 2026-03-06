'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface NodeData {
  id: string;
  type: 'company' | 'counterparty';
}

interface LinkData {
  source: string;
  target: string;
  value: number;
}

export default function FraudGraph({
  nodes,
  links,
}: {
  nodes: NodeData[];
  links: LinkData[];
}) {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const width = 560;
    const height = 320;
    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();

    const simulation = d3
      .forceSimulation(nodes as any)
      .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(110))
      .force('charge', d3.forceManyBody().strength(-260))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#6f8e5f')
      .attr('stroke-opacity', 0.7)
      .attr('stroke-width', (d) => Math.max(1, d.value / 20));

    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', (d) => (d.type === 'company' ? 13 : 9))
      .attr('fill', (d) => (d.type === 'company' ? '#4cbb17' : '#7ba95a'))
      .call(
        d3
          .drag<any, any>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    const text = svg
      .append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .text((d) => d.id)
      .attr('font-size', 11)
      .attr('fill', '#e8f2df');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
      text.attr('x', (d: any) => d.x + 11).attr('y', (d: any) => d.y + 4);
    });

    return () => {
      simulation.stop();
    };
  }, [links, nodes]);

  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
      <h3 className="text-white font-semibold text-lg mb-3">Fraud Fingerprinting Graph</h3>
      <svg ref={ref} width={560} height={320} className="w-full h-auto rounded bg-slate-900/50" />
    </div>
  );
}
