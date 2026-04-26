'use client';

import React, { useEffect, useRef, useState } from 'react';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

interface LogTerminalProps {
  jobId: string | null;
}

export const LogTerminal: React.FC<LogTerminalProps> = ({ jobId }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!jobId) {
      setLogs([]);
      return;
    }

    const eventSource = new EventSource(api.getLogStreamUrl(jobId));

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs((prev) => [...prev, data.message]);
    };

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="flex flex-col h-full bg-[#1e1f1c] rounded-lg border border-[#49483e] overflow-hidden font-mono text-sm">
      <div className="flex items-center justify-between px-4 py-2 bg-[#272822] border-b border-[#49483e]">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#F92672]/20 border border-[#F92672]/50" />
          <div className="w-3 h-3 rounded-full bg-[#E6DB74]/20 border border-[#E6DB74]/50" />
          <div className="w-3 h-3 rounded-full bg-[#A6E22E]/20 border border-[#A6E22E]/50" />
          <span className="ml-2 text-[#75715E] text-xs font-bold uppercase tracking-wider">terminal — {jobId || 'idle'}</span>
        </div>
      </div>
      <div 
        ref={scrollRef}
        className="flex-1 p-4 overflow-y-auto space-y-1 custom-scrollbar"
      >
        {logs.length === 0 ? (
          <div className="text-[#75715E] italic">Waiting for logs...</div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="flex gap-2">
              <span className="text-[#49483e] select-none text-right w-8">{i + 1}</span>
              <span className={cn(
                "break-all",
                log.toLowerCase().includes('error') ? 'text-[#F92672]' : 
                log.toLowerCase().includes('success') ? 'text-[#A6E22E]' :
                'text-[#F8F8F2]'
              )}>
                {log}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
