import time
from openai import OpenAI
from config import OPENAI_API_KEY, CHAT_MODEL
from tools import (
    check_sender_reputation,
    detect_phishing_patterns,
    detect_sensitive_data,
    analyze_login_anomaly,
)
from rag import CaseRetriever
from storage import save_case


client = OpenAI(api_key=OPENAI_API_KEY)
retriever = CaseRetriever()


class DetectionAgent:
    def analyze(self, alert):
        content = alert["content"]
        return [
            check_sender_reputation(content),
            detect_phishing_patterns(content),
            detect_sensitive_data(content),
            analyze_login_anomaly(content),
        ]


class RetrievalAgent:
    def retrieve_context(self, alert, k=2):
        return retriever.retrieve(alert["content"], k=k)


class DecisionAgent:
    def compute_risk_score(self, alert, tool_results):
        relevant_scores = []
        alert_type = alert["type"]

        for item in tool_results:
            tool = item["tool"]
            if (alert_type == "phishing" and tool in ["sender_reputation", "phishing_pattern_detector"]):
                relevant_scores.append(item["score"])
            elif (alert_type == "dlp" and tool == "sensitive_data_detector"):
                relevant_scores.append(item["score"])
            elif (alert_type == "login_anomaly" and tool == "login_anomaly_analyzer"):
                relevant_scores.append(item["score"])
        if not relevant_scores:
            relevant_scores = [item["score"] for item in tool_results]
        
        return round(sum(relevant_scores) / len(relevant_scores), 2)
        
    


    def decide(self, alert, tool_results, retrieved_cases):
        score = self.compute_risk_score(alert, tool_results)

        if score >= 0.75:
            severity, action = "high", "escalate"
        elif score >= 0.40:
            severity, action = "medium", "review"
        else:
            severity, action = "low", "close"

        adjusted_action, guardrail_note = self.apply_guardrails(alert, severity, action)

        return {
            "score": score,
            "severity": severity,
            "action": adjusted_action,
            "guardrail_note": guardrail_note,
        }

    def apply_guardrails(self, alert, severity, action):
        alert_type = alert["type"]

        if alert_type == "benign" and action == "escalate":
            return "review", "Guardrail prevented unnecessary escalation of likely benign content."

        if alert_type == "dlp" and action == "close":
            return "review", "Guardrail prevented auto-closing a potential sensitive-data event."

        return action, "No guardrail adjustment applied."


class ActionAgent:
    def execute(self, alert, severity, action):
        """
        Simulated enterprise action layer.
        In a real system, this would call APIs like:
        - quarantine email
        - disable account
        - block sender/domain
        - open SOC ticket
        """
        if action == "escalate":
            return {
                "status": "pending_review",
                "action_taken":
                (
                    "AI recommends escalation. "
                    "Awaiting analyst approval "
                    "before execution."
                ),
                "requires_approval": True

            }

        if action == "review":
            return {
                "status": "queued",
                "action_taken": "Simulated: routed alert to analyst review queue."
            }

        return {
            "status": "closed",
            "action_taken": "Simulated: closed low-risk alert with no further action."
        }


class AuditAgent:
    def generate_reasoning(self, alert, tool_results, retrieved_cases, severity, action, execution_result, guardrail_note):
        prompt = f"""
You are an enterprise cybersecurity analyst.

Analyze this alert and explain the final decision.

Alert:
Title: {alert["title"]}
Type: {alert["type"]}
Content: {alert["content"]}
Source: {alert["source"]}

Tool findings:
{tool_results}

Retrieved historical cases:
{retrieved_cases}

Decision:
Severity: {severity}
Action: {action}
Execution result: {execution_result}
Guardrail note: {guardrail_note}

Write a concise analyst explanation that:
1. explains the most important risk signals,
2. references the retrieved historical context,
3. explains why the chosen action makes sense,
4. mentions the simulated action taken,
5. is clear enough for an enterprise SOC dashboard.
"""
        
        llm_start = time.time()

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        llm_latency = (
            time.time() - llm_start
        ) * 1000

        return {
            "reasoning":
                response.choices[0].message.content,

            "llm_latency":
                llm_latency
        }

    def log_case(self, alert, severity, action, score, execution_result):
        case_record = {
            "alert_id": alert["id"],
            "alert_type": alert["type"],
            "title": alert["title"],
            "content": alert["content"],

            "severity": severity,
            "action": action,
            "score": score,

            "review_status":
                (
                    "pending"
                    if execution_result.get(
                        "requires_approval",
                        False
                    )
                    else "completed"
                ),
            "reviewer": None,

            "approved": False,

            "execution_status":execution_result["status"],
            
            "execution_action": execution_result["action_taken"],
        }
        save_case(case_record)


def triage_alert(alert):
    workflow_start = time.time()
    steps = []

    detection_agent = DetectionAgent()
    retrieval_agent = RetrievalAgent()
    decision_agent = DecisionAgent()
    action_agent = ActionAgent()
    audit_agent = AuditAgent()

    steps.append("Perception: Ingested security alert.")

    tool_results = detection_agent.analyze(alert)
    steps.append("Detection Agent: Analyzed sender reputation, phishing patterns, sensitive data, and login anomalies.")

    retrieval_start = time.time()

    retrieved_cases = retrieval_agent.retrieve_context(alert, k=2)

    retrieval_latency = (
    time.time() - retrieval_start
    ) * 1000

    steps.append("Retrieval Agent: Retrieved similar historical incidents from vector store.")

    decision = decision_agent.decide(alert, tool_results, retrieved_cases)
    score = decision["score"]
    severity = decision["severity"]
    action = decision["action"]
    guardrail_note = decision["guardrail_note"]
    steps.append(f"Decision Agent: Computed risk score of {score} and selected action '{action}' with severity '{severity}'.")

    execution_result = action_agent.execute(alert, severity, action)
    steps.append(f"Action Agent: {execution_result['action_taken']}")

    reasoning_result = audit_agent.generate_reasoning(
        alert=alert,
        tool_results=tool_results,
        retrieved_cases=retrieved_cases,
        severity=severity,
        action=action,
        execution_result=execution_result,
        guardrail_note=guardrail_note,
    )
    reasoning = reasoning_result["reasoning"]
    llm_latency = reasoning_result["llm_latency"]


    steps.append("Audit Agent: Generated analyst-facing explanation.")

    audit_agent.log_case(alert, severity, action, score, execution_result)
    steps.append("Learning: Stored case outcome and simulated execution details for future analysis.")


    total_workflow_latency = (
    time.time() - workflow_start
    ) * 1000

    workflow_metrics = {

        "retrieval_latency_ms":
            round(retrieval_latency, 2),

        "llm_latency_ms":
            round(llm_latency, 2),

        "total_workflow_latency_ms":
            round(total_workflow_latency, 2),

        "tools_used":
            len(tool_results),

        "retrieved_cases":
            len(retrieved_cases),
}
    return {
        "alert_id": alert["id"],
        "severity": severity,
        "action": action,
        "confidence": score,
        "tool_results": tool_results,
        "retrieved_cases": retrieved_cases,
        "execution_result": execution_result,
        "reasoning": reasoning,
        "steps": steps,
        "workflow_metrics": workflow_metrics,
        "auto_resolved": action == "close",
    }