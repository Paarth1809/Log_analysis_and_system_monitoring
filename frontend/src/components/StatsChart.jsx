import React from 'react';
import { BarChart, Bar, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from 'recharts';

export default function StatsChart({ data, title, color = "#3b82f6", type = "bar" }) {
    const ChartComponent = type === 'area' ? AreaChart : BarChart;
    const hasData = data && data.length > 0 && data.some(d => d.value > 0);

    return (
        <div className="bg-slate-800/50 backdrop-blur-md p-6 rounded-2xl border border-slate-700/50 shadow-xl h-[350px] flex flex-col">
            <h3 className="text-lg font-bold mb-6 text-white flex items-center gap-2">
                <span className="w-1 h-6 rounded-full" style={{ backgroundColor: color }}></span>
                {title}
            </h3>
            <div className="flex-1 w-full min-h-0 relative">
                {!hasData ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
                        <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-2">
                            <span className="text-2xl opacity-50">?</span>
                        </div>
                        <p className="text-sm">No data available</p>
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <ChartComponent data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <defs>
                                <linearGradient id={`color${title}`} x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                                    <stop offset="95%" stopColor={color} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                            <XAxis
                                dataKey="name"
                                stroke="#94a3b8"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                dy={10}
                            />
                            <YAxis
                                stroke="#94a3b8"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#0f172a',
                                    border: '1px solid #334155',
                                    borderRadius: '8px',
                                    color: '#fff',
                                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                                }}
                                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                            />
                            {type === 'area' ? (
                                <Area
                                    type="monotone"
                                    dataKey="value"
                                    stroke={color}
                                    fillOpacity={1}
                                    fill={`url(#color${title})`}
                                    strokeWidth={2}
                                />
                            ) : (
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {data.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={color} />
                                    ))}
                                </Bar>
                            )}
                        </ChartComponent>
                    </ResponsiveContainer>
                )}
            </div>
        </div>
    );
}
