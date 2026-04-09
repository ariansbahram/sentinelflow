alerts = [
    {
        "id": 101,
        "type": "phishing",
        "title": "Suspicious password reset email",
        "content": "Urgent: Your mailbox has been suspended. Click http://secure-login-alert.com immediately to restore access.",
        "source": "email_gateway"
    },
    {
        "id": 102,
        "type": "login_anomaly",
        "title": "Impossible travel login",
        "content": "User logged in from California and then from Russia 12 minutes later after 6 failed attempts.",
        "source": "identity_provider"
    },
    {
        "id": 103,
        "type": "dlp",
        "title": "External file transfer",
        "content": "Employee emailed file client_ssn_export.xlsx to an external Gmail account.",
        "source": "data_loss_prevention"
    },
    {
        "id": 104,
        "type": "benign",
        "title": "HR newsletter",
        "content": "Monthly HR newsletter with policy reminders and upcoming events.",
        "source": "email_gateway"
    }
]
