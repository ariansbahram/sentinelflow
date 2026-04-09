from typing import Dict

def check_sender_reputation(content: str) -> Dict:
    lowered = content.lower()
    if "secure-login-alert.com" in lowered:
        return {
            "tool": "sender_reputation",
            "score": 0.92,
            "label": "suspicious",
            "message": "Domain has characteristics of a deceptive login-reset sender."
        }
    return {
        "tool": "sender_reputation",
        "score": 0.10,
        "label": "safe",
        "message": "No obvious sender reputation issues detected."
    }

def detect_phishing_patterns(content: str) -> Dict:
    lowered = content.lower()
    indicators = ["urgent", "click", "restore access", "reset", "suspended"]
    matches = [word for word in indicators if word in lowered]

    if len(matches) >= 2:
        return {
            "tool": "phishing_pattern_detector",
            "score": 0.85,
            "label": "suspicious",
            "message": f"Detected phishing-style urgency and call-to-action patterns: {matches}"
        }

    return {
        "tool": "phishing_pattern_detector",
        "score": 0.15,
        "label": "safe",
        "message": "No significant phishing language detected."
    }

def detect_sensitive_data(content: str) -> Dict:
    lowered = content.lower()
    sensitive_terms = ["ssn", "social security", "client_ssn_export", "confidential", "pii"]
    matches = [term for term in sensitive_terms if term in lowered]

    if matches:
        return {
            "tool": "sensitive_data_detector",
            "score": 0.95,
            "label": "high_risk",
            "message": f"Potential sensitive data exposure detected: {matches}"
        }

    return {
        "tool": "sensitive_data_detector",
        "score": 0.10,
        "label": "none",
        "message": "No sensitive data indicators found."
    }

def analyze_login_anomaly(content: str) -> Dict:
    lowered = content.lower()
    suspicious = any(term in lowered for term in ["russia", "failed attempts", "impossible travel", "foreign ip"])

    if suspicious:
        return {
            "tool": "login_anomaly_analyzer",
            "score": 0.80,
            "label": "anomalous",
            "message": "Detected indicators of suspicious login behavior."
        }

    return {
        "tool": "login_anomaly_analyzer",
        "score": 0.12,
        "label": "normal",
        "message": "No notable login anomaly signals found."
    }
