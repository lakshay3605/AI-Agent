# ParcelPilot AI — Product Note

## 1. Additional Client Problem

Beyond answering support questions, ParcelPilot AI addresses the operational problem of turning support requests into controlled actions.

A support agent should not only be able to determine what happened, but should also be able to initiate the next operational step.

ParcelPilot therefore supports controlled actions such as preparing ticket escalations.

The system separates:

**Understanding → Preparation → Human Confirmation → Action**

This allows an AI agent to assist with operational workflows without giving it unrestricted authority to modify business state.

## 2. What I Would Build Next

If continued beyond the assessment, I would add:

- More operational actions such as shipment cancellation and rerouting
- Deeper integration with real logistics systems
- Authentication and role-based permissions
- Persistent ticket/action history
- Better document retrieval and reranking
- Evaluation and observability dashboards
- Human-agent handoff
- Audit logs for every AI-generated action
- Customer-specific policy management
- Real-time shipment and carrier integrations

## 3. Intentionally Left Out

To keep the submission focused, the following were intentionally kept outside the scope:

- Production carrier API integrations
- Full authentication and enterprise RBAC
- Real payment/refund processing
- Large-scale distributed infrastructure
- Production-grade observability
- Full legal/contract review workflows

The submission focuses on demonstrating the core agentic architecture, retrieval, structured-data access, reasoning, and controlled actions.

## 4. Success Metric

The primary metric I would use is:

**Support Resolution Rate**

> Percentage of support requests that the AI resolves correctly without requiring manual intervention.

I would additionally track:

- Tool-call success rate
- RAG answer accuracy
- Action confirmation rate
- Human escalation rate
- Average resolution time
- Cost per resolved request
