"use client";

import React, { useState } from "react";
import { CheckCircle2, Info, ChevronDown, ChevronUp } from "lucide-react";
import { AgentStep } from "@/types/chat";

interface AgentActivityProps {
  steps: AgentStep[];
}

export const AgentActivity: React.FC<AgentActivityProps> = ({ steps }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!steps || steps.length === 0) return null;

  return (
    <div className="mt-3 border-t border-slate-100 pt-3">
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between py-1 cursor-pointer select-none group"
      >
        <span className="text-xs font-semibold text-slate-700 group-hover:text-slate-900 transition-colors">
          Agent Activity
        </span>
        <div className="flex items-center gap-1.5 text-slate-400 text-xs">
          {!isExpanded && <span className="text-[11px] text-slate-400">{steps.length} steps completed</span>}
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </div>

      {isExpanded && (
        <div className="mt-2 space-y-2">
          {steps.map((step) => (
            <div key={step.id} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                {step.type === "success" && (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                )}
                {step.type === "info" && (
                  <Info className="w-4 h-4 text-blue-500 shrink-0" />
                )}
                {step.type === "pending" && (
                  <div className="w-4 h-4 rounded-full border-2 border-slate-300 border-t-blue-500 animate-spin shrink-0" />
                )}
                <span className="text-slate-700 font-medium">{step.label}</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">{step.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
