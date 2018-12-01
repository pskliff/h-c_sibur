from hc.BaseDetector import *
import numpy as np
import cv2


class SmokeOpenCVDetector(BaseDetector):

    def processFrame(self, frame):
        """
        Process frame and return bounding boxes with scores

        :param frame Video frame to process
        """
        fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # gray_frame = cv2.medianBlur(gray_frame, 5)
        gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 5)
        fmask = fgbg.apply(gray_frame)
        kernel = np.ones((20, 20), np.uint8)
        fmask = cv2.medianBlur(fmask, 3)
        fmask = cv2.dilate(fmask, kernel)

        contour_img, contours, hierarchy = cv2.findContours(fmask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        bboxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            bboxes.append((x, y, w, h))

        if len(bboxes) == 0:
            return None, None

        return bboxes, [1] * len(bboxes)

    def close(self):
        """Close detector and free all resources"""
        pass

DEFAULT_VIDEO_SRC = '../../data/videos/vc_11_smoke_0_persones_0_01.mp4'

if __name__ == '__main__':
    import sys
    try:
        video_src = sys.argv[1]
    except IndexError:
        video_src = DEFAULT_VIDEO_SRC

    cap = cv2.VideoCapture(video_src)
    detector = SmokeOpenCVDetector()

    while 1:
        ret, frame = cap.read()
        if frame is None:
            print("The End!!!")
            break

        bboxes, scores = detector.processFrame(frame)
        for x, y, w, h in bboxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow('aa', frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

