'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, Component } from '@/lib/api';
import { Package, Search, Plus, Save, X, Code, FileText, Bot, Zap, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function RegistryPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null);
  const [selectedType, setSelectedType] = useState<string>('agent');
  const [editContent, setEditContent] = useState('');

  const { data: components, isLoading } = useQuery({
    queryKey: ['registry'],
    queryFn: api.getRegistry,
  });

  const { data: compDetail } = useQuery({
    queryKey: ['component', selectedComponent?.type, selectedComponent?.id],
    queryFn: () => api.getComponent(selectedComponent!.type, selectedComponent!.id),
    enabled: !!selectedComponent,
  });

  const mutation = useMutation({
    mutationFn: (content: string) => 
      api.upsertComponent(selectedComponent!.type, selectedComponent!.id, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['component', selectedComponent?.type, selectedComponent?.id] });
      alert('Component saved successfully!');
    },
  });

  const types = ['agent', 'workflow', 'tool', 'guardrail'];

  const filteredItems = components?.filter(c => 
    c.type === selectedType &&
    (c.id.toLowerCase().includes(search.toLowerCase()) || 
     c.name?.toLowerCase().includes(search.toLowerCase()))
  ) || [];

  const getIcon = (type: string) => {
    switch (type) {
      case 'agent': return Bot;
      case 'workflow': return Zap;
      case 'tool': return Code;
      case 'guardrail': return Shield;
      default: return Package;
    }
  };

  const handleEdit = (comp: Component) => {
    setSelectedComponent(comp);
    setEditContent(''); // Will be populated by the query
  };

  React.useEffect(() => {
    if (compDetail) {
      setEditContent(compDetail.content);
    }
  }, [compDetail]);

  return (
    <div className="p-8 h-full flex flex-col space-y-6 max-w-7xl mx-auto">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-[#F8F8F2] tracking-tight">Registry Manager</h1>
          <p className="text-[#75715E] mt-1">Manage your library of Agents, Workflows, and Tools.</p>
        </div>
      </header>

      <div className="flex gap-8 flex-1 overflow-hidden">
        {/* Sidebar List */}
        <div className="w-80 flex flex-col gap-6">
          {/* Tabs */}
          <div className="flex bg-[#1e1f1c] p-1 rounded-xl border border-[#49483e]">
            {types.map((type) => {
              const Icon = getIcon(type);
              const isActive = selectedType === type;
              return (
                <button
                  key={type}
                  onClick={() => setSelectedType(type)}
                  title={type.charAt(0).toUpperCase() + type.slice(1) + 's'}
                  className={cn(
                    "flex-1 flex items-center justify-center py-2 rounded-lg transition-all",
                    isActive 
                      ? "bg-[#A6E22E] text-[#272822] shadow-sm" 
                      : "text-[#75715E] hover:text-[#F8F8F2]"
                  )}
                >
                  <Icon className="w-4 h-4" />
                </button>
              );
            })}
          </div>

          <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#75715E] group-focus-within:text-[#66D9EF] transition-colors" />
            <input 
              type="text" 
              placeholder={`Search ${selectedType}s...`}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#1e1f1c] border border-[#49483e] rounded-xl py-2 pl-10 pr-4 text-sm text-[#F8F8F2] placeholder:text-[#49483e] focus:outline-none focus:ring-2 focus:ring-[#66D9EF]/50 transition-all"
            />
          </div>

          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
            {isLoading ? (
              <div className="text-[#75715E] text-center py-8">Loading...</div>
            ) : (
              <div className="space-y-1">
                {filteredItems.length > 0 ? filteredItems.map((comp) => {
                  const Icon = getIcon(comp.type);
                  const isSelected = selectedComponent?.id === comp.id;
                  return (
                    <button
                      key={comp.id}
                      onClick={() => handleEdit(comp)}
                      className={cn(
                        "w-full flex items-center gap-3 p-3 rounded-xl border transition-all text-left group",
                        isSelected 
                          ? "bg-[#49483e] border-[#75715E] text-[#A6E22E]" 
                          : "bg-[#1e1f1c]/50 border-[#49483e] text-[#75715E] hover:border-[#75715E] hover:bg-[#272822]"
                      )}
                    >
                      <div className={cn(
                        "w-8 h-8 rounded-lg flex items-center justify-center transition-colors",
                        isSelected ? "bg-[#A6E22E]/20" : "bg-[#272822] group-hover:bg-[#1e1f1c]"
                      )}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-sm truncate text-[#F8F8F2]">{comp.id}</div>
                      </div>
                    </button>
                  );
                }) : (
                  <div className="text-center py-12 text-[#75715E] italic text-sm">
                    No {selectedType}s found.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Editor Area */}
        <div className="flex-1 bg-[#1e1f1c] border border-[#49483e] rounded-3xl overflow-hidden flex flex-col relative">
          {selectedComponent ? (
            <>
              <div className="flex items-center justify-between px-6 py-4 border-b border-[#49483e] bg-[#272822]">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#1e1f1c] rounded-xl flex items-center justify-center text-[#75715E]">
                    {React.createElement(getIcon(selectedComponent.type), { className: "w-5 h-5 text-[#FD971F]" })}
                  </div>
                  <div>
                    <h2 className="font-bold text-[#F8F8F2]">{selectedComponent.id}</h2>
                    <p className="text-[10px] uppercase tracking-widest text-[#75715E] font-bold">{selectedComponent.type}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => mutation.mutate(editContent)}
                    disabled={mutation.isPending}
                    className="flex items-center gap-2 bg-[#A6E22E] hover:bg-[#A6E22E]/90 text-[#272822] px-4 py-2 rounded-xl text-sm font-bold transition-all active:scale-95 disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                    Save Changes
                  </button>
                  <button 
                    onClick={() => setSelectedComponent(null)}
                    className="p-2 text-[#75715E] hover:text-[#F8F8F2] transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <div className="flex-1 relative">
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  spellCheck={false}
                  className="absolute inset-0 w-full h-full bg-transparent p-8 font-mono text-sm text-[#F8F8F2] resize-none focus:outline-none custom-scrollbar"
                />
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-[#75715E] gap-4">
              <div className="w-16 h-16 bg-[#272822] rounded-2xl flex items-center justify-center">
                <FileText className="w-8 h-8 opacity-20" />
              </div>
              <p>Select a component to view or edit its source code.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
