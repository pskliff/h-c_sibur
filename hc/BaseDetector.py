class BaseDetector:
    """Base class for detectors"""

    def processFrame(self, frame):
        """Process frame and return bounding boxes with scores"""
        pass

    def close(self):
        """Close detector and free all resources"""
        pass
