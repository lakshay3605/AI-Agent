"use client";

import React from "react";
import { Sparkles, FileSearch, Database, Calculator, Send } from "lucide-react";
import { AgentTool } from "@/types/chat";

interface AgentToolsCardProps {
  tools: AgentTool[];
}

export const AgentToolsCard: React.FC<AgentToolsCardProps> = ({ tools }) => {
  const getToolIcon = (iconName: AgentTool["iconName"]) => {
    switch (iconName) {
      case "document":
        return <FileSearch className="w-4 h-4 text-slate-600" />;
      case "data":
        return <Database className="w-4 h-4 text-slate-600" />;
      case "calculator":
        return <Calculator className="w-4 h-4 text-slate-600" />;
      case "action":
        return <Send className="w-4 h-4 text-slate-600" />;
      default:
        return <Sparkles className="w-4 h-4 text-slate-600" />;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-4 space-y-3 shadow-xs">
      <div className="flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-blue-600" />
        <h3 className="text-xs font-bold text-slate-900 tracking-tight">
          Agent Tools
        </h3>
      </div>

      <div className="space-y-3">
        {tools.map((tool) => (
          <div key={tool.id} className="flex items-start gap-3 group">
            <div className="p-1.5 rounded-lg bg-slate-100 group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors shrink-0">
              {getToolIcon(tool.iconName)}
            </div>
            <div className="text-left">
              <h4 className="text-xs font-semibold text-slate-800 leading-tight">
                {tool.name}
              </h4>
              <p className="text-[11px] text-slate-400 leading-snug mt-0.5">
                {tool.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
