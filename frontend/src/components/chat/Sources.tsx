"use client";

import React, { useState } from "react";
import { FileText, ChevronRight, ChevronDown, ChevronUp } from "lucide-react";
import { SourceDocument } from "@/types/chat";

interface SourcesProps {
  sources: SourceDocument[];
}

export const Sources: React.FC<SourcesProps> = ({ sources }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!sources || sources.length === 0) return null;

  const getCategoryBadgeClass = (category: SourceDocument["category"]) => {
    switch (category) {
      case "Customer Agreement":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "SOP":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "Policy":
        return "bg-purple-50 text-purple-700 border-purple-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  return (
    <div className="mt-3 border-t border-slate-100 pt-3">
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between py-1 cursor-pointer select-none group"
      >
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 group-hover:text-slate-900 transition-colors">
          <FileText className="w-3.5 h-3.5 text-slate-500" />
          <span>Sources ({sources.length})</span>
        </div>
        {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-slate-400" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-400" />}
      </div>

      {isExpanded && (
        <div className="mt-2 space-y-2">
          {sources.map((src) => (
            <div
              key={src.id}
              className="flex items-center justify-between p-2.5 rounded-lg border border-slate-200/80 bg-slate-50/50 hover:bg-slate-100/60 hover:border-slate-300 transition-all cursor-pointer group"
            >
              <div className="flex items-center gap-2.5">
                <FileText className="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
                <span className="text-xs font-medium text-slate-800">{src.title}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getCategoryBadgeClass(src.category)}`}>
                  {src.category}
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 transition-colors" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
