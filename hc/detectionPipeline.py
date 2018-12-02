# import numpy
import os
# import tensorflow as tf
import cv2
import time
import datetime
from BaseDetector import BaseDetector
import json
import logging
from pprint import pprint
LOG_LEVEL = logging.INFO
FPSD = 5

def callback(rule2score):
    pass

class detectionPipeline(BaseDetector):
    available_rules2alg = {'smoke': BaseDetector(), 'person': BaseDetector()}

    def __init__(self, video_path, config_path):

        logging.basicConfig(level=LOG_LEVEL)

        self.outlier = False
        self.video_path = video_path
        # self.cap = cv2.VideoCapture(video_path)

        with open(config_path) as f:
            self.config = json.load(f)

        self.cam_id = self.config['cam_id']
        # self.threshold = self.config['threshold']
        self.rule2alg = {}
        self.info = {}

        for rule_grp in self.config['rules']:
            for rule, num in rule_grp.items():
                if rule not in self.available_rules2alg:
                    logging.warning(f'{rule} rule is not in `available rules`')
                else:
                    if rule not in self.rule2alg.keys() or num[0] < self.rule2alg[rule][1]:
                        self.rule2alg[rule] = [self.available_rules2alg[rule], num[0], num[1]]
                        # self.rule2score[rule] = None

        logging.info(self.rule2alg)



    def processFrame(self, img, **kwargs):
        """Process frame and return bounding boxes with scores"""
        rule2score = {}
        imframe = img.copy()
        # iterate events
        for rule, alg, bbox_num, threshold in self.rule2alg.items():
            rule2score[rule] = 0

            # find bboxes for event
            boxes, scores, classes, num = alg.processFrame(img)

            if num < bbox_num:
                rule2score[rule] = 0
            else:
                # iterate every bbox and draw bboxes
                for i in range(len(boxes)):
                    if classes[i] == 1 and scores[i] > threshold:
                        rule2score[rule] = scores[i] if rule2score[rule] < scores[i] else rule2score[rule]
                        box = boxes[i]
                        cv2.rectangle(imframe, (box[1], box[0]), (box[3], box[2]), (255, 0, 0), 2)
                    else:
                        rule2score[rule] = 0

        glob_alert_list = []

        for rule_grp in self.config['rules']:
            alert_list = []
            for rule, num in rule_grp.items():
                alert_list.append(rule2score[rule] > 0)
            is_alert = True #alert_list[0]
            for al in alert_list:
                is_alert = is_alert & al
            glob_alert_list.append(is_alert)
        # glob_is_alert = False

        for i, al in enumerate(glob_alert_list):
            if al:
                rule2score['alert'] = al
                rule2score['alert_desc'] = self.config['rules'][i]

        rule2score['cam_id'] = self.config['cam_id']
        rule2score['time'] = datetime.datetime.now()
        rule2score['img'] = imframe
        return rule2score
        # pass



    def processVideo(self):
        int fps = 0
        while True:
            if fps % FPSD == 0:
                r, img = self.cap.read()
                img = cv2.resize(img, (1280, 720))
                rule2score = self.processFrame(img=img)
                if self.outlier:
                    if rule2score['alert']:
                        continue
                    else:
                        self.outlier = False
                        callback(rule2score=rule2score)
                elif rule2score['alert']:
                    self.outlier = True
                    callback(rule2score=rule2score)
            fps += 1
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
        pass


    def close(self):
        """Close detector and free all resources"""
        for rule, alg, bbox_num, threshold in self.rule2alg.items():
            alg.close()
        pass

if __name__ == "__main__":
    pipe = detectionPipeline('./', './config_ex.json')
