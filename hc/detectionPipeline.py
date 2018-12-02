# import numpy
import os
import sys

from hc.detectors.BaseDetector import BaseDetector

sys.path.append('./detectors/')
# import tensorflow as tf
import cv2
import time
import datetime
from hc.detectors.human_detector import HumanDetector
import json
import logging
import argparse
from pprint import pprint

LOG_LEVEL = logging.INFO
FPSD = 5
CNTR_DELAY = 50


def callback(rule2score):
    pass


class detectionPipeline(BaseDetector):
    available_rules2alg = {'person': HumanDetector}

    def __init__(self, video_path, config_path, models_paths):

        logging.basicConfig(level=LOG_LEVEL)

        # init algs with model paths
        for i, k in enumerate(self.available_rules2alg.keys()):
            m_path = models_paths[i]
            self.available_rules2alg[k] = self.available_rules2alg[k](m_path)


        self.outlier = False
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

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
                        self.rule2alg[rule] = (self.available_rules2alg[rule], num[0], num[1])
                        # self.rule2score[rule] = None

        logging.info(self.rule2alg)

    def processFrame(self, img):
        """Process frame and return bounding boxes with scores"""
        rule2score = {}
        imframe = img.copy()
        # iterate events
        for rule, (alg, bbox_num, threshold) in self.rule2alg.items():
            rule2score[rule] = 0
            rule2score['alert'] = 0

            # find bboxes for event
            boxes, scores, classes, num = alg.processFrame(img)

            if num < bbox_num:
                rule2score[rule] = 0
            else:
                # iterate every bbox and draw bboxes
                for i in range(len(boxes)):
                    if classes[i] == 1 and scores[i] > threshold:
                        rule2score[rule] = scores[i] if rule2score[rule] < scores[i] else rule2score[rule]
                        rule2score['alert'] = 1
                        box = boxes[i]
                        cv2.rectangle(imframe, (box[1], box[0]), (box[3], box[2]), (255, 0, 0), 2)
                    else:
                        rule2score[rule] = 0
        # if rule2score['alert'] == 1:
        #     logging.info(f'Rule2score after RULE FILL = \n{rule2score}\n')
        glob_alert_list = []

        for rule_grp in self.config['rules']:
            alert_list = []
            for rule, num in rule_grp.items():
                alert_list.append(rule2score[rule] > 0)
            is_alert = True  # alert_list[0]
            for al in alert_list:
                is_alert = is_alert & al
            glob_alert_list.append(is_alert)
        # glob_is_alert = False

        for i, al in enumerate(glob_alert_list):
            if al:
                rule2score['alert'] = al
                rule2score['alert_desc'] = self.config['rules'][i]
        # if rule2score['alert'] == 1:
        #     logging.info(f'Rule2score after ALERT FILL = \n{rule2score}\n')

        rule2score['cam_id'] = self.config['cam_id']
        rule2score['time'] = datetime.datetime.now()
        rule2score['img'] = imframe
        return rule2score
        # pass

    def processVideo(self):
        fps = 0
        cntr = 0
        while True:
            if fps % FPSD == 0:
                r, img = self.cap.read()
                if img is None:
                    break
                img = cv2.resize(img, (1280, 720))
                rule2score = self.processFrame(img=img)
                # if rule2score['alert'] == 1:
                #     logging.info(f'FINAL Rule2score after process video = \n{rule2score}\n')
                if self.outlier:
                    if rule2score['alert']:
                        continue
                    else:
                        self.outlier = False
                        callback(rule2score=rule2score)
                        cntr = 0
                elif rule2score['alert'] and cntr >= CNTR_DELAY:
                    logging.info(f'FINAL Rule2score after process video = \n{rule2score}\n')
                    self.outlier = True
                    callback(rule2score=rule2score)
                else:
                    cntr += 1
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


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default="l_05_persons_0_01.mp4",
                        help="increase output verbosity")
    return parser

if __name__ == "__main__":
    parser = process_args()
    args = parser.parse_args()

    model_path = os.path.join('/Users/lucky13/Downloads', 'ssd_mobilenet_v1_coco_2018_01_28/frozen_inference_graph.pb')
    pipe = detectionPipeline('/Users/lucky13/Downloads/Hack/l_05_persons_0_smoke_1_01.mp4', './config_ex.json', models_paths=[model_path])

    pipe.processVideo()
