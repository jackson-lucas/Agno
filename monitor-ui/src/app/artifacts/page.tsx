'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Database, FileText, Download, Clock, HardDrive } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function ArtifactsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['artifacts'],
    queryFn: api.getArtifacts,
  });

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-8 h-full flex flex-col space-y-6 max-w-7xl mx-auto">
      <header>
        <h1 className="text-3xl font-bold text-[#F8F8F2] tracking-tight">Artifact Repository</h1>
        <p className="text-[#75715E] mt-1">Manage and download generated files and datasets.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 overflow-y-auto pr-2 custom-scrollbar flex-1">
        {isLoading ? (
          <div className="col-span-full text-center py-20 text-[#75715E]">Loading artifacts...</div>
        ) : data?.artifacts?.map((file: any) => (
          <div key={file.path} className="bg-[#1e1f1c] border border-[#49483e] rounded-3xl p-6 group hover:border-[#75715E] transition-all relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
              <FileText className="w-16 h-16 text-[#66D9EF]" />
            </div>
            
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-[#272822] rounded-2xl flex items-center justify-center text-[#FD971F]">
                <FileText className="w-6 h-6" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-bold text-[#F8F8F2] truncate">{file.name}</h3>
                <p className="text-[10px] text-[#75715E] font-mono uppercase tracking-widest">{file.path.split('.').pop()}</p>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-center gap-2 text-xs text-[#75715E]">
                <HardDrive className="w-3 h-3" />
                <span>{formatSize(file.size)}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-[#75715E]">
                <Clock className="w-3 h-3" />
                <span>{new Date(file.modified * 1000).toLocaleString()}</span>
              </div>
            </div>

            <button className="w-full flex items-center justify-center gap-2 bg-[#272822] hover:bg-[#49483e] text-[#F8F8F2] py-2 rounded-xl text-sm font-bold border border-[#49483e] transition-all active:scale-95 group-hover:border-[#75715E]">
              <Download className="w-4 h-4" />
              Download
            </button>
          </div>
        ))}
        {(!data?.artifacts || data.artifacts.length === 0) && (
          <div className="col-span-full flex flex-col items-center justify-center py-32 text-[#75715E] gap-4">
            <Database className="w-16 h-16 opacity-10" />
            <p>No artifacts generated yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
