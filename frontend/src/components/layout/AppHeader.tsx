"use client";

import React from "react";
import { HelpCircle, Bell, Menu, PanelRight } from "lucide-react";
import { AutonomyModeSelector } from "../controls/AutonomyModeSelector";
import { AutonomyMode } from "@/types/chat";

interface AppHeaderProps {
  mode: AutonomyMode;
  onChangeMode: (mode: AutonomyMode) => void;
  onToggleSidebar?: () => void;
  onToggleRightPanel?: () => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  mode,
  onChangeMode,
  onToggleSidebar,
  onToggleRightPanel,
}) => {
  return (
    <header className="h-14 border-b border-slate-200/80 bg-white px-4 md:px-6 flex items-center justify-between shrink-0 select-none">
      {/* Title & Status Indicator */}
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-1.5 rounded-lg text-slate-500 hover:bg-slate-100"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <h1 className="font-bold text-slate-900 text-sm md:text-base tracking-tight">
          ParcelPilot AI
        </h1>
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[11px] font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>Operational</span>
        </div>
      </div>

      {/* Mode Controls & Header Actions */}
      <div className="flex items-center gap-3">
        <AutonomyModeSelector mode={mode} onChangeMode={onChangeMode} />

        <div className="h-4 w-[1px] bg-slate-200 hidden sm:block" />

        <div className="flex items-center gap-1">
          <button className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors">
            <HelpCircle className="w-4 h-4" />
          </button>

          <button className="relative p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-3.5 h-3.5 rounded-full bg-rose-500 text-white text-[9px] font-bold flex items-center justify-center">
              3
            </span>
          </button>
        </div>

        <div className="hidden lg:flex items-center gap-2 pl-1 border-l border-slate-200">
          <div className="w-7 h-7 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold flex items-center justify-center">
            LK
          </div>
          <div className="text-left text-[11px] leading-tight">
            <span className="font-semibold text-slate-800 block">Lakshay</span>
            <span className="text-slate-400 block text-[10px]">Support Agent</span>
          </div>
        </div>

        {onToggleRightPanel && (
          <button
            onClick={onToggleRightPanel}
            className="xl:hidden p-1.5 rounded-lg text-slate-500 hover:bg-slate-100"
            title="Toggle Context Panel"
          >
            <PanelRight className="w-5 h-5" />
          </button>
        )}
      </div>
    </header>
  );
};
