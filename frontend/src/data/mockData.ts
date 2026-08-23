import { ConversationDetails, AgentTool } from "@/types/chat";

export const initialConversationDetails: ConversationDetails = {
  customer: "Northstar Logistics",
  order: "ORD-1001",
  channel: "Portal",
  ticket: "T-102",
  created: "May 20, 2025 • 10:24 AM",
};

export const initialTools: AgentTool[] = [
  {
    id: "tool-doc",
    name: "Document Search",
    description: "Searching policies, SOPs, and agreements",
    iconName: "document",
    status: "active",
  },
  {
    id: "tool-data",
    name: "Data Lookup",
    description: "Querying orders, customers, tickets",
    iconName: "data",
    status: "active",
  },
  {
    id: "tool-calc",
    name: "Calculations",
    description: "Running eligibility and fee calculations",
    iconName: "calculator",
    status: "active",
  },
  {
    id: "tool-action",
    name: "Action Center",
    description: "Preparing actions and escalations",
    iconName: "action",
    status: "active",
  },
];

export const quickPrompts: string[] = [
  "What is the current status of ORD-1001?",
  "Can Northstar Logistics cancel ORD-1001 without a fee?",
  "Escalate TKT-501 to Tier-2 Engineering.",
];
