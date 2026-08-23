# ParcelPilot AI — Architecture Note

## 1. Agent Design

ParcelPilot AI uses an agentic workflow built around an LLM and a set of specialized tools.

The agent interprets the user's request, determines what information or action is required, and invokes the appropriate tool rather than relying solely on the language model's internal knowledge.

The main capabilities include:

- Operational order lookup
- Customer lookup
- Support-ticket lookup
- Document / policy search through RAG
- SLA/service-credit calculation
- Controlled escalation actions

The agent is designed to separate information retrieval from state-changing operations. Read-only operations can be performed directly, while state-changing actions create a pending action that requires human confirmation.

## 2. Tool Design

Tools are implemented as structured functions with explicit inputs and outputs.

Core tools include:

- `get_order`
- `get_customer`
- `get_ticket`
- `search_documents`
- `calculate_service_credit`
- `create_escalation`

The tool layer provides a controlled interface between the LLM and the application's data and actions.

State-changing operations are intentionally separated from normal retrieval. For example, an escalation is first prepared as a pending action rather than immediately modifying state.

## 3. Document and Structured-Data Handling

Structured operational data is stored in the assessment dataset and accessed through a dedicated data service.

Documents such as policies, SOPs, operations guides, and customer agreements are processed through a RAG pipeline:

1. PDF parsing
2. Document chunking
3. Metadata preservation
4. Embedding generation using `BAAI/bge-small-en-v1.5`
5. Storage in ChromaDB
6. Semantic retrieval during agent execution

Document metadata includes information such as:

- Customer
- Document type
- Status
- Page number
- Authority

This allows retrieval to be scoped to the relevant customer and document context.

## 4. Source Reliability and Conflict Handling

ParcelPilot distinguishes between different sources of authority.

Documents are classified into categories including:

- Customer agreements
- Current SOPs
- General policies
- Operations guides
- Deprecated documents

Customer-specific agreements have higher authority than generic policies when the two conflict.

Deprecated documents are retained for traceability but are explicitly identified as deprecated rather than being treated as current authoritative policy.

The agent also exposes retrieved sources and agent activity to make the reasoning process more transparent to the user.

## 5. Major Technical Trade-offs

### Local embeddings vs. hosted embedding APIs

The system uses a local Sentence Transformer model for embeddings. This avoids additional per-request embedding costs and keeps document retrieval independent of another paid API.

### ChromaDB vs. managed vector database

ChromaDB was chosen because the assessment dataset is relatively small and a persistent local vector store is sufficient for the prototype.

### Agentic tools vs. a single LLM prompt

A tool-based architecture was chosen instead of putting all data into the prompt. This provides more deterministic access to operational records and allows actions to be explicitly controlled.

### Human confirmation for actions

The system intentionally adds a confirmation step before state-changing operations. This introduces an additional interaction step but reduces the risk of unintended operational changes.

### GPT-5 nano

GPT-5 nano was selected as the production LLM to keep inference costs low while providing sufficient reasoning capability for the support-agent workflow.
