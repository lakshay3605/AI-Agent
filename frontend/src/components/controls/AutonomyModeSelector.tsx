"use client";

import React from "react";
import { Zap } from "lucide-react";
import { AutonomyMode } from "@/types/chat";

interface AutonomyModeSelectorProps {
  mode: AutonomyMode;
  onChangeMode: (mode: AutonomyMode) => void;
}

export const AutonomyModeSelector: React.FC<AutonomyModeSelectorProps> = ({ mode, onChangeMode }) => {
  return (
    <div className="flex items-center p-0.5 rounded-lg bg-slate-100/90 border border-slate-200 text-xs select-none">
      <button
        onClick={() => onChangeMode("copilot")}
        className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-all font-medium ${
          mode === "copilot"
            ? "bg-white text-blue-600 shadow-sm border border-slate-200/80"
            : "text-slate-600 hover:text-slate-900"
        }`}
      >
        <Zap className="w-3.5 h-3.5 fill-blue-500 text-blue-500" />
        <span>Copilot</span>
      </button>

      <button
        onClick={() => onChangeMode("autonomous")}
        className={`px-3 py-1 rounded-md transition-all font-medium ${
          mode === "autonomous"
            ? "bg-white text-slate-900 shadow-sm border border-slate-200/80"
            : "text-slate-600 hover:text-slate-900"
        }`}
      >
        <span>Autonomous</span>
      </button>
    </div>
  );
};
