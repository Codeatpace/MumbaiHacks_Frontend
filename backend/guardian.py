from datetime import datetime

class Guardian:
    def __init__(self):
        self.alerts = []
        self.active_call = None
        self.is_monitoring = True

    def add_alert(self, alert_type, content, reason, severity="high"):
        alert = {
            "id": len(self.alerts) + 1,
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "content": content,
            "reason": reason,
            "severity": severity,
            "status": "new"
        }
        self.alerts.append(alert)
        return alert

    def get_alerts(self):
        return sorted(self.alerts, key=lambda x: x['timestamp'], reverse=True)

    def clear_alerts(self):
        self.alerts = []

guardian_instance = Guardian()
