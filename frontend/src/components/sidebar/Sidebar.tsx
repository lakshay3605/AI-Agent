"use client";

import React from "react";
import { 
  Package, 
  MessageSquare, 
  AlertCircle, 
  Ticket, 
  Users, 
  BarChart3, 
  Settings, 
  HelpCircle,
  ChevronDown
} from "lucide-react";
import { NavTab } from "@/types/chat";

interface SidebarProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab, className = "" }) => {
  return (
    <aside className={`w-56 bg-white border-r border-slate-200/80 flex flex-col justify-between shrink-0 select-none ${className}`}>
      <div>
        {/* Brand Header */}
        <div className="h-14 px-4 flex items-center gap-2.5 border-b border-slate-100">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <Package className="w-4 h-4" />
          </div>
          <span className="font-semibold text-slate-900 text-sm tracking-tight">ParcelPilot</span>
        </div>

        {/* Primary Navigation */}
        <div className="p-3 space-y-1">
          <button
            onClick={() => onSelectTab("ai-support")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === "ai-support"
                ? "bg-blue-50 text-blue-600 font-semibold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            <MessageSquare className={`w-4 h-4 ${activeTab === "ai-support" ? "text-blue-600" : "text-slate-400"}`} />
            <span>AI Support</span>
          </button>

          <button
            onClick={() => onSelectTab("issues")}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === "issues"
                ? "bg-blue-50 text-blue-600 font-semibold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-4 h-4 text-slate-400" />
              <span>Issues</span>
            </div>
            <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-rose-500 text-white font-semibold">
              12
            </span>
          </button>

          <button
            onClick={() => onSelectTab("tickets")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === "tickets"
                ? "bg-blue-50 text-blue-600 font-semibold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            <Ticket className="w-4 h-4 text-slate-400" />
            <span>Tickets</span>
          </button>

          <button
            onClick={() => onSelectTab("customers")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === "customers"
                ? "bg-blue-50 text-blue-600 font-semibold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            <Users className="w-4 h-4 text-slate-400" />
            <span>Customers</span>
          </button>

          <button
            onClick={() => onSelectTab("analytics")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === "analytics"
                ? "bg-blue-50 text-blue-600 font-semibold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            <BarChart3 className="w-4 h-4 text-slate-400" />
            <span>Analytics</span>
          </button>
        </div>
      </div>

      {/* Secondary Bottom Navigation & Profile */}
      <div>
        <div className="p-3 border-t border-slate-100 space-y-0.5">
          <button
            onClick={() => onSelectTab("settings")}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all"
          >
            <Settings className="w-4 h-4 text-slate-400" />
            <span>Settings</span>
          </button>

          <button
            onClick={() => onSelectTab("help")}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all"
          >
            <HelpCircle className="w-4 h-4 text-slate-400" />
            <span>Help & Docs</span>
          </button>
        </div>

        {/* User Profile Card matching reference image */}
        <div className="p-3 border-t border-slate-100">
          <div className="flex items-center justify-between p-1.5 rounded-lg hover:bg-slate-50 transition-all cursor-pointer">
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <div className="w-7 h-7 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold flex items-center justify-center">
                  LK
                </div>
                <span className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-white" />
              </div>
              <div className="text-left leading-tight">
                <p className="text-xs font-semibold text-slate-800">Lakshay</p>
                <p className="text-[10px] text-slate-400">Support Agent</p>
              </div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </div>
        </div>
      </div>
    </aside>
  );
};
