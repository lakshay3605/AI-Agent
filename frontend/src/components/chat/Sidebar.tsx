"use client";

import React from "react";
import { 
  PackageCheck, 
  MessageSquare, 
  FileText, 
  Truck, 
  Sliders, 
  HelpCircle,
  Database,
  CheckCircle2,
  AlertCircle
} from "lucide-react";

interface SidebarProps {
  backendOnline: boolean | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ backendOnline }) => {
  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between hidden md:flex shrink-0">
      <div>
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-800/80 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <PackageCheck className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-semibold text-slate-100 text-sm tracking-wide">ParcelPilot AI</h1>
            <p className="text-xs text-slate-400">Support Operations</p>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="p-3 space-y-6">
          <div>
            <p className="px-3 text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-2">
              Workspace
            </p>
            <nav className="space-y-1">
              <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium bg-slate-800/80 text-blue-400 transition-colors">
                <MessageSquare className="w-4 h-4" />
                Support Chat
              </a>
              <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-colors">
                <FileText className="w-4 h-4" />
                Policy Knowledge
              </a>
              <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-colors">
                <Truck className="w-4 h-4" />
                Shipment Lookup
              </a>
            </nav>
          </div>

          <div>
            <p className="px-3 text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-2">
              System Modules
            </p>
            <nav className="space-y-1">
              <div className="flex items-center justify-between px-3 py-2 rounded-md text-xs text-slate-400">
                <span className="flex items-center gap-2">
                  <Database className="w-3.5 h-3.5" />
                  RAG Pipeline
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 font-mono">Standby</span>
              </div>
              <div className="flex items-center justify-between px-3 py-2 rounded-md text-xs text-slate-400">
                <span className="flex items-center gap-2">
                  <Sliders className="w-3.5 h-3.5" />
                  Agent Core
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 font-mono">v0.1.0</span>
              </div>
            </nav>
          </div>
        </div>
      </div>

      {/* Backend Health Status Badge */}
      <div className="p-3 border-t border-slate-800/80">
        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {backendOnline === true && (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            )}
            {backendOnline === false && (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            {backendOnline === null && (
              <div className="w-3 h-3 rounded-full bg-amber-400 animate-pulse shrink-0" />
            )}
            <div>
              <p className="text-xs font-medium text-slate-200">FastAPI Backend</p>
              <p className="text-[11px] text-slate-400 font-mono truncate max-w-[140px]">
                {backendOnline === true
                  ? (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000")
                  : backendOnline === false
                    ? "Offline / Disconnected"
                    : "Checking status..."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
