"use client";

import React from "react";
import { ConversationDetailsCard } from "./ConversationDetailsCard";
import { AgentToolsCard } from "./AgentToolsCard";
import { ActionApprovalCard } from "./ActionApprovalCard";
import { ConversationDetails, AgentTool, PendingAction, AutonomyMode } from "@/types/chat";
import { X } from "lucide-react";

interface RightPanelProps {
  conversationDetails: ConversationDetails;
  tools: AgentTool[];
  pendingAction: PendingAction | null;
  mode: AutonomyMode;
  onApproveAction: () => void;
  onCancelAction: () => void;
  onCloseMobile?: () => void;
  className?: string;
}

export const RightPanel: React.FC<RightPanelProps> = ({
  conversationDetails,
  tools,
  pendingAction,
  mode,
  onApproveAction,
  onCancelAction,
  onCloseMobile,
  className = "",
}) => {
  return (
    <aside className={`w-80 bg-white border-l border-slate-200/80 p-4 space-y-4 shrink-0 overflow-y-auto ${className}`}>
      {onCloseMobile && (
        <div className="flex justify-between items-center xl:hidden pb-2 border-b border-slate-100">
          <span className="text-xs font-bold text-slate-900">Context Panel</span>
          <button onClick={onCloseMobile} className="p-1 rounded text-slate-500 hover:bg-slate-100">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <ConversationDetailsCard details={conversationDetails} />

      <AgentToolsCard tools={tools} />

      {pendingAction && (
        <ActionApprovalCard
          action={pendingAction}
          mode={mode}
          onApprove={onApproveAction}
          onCancel={onCancelAction}
        />
      )}
    </aside>
  );
};
