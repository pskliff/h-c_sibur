import sys
from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, \
    QListWidget, QApplication, QListWidgetItem, QCheckBox, QPushButton, QDialog, QGridLayout
# from PyQt4.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, \
#     QListWidget, QApplication, QListWidgetItem, QCheckBox, QPushButton, QDialog, QGridLayout
from PyQt4 import QtCore
from time import sleep
import os
from detectionPipeline import detectionPipeline
import cv2
import argparse

from alert import AlertInfo, Alert
from simple_thread import SimpleThread

class AlertInfoWindow(QDialog, QWidget):
    def __init__(self, alert, parent=None):
        QDialog.__init__(self, parent)
        super().__init__()
        self.left = 100
        self.top = 100
        self.width = 650
        self.height = 600
        self.img = alert.img
        self.rules = alert.info.rules
        info = 'alert time: ' + str(alert.info.time) + '\n' + 'camera_id: ' + str(alert.info.camera)
        self.info = info
        self.alert = alert
        self.choice = 'cancel'
        self.initUI()

    def initUI(self):
        label = QLabel(self)
        img =  cv2.resize(self.img, (600, 300))
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        image = QtGui.QImage(img.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap(image)
        label.setPixmap(pixmap)
        label.move(25, 25)

        label_h_rules = QLabel("Rules:", self)
        label_h_rules.setFont(QtGui.QFont("Times", 14,QtGui. QFont.Bold))
        label_h_rules.move(50, 350)
        label_rules = QLabel(self.rules, self)
        label_rules.setFont(QtGui.QFont("Times", 14))
        label_rules.move(60, 380)

        label_h_info = QLabel("Info:", self)
        label_h_info.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Bold))
        label_h_info.move(400, 350)
        label_info = QLabel(self.info, self)
        label_info.setFont(QtGui.QFont("Times", 14))
        label_info.move(410, 380)

        resolve_button = QPushButton("Resolve", self)
        resolve_button.clicked.connect(self.on_resolve)
        resolve_button.move(50, 550)
        resolve_button.setEnabled(self.alert.is_resolved)


        ignore_button = QPushButton("Ignore", self)
        ignore_button.clicked.connect(self.on_ignore)
        ignore_button.move(250, 550)

        if self.alert.state != 'alert' :
            resolve_button.setEnabled(False)
            ignore_button.setEnabled(False)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.on_cancel)
        cancel_button.move(450, 550)

        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def on_resolve(self):
        self.choice = 'resolved'
        self.accept()

    def on_ignore(self):
        self.choice = 'ignored'
        self.accept()

    def on_cancel(self):
        self.reject()


class QCustomQWidget (QWidget):
    def __init__ (self, parent = None):
        super(QCustomQWidget, self).__init__(parent)
        self.textQVBoxLayout = QVBoxLayout()
        self.textUpQLabel    = QLabel()
        self.textMidQLabel  = QLabel()
        self.textDownQLabel  = QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textMidQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout  = QHBoxLayout()
        self.iconQLabel      = QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)


    def setItemFromAlert(self, alert: Alert):
        self.textUpQLabel.setText('alert time: ' + str(alert.info.time))
        self.textMidQLabel.setText('camera_id: ' + str(alert.info.camera))
        self.textDownQLabel.setText('rule: ' + alert.info.rules)
        self.setIcon(alert.state + '.png')

    def setTextUp (self, text):
        self.textUpQLabel.setText(text)

    def setTextDown (self, text):
        self.textDownQLabel.setText(text)

    def setIcon (self, imagePath):
        pixmap = QtGui.QPixmap(imagePath)
        self.iconQLabel.setPixmap( pixmap.scaled(48, 48,  QtCore.Qt.KeepAspectRatio))

class MainQMainWindow (QMainWindow):
    def __init__ (self):
        super(MainQMainWindow, self).__init__()
        # Create QListWidget
        self.setFixedSize(800, 500)
        self.myQListWidget = QListWidget(self)
        self.alerts = []
        for alert in self.alerts[::-1]:
            # Create QCustomQWidget
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.setItemFromAlert(alert)
            # Create QListWidgetItem
            myQListWidgetItem = QListWidgetItem(self.myQListWidget)
            # Set size hint
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.myQListWidget.addItem(myQListWidgetItem)
            self.myQListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

        self.myQListWidget.itemDoubleClicked.connect(self._handleDoubleClick)
        self.setCentralWidget(self.myQListWidget)

    #TODO: update 1 element
    def updateValues(self, alerts):
        self.myQListWidget.clear()
        for alert in alerts[::-1]:
            print(alert.state)
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.setItemFromAlert(alert)
            # Create QListWidgetItem
            myQListWidgetItem = QListWidgetItem(self.myQListWidget)
            # Set size hint
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.myQListWidget.addItem(myQListWidgetItem)
            self.myQListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

        self.alerts = alerts


    @SimpleThread
    def server(self, primaryText):

        model_path = os.path.join('frozen_inference_graph.pb')
        pipe = detectionPipeline(args.filename, './config_ex.json',
                                 models_paths=[model_path], gui=self)
        pipe.processVideo()

    ##TODO: ADD HASHMAP
    def search_for_alert(self, cam):
        for idx, alert in enumerate(self.alerts):
            if alert.state == 'alert' and alert.info.camera == cam:
                return idx
        return None


    def _handleDoubleClick(self, item):
        selected_index = self.myQListWidget.currentRow()
        alerts = self.alerts[::-1].copy()
        dialog = AlertInfoWindow(alert=alerts[selected_index], parent=self)
        if dialog.exec_() == QDialog.Accepted:
            alerts[selected_index].state = dialog.choice
            for a in alerts:
                print('AQQQ' + a.state)
            self.updateValues(alerts[::-1])
        else:
            print('Cancelled')
        dialog.deleteLater()

def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default="l_05_persons_0_01.mp4",
                        help="increase output verbosity")
    return parser

argparser = process_args()
args = argparser.parse_args()

app = QApplication([])
window = MainQMainWindow()
window.show()
window.server('From thread', thr_start=True)
sys.exit(app.exec_())