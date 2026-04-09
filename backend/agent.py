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
    def compute_risk_score(self, tool_results):
        return round(sum(item["score"] for item in tool_results) / len(tool_results), 2)

    def decide(self, alert, tool_results, retrieved_cases):
        score = self.compute_risk_score(tool_results)

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
            if alert["type"] == "phishing":
                return {
                    "status": "executed",
                    "action_taken": "Simulated: quarantined suspicious email and opened SOC incident."
                }
            if alert["type"] == "login_anomaly":
                return {
                    "status": "executed",
                    "action_taken": "Simulated: flagged account and required step-up authentication."
                }
            if alert["type"] == "dlp":
                return {
                    "status": "executed",
                    "action_taken": "Simulated: blocked external transfer and alerted security team."
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

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def log_case(self, alert, severity, action, score, execution_result):
        case_record = {
            "alert_id": alert["id"],
            "alert_type": alert["type"],
            "title": alert["title"],
            "content": alert["content"],
            "severity": severity,
            "action": action,
            "score": score,
            "execution_status": execution_result["status"],
            "execution_action": execution_result["action_taken"],
        }
        save_case(case_record)


def triage_alert(alert):
    steps = []

    detection_agent = DetectionAgent()
    retrieval_agent = RetrievalAgent()
    decision_agent = DecisionAgent()
    action_agent = ActionAgent()
    audit_agent = AuditAgent()

    steps.append("Perception: Ingested security alert.")

    tool_results = detection_agent.analyze(alert)
    steps.append("Detection Agent: Analyzed sender reputation, phishing patterns, sensitive data, and login anomalies.")

    retrieved_cases = retrieval_agent.retrieve_context(alert, k=2)
    steps.append("Retrieval Agent: Retrieved similar historical incidents from vector store.")

    decision = decision_agent.decide(alert, tool_results, retrieved_cases)
    score = decision["score"]
    severity = decision["severity"]
    action = decision["action"]
    guardrail_note = decision["guardrail_note"]
    steps.append(f"Decision Agent: Computed risk score of {score} and selected action '{action}' with severity '{severity}'.")

    execution_result = action_agent.execute(alert, severity, action)
    steps.append(f"Action Agent: {execution_result['action_taken']}")

    reasoning = audit_agent.generate_reasoning(
        alert=alert,
        tool_results=tool_results,
        retrieved_cases=retrieved_cases,
        severity=severity,
        action=action,
        execution_result=execution_result,
        guardrail_note=guardrail_note,
    )
    steps.append("Audit Agent: Generated analyst-facing explanation.")

    audit_agent.log_case(alert, severity, action, score, execution_result)
    steps.append("Learning: Stored case outcome and simulated execution details for future analysis.")

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
        "auto_resolved": action == "close",
    }