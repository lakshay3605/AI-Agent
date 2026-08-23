"use client";

import React from "react";
import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { PendingAction, AutonomyMode } from "@/types/chat";

interface ActionApprovalCardProps {
  action: PendingAction;
  mode: AutonomyMode;
  onApprove: () => void;
  onCancel: () => void;
}

export const ActionApprovalCard: React.FC<ActionApprovalCardProps> = ({
  action,
  mode,
  onApprove,
  onCancel,
}) => {
  return (
    <div className="bg-amber-50/40 border border-amber-300/80 rounded-xl p-4 space-y-3.5 shadow-xs relative overflow-hidden">
      {/* Top Banner Header */}
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-md bg-amber-500 text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-xs">
          !
        </div>
        <h3 className="text-xs font-bold text-amber-900 tracking-tight">
          Action Requires Approval
        </h3>
      </div>

      {action.status === "pending_approval" ? (
        <>
          <p className="text-xs font-semibold text-slate-800">
            Create escalation for this issue?
          </p>

          <div className="space-y-2 text-xs border-t border-amber-200/60 pt-2.5">
            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Action Type</span>
              <span className="font-semibold text-slate-800">{action.actionType}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Customer</span>
              <span className="font-medium text-slate-800">{action.customer}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Ticket</span>
              <span className="font-mono font-medium text-slate-800">{action.ticket}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Reason</span>
              <span className="text-slate-700 font-medium text-[11px] truncate max-w-[150px]">
                {action.reason}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-500 font-medium">Priority</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-100 text-amber-800 border border-amber-300">
                {action.priority}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              onClick={onCancel}
              className="px-3.5 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-xs font-medium text-slate-700 transition-colors shadow-xs"
            >
              Cancel
            </button>
            <button
              onClick={onApprove}
              className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-xs font-semibold text-white transition-all shadow-sm"
            >
              Approve & Execute
            </button>
          </div>
        </>
      ) : action.status === "approved" || action.status === "executed" ? (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center gap-2.5 text-xs text-emerald-800">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <div>
            <p className="font-semibold">Action Approved & Executed</p>
            <p className="text-[11px] text-emerald-600 mt-0.5">
              Escalation ticket {action.ticket} created successfully.
            </p>
          </div>
        </div>
      ) : (
        <div className="p-3 bg-slate-100 border border-slate-200 rounded-lg flex items-center gap-2.5 text-xs text-slate-600">
          <XCircle className="w-4 h-4 text-slate-400 shrink-0" />
          <div>
            <p className="font-semibold">Action Cancelled</p>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Escalation was cancelled by human executive.
            </p>
          </div>
        </div>
      )}

      {mode === "autonomous" && (
        <div className="mt-2 p-2 rounded bg-amber-100/60 text-[10px] text-amber-800 font-medium border border-amber-200">
          ⚡ Autonomous Mode Active: Safety policy requires human sign-off for state-changing escalation actions.
        </div>
      )}
    </div>
  );
};
