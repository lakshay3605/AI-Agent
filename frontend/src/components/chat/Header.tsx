"use client";

import React from "react";
import { Package, RefreshCw, ShieldAlert, Sparkles } from "lucide-react";

interface HeaderProps {
  onRefreshHealth: () => void;
  isChecking: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onRefreshHealth, isChecking }) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md px-6 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          <span>ParcelPilot Support Assistant</span>
        </div>
        <span className="text-slate-600 text-sm">|</span>
        <span className="text-xs text-slate-400 font-mono">Step 1: Foundation Mode</span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onRefreshHealth}
          disabled={isChecking}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-xs font-medium text-slate-300 transition-colors disabled:opacity-50"
          title="Check backend health endpoint"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isChecking ? "animate-spin text-blue-400" : ""}`} />
          <span>Check Health</span>
        </button>
      </div>
    </header>
  );
};
