"""
mac-typing-cat

A movable floating bongo-cat that types while you type.

Author: Meiru Zhang
Date: 2024-07-04
"""


import sys
import warnings
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QMouseEvent
from ApplicationServices import *

warnings.filterwarnings("ignore", category=DeprecationWarning)

class CatTypingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.l1 = self.l2 = self.r1 = self.r2 = 0
        self.lstate = self.rstate = 0
        self.initUI()
        self.setupKeyboardAreas()
        self.setupEventTap()
        self.dragging = False
        self.offset = QPoint()


    def initUI(self):
        self.setGeometry(300, 300, 100, 100)  # Set a fixed size for the window
        self.setWindowTitle('Cat Typing')
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        self.setLayout(layout)

        self.label = QLabel(self)
        self.label.setFixedSize(100, 100)  # Set a fixed size for the label
        self.label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")  # Fully transparent
        layout.addWidget(self.label)

        self.close_button = QPushButton("×", self)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 100);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 200);
            }
        """)
        self.close_button.setFixedSize(15, 15)
        self.close_button.clicked.connect(self.close_application)
        self.close_button.move(80, 5)  # Position in top-right corner

        self.images = [
            [QPixmap(f"res/{i}{j}.gif").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
             for j in range(3)]
            for i in range(3)
        ]

        self.updateImage()
        self.show()





    def close_application(self):
        QApplication.quit()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def setupKeyboardAreas(self):
        self.l1keys = set('`1qaz2ws')
        self.l2keys = set('3edc4rfv5tgb x')
        self.r1keys = set('6yhn7ujm8ik,')
        self.r2keys = set('9ol.0p;/-[=]')

        self.l1keys.update(["[tab]", "[esc]", "[caps]", "[left-ctrl]", "[left-shift]", "[left-option]", "[f1]", "[f2]"])
        self.l2keys.update(["[left-cmd]", "[f3]", "[f4]", "[f5]"])
        self.r1keys.update(["[right-cmd]", "[F6]", "[F7]", "[F8]", "[left]"])
        self.r2keys.update(["\\", "'", "[right-ctrl]", "[right-shift]", "[right-option]", "[F9]", "[F10]", "[F11]", "[F12]"])

    # def updateImage(self):
    #     self.label.setPixmap(self.images[self.lstate][self.rstate].scaled(
    #         self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
    def updateImage(self):
        self.label.setPixmap(self.images[self.lstate][self.rstate])

    def CGEventCallback(self, proxy, type, event, refcon):
        if type not in [kCGEventKeyDown, kCGEventFlagsChanged, kCGEventKeyUp]:
            return event

        keyCode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
        keyname = self.convertKeyCode(keyCode)

        flags = CGEventGetFlags(event)
        if keyname.lower() == 'q' and type == kCGEventKeyDown and (flags & kCGEventFlagMaskCommand or flags & kCGEventFlagMaskControl):
            QTimer.singleShot(0, self.close_application)
            return event

        if type == kCGEventKeyDown:
            s = "down"
        elif type == kCGEventKeyUp:
            s = "up"
        elif type == kCGEventFlagsChanged:
            if (flags & self.modflag.get(keyname, 0)) == self.modflag.get(keyname, 1):
                s = "down"
            else:
                s = "up"

        keyarea = 4  # 1/2/3/4, 4 by default
        if keyname in self.l1keys:
            keyarea = 1
        elif keyname in self.l2keys:
            keyarea = 2
        elif keyname in self.r1keys:
            keyarea = 3
        elif keyname in self.r2keys:
            keyarea = 4

        newstate = 1 if s == "down" else 0
        if keyarea == 1:
            self.l1 = newstate
        elif keyarea == 2:
            self.l2 = newstate
        elif keyarea == 3:
            self.r1 = newstate
        elif keyarea == 4:
            self.r2 = newstate

        if self.l1 == 0 and self.l2 == 0:
            self.lstate = 0
        elif (self.l1 == 1 and self.l2 == 0) or (self.l1 == 1 and self.l2 == 1 and s == "down" and keyarea == 1):
            self.lstate = 1
        elif (self.l1 == 0 and self.l2 == 1) or (self.l1 == 1 and self.l2 == 1 and s == "down" and keyarea == 2):
            self.lstate = 2

        if self.r1 == 0 and self.r2 == 0:
            self.rstate = 0
        elif (self.r1 == 1 and self.r2 == 0) or (self.r1 == 1 and self.r2 == 1 and s == "down" and keyarea == 3):
            self.rstate = 1
        elif (self.r1 == 0 and self.r2 == 1) or (self.r1 == 1 and self.r2 == 1 and s == "down" and keyarea == 4):
            self.rstate = 2

        QTimer.singleShot(0, self.updateImage)
        return event

    def convertKeyCode(self, keyCode):
        # Include the full keyCode to keyname mapping here
        keymap = {
            0: "a", 1: "s", 2: "d", 3: "f", 4: "h", 5: "g", 6: "z", 7: "x",
            8: "c", 9: "v", 11: "b", 12: "q", 13: "w", 14: "e", 15: "r",
            16: "y", 17: "t", 18: "1", 19: "2", 20: "3", 21: "4", 22: "6",
            23: "5", 24: "=", 25: "9", 26: "7", 27: "-", 28: "8", 29: "0",
            30: "]", 31: "o", 32: "u", 33: "[", 34: "i", 35: "p", 37: "l",
            38: "j", 39: "'", 40: "k", 41: ";", 42: "\\", 43: ",", 44: "/",
            45: "n", 46: "m", 47: ".", 50: "`", 65: "[decimal]", 67: "[asterisk]",
            69: "[plus]", 71: "[clear]", 75: "[divide]", 76: "[enter]", 78: "[hyphen]",
            81: "[equals]", 82: "0", 83: "1", 84: "2", 85: "3", 86: "4", 87: "5",
            88: "6", 89: "7", 91: "8", 92: "9", 36: "[return]", 48: "[tab]",
            49: " ", 51: "[del]", 53: "[esc]", 54: "[right-cmd]", 55: "[left-cmd]",
            56: "[left-shift]", 57: "[caps]", 58: "[left-option]", 59: "[left-ctrl]",
            60: "[right-shift]", 61: "[right-option]", 62: "[right-ctrl]", 63: "[fn]",
            64: "[f17]", 72: "[volup]", 73: "[voldown]", 74: "[mute]", 79: "[f18]",
            80: "[f19]", 90: "[f20]", 96: "[f5]", 97: "[f6]", 98: "[f7]", 99: "[f3]",
            100: "[f8]", 101: "[f9]", 103: "[f11]", 105: "[f13]", 106: "[f16]",
            107: "[f14]", 109: "[f10]", 111: "[f12]", 113: "[f15]", 114: "[help]",
            115: "[home]", 116: "[pgup]", 117: "[fwddel]", 118: "[f4]", 119: "[end]",
            120: "[f2]", 121: "[pgdown]", 122: "[f1]", 123: "[left]", 124: "[right]",
            125: "[down]", 126: "[up]"
        }
        return keymap.get(keyCode, "[unknown]")

    def setupEventTap(self):
        self.modflag = {
            "[left-shift]"   : 0b000000100000000000000010,
            "[right-shift]"  : 0b000000100000000000000100,
            "[left-ctrl]"    : 0b000001000000000000000001,
            "[right-ctrl]"   : 0b000001000010000000000000,
            "[left-option]"  : 0b000010000000000000100000,
            "[right-option]" : 0b000010000000000001000000,
            "[left-cmd]"     : 0b000100000000000000001000,
            "[right-cmd]"    : 0b000100000000000000010000
        }

        eventMask = (CGEventMaskBit(kCGEventKeyDown) | CGEventMaskBit(kCGEventKeyUp) | CGEventMaskBit(kCGEventFlagsChanged))
        eventTap = CGEventTapCreate(kCGSessionEventTap, kCGHeadInsertEventTap, 0, eventMask, self.CGEventCallback, 0)
        
        if not eventTap:
            print("ERROR: Unable to create event tap.")
            sys.exit(-1)

        runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, eventTap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, kCFRunLoopCommonModes)
        CGEventTapEnable(eventTap, True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CatTypingWindow()
    sys.exit(app.exec_())