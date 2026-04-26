'use client';

import React, { useState } from 'react';
import { LogTerminal } from '@/components/monitor/LogTerminal';
import { api } from '@/lib/api';
import { Plus, Play, Brain, Package, Activity, Terminal as TerminalIcon } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

export default function Dashboard() {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [task, setTask] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: traces } = useQuery({
    queryKey: ['traces'],
    queryFn: () => api.getTraces(),
  });

  const handleRunJob = async () => {
    if (!task.trim()) return;
    try {
      const { job_id } = await api.createJob(task);
      setCurrentJobId(job_id);
      setIsModalOpen(false);
      setTask('');
    } catch (err) {
      console.error('Failed to run job:', err);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-[#F8F8F2] tracking-tight">Dashboard</h1>
          <p className="text-[#75715E] mt-1">Monitor and orchestrate your AI agents in real-time.</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-[#A6E22E] hover:bg-[#A6E22E]/90 text-[#272822] px-4 py-2 rounded-lg font-bold transition-all shadow-lg shadow-[#A6E22E]/20 active:scale-95"
        >
          <Plus className="w-4 h-4" />
          Create Request
        </button>
      </header>

      {/* Pipeline Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#1e1f1c] border border-[#49483e] p-6 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Brain className="w-16 h-16 text-[#66D9EF]" />
          </div>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-[#66D9EF]/10 rounded-xl flex items-center justify-center text-[#66D9EF]">
              <Brain className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-[#75715E] uppercase text-xs tracking-widest">Active Jobs</h3>
          </div>
          <div className="text-3xl font-bold text-[#F8F8F2]">{currentJobId ? 1 : 0}</div>
        </div>

        <div className="bg-[#1e1f1c] border border-[#49483e] p-6 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Activity className="w-16 h-16 text-[#A6E22E]" />
          </div>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-[#A6E22E]/10 rounded-xl flex items-center justify-center text-[#A6E22E]">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-[#75715E] uppercase text-xs tracking-widest">Total Traces</h3>
          </div>
          <div className="text-3xl font-bold text-[#F8F8F2]">{traces?.length || 0}</div>
        </div>

        <div className="bg-[#1e1f1c] border border-[#49483e] p-6 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Package className="w-16 h-16 text-[#AE81FF]" />
          </div>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-[#AE81FF]/10 rounded-xl flex items-center justify-center text-[#AE81FF]">
              <Package className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-[#75715E] uppercase text-xs tracking-widest">Registry Components</h3>
          </div>
          <div className="text-3xl font-bold text-[#F8F8F2]">12</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Log Stream Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-[#F8F8F2] font-bold uppercase tracking-widest text-xs">
            <TerminalIcon className="w-4 h-4 text-[#FD971F]" />
            Real-time Logs
          </div>
          <div className="h-[500px]">
            <LogTerminal jobId={currentJobId} />
          </div>
        </div>

        {/* Recent Traces Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-[#F8F8F2] font-bold uppercase tracking-widest text-xs">
            <Activity className="w-4 h-4 text-[#A6E22E]" />
            Recent Traces
          </div>
          <div className="bg-[#1e1f1c] border border-[#49483e] rounded-2xl overflow-hidden h-[500px]">
            <div className="overflow-auto h-full custom-scrollbar">
              <table className="w-full text-left border-collapse">
                <thead className="bg-[#272822] sticky top-0 z-10">
                  <tr>
                    <th className="px-6 py-4 text-xs font-bold text-[#75715E] uppercase tracking-wider">Trace ID</th>
                    <th className="px-6 py-4 text-xs font-bold text-[#75715E] uppercase tracking-wider">Status</th>
                    <th className="px-6 py-4 text-xs font-bold text-[#75715E] uppercase tracking-wider">Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#49483e]/50">
                  {traces?.slice(0, 10).map((trace) => (
                    <tr key={trace.trace_id} className="hover:bg-[#272822] transition-colors group">
                      <td className="px-6 py-4 text-sm font-mono text-[#66D9EF] group-hover:text-[#A6E22E]">
                        {trace.trace_id.substring(0, 8)}...
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-tighter ${
                          trace.status === 'OK' ? 'bg-[#A6E22E]/10 text-[#A6E22E]' : 'bg-[#F92672]/10 text-[#F92672]'
                        }`}>
                          {trace.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-[#75715E]">
                        {trace.duration_ms}ms
                      </td>
                    </tr>
                  ))}
                  {(!traces || traces.length === 0) && (
                    <tr>
                      <td colSpan={3} className="px-6 py-8 text-center text-[#75715E] italic">
                        No traces found yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Create Request Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-[#1e1f1c]/80 backdrop-blur-sm" onClick={() => setIsModalOpen(false)} />
          <div className="bg-[#272822] border border-[#49483e] rounded-3xl p-8 w-full max-w-lg relative z-10 shadow-2xl">
            <h2 className="text-2xl font-bold text-[#F8F8F2] mb-2">New Request</h2>
            <p className="text-[#75715E] mb-6">Describe the task you want the Agno orchestrator to solve.</p>
            
            <textarea
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="e.g. Research the latest AI trends and generate a summary report."
              className="w-full h-40 bg-[#1e1f1c] border border-[#49483e] rounded-2xl p-4 text-[#F8F8F2] placeholder:text-[#49483e] focus:outline-none focus:ring-2 focus:ring-[#66D9EF] transition-all resize-none mb-6 font-mono text-sm"
            />

            <div className="flex gap-3 justify-end">
              <button 
                onClick={() => setIsModalOpen(false)}
                className="px-6 py-2 rounded-xl text-[#75715E] hover:text-[#F8F8F2] font-bold transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={handleRunJob}
                disabled={!task.trim()}
                className="flex items-center gap-2 bg-[#A6E22E] hover:bg-[#A6E22E]/90 disabled:opacity-50 text-[#272822] px-8 py-2 rounded-xl font-bold transition-all active:scale-95"
              >
                <Play className="w-4 h-4 fill-current" />
                Execute Job
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
