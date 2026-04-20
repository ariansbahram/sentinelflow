# SentinelFlow: Agentic AI for Security Alert Triage

SentinelFlow is a prototype agentic AI system designed to simulate how security operations teams can triage, prioritize, and respond to alerts more efficiently.

---

## Motivation

Security teams often face overwhelming volumes of alerts, many of which require manual triage. While detection tools are effective at generating signals, the real challenge lies in prioritizing meaningful alerts, reducing noise, and supporting consistent decision-making

SentinelFlow explores how agentic AI workflows can sit on top of existing detection systems to improve triage and operational efficiency.

---

## System Overview

The system follows an agentic loop:

**Perception → Reasoning → Action → Learning**

### 1. Perception (Input Layer)
- Ingests alerts such as: phishing emails, login anomalies, data loss signals

### 2. Reasoning (Analysis Layer)
- Combines: Rule-based detection (e.g., phishing patterns, anomalies), retrieval-Augmented Generation (RAG), uses a FAISS vector database to retrieve similar past incidents, provides context-aware reasoning grounded in historical data

### 3. Decision & Action
- Assigns severity levels (low / medium / high)
- Simulates actions such as: escalating alerts, quarantining emails, flagging accounts

### 4. Learning (Feedback Loop)
- Stores processed alerts
- Builds a growing knowledge base of historical cases
- Improves consistency over time


## Tech Stack

- **Backend:** FastAPI
- **Vector Database:** FAISS
- **Embeddings:** OpenAI Embeddings
- **Frontend:** React (basic UI for alert visualization)
- **Architecture:** Agent-based workflow simulation

---

##  Why RAG?

- Security decisions require context and consistency. RAG allows the system to reference similar historical incidents, improve trust in decisions, and provide explainable outputs
---

## Future Improvements

- Potentially integrate real-time data sources rather than sample ones for testing
- Add evaluation metrics (precision, response time reduction)
- Connect to real security tools 

---

## Takeaway

SentinelFlow demonstrates how agentic AI can:

- Reduce alert fatigue
- Improve triage workflows
- Support security teams with context-aware decision-making

Rather than focusing on model complexity, the project emphasizes practical system design aligned with real-world enterprise needs.
