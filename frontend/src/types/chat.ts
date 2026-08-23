export type AutonomyMode = "copilot" | "autonomous";

export type NavTab = "ai-support" | "issues" | "tickets" | "customers" | "analytics" | "settings" | "help";

export interface AgentStep {
  id: string;
  type: "success" | "info" | "pending";
  label: string;
  timestamp: string;
}

export interface SourceDocument {
  id: string;
  title: string;
  category: "Customer Agreement" | "SOP" | "Policy";
  url?: string;
}

export interface Message {
  id: string;
  sender: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  agentSteps?: AgentStep[];
  sources?: SourceDocument[];
  isThinking?: boolean;
}

export interface ConversationDetails {
  customer: string;
  order: string;
  channel: string;
  ticket: string;
  created: string;
}

export interface AgentTool {
  id: string;
  name: string;
  description: string;
  iconName: "document" | "data" | "calculator" | "action";
  status: "active" | "standby";
}

export interface PendingAction {
  id: string;
  action_id?: string;
  actionType: string;
  customer: string;
  ticket: string;
  reason: string;
  priority: "High" | "Medium" | "Low";
  status: "pending_approval" | "approved" | "cancelled" | "executed";
}

export const NORTHSTAR_USER_CONTEXT = {
  user_id: "usr_lakshay",
  role: "support_agent",
  account_scope: "Northstar Logistics",
} as const;
