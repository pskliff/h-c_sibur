class AlertInfo:
    def __init__(self, time, camera, rules):
        self.time = time
        self.camera = camera
        self.rules = rules

#states: alert, resolved, ignored
class Alert:
    def __init__(self, alert_info: AlertInfo, state='alert', img=None, is_resolved=False):
        self.state = state
        self.is_resolved = is_resolved
        self.img = img
        self.info = alert_info

