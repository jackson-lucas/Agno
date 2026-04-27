'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, Trace, Span } from '@/lib/api';
import { Activity, ChevronRight, ChevronDown, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function TracesPage() {
  const [selectedTrace, setSelectedTrace] = useState<string | null>(null);

  const { data: traces, isLoading } = useQuery({
    queryKey: ['traces'],
    queryFn: api.getTraces,
  });

  const { data: spans, isLoading: isLoadingSpans } = useQuery({
    queryKey: ['spans', selectedTrace],
    queryFn: () => api.getSpans(selectedTrace!),
    enabled: !!selectedTrace,
  });

  return (
    <div className="p-8 h-full flex flex-col space-y-6 max-w-7xl mx-auto">
      <header>
        <h1 className="text-3xl font-bold text-[#F8F8F2] tracking-tight">Observability Traces</h1>
        <p className="text-[#75715E] mt-1">Inspect the execution lifecycle of your agents and tools.</p>
      </header>

      <div className="flex gap-8 flex-1 overflow-hidden">
        {/* Trace List */}
        <div className="w-96 flex flex-col gap-4">
          <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
            {isLoading ? (
              <div className="text-[#75715E] text-center py-8">Loading traces...</div>
            ) : traces?.map((trace) => (
              <button
                key={trace.trace_id}
                onClick={() => setSelectedTrace(trace.trace_id)}
                className={cn(
                  "w-full flex flex-col gap-2 p-4 rounded-2xl border transition-all text-left",
                  selectedTrace === trace.trace_id 
                    ? "bg-[#49483e] border-[#75715E] text-[#A6E22E]" 
                    : "bg-[#1e1f1c]/50 border-[#49483e] text-[#75715E] hover:border-[#75715E] hover:bg-[#272822]"
                )}
              >
                <div className="flex justify-between items-start">
                  <div className="font-mono text-xs opacity-60 text-[#66D9EF]">{trace.trace_id.substring(0, 8)}</div>
                  <div className={cn(
                    "flex items-center gap-1 text-[10px] font-bold uppercase",
                    trace.status === 'OK' ? "text-[#A6E22E]" : "text-[#F92672]"
                  )}>
                    {trace.status === 'OK' ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                    {trace.status}
                  </div>
                </div>
                <div className="font-bold text-[#F8F8F2]">{trace.name}</div>
                <div className="flex items-center gap-3 text-xs text-[#75715E]">
                  <div className="flex items-center gap-1 font-mono"><Clock className="w-3 h-3" /> {trace.duration_ms}ms</div>
                  <div>{new Date(trace.start_time).toLocaleTimeString()}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Span Detail View */}
        <div className="flex-1 bg-[#1e1f1c] border border-[#49483e] rounded-3xl overflow-hidden flex flex-col">
          {selectedTrace ? (
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="px-6 py-4 border-b border-[#49483e] bg-[#272822]">
                <h2 className="font-bold text-[#F8F8F2]">Execution Timeline</h2>
              </div>
              <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
                {isLoadingSpans ? (
                  <div className="text-[#75715E]">Loading spans...</div>
                ) : spans?.map((span, i) => (
                  <div key={span.span_id} className="relative pl-8 group">
                    {/* Vertical Line */}
                    {i < spans.length - 1 && (
                      <div className="absolute left-3 top-6 bottom-[-20px] w-px bg-[#49483e]" />
                    )}
                    
                    {/* Dot */}
                    <div className="absolute left-1.5 top-2 w-3 h-3 rounded-full bg-[#1e1f1c] border-2 border-[#49483e] group-hover:border-[#A6E22E] transition-colors" />
                    
                    <div className="bg-[#272822] border border-[#49483e]/50 rounded-2xl p-4 hover:border-[#75715E] transition-all">
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-bold text-[#66D9EF]">{span.name}</div>
                        <div className="text-xs text-[#75715E] font-mono">{span.duration_ms}ms</div>
                      </div>
                      
                      {span.attributes && Object.keys(span.attributes).length > 0 && (
                        <div className="space-y-1 bg-[#1e1f1c] p-3 rounded-xl border border-[#49483e]/30">
                          {Object.entries(span.attributes).map(([k, v]) => (
                            <div key={k} className="text-[10px] flex gap-2">
                              <span className="text-[#F92672] uppercase font-bold w-20 shrink-0">{k}:</span>
                              <span className="text-[#E6DB74] font-mono line-clamp-2">{JSON.stringify(v)}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-[#75715E] gap-4">
              <Activity className="w-12 h-12 opacity-20" />
              <p>Select a trace from the left to view its detailed span lifecycle.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
