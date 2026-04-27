'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Activity, 
  Database, 
  Package, 
  FileCode, 
  Settings 
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Dashboard', icon: LayoutDashboard, href: '/' },
  { name: 'Traces', icon: Activity, href: '/traces' },
  { name: 'Registry', icon: Package, href: '/registry' },
  { name: 'Artifacts', icon: Database, href: '/artifacts' },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#1e1f1c] border-r border-[#49483e] flex flex-col">
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[#A6E22E] rounded flex items-center justify-center font-bold text-[#272822]">
            A
          </div>
          <span className="font-bold text-xl tracking-tight text-[#F8F8F2]">AGNO</span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-2 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive 
                  ? "bg-[#49483e] text-[#66D9EF] border border-[#75715E]" 
                  : "text-[#75715E] hover:bg-[#272822] hover:text-[#F8F8F2]"
              )}
            >
              <item.icon className="w-4 h-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-[#49483e]">
        <div className="flex items-center gap-2 px-3 py-2 text-xs text-[#75715E]">
          <div className="w-2 h-2 rounded-full bg-[#A6E22E] animate-pulse" />
          System Online
        </div>
      </div>
    </aside>
  );
};
