"use client";

import React from "react";
import { ConversationDetails } from "@/types/chat";

interface ConversationDetailsCardProps {
  details: ConversationDetails;
}

export const ConversationDetailsCard: React.FC<ConversationDetailsCardProps> = ({ details }) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-4 space-y-3 shadow-xs">
      <h3 className="text-xs font-bold text-slate-900 tracking-tight">
        Conversation Details
      </h3>

      <div className="space-y-2.5 text-xs">
        <div className="flex justify-between items-center">
          <span className="text-slate-400 font-medium">Customer</span>
          <span className="font-semibold text-slate-800">{details.customer}</span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-slate-400 font-medium">Order</span>
          <span className="font-mono font-medium text-slate-800">{details.order}</span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-slate-400 font-medium">Channel</span>
          <span className="font-medium text-slate-800">{details.channel}</span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-slate-400 font-medium">Ticket</span>
          <span className="font-mono font-medium text-slate-800">{details.ticket}</span>
        </div>

        <div className="flex justify-between items-center pt-1 border-t border-slate-100">
          <span className="text-slate-400 font-medium">Created</span>
          <span className="text-slate-600 font-mono text-[11px]">{details.created}</span>
        </div>
      </div>
    </div>
  );
};
