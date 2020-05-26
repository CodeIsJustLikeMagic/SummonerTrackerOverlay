# Bot.py
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QVBoxLayout, QSystemTrayIcon, QMenu, QDesktopWidget, \
    QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer, QCoreApplication
import paho.mqtt.client as mqtt
import threading
import lcu_connector_python as lcu
from numpy import unicode
import numpy as np


class Communicate(QObject):
    text = pyqtSignal(str)
    initMove = pyqtSignal(int, int)

c = Communicate()

class MainWindow(QDialog):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.l = QLabel('connecting...')

        font = QFont('Serif', 11)
        font.setWeight(62)
        self.l.setFont(font)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(0)
        effect.setColor(QColor(0,0,0,255))
        effect.setOffset(1)
        self.l.setGraphicsEffect(effect)
        c.text.connect(lambda m: self.l.setText(m))
        layout.addWidget(self.l)
        self.setFocusPolicy(Qt.NoFocus)
        self.ismovable = False
        self.l.setStyleSheet("color: rgb(230,230,230)")
        trayIcon = QSystemTrayIcon(QIcon("trackerIcon.xpm"), self)
        menu = QMenu()
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(lambda: QCoreApplication.exit())
        moveAction = menu.addAction("Move")
        moveAction.triggered.connect(lambda: self.movable())
        resetPosAction = menu.addAction("Reset Position")
        resetPosAction.triggered.connect(self.resetPos)
        showmqttInfoAction= menu.addAction("show mqtt info")
        global connectionInfo
        showmqttInfoAction.triggered.connect(lambda : c.text.emit(connectionInfo))
        newConnection = menu.addAction('new Connection')
        newConnection.triggered.connect(renonnectmqtt)


        trayIcon.setContextMenu(menu)
        trayIcon.show()

        self.show()
        try:
            with open("pos.txt") as f:
                pos = f.read()
                pos = pos.split(' ')
                if len(pos) == 2:
                    print('move')
                    self.move(int(int(pos[0]) / 2), int(int(pos[1]) / 2))
        except FileNotFoundError:
            print('no position file')

    def resetPos(self):
        centerPoint = QDesktopWidget().availableGeometry().center()
        self.move(centerPoint)
        self.savePosition()

    def enterEvent(self, event):
        if self.ismovable:
            return
        self.l.hide()
        QTimer.singleShot(400, self.visibleIfNoMouse)

    def savePosition(self):
        newPos = self.mapToGlobal(self.pos())
        f = open("pos.txt", "w")
        f.write(str(newPos.x()) + ' ' + str(newPos.y()))
        f.close()

    def movable(self):
        self.ismovable = True
        print('moveable')
        self.setAttribute(Qt.WA_TranslucentBackground, on=False)
        self.setAutoFillBackground(False)
        self.l.setStyleSheet("border: 3px solid white; color : white")

    def unmovable(self):
        print('unmovable')
        self.ismovable = False
        self.l.setStyleSheet("border: none; color : white")

    def visibleIfNoMouse(self):
        if self.l.underMouse() is False:
            self.l.setHidden(False)
            return
        QTimer.singleShot(400, self.visibleIfNoMouse)

    def mousePressEvent(self, event):
        print('mouse Press Event')
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)
            self.__mouseMovePos = globalPos

    def mouseReleaseEvent(self, event):
        self.unmovable()
        self.savePosition()
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

def on_message(client,userdata,message):
    message = message.payload.decode("utf-8")
    message = message.replace(', ', '\n')
    message = message.replace(',', '')
    print('revieced message', message)
    c.text.emit(message)

def loadTopicsuffix():

    # api_connection_data = lcu.connect("D:/Program/RiotGames/LeagueOfLegends")
    try:
        r = requests.get("https://127.0.0.1:2999/liveclientdata/playerlist", verify=False)
    except Exception as e:
        print('catch error')
        print(e)
        return None,None
    activeplayer = requests.get("https://127.0.0.1:2999/liveclientdata/activeplayername", verify = False)
    activeplayer = json.loads(activeplayer.content)
    j = json.loads(r.content)
    print(j)
    li = np.array([])
    for player in j:
        li = np.append(li, player.get("summonerName", ""))
    topic = str(hashNames(li))
    print(topic)
    return topic, str(java_string_hashcode(activeplayer))

connectionInfo = 'will connect once game starts'
clientHolder = None
def mqttclient():
    print('connecting mqtt client')
    topicsuffix,clientIdSuffix = loadTopicsuffix()
    if topicsuffix is None:
        topicsuffix = "0"
        clientIdSuffix = "000"
    broker_address="mqtt.eclipse.org"
    clientID = "observer"+clientIdSuffix
    topic = "SpellTracker/Match" + topicsuffix
    client = mqtt.Client(clientID)
    client.on_message = on_message
    print(clientID,topic)
    client.connect(broker_address)
    global connectionInfo
    connectionInfo = 'topic ' + topic + '\nclient id '+clientID
    c.text.emit('connected\n'+connectionInfo)
    client.subscribe(topic)
    client.loop_start()
    global clientHolder
    clientHolder = client
    time.sleep(6)
    c.text.emit('')
def disconnectmqtt():
    global clientHolder
    clientHolder.disconnect()
def renonnectmqtt():
    disconnectmqtt()
    mqttclient()
def java_string_hashcode(s):
    """Mimic Java's hashCode in python 2"""
    try:
        s = unicode(s)
    except:
        try:
            s = unicode(s.decode('utf8'))
        except:
            raise Exception("Please enter a unicode type string or utf8 bytestring.")
    h = 0
    for c in s:
        h = int((((31 * h + ord(c)) ^ 0x80000000) & 0xFFFFFFFF) - 0x80000000)
    return h

def hashNames(li):
    print('hashNames', li)
    li = np.sort(li)
    con = ''
    for e in li:
        con = con + e
    print(con)
    h = java_string_hashcode(con)
    return h

import requests
import json
import numpy as np

import time
activeGameFound = False
tries = 1
def dismaldiesmaldiesmal(s):
    global activeGameFound
    global tries
    #print('activeGameFound', activeGameFound)
    try:
        print('activeGame Try')
        then = time.time()
        r = s.get("https://127.0.0.1:2999/help", verify = False)

        if activeGameFound is False:
            activeGameFound = True
            mqttclient()
            tries = 1
    except Exception as e:
        print('exception: no active game, tries '+ str(tries))
        if tries >= 2 :
            c.text.emit('')
        else :
            c.text.emit('no active game found')
            print('disconnectmqtt')
        if activeGameFound:
            disconnectmqtt()
        tries = tries +1
        activeGameFound = False
    #print(time.time() - then)
    time.sleep(20)
    dismaldiesmaldiesmal(s)
def gameStart():
    s = requests.Session()
    t = threading.Thread(name='activeGameSearch', target = lambda: dismaldiesmaldiesmal(s))
    t.setDaemon(True)
    t.start()
if __name__ == '__main__':
    gameStart()
    app = QApplication([])
    window = MainWindow()
    app.exec_()