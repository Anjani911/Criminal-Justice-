import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { networkService } from '@/services/network.service';
import { motion } from 'framer-motion';
import { GitCommit, Network, ShieldAlert, FileText, Lock, Search, Filter } from 'lucide-react';
import type { NetworkNode } from '@/types';

export default function NetworkPage() {
  const { data: network, isLoading: isNetworkLoading } = useQuery({
    queryKey: ['network'],
    queryFn: networkService.getFullNetwork,
  });

  const { data: metrics, isLoading: isMetricsLoading } = useQuery({
    queryKey: ['networkMetrics'],
    queryFn: networkService.getMetrics,
  });

  const [selectedNode, setSelectedNode] = useState<NetworkNode['data'] | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const nodes = network?.nodes ?? [];
  const edges = network?.edges ?? [];

  const filteredNodes = nodes.filter((n) => {
    const matchesType = filterType === 'all' || n.data.node_type === filterType;
    const matchesSearch =
      !searchTerm ||
      n.data.label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.data.id?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesType && matchesSearch;
  });

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'case':
        return 'border-sky-500 bg-sky-950/80 text-sky-300 shadow-sky-900/30';
      case 'accused':
        return 'border-amber-500 bg-amber-950/80 text-amber-300 shadow-amber-900/30';
      case 'arrest':
        return 'border-purple-500 bg-purple-950/80 text-purple-300 shadow-purple-900/30';
      default:
        return 'border-slate-700 bg-slate-900 text-slate-300';
    }
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'case':
        return <FileText size={16} className="text-sky-400" />;
      case 'accused':
        return <ShieldAlert size={16} className="text-amber-400" />;
      case 'arrest':
        return <Lock size={16} className="text-purple-400" />;
      default:
        return <GitCommit size={16} className="text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-medium text-sky-400">Criminal Intelligence Network</p>
          <h2 className="text-2xl font-semibold tracking-tight">Interactive Entity Link Graph</h2>
        </div>
        {network?.metadata && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-sky-500/30 bg-sky-500/10 px-3 py-1 text-xs text-sky-300">
              Nodes: {network.metadata.node_count}
            </span>
            <span className="rounded-full border border-purple-500/30 bg-purple-500/10 px-3 py-1 text-xs text-purple-300">
              Edges: {network.metadata.edge_count}
            </span>
          </div>
        )}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
        {/* GRAPH VISUALIZATION AREA */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
        >
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2">
              <Network size={20} className="text-sky-400" />
              <h3 className="text-lg font-semibold">Graph Network Visualization</h3>
            </div>
            {/* Filter & Search Bar */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search entity..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="rounded-xl border border-slate-700 bg-slate-950/80 py-1.5 pl-8 pr-3 text-xs outline-none focus:border-sky-500"
                />
              </div>
              <div className="flex items-center gap-1 rounded-xl border border-slate-700 bg-slate-950/80 p-1">
                <Filter size={12} className="ml-1 text-slate-400" />
                {(['all', 'case', 'accused', 'arrest'] as const).map((type) => (
                  <button
                    key={type}
                    onClick={() => setFilterType(type)}
                    className={`rounded-lg px-2 py-1 text-xs capitalize transition ${
                      filterType === type ? 'bg-sky-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Canvas Graph Board */}
          <div className="relative mt-4 flex min-h-[420px] flex-1 flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-950/90 p-6">
            {isNetworkLoading ? (
              <div className="text-sm text-slate-400">Loading graph data from backend...</div>
            ) : filteredNodes.length === 0 ? (
              <div className="text-sm text-slate-400">No matching nodes found.</div>
            ) : (
              <div className="w-full">
                {/* Node Grid Layout */}
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {filteredNodes.map((node) => {
                    const isSelected = selectedNode?.id === node.data.id;
                    const connectedEdgeCount = edges.filter(
                      (e) => e.data.source === node.data.id || e.data.target === node.data.id
                    ).length;

                    return (
                      <motion.div
                        key={node.data.id}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => setSelectedNode(node.data)}
                        className={`cursor-pointer rounded-2xl border p-4 shadow-lg transition ${getNodeColor(
                          node.data.node_type
                        )} ${isSelected ? 'ring-2 ring-sky-400 ring-offset-2 ring-offset-slate-950' : ''}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            {getNodeIcon(node.data.node_type)}
                            <span className="text-xs font-semibold uppercase tracking-wider opacity-80">
                              {node.data.node_type}
                            </span>
                          </div>
                          <span className="rounded-full bg-slate-900/60 px-2 py-0.5 text-[10px] text-slate-300">
                            {connectedEdgeCount} links
                          </span>
                        </div>
                        <p className="mt-2 text-sm font-semibold truncate">{node.data.label}</p>
                        {node.data.district && (
                          <p className="mt-1 text-xs opacity-75">{node.data.district} · {node.data.unit}</p>
                        )}
                        {node.data.status && (
                          <span className="mt-2 inline-block rounded-md bg-slate-900/80 px-2 py-0.5 text-[10px]">
                            Status: {node.data.status}
                          </span>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Selected Node Details Bar */}
          {selectedNode && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 rounded-2xl border border-sky-500/30 bg-sky-950/40 p-4 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sky-300">Selected Node Details</span>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-slate-400 hover:text-slate-200"
                >
                  Close
                </button>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-2 text-slate-300 sm:grid-cols-4">
                <div><span className="text-slate-500 block">ID</span>{selectedNode.id}</div>
                <div><span className="text-slate-500 block">Label</span>{selectedNode.label}</div>
                <div><span className="text-slate-500 block">Type</span>{selectedNode.node_type}</div>
                <div><span className="text-slate-500 block">Status</span>{selectedNode.status || 'N/A'}</div>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* METRICS & RANKED CENTRALITY */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Top Cases */}
          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <FileText size={18} className="text-sky-400" />
              Top Connected Cases
            </h3>
            <div className="mt-4 space-y-2">
              {isMetricsLoading ? (
                <p className="text-xs text-slate-400">Loading metrics...</p>
              ) : metrics?.top_cases && metrics.top_cases.length > 0 ? (
                metrics.top_cases.map((c) => (
                  <div
                    key={c.node_id}
                    className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs"
                  >
                    <div>
                      <p className="font-medium text-slate-200">{c.label}</p>
                      <p className="text-[10px] text-slate-500">{c.node_id}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sky-400 font-semibold">{Math.round(c.degree_centrality * 100)}% Centrality</p>
                      <p className="text-[10px] text-slate-400">Betw: {c.betweenness_centrality ?? 0}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500">No case rankings available.</p>
              )}
            </div>
          </div>

          {/* Top Accused */}
          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <ShieldAlert size={18} className="text-amber-400" />
              Key Accused Centrality
            </h3>
            <div className="mt-4 space-y-2">
              {isMetricsLoading ? (
                <p className="text-xs text-slate-400">Loading metrics...</p>
              ) : metrics?.top_accused && metrics.top_accused.length > 0 ? (
                metrics.top_accused.map((a) => (
                  <div
                    key={a.node_id}
                    className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs"
                  >
                    <div>
                      <p className="font-medium text-amber-200">{a.label}</p>
                      <p className="text-[10px] text-slate-500">{a.node_id}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-amber-400 font-semibold">{Math.round(a.degree_centrality * 100)}% Centrality</p>
                      <p className="text-[10px] text-slate-400">Betw: {a.betweenness_centrality ?? 0}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500">No accused rankings available.</p>
              )}
            </div>
          </div>

          {/* Top Arrests */}
          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <Lock size={18} className="text-purple-400" />
              Arrest Node Centrality
            </h3>
            <div className="mt-4 space-y-2">
              {isMetricsLoading ? (
                <p className="text-xs text-slate-400">Loading metrics...</p>
              ) : metrics?.top_arrests && metrics.top_arrests.length > 0 ? (
                metrics.top_arrests.map((ar) => (
                  <div
                    key={ar.node_id}
                    className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs"
                  >
                    <div>
                      <p className="font-medium text-purple-200">{ar.label}</p>
                      <p className="text-[10px] text-slate-500">{ar.node_id}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-purple-400 font-semibold">{Math.round(ar.degree_centrality * 100)}% Centrality</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500">No arrest rankings available.</p>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
