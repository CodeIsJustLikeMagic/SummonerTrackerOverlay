# Bot.py
from datetime import datetime

from PIL.ImageDraw import ImageDraw
from PIL import Image, ImageEnhance, ImageDraw
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QSystemTrayIcon, QMenu, QDesktopWidget, \
    QGraphicsDropShadowEffect, QPushButton, QGridLayout, QFrame, QMessageBox, QProgressBar, QHBoxLayout, QWidget, \
    QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread
import paho.mqtt.client as mqtt
import threading
from numpy import unicode
import os, sys
import requests
import json
import time
from datetime import datetime
from datetime import date
import ctypes
import keyboard
import re
import logging
import shutil

class Communicate(QObject):
    text = pyqtSignal(str)
    initMove = pyqtSignal(int, int)
    setterChampion = pyqtSignal(int, str)
    settSpell = pyqtSignal(int, str, str)
    resetPos = pyqtSignal()
    move = pyqtSignal()
    unmovable = pyqtSignal()
    styleactiveButton = pyqtSignal(int)
    styleupButton = pyqtSignal(int)
    exitC = pyqtSignal()
    hotkeyClicked = pyqtSignal()
    status = pyqtSignal(str)
    unsetAll = pyqtSignal()
    showmqtt = pyqtSignal()
    updateColors = pyqtSignal()
    block = pyqtSignal(int)
    toogleShow = pyqtSignal()
    updateTimers = pyqtSignal()
    helloInfo = pyqtSignal()


c = Communicate()


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


class SetterWindow(QDialog):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)
        self.ismovable = False
        self.setStyledark = "color: rgb(150,150,150); background-color: rgb(90,90,90)"
        self.unSetStylelight = "color: rgb(230,230,230); background-color: rgb(150,150,150)"
        self.redStyle = "color: rgb(230,230,230); background-color: rgb(200,50,50)"

        font = QFont('Serif', 11)
        font.setWeight(62)

        self.championLabels = []
        self.ultButtons = []
        for x in range(5):
            champlbl = QLabel("player" + str(x + 1))
            champlbl.setFont(font)
            champlbl.setStyleSheet("color: rgb(230,230,230)")
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            champlbl.setGraphicsEffect(effect)
            grid_layout.addWidget(champlbl, x * 2, 0)
            self.championLabels.append(champlbl)
            champsult = SpellButton("ult")
            # champsult.setFixedSize(70, 35)
            champsult.setFont(font)
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            champsult.setGraphicsEffect(effect)
            champsult.setStyleSheet(self.unSetStylelight)
            grid_layout.addWidget(champsult, 1 + (x * 2), 0)
            self.ultButtons.append(champsult)

        self.spellButtons = []
        self.minButtons = []
        for x in range(10):
            spellButton = SpellButton("spell")
            spellButton.setFixedSize(33, 33)
            spellButton.setFont(font)
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            spellButton.setGraphicsEffect(effect)
            spellButton.setStyleSheet("color: rgb(230,230,230); background-color: rgb(150,150,150)")
            grid_layout.addWidget(spellButton, x, 1)
            self.spellButtons.append(spellButton)
            minButton = QPushButton("-30 sec")
            minButton.setFont(font)
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            minButton.setGraphicsEffect(effect)
            minButton.setStyleSheet(self.unSetStylelight)
            grid_layout.addWidget(minButton, x, 2)
            self.minButtons.append(minButton)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        grid_layout.addWidget(line, 14, 4)

        self.moveLabel = QLabel('grab me!')
        self.moveLabel.setFont(font)
        self.moveLabel.setStyleSheet(
            "border: 5px solid white; color: rgb(230,230,230); background-color: rgb(150,150,150)")
        grid_layout.addWidget(self.moveLabel, 13, 2)
        self.moveLabel.hide()

        self.reloadButton = QPushButton('reload')
        self.reloadButton.setFont(font)
        self.reloadButton.setStyleSheet("color: rgb(230,230,230); background-color: rgb(150,150,150)")
        grid_layout.addWidget(self.reloadButton, 12, 2)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(0)
        effect.setColor(QColor(0, 0, 0, 255))
        effect.setOffset(1)
        self.reloadButton.setGraphicsEffect(effect)
        self.reloadButton.clicked.connect(lambda: mqttclient.renonnectmqtt())

        self.spellButtons[0].clicked.connect(lambda: self.StartSpellTrack(0, 7))
        self.spellButtons[1].clicked.connect(lambda: self.StartSpellTrack(1, 7))
        self.spellButtons[2].clicked.connect(lambda: self.StartSpellTrack(2, 7))
        self.spellButtons[3].clicked.connect(lambda: self.StartSpellTrack(3, 7))
        self.spellButtons[4].clicked.connect(lambda: self.StartSpellTrack(4, 7))
        self.spellButtons[5].clicked.connect(lambda: self.StartSpellTrack(5, 7))
        self.spellButtons[6].clicked.connect(lambda: self.StartSpellTrack(6, 7))
        self.spellButtons[7].clicked.connect(lambda: self.StartSpellTrack(7, 7))
        self.spellButtons[8].clicked.connect(lambda: self.StartSpellTrack(8, 7))
        self.spellButtons[9].clicked.connect(lambda: self.StartSpellTrack(9, 7))

        self.minButtons[0].clicked.connect(lambda: self.ModifySpellTrack(0))
        self.minButtons[1].clicked.connect(lambda: self.ModifySpellTrack(1))
        self.minButtons[2].clicked.connect(lambda: self.ModifySpellTrack(2))
        self.minButtons[3].clicked.connect(lambda: self.ModifySpellTrack(3))
        self.minButtons[4].clicked.connect(lambda: self.ModifySpellTrack(4))
        self.minButtons[5].clicked.connect(lambda: self.ModifySpellTrack(5))
        self.minButtons[6].clicked.connect(lambda: self.ModifySpellTrack(6))
        self.minButtons[7].clicked.connect(lambda: self.ModifySpellTrack(7))
        self.minButtons[8].clicked.connect(lambda: self.ModifySpellTrack(8))
        self.minButtons[9].clicked.connect(lambda: self.ModifySpellTrack(9))

        self.ultButtons[0].clicked.connect(lambda: self.StartSpellTrack(10, 7))
        self.ultButtons[1].clicked.connect(lambda: self.StartSpellTrack(11, 7))
        self.ultButtons[2].clicked.connect(lambda: self.StartSpellTrack(12, 7))
        self.ultButtons[3].clicked.connect(lambda: self.StartSpellTrack(13, 7))
        self.ultButtons[4].clicked.connect(lambda: self.StartSpellTrack(14, 7))

        for btn in self.spellButtons:
            btn.installEventFilter(self)
        for btn in self.ultButtons:
            btn.installEventFilter(self)

        self.postxtfilepath = os.path.join(appdatadir.overlaydir, "pos2.txt")
        self.a = c
        c.setterChampion.connect(lambda index, val: self.setchampionlabel(index, val))
        c.settSpell.connect(lambda index, val, id: self.setbuttondata(index, val, id))
        c.resetPos.connect(self.resetPos)
        c.move.connect(self.movable)
        c.styleactiveButton.connect(lambda index: self.styleactiveButton(index))
        c.styleupButton.connect(lambda index: self.unsetColorButton(index))
        c.exitC.connect(self.close)
        c.unmovable.connect(self.unmovable)
        c.hotkeyClicked.connect(self.showOnKeyboardPress)
        c.unsetAll.connect(self.clearAllButtons)
        c.updateColors.connect(self.updateColors)
        c.block.connect(lambda index: self.blockButton(index))
        c.toogleShow.connect(lambda: self.toogleShow())
        c.updateTimers.connect(self.updateTimers)
        self.lastAction = time.time()

        self.move(width * 0.85, height * 0.2)

        self.show()
        try:

            with open(self.postxtfilepath) as f:
                pos = f.read()
                pos = pos.split(' ')
                if len(pos) == 2:
                    # print('moving overlay to position from appdata file')
                    self.move(int(int(pos[0]) / 2), int(int(pos[1]) / 2))
        except FileNotFoundError:
            pass
        self.hide()
        logging.debug('m1 setter window created')
        self.allwaysShow = False
        self.cdtimer = QTimer()
        self.cdtimer.timeout.connect(self.updateTimers)
        self.cdtimer.setInterval(1000)
        self.cdtimer.start()

    def updateTimers(self):
        for btn in self.spellButtons:
            self.updateTimerButton(btn)
        for btn in self.ultButtons:
            self.updateTimerButton(btn)

    def updateTimerButton(self, spellbutton):
        if spellbutton.showflag:
            track = dataholder.getTrack(spellbutton.id)
            if track is not None:
                left = int(track.endTrack - gameTime.elapsed)
                if left < 0:
                    print('settext ""')
                    spellbutton.setText("")
                else:
                    spellbutton.setText(str(left))

    def getButton(self, index):
        if index >= 10:
            return self.ultButtons[index - 10]
        else:
            return self.spellButtons[index]

    def blockButton(self, index):
        btn = self.getButton(index)
        if btn.justPressed:
            btn.justPressed = False
            print('ignore disable', index)
            return
        btn.setEnabled(False)
        print('disabled', index)
        QTimer.singleShot(1300, lambda: self.unblock(index))

    def unblock(self, index):
        spellbutton = self.getButton(index)
        spellbutton.setEnabled(True)
        if spellbutton.underMouse():
            self.redButton(spellbutton)
        print('enabled', index)

    def eventFilter(self, spellbutton, event):
        if event.type() == QtCore.QEvent.HoverEnter:
            self.waitandSeeIfIdle()
            if spellbutton.isEnabled() and spellbutton.set:
                self.redButton(spellbutton)
                return True
            if not spellbutton.set:
                id = (spellbutton.id)
                spell = dataholder.getSpell(id)
                cd = float("{:.2f}".format(calculateCD(spell)))
                if spellbutton.spellName != 'ult':
                    cd = int(cd)
                spellbutton.setText(str(cd))
                print(spellbutton.brighterStyle)
                spellbutton.setStyleSheet(spellbutton.brighterStyle)
                print('show')
        if event.type() == QtCore.QEvent.HoverLeave:
            self.waitandSeeIfIdle()
            if spellbutton.set:
                self.darkButton(spellbutton)
            else:
                self.brightButton(spellbutton)
            return True
        return False

    def showOnKeyboardPress(self):
        if self.isHidden():
            self.waitandSeeIfIdle()
            self.setHidden(False)
        else:
            self.hide()
        # show but dont steal focus on hotkeypressnnn
        # hide again if hotkey is pressed again

    def policyAllwaysShow(self):
        self.setHidden(False)
        self.allwaysShow = True

    def policyhideWhenInactive(self):
        self.hide()
        self.allwaysShow = False

    def toogleShow(self):
        # change policy. toogle between allwaysshow and hide when inactive
        if self.allwaysShow:
            self.policyhideWhenInactive()
        else:
            self.policyAllwaysShow()

    def clearAllButtons(self):
        for num, lbl in enumerate(self.championLabels, start=1):
            lbl.setText('player' + str(num))
        for btn in self.spellButtons:
            btn.setText('spell')
            btn.spellName = 'spell'
            btn.set = False
            btn.justPressed = False
            btn.setStyleSheet(self.unSetStylelight)
            btn.brighterStyle = self.unSetStylelight
            btn.brightStyle = self.unSetStylelight
            btn.darkStyle = self.setStyledark
        for btn in self.minButtons:
            btn.setStyleSheet(self.unSetStylelight)
        for num, btn in enumerate(self.ultButtons, start=0):
            btn.setStyleSheet(self.unSetStylelight)
            btn.set = False
            btn.justPressed = False

    def updateColors(self):
        for btn in self.spellButtons:
            self.brightButton(btn)
            btn.set = False
        for btn in self.ultButtons:
            self.brightButton(btn)
            btn.set = False
        tracks = {}
        with datalock:
            tracks = dataholder.tracks
        if len(tracks) == 0:
            return
        else:
            for id, track in dataholder.tracks.items():
                if track.endTrack > gameTime.elapsed:
                    btnindex = dataholder.buttons.get(id)
                    self.styleactiveButton(btnindex)

    def unsetColorButton(self, index):
        btn = self.getButton(index)
        if btn.set:
            self.brightButton(btn)
            btn.set = False

    def styleactiveButton(self, index):
        btn = self.getButton(index)
        btn.set = True
        if btn.justPressed:
            if btn.underMouse():
                self.redButton(btn)
                return
        self.darkButton(btn)
        return

    def redButton(self, spellbutton):
        spellbutton.setText("X")
        spellbutton.setStyleSheet(self.redStyle)
        spellbutton.showflag = False

    def brightButton(self, spellbutton):
        spellbutton.setStyleSheet(spellbutton.brightStyle)
        print('setbrightbutton')
        spellbutton.setText(spellbutton.spellName)
        spellbutton.showflag = False

    def darkButton(self, spellbutton):
        spellbutton.setStyleSheet(spellbutton.darkStyle)
        spellbutton.setText(spellbutton.spellName)
        spellbutton.showflag = True
        self.updateTimerButton(spellbutton)

    def brightStyle(self, iconName):
        path = os.path.join(appdatadir.jsondir, iconName + ".png")
        path = path.replace('\\', '/')
        # spellButton.setStyleSheet('border-image: url("'+path+'");')
        return 'border-image: url("' + path + '"); color:rgb(240,240,240);'

    def darkStyle(self, iconName):
        return self.brightStyle(iconName + 'darken') + "color: rgb(230,230,230);"

    def brighterStyle(self, iconName):
        path = os.path.join(appdatadir.jsondir, iconName + "brighten.png")
        path = path.replace('\\', '/')
        # spellButton.setStyleSheet('border-image: url("'+path+'");')
        return 'border-image: url("' + path + '"); color:rgb(0,0,0);'

    def setchampionlabel(self, index, val):
        self.championLabels[index].setText(val)

    def setbuttondata(self, index, val, id):
        print('setbuttondata', index, val, id)
        logging.debug('     gc* setting spell label ' + str(index) + ' ' + str(val))
        spellButton = self.getButton(index)
        spellButton.setText('')

        if index >= 10:
            spellButton.setText(val)
            spellButton.spellName = val
            spellButton.id = id
        else:
            spell = spellDatabase.get(val)
            icon = spell.icon
            spellButton.spellName = ''
            spellButton.brightStyle = self.brightStyle(icon)
            spellButton.darkStyle = self.darkStyle(icon)
            spellButton.brighterStyle = self.brighterStyle(icon)
            spellButton.id = id
            # set icon
            self.brightButton(spellButton)

    def resetPos(self):
        centerPoint = QDesktopWidget().availableGeometry().center()
        self.move(centerPoint)
        self.savePosition()

    def savePosition(self):
        newPos = self.mapToGlobal(self.pos())
        f = open(self.postxtfilepath, "w")
        f.write(str(newPos.x()) + ' ' + str(newPos.y()))
        f.close()

    def movable(self):
        self.setHidden(False)
        self.ismovable = True
        self.moveLabel.setHidden(False)
        self.policyAllwaysShow()

    def unmovable(self):
        self.ismovable = False
        self.moveLabel.hide()
        self.hide()
        self.policyhideWhenInactive()

    def mousePressEvent(self, event):
        # print('mouse Press Event')
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if (self.ismovable):
                # adjust offset from clicked point to origin of widget
                currPos = self.mapToGlobal(self.pos())
                globalPos = event.globalPos()
                diff = globalPos - self.__mouseMovePos
                newPos = self.mapFromGlobal(currPos + diff)
                self.move(newPos)
                self.__mouseMovePos = globalPos

    def mouseReleaseEvent(self, event):

        self.savePosition()
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

    def waitandSeeIfIdle(self):
        self.lastAction = time.time()
        if not self.allwaysShow:
            QTimer.singleShot(6000, self.checkStillIdle)

    def checkStillIdle(self):
        if time.time() - self.lastAction >= 5.8:
            # print('idle detected')
            self.hide()

    def ModifySpellTrack(self, index):
        print('modify spell track')
        logging.debug('st0 modify spell -30 sec')
        self.waitandSeeIfIdle()
        id = dataholder.getIdByBtnIndex(index)
        spell = dataholder.getSpell(id)
        if spell is None:
            logging.debug('stError spell not found')
            return
        old = dataholder.getTrack(id)
        if old is not None:  # old exists
            if old.endTrack > gameTime.elapsed:  # and is not elapsed
                # modify spell
                modendtrack = old.endTrack - 30
                mqttclient.send('m_' + str(id) + '_' + str(modendtrack))
                logging.debug('st3 send mqtt modified old')
                print('just pressed', index)
                self.getButton(index).justPressed = True
                return
        trackentry = TrackEntry(spell, 30)
        mqttclient.send('a_' + str(id) + '_' + str(trackentry.endTrack))
        logging.debug('st3 send -30 sec mqtt')
        print('just pressed', index)
        self.getButton(index).justPressed = True

    def StartSpellTrack(self, index, modifier):
        logging.debug('st0 starting spell track (0/10)')

        self.waitandSeeIfIdle()
        id = dataholder.getIdByBtnIndex(index)
        spell = dataholder.getSpell(id)
        if spell is None:
            logging.debug('stError spell not found')
            return
        old = dataholder.getTrack(id)
        if old is not None:
            if old.endTrack > gameTime.elapsed:
                mqttclient.send('r_' + str(id))
                return
        trackentry = TrackEntry(spell, modifier)
        print('just pressed', index)
        self.getButton(index).justPressed = True
        mqttclient.send('a_' + str(id) + '_' + str(trackentry.endTrack))
        logging.debug('st3 send mqtt')


class SpellButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.spellName = text
        self.brightStyle = "color: rgb(230,230,230); background-color: rgb(150,150,150)"
        self.darkStyle = "color: rgb(230,230,230); background-color: rgb(90,90,90)"
        self.brighterStyle = "color: rgb(230,230,230); background-color: rgb(150,150,150)"
        self.set = False
        self.justPressed = False
        self.id = 'empty'
        self.showflag = False


def blockButton(id):
    # just added the track. block removing it for a second
    index = dataholder.getButton(id)
    c.block.emit(index)


def saveTrack(id, endTrack):
    logging.debug('st5 attempting to save track (mqtt)')
    buttonIndex = dataholder.getButton(id)
    trackentry = TrackEntry(dataholder.getSpell(id), 0)
    trackentry.updateEndTrack(float(endTrack))
    t = trackentry
    dataholder.addTrack(id, trackentry)
    showTrackEntrys()
    c.styleactiveButton.emit(int(buttonIndex))
    logging.debug('st10 save track success')
    c.updateTimers.emit()


def RemoveTrack(id):
    logging.debug('st3 attempting to remove track (mqtt)')
    track = dataholder.getTrack(id)
    if track is not None:
        dataholder.removeTrack(track)
        showTrackEntrys()
    logging.debug('st8 remove track success')
    c.updateTimers.emit()


def modifyTrack(id, endTrack):
    track = dataholder.getTrack(id)
    if track is not None:
        track.updateEndTrack(float(endTrack))
        dataholder.addTrack(id, track)
        showTrackEntrys()
        c.updateTimers.emit()


class InformationWindow(QDialog):

    def __init__(self, width, height):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.l = QLabel('')

        font = QFont('Serif', 11)
        font.setWeight(62)
        self.l.setFont(font)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(0)
        effect.setColor(QColor(0, 0, 0, 255))
        effect.setOffset(1)
        self.l.setGraphicsEffect(effect)
        self.l.setStyleSheet("color: rgb(230,230,230)")

        self.moveLabel = QLabel('grab me!')
        self.moveLabel.setFont(font)
        self.moveLabel.setStyleSheet(
            "border: 5px solid white; color: rgb(230,230,230); background-color: rgb(150,150,150)")
        layout.addWidget(self.moveLabel, 1, 0)
        self.moveLabel.hide()

        self.statuslbl = QLabel('Overlay Started')
        self.statuslbl.setFont(font)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(0)
        effect.setColor(QColor(0, 0, 0, 255))
        effect.setOffset(1)
        self.statuslbl.setGraphicsEffect(effect)
        self.statuslbl.setStyleSheet("color: rgb(230,230,230);background-color: rgb(90,90,90)")

        c.status.connect(lambda m: self.showStatus(m))
        c.text.connect(lambda m: self.l.setText(m))
        c.showmqtt.connect(self.showMQTTInfo)
        layout.addWidget(self.l, 0, 0)
        layout.addWidget(self.statuslbl, 2, 0)
        self.setFocusPolicy(Qt.NoFocus)
        self.ismovable = False

        # Translate asset paths to useable format for PyInstaller
        icon = QIcon(resource_path('./assets/trackerIcon.xpm'))
        trayIcon = QSystemTrayIcon(icon, self)
        self.setWindowIcon(icon)
        menu = QMenu()
        openHotKeyFileAction = menu.addAction("Set Hotkey")
        global hotkeyFilePath
        openHotKeyFileAction.triggered.connect(self.setHotkey)
        moveAction = menu.addAction("Toggle moveable")
        moveAction.triggered.connect(self.toggleMovable)
        resetPosAction = menu.addAction("Reset Position")
        resetPosAction.triggered.connect(self.resetPos)
        toggleSetterAction = menu.addAction("Toggle hide Setter when idle")
        toggleSetterAction.triggered.connect(lambda: c.toogleShow.emit())
        menu.addSeparator()
        showmqttInfoAction = menu.addAction("Show mqtt info")
        showmqttInfoAction.triggered.connect(self.showMQTTInfo)
        newConnection = menu.addAction('Reload CurrentGame Info')
        newConnection.triggered.connect(mqttclient.renonnectmqtt)
        cdragon = menu.addAction("Update Spell and Item Data")
        cdragon.triggered.connect(self.updateCDragon)
        menu.addSeparator()
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(self.close)
        # self.aboutToQuit(disconnectmqtt())
        c.unmovable.connect(self.unmovable)
        c.helloInfo.connect(self.showHelloInfo)

        self.postxtfilepath = os.path.join(appdatadir.overlaydir, "pos.txt")


        trayIcon.setContextMenu(menu)
        trayIcon.show()
        self.timer = QTimer()
        self.timer.timeout.connect(self.clearStatus)
        self.timer.setSingleShot(True)

        self.move(width * 0.0, height * 0.5)

        self.show()
        try:
            with open(self.postxtfilepath) as f:
                pos = f.read()
                pos = pos.split(' ')
                if len(pos) == 2:
                    self.move(int(int(pos[0]) / 2), int(int(pos[1]) / 2))
        except FileNotFoundError:
            pass
            logging.debug('m* no position file')

        logging.debug('m2 overlay window created')

    def updateCDragon(self):
        updateCDragon()
        updateAllUlts()

    def showHelloInfo(self):
        c.status.emit(mqttclient.helloInfo)
        self.timer.start(10000)

    def showMQTTInfo(self):
        c.status.emit(mqttclient.connectionInfo)

        self.timer.start(10000)

    def setHotkey(self):
        os.startfile(hotkeyFilePath)
        QTimer.singleShot(10000, loadHotkey)

    def clearStatus(self):
        c.status.emit('')

    def showStatus(self, m):
        if len(m) == 0:
            self.statuslbl.hide()
        else:
            self.statuslbl.setHidden(False)
            self.statuslbl.setText(m)

    def closeEvent(self, event) -> None:
        logging.debug('m5 closeing Overlay!')
        mqttclient.disconnectmqtt()
        c.exitC.emit()
        event.accept()

    def resetPos(self):
        c.resetPos.emit()
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
        f = open(self.postxtfilepath, "w")
        f.write(str(newPos.x()) + ' ' + str(newPos.y()))
        f.close()

    def toggleMovable(self):
        if self.ismovable:
            self.unmovable()
            c.unmovable.emit()
        else:
            self.movable()

    def movable(self):
        c.move.emit()
        self.ismovable = True
        self.moveLabel.setHidden(False)

    def unmovable(self):
        self.ismovable = False
        self.moveLabel.setHidden(True)

    def visibleIfNoMouse(self):
        if self.l.underMouse() is False:
            self.l.setHidden(False)
            return
        QTimer.singleShot(400, self.visibleIfNoMouse)

    def mousePressEvent(self, event):
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

        self.savePosition()
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return


class Spell():
    def __init__(self, shortName, cd, icon):
        self.shortName = shortName
        self.cd = cd
        self.icon = icon


def calculateCD(spellObject):
    if spellObject is None:
        return -1
    gtcdr = dataholder.getgameTypeCdr()
    if isinstance(spellObject, UltSpell):
        lvl = str(dataholder.getLvL(spellObject.champion))
        cd = spellObject.cddir.get(lvl)
        cdr = getItemUcdr(spellObject)

        if cdr >= 40:
            cdr = 40
        cdr = cdr + dataholder.getclouddrakes()
        cdr = cdr + spellObject.cosmicInsight
        cd = cd * (1 - (cdr / 100.0))
        logging.debug('st? calculate ultspell cd ' + str(cd))
        return cd
    else:
        cd = spellObject.cd
        if spellObject.spellname == 'tp':
            cd = tpCD(spellObject)
        if gtcdr == spellDatabase.get("ARAM"):
            cd = cd * (1.0 - (spellObject.cosmicInsight / 100.0))
            cdr = gtcdr + getItemScdr(spellObject)
            cd = cd * (1.0 - ((gtcdr + getItemScdr(spellObject)) / 100.0))
        else:
            cd = cd * (1.0 - ((getItemScdr(spellObject) + spellObject.cosmicInsight) / 100.0))
        logging.debug('st? calculate summonerspell cd ' + str(cd))
        return cd


class TrackEntry():
    def __init__(self, spell, modifier):
        cd = calculateCD(spell)
        now = gameTime.elapsed
        self.endTrack = now + cd
        self.endTrack = self.endTrack - modifier
        self.spell = spell
        self.endTrack = float("{:.2f}".format(self.endTrack))
        print('created Track', cd, spell.spellname)
        self.updateEndTrack(self.endTrack)

    def updateEndTrack(self, endTrack):
        self.endTrack = endTrack
        self.endTrackMins = time.strftime("%M:%S", time.gmtime(self.endTrack))
        self.desc = self.spell.champion + ' ' + self.spell.spellname + ' ' + self.endTrackMins


class SummonerSpell():
    def __init__(self, cham, spellname, mqttdesc, cosmicInsight):
        self.champion = cham
        self.cosmicInsight = cosmicInsight
        if spellDatabase.get(spellname) is None:
            logging.debug('     gc6 ssError spell ' + spellname + ' doesnt exist in database')
        self.spellname = spellDatabase.get(spellname).shortName
        self.cd = spellDatabase.get(spellname).cd
        self.mqttdesc = mqttdesc
        logging.debug('     gc6 ss0 created summonerspell ' + self.spellname + ' ' + str(self.cd) + ' ' + str(
            self.mqttdesc) + '(0/1)')


class UltSpell():
    def __init__(self, cham, cddir, mqttdesc, runecdr):
        self.champion = cham
        self.cosmicInsight = runecdr
        self.spellname = 'ult'
        self.cddir = cddir
        self.mqttdesc = mqttdesc


class GameTime():
    def __init__(self):
        self.gameStart = time.time()
        self.elapsed = time.time() - self.gameStart

    def setGameTime(self, currentGameTime):
        now = time.time()
        self.gameStart = now - currentGameTime
        now = time.time()
        self.elapsed = now - self.gameStart

    def advanceGameTime(self):
        now = time.time()
        self.elapsed = now - self.gameStart
        self.gameTimeMins = time.strftime("%M:%S", time.gmtime(self.elapsed))


gameTime = GameTime()


def timeAndShow():
    logging.debug('s1 running timeAndShow')
    global activeGameFound
    if activeGameFound:
        gameTime.advanceGameTime()
        showTrackEntrys()
    else:
        # disconnect from game
        dataholder.clear()
        c.text.emit('')
        c.unsetAll.emit()
        global eventnum
        eventnum = -1


def showTrackEntrys():
    show = ''
    with datalock:
        for id, track in dataholder.tracks.items():
            if track.endTrack > gameTime.elapsed:
                show = show + track.desc + '\n'
            else:
                btnindex = dataholder.buttons.get(id)
                c.styleupButton.emit(btnindex)
    if len(show) > 0:
        show = gameTime.gameTimeMins + '\n\n' + show
    c.text.emit(show)


datalock = threading.Lock()


class Dataholder():
    def __init__(self):
        with datalock:
            self.spells = {}
            self.lvls = {}
            self.tracks = {}
            self.championitems = {}
            self.buttons = {}
            self.gtcdr = 0.0
            self.coulddrake = 0.0
            self.enemies = {}

    def saveItems(self, dict):
        with datalock:
            self.allitems = dict

    def getItemCD(self, id):
        with datalock:
            ret = self.allitems.get(str(id))
        return ret

    def saveChampionIds(self, dict):
        with datalock:
            self.championIds = dict

    def getChampionIds(self, name):
        with datalock:
            ret = self.championIds.get(name)
        return ret

    def setgameTypeCdr(self, cdr):
        with datalock:
            self.gtcdr = cdr

    def getgameTypeCdr(self):
        with datalock:
            ret = self.gtcdr
        return ret

    def clear(self):
        with datalock:
            logging.debug('clearing data')
            self.spells = {}
            self.lvls = {}
            self.tracks = {}
            self.buttons = {}
            self.championitems = {}
            self.gtcdr = 0.0
            self.coulddrake = 0.0
            self.enemies = {}

    def getclouddrakes(self):
        with datalock:
            ret = self.coulddrake
        return ret

    def addEnemy(self, champ):
        with datalock:
            self.enemies[champ] = True

    def isEnemy(self, champ):
        with datalock:
            ret = self.enemies.get(champ)
        return ret

    def setcoulddrakes(self, cdr):
        with datalock:
            self.coulddrake = cdr

    def setItems(self, champion, j):
        with datalock:
            self.championitems[champion] = j

    def addButton(self, id, btnindex):
        with datalock:
            self.buttons[id] = btnindex

    def addSpell(self, id, spell):
        with datalock:
            self.spells[id] = spell
            logging.debug('     gc6 ss1 spell saved ' + spell.spellname)

    def setLvl(self, champion, lvl):
        with datalock:
            self.lvls[champion] = lvl
        logging.debug(' gc* ll* set level for ' + champion + ' ' + str(lvl))

    def addTrack(self, id, trackentry):
        logging.debug('st7 attempting to add track')
        with datalock:
            logging.debug('st8 add track')
            dataholder.tracks[id] = trackentry
            sortTracks()

    def removeTrack(self, track):
        with datalock:
            logging.debug('st? removeTrack')
            track.endTrack = float(0)
            sortTracks()

    def getLvL(self, champion):
        with datalock:
            ret = self.lvls.get(champion)
        return ret

    def getItem(self, champion):
        with datalock:
            ret = self.championitems.get(champion)
        return ret

    def getSpell(self, id):
        logging.debug('st1+6 attempting to get spell')
        with datalock:
            ret = self.spells.get(id)
        return ret

    def getTrack(self, id):
        with datalock:
            ret = self.tracks.get(id)
        return ret

    def getButton(self, id):
        with datalock:
            ret = self.buttons.get(id)
        return ret

    def getIdByBtnIndex(self, index):
        with datalock:
            ret = dict((v, k) for k, v in self.buttons.items()).get(index)
        return ret

    def clearButtons(self):
        with datalock:
            self.buttons = {}


def sortTracks():  # called while thread is locked
    logging.debug('st?9 sorting tracks')
    dataholder.tracks = dict(sorted(dataholder.tracks.items(), key=lambda x: x[1].endTrack))


dataholder = Dataholder()


def getItemScdr(summonerspell):
    items = dataholder.getItem(summonerspell.champion)
    scdr = 0.0
    for item in items:
        name = item.get("displayName")
        r = spellDatabase.get(name)
        if r is None:
            r = 0.0
        scdr = scdr + r
    return scdr


def getItemUcdr(ultspell):
    items = dataholder.getItem(ultspell.champion)
    ucdr = 0.0
    # basecdr
    s = []
    for item in items:
        id = item.get('itemID')
        cd = dataholder.getItemCD(id)
        if cd is not None:
            s.append(id)
            cd = cd.get('base')
            if cd is not None:
                ucdr = ucdr + cd
    # qunique
    itemset = set(s)
    for id in itemset:
        cd = dataholder.getItemCD(id)
        cd = cd.get('unique')
        if cd is not None:
            ucdr = ucdr + cd
    for id in itemset:
        cd = dataholder.getItemCD(id)
        cd = cd.get('haste')
        if cd is not None:
            ucdr = ucdr + cd
            break

    return ucdr


def updateAllUlts():
    allspells = {}
    with datalock:
        allspells = dataholder.spells

    for id, spellobject in allspells.items():
        if isinstance(spellobject, UltSpell):
            cdDir = loadUlt(spellobject.champion)
            spellobject.cddir = cdDir
            dataholder.addSpell(id, spellobject)
    # cdDir = loadUlt(champ)
    # dataholder.addSpell(id, UltSpell(champ, cdDir, ultindex, runecdr))


eventnum = -1


def loadLevelsAndItems():
    global eventnum
    logging.debug('gc* ll0 attempting to load levels (0/1)')
    try:
        r = requests.get("https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False)
    except Exception as e:
        logging.debug(str(e))
    j = json.loads(r.content)
    players = j.get("allPlayers")
    for player in players:
        if player.get("team", "") != myteam:
            champ = player.get("championName", "")
            lvl = player.get("level", "")
            dataholder.setLvl(champ, lvl)
            items = player.get("items")
            dataholder.setItems(champ, items)
    events = j.get('events').get('Events')
    for event in events:
        eventId = event.get("EventID")
        if eventId > eventnum:  # not proecessed yet.
            eventnum = eventId
            if event.get("EventName") == "DragonKill":  # check for air drake kill
                if event.get("DragonType") == "Air":
                    # check if killer is enemy
                    killer = event.get("KillerName")
                    logging.debug('gc* ll* could drake killed by enemy')
                    if dataholder.isEnemy(killer) is not None:
                        old = dataholder.getclouddrakes()
                        print('new cloud drake killed by enemy')
                        # cloud drake cdr hardcoded!!!
                        new = old + 10
                        dataholder.setcoulddrakes(new)
    logging.debug('gc*  ll1 loadlevel success')


myteam = "empty"


def loadWithApi():
    logging.debug('gc3 loading with api')
    # api_connection_data = lcu.connect("D:/Program/RiotGames/LeagueOfLegends")
    try:
        r = requests.get("https://127.0.0.1:2999/liveclientdata/playerlist", verify=False)
    except Exception as e:
        return None, None
    activeplayer = requests.get("https://127.0.0.1:2999/liveclientdata/activeplayername", verify=False)
    activeplayer = json.loads(activeplayer.content)
    status = requests.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify=False)
    gametype = json.loads(status.content).get("gameMode")
    logging.debug('gc4 activeplayer ' + activeplayer)
    j = json.loads(r.content)
    li = []
    global myteam
    for player in j:
        name = player.get("summonerName", "")
        if name == activeplayer:
            myteam = player.get("team", "")
        li.append(player.get("summonerName", ""))
    li.append(myteam)
    logging.debug('gc5 using for topic: ' + str(li))
    index = 0
    ultindex = 10
    dataholder.clearButtons()
    gtcdr = spellDatabase.get(gametype)
    if gtcdr is None:
        runecdr = 0.0
    dataholder.setgameTypeCdr(gtcdr)
    for player in j:
        if player.get("team", "") != myteam:
            name = player.get("summonerName", "")
            champ = player.get("championName", "")
            dataholder.addEnemy(name)
            sp1 = player.get("summonerSpells").get("summonerSpellOne").get("displayName")
            sp2 = player.get("summonerSpells").get("summonerSpellTwo").get("displayName")

            if sp2 == 'Flash':
                temp = sp2
                sp2 = sp1
                sp1 = temp

            runecdr = 0.0
            runes = player.get('runes')
            for rune in runes:
                rune = runes.get(rune)
                name = rune.get("displayName")
                cdr = spellDatabase.get(name)
                if cdr is not None:
                    runecdr = runecdr + cdr
            logging.debug(' gc6_0 enemy ' + name + ' ' + champ + ' ' + sp1)
            id = champ + 'Spell1'
            dataholder.addSpell(id, SummonerSpell(champ, sp1, index, runecdr))
            dataholder.addButton(id, index)
            temp = c
            c.settSpell.emit(index, sp1, id)
            index = index + 1

            id = champ + 'Spell2'
            logging.debug(' gc6_1 enemy ' + name + ' ' + champ + ' ' + sp2)
            dataholder.addSpell(id, SummonerSpell(champ, sp2, index, runecdr))
            dataholder.addButton(id, index)
            c.settSpell.emit(index, sp2, id)
            index = index + 1
            id = champ + 'Ult' \
                         ''
            cdDir = loadUlt(champ)
            dataholder.addSpell(id, UltSpell(champ, cdDir, ultindex, runecdr))
            dataholder.addButton(id, ultindex)
            c.settSpell.emit(ultindex, 'ult', id)
            # set sp1, sp2, champName in window (change setterWindow with list of champions and spells)
            c.setterChampion.emit(ultindex - 10, champ)
            ultindex = ultindex + 1
            logging.debug(' gc6_2 enemy done')
    topic = str(hashNames(li))
    logging.debug('gc7 sucessfull loading with api')
    return topic, str(java_string_hashcode(activeplayer))


def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    logging.debug('st4 reciveing mqtt message ' + str(msg))
    # print('message', msg)
    msg = msg.split('_')
    if msg[0] == 'a':
        saveTrack(msg[1], msg[2])
        blockButton(msg[1])
        return
    if msg[0] == 'r':
        RemoveTrack(msg[1])
        return
    if msg[0] == 'm':
        modifyTrack(msg[1], msg[2])
        blockButton(msg[1])
        return
    return


class Mqttclient():
    def __init__(self):
        self.clientHolder = None
        self.connectionInfo = 'will connect once game starts'

    def connect(self, topicsuffix, clientIdSuffix):
        # print('connecting mqtt client')
        if topicsuffix is None:
            return
        broker_address = "mqtt.eclipse.org"
        self.clientID = "observer" + clientIdSuffix
        self.topic = "SpellTracker2/Match" + topicsuffix
        client = mqtt.Client(self.clientID)
        client.on_message = on_message
        # print(clientID,topic)
        client.connect(broker_address)
        self.connectionInfo = 'connected\n' + 'topic ' + self.topic + '\nclient id ' + self.clientID
        keys = '^'
        try:
            with open(hotkeyFilePath, encoding="utf-8") as f:
                keys = (f.read())
        except FileNotFoundError:
            pass
        self.helloInfo = 'connected to game\npress hotkey ' + keys + ' to start Timers'
        c.helloInfo.emit()
        client.subscribe(self.topic)
        client.loop_start()
        self.clientHolder = client
        logging.debug('gc8 sucessfull mqtt connect')

    def send(self, msg):
        if self.clientHolder is not None:
            logging.debug('st2 publishing ' + str(msg))
            self.clientHolder.publish(self.topic, msg)

    def disconnectmqtt(self):
        if self.clientHolder is not None:
            self.clientHolder.disconnect()

    def renonnectmqtt(self):
        logging.debug('gc0123 user issued reconnect. loading and connecting mqtt (0/8)')
        self.disconnectmqtt()
        topicsuffix, clientIdSuffix = loadWithApi()
        self.connect(topicsuffix, clientIdSuffix)
        loadHotkey()
        # reset the colors of buttons
        c.updateColors.emit()


mqttclient = Mqttclient()


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
    # print('hashNames', li)
    li = sorted(li)
    con = ''
    for e in li:
        con = con + e
    h = java_string_hashcode(con)
    return h


activeGameFound = False
tries = 1


def testConnection(s):
    global activeGameFound
    logging.debug('gc1 trying to find game/ updating time and levels. game found :' + str(activeGameFound))
    # print(activeGameFound)
    global tries
    try:
        r = s.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify=False)
        if r.status_code != 200:
            return
        if activeGameFound is False:
            activeGameFound = True
            logging.debug('gc2 connecting to game')
            j = json.loads(r.content)
            currentTime = j.get("gameTime")
            gameTime.setGameTime(currentTime)
            topicsuffix, clientIdSuffix = loadWithApi()
            mqttclient.connect(topicsuffix, clientIdSuffix)
            loadLevelsAndItems()
            tries = 1
            startShowTrackThread()
            return
        logging.debug('gc2 game is running, updating time and level')
        j = json.loads(r.content)
        currentTime = j.get("gameTime")
        gameTime.setGameTime(currentTime)
        loadLevelsAndItems()
        return
    except Exception as e:
        logging.debug('gc2 encountered (network)error in gamecheck' + str(e))
        # print(tries)
        if tries == 3:
            # print(tries, 1)
            c.status.emit('')
            tries = tries + 1
        elif tries == 2:
            c.status.emit('Will keep looking even when hiding')
            tries = tries + 1
        elif tries == 1:
            # print(tries, 'no active game')
            c.status.emit('Looking for active game...')
            tries = tries + 1
        if activeGameFound:
            # print('disconnect previous mqtt connection')
            mqttclient.disconnectmqtt()
        activeGameFound = False
        return


def gameCheck(s):
    logging.debug('gc0 gameCheck thread loop alive (0/8 connection)')
    while True:
        testConnection(s)
        time.sleep(10)


def startThreads():
    logging.debug('m4 starting threads. looking for game')
    s = requests.Session()
    t = threading.Thread(name='activeGameSearch', target=lambda: gameCheck(s))
    t.setDaemon(True)
    t.start()
    t3 = threading.Thread(name='hotkey', target=loadHotkey)
    t3.setDaemon(True)
    t3.start()


def startShowTrackThread():
    logging.debug('s0 starting show and time thread')
    t2 = threading.Thread(name='advanceTime', target=gameTimeThread)
    t2.setDaemon(True)
    t2.start()


def gameTimeThread():
    global activeGameFound
    while activeGameFound:
        time.sleep(1)
        timeAndShow()
    logging.error('s2 gameTime Thread active game lost. no longer running timeAndShow')


hotkeyFilePath = ''


def loadHotkey():
    logging.debug('loading hotkey')
    global hotkeyFilePath
    hotkeyFilePath = os.path.join(appdatadir.overlaydir, "hotkey.txt")
    keys = '^'

    try:
        with open(hotkeyFilePath, encoding="utf-8") as f:
            keys = f.read()
            keys = keys.rstrip()
            keys = keys.replace(' ', '')
    except FileNotFoundError:
        pass
    f = open(hotkeyFilePath, "w")
    f.write(keys)
    f.close()
    try:
        keyboard.clear_all_hotkeys()
    except Exception as e:
        pass
    keyboard.add_hotkey(keys, reactToHotKey)


def reactToHotKey():
    global activeGameFound
    if activeGameFound:
        c.hotkeyClicked.emit()


class AppDataDir():
    def __init__(self):
        self.overlaydir = os.path.join(os.getenv('APPDATA'), "SummonerTrackerOverlay")
        self.jsondir = os.path.join(self.overlaydir, "CDragon")


appdatadir = AppDataDir()


def saveCurrentLogDate(path):
    f = open(path, "w")
    f.write(str(date.today()))
    f.close()


# tp CoolDown Hardcoded!!!!!
def tpCD(spell):
    lvl = dataholder.getLvL(spell.champion)
    ret = (lvl - 1) * ((240 - 420) / 17) + 420

    return ret


spellDatabase = {
    'Heal': Spell('h', 240, 'Heal'),
    'Ghost': Spell('ghost', 210, 'Ghost'),
    'Barrier': Spell('barr', 180, 'Barrier'),
    'Exhaust': Spell('exh', 210, 'Exhaust'),
    'Clarity': Spell('clarity', 240, 'Clarity'),
    'Flash': Spell('f', 300, 'Flash'),
    'HexFlash': Spell('f', 300, 'Flash'),
    'Teleport': Spell('tp', 240, 'Teleport'),
    'Smite': Spell('smite', 15, 'Smite'),
    'Cleanse': Spell('cleanse', 210, 'Cleanse'),
    'Ignite': Spell('ign', 180, 'Ignite'),
    'Mark': Spell('mark', 80, 'Mark'),
    'Dash': Spell('mark', 80, 'Mark'),
    'Challenging Smite': Spell('smite', 15, 'Smite'),
    'Chilling Smite': Spell('smite', 15, 'Smite'),
    'Poro Toss': Spell('p-mark', 80, 'Poro Toss'),
    'Poro Dash': Spell('p-dash', 80, 'Poro Toss'),
    'To the King!': Spell('king', 10, 'To the King!'),
    'Resuscitate': Spell('rev', 100, 'Clarity'),
    'Warp': Spell('warp', 15, 'Teleport'),

    'Ionial Boots of Lucidity': 10.0,
    'ARAM': 40.0,
    'Inspiration': 5.0
}


def initCDragon():
    if not readSummonerSpellsFromFile() or not readChampionIdsFromFile() or not loadItems():
        updateCDragon()
        readSummonerSpellsFromFile()
        readChampionIdsFromFile()
        loadItems()


def deleteOldDragonData():
    folder = appdatadir.jsondir
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            logging.error('m? ucd0 failed to delete old dragon data ' + str(e))


def updateCDragon():
    deleteOldDragonData()
    logging.debug('m? ucd1 updating game data with community dragon')
    updateSummonSpellJson()
    updateChampionIds()
    updateItems()


def updateSummonerIcon(name, iconPath):
    if len(name) == 0:
        return
    name.lower()
    iconPath = iconPath.split('/')
    iconPath = iconPath[len(iconPath) - 1].lower()

    try:
        filepath = os.path.join(appdatadir.jsondir, name + '.png')
        darken = os.path.join(appdatadir.jsondir, name + 'darken.png')
        brighten = os.path.join(appdatadir.jsondir, name + 'brighten.png')
        f = open(filepath, 'wb')
        data = requests.get("http://raw.communitydragon.org/latest/game/data/spells/icons2d/" + iconPath,
                            verify=False).content

        f.write(data)
        f.close()
        im1 = Image.open(filepath)
        factor = 0.5  # darkens the image
        enhancer = ImageEnhance.Brightness(im1)
        im2 = enhancer.enhance(factor)
        im2.save(darken)

        draw = ImageDraw.Draw(im1)
        draw.rectangle((5, 15, 61, 45), fill=(230, 230, 230))

        im1.save(brighten)
    except Exception as e:
        return


def loadUlt(chamName):
    chamNum = dataholder.getChampionIds(chamName)
    ret = loadUltFromFile(chamNum)
    if ret == None:
        updateUltJson(chamNum)
        return loadUltFromFile(chamNum)
    else:
        return ret


def loadUltFromFile(champNum):
    filepath = os.path.join(appdatadir.jsondir, str(champNum) + ".json")
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
            ret = data
        return ret
    except IOError:
        return None


def updateUltJson(champNum):
    logging.debug('m? ucd1 updating summonerspell cd and icons')
    try:
        r = requests.get(
            "http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/" + str(
                champNum) + ".json",
            verify=False)
    except Exception as e:
        logging.debug('m? ucdError ' + e)
        return
    j = json.loads(r.content)
    spellList = j.get('spells')
    ultspell = spellList[len(spellList) - 1]
    basecd = ultspell.get('cooldownCoefficients')
    lvl6 = basecd[0]
    lvl11 = basecd[1]
    lvl16 = basecd[2]
    leveldict = {}
    for i in range(1, 6):
        leveldict[i] = 0
    for i in range(6, 11):
        leveldict[i] = lvl6
    for i in range(11, 16):
        leveldict[i] = lvl11
    for i in range(16, 19):
        leveldict[i] = lvl16

    filepath = os.path.join(appdatadir.jsondir, str(champNum) + ".json")
    with open(filepath, 'w') as outfile:
        json.dump(leveldict, outfile)


def updateSummonSpellJson():
    logging.debug('m? ucd1 updating summonerspell cd and icons')
    try:
        r = requests.get(
            "http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells.json",
            verify=False)
    except Exception as e:
        logging.debug('m? ucdError ' + e)
        return
    j = json.loads(r.content)
    for spell in j:
        # find spell image and save it
        name = spell.get('name')
        iconPath = spell.get('iconPath')
        updateSummonerIcon(name, iconPath)
    filepath = os.path.join(appdatadir.jsondir, "summoner-spells.json")
    with open(filepath, 'w') as outfile:
        json.dump(j, outfile)
    logging.debug('m? ucd2 updating summonerspell cd and icons success')


def updateChampionIds():
    try:
        r = requests.get(
            "http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json",
            verify=False)
    except Exception as e:
        return
    j = json.loads(r.content)
    dict = {}
    for champion in j:
        # find spell image and save it
        name = champion.get('name')
        id = champion.get('id')
        dict[name] = id
    filepath = os.path.join(appdatadir.jsondir, "championId.json")
    with open(filepath, 'w') as outfile:
        json.dump(dict, outfile)


def readChampionIdsFromFile():
    filepath = os.path.join(appdatadir.jsondir, "championId.json")
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
            dataholder.saveChampionIds(data)
        return True
    except IOError:
        return False


def readSummonerSpellsFromFile():
    filepath = os.path.join(appdatadir.jsondir, "summoner-spells.json")
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
            for spell in data:
                name = spell.get('name')
                cd = spell.get('cooldown')
                spell = spellDatabase.get(name)
                if spell is None:
                    spell = Spell(name, cd, name)
                spell.cd = cd
                spellDatabase[name] = spell
        return True
    except IOError:
        return False


def ultcd(champId):
    try:
        r = requests.get(
            "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/101.json",
            verify=False)
    except Exception as e:
        return
    j = json.loads(r.content)


def updateItems():
    try:
        r = requests.get(
            "http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/items.json",
            verify=False)
    except Exception as e:
        return
    j = json.loads(r.content)
    p = re.compile('([0-9]*)% Cooldown Reduction')
    dict = {}
    i = {}
    for item in j:
        itemid = item.get('id')
        for c in item.get('categories'):
            if c == 'CooldownReduction':
                desc = item.get('description')
                l = re.split('UNIQUE', desc, maxsplit=1)
                i = {}
                for desc in l:
                    cdlist = p.findall(desc)
                    if len(cdlist) > 0:
                        cd = 0
                        for c in cdlist:
                            cd = cd + int(c)
                        if re.search('Haste', desc) is not None:
                            i['haste'] = cd
                        elif re.search('UNIQUE', desc) is not None:
                            i['unique'] = cd
                        else:
                            i['base'] = cd
                dict[itemid] = i
    filepath = os.path.join(appdatadir.jsondir, "items.json")
    with open(filepath, 'w') as outfile:
        json.dump(dict, outfile)


def loadItems():
    filepath = os.path.join(appdatadir.jsondir, "items.json")
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
            dataholder.saveItems(data)
        return True
    except IOError:
        return False




def lookForUpdate():
    source = __file__
    base = os.path.basename(__file__)
    base = base.split('.')
    base[0] = base[0].replace('Updated', '')
    dir = os.path.dirname(__file__)
    updated =  os.path.join(dir , base[0] + "Updated.exe")
    notupdated = os.path.join(dir , base[0]+"."+base[1])
    if str(__file__).endswith("Updated."+base[1]):
        shutil.copyfile(source,notupdated)
        logging.debug('update copy self to name without update')
        os.startfile(notupdated)
        sys.exit()
    else:
        #delete if updated exists.
        downloadurl, newversion, notes = outdated()
        if downloadurl is not None: # we are not up to date
            return downloadurl, updated, newversion, notes
        else: # we are up to data. check if updated exists.
            try:
                os.unlink(updated)
                logging.debug('update erased unesesarry updated version')
            except Exception as e:
                print(e)
            return None, None, None, None
def outdated():
    try:
        r = requests.get("https://api.github.com/repos/CodeIsJustLikeMagic/SummonerTrackerOverlay/releases/latest",
                         verify=False)
    except Exception as e:
        return
    j = json.loads(r.content)
    tagName = j.get('tag_name')
    global version
    if tagName == version:
        False
    else:
        # visit github to get the latest release
        # https://github.com/CodeIsJustLikeMagic/SummonerTrackerOverlay/releases/latest
        ret = j.get('assets')[0].get('browser_download_url')
        return ret, tagName, j.get('body')


class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)
    def setText(self, text):
        self.label.setText(text)
class DownLoadWidget(QWidget):
    def __init__(self, downloadUrl, filepath, newversion, notes):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setWindowTitle("Updating...")
        icon = QIcon(resource_path('./assets/trackerIcon.xpm'))
        self.setWindowIcon(icon)
        self.label = QLabel("Update to TrackerOverlay "+newversion +"\n")
        self.label.setStyleSheet('font-size: 10pt')
        layout.addWidget(self.label)
        self.notes = ScrollLabel()
        self.notes.setText(notes)
        self.resize(100,300)
        layout.addWidget(self.notes)
        self.progressBar = QProgressBar(self,minimumWidth = 400)
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)
        self.url = downloadUrl
        self.filepath = filepath
        centerPoint = QDesktopWidget().availableGeometry().center()
        self.move(centerPoint)

        self.show()
    def start(self):
        filesize = requests.get(url, stream=True).headers['Content-Length']
        fileobject = open(self.filepath, 'wb')
        self.downloadThread = downloadThread(url, filesize, fileobject, buffer=10240)
        self.downloadThread.download_proess_signal.connect(self.set_progressbar_value)
        self.downloadThread.start()

    # Setting progress bar
    def set_progressbar_value(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            logging.debug('update downloaded updated version')
            os.startfile(self.filepath)
            self.close()

#################################################################
#Download thread
##################################################################
class downloadThread(QThread):
    download_proess_signal = pyqtSignal(int)                        #Create signal

    def __init__(self, url, filesize, fileobj, buffer):
        super(downloadThread, self).__init__()
        self.url = url
        self.filesize = filesize
        self.fileobj = fileobj
        self.buffer = buffer


    def run(self):
        try:
            rsp = requests.get(self.url, stream=True)                #Streaming download mode
            offset = 0
            for chunk in rsp.iter_content(chunk_size=self.buffer):
                if not chunk: break
                self.fileobj.seek(offset)                            #Setting Pointer Position
                self.fileobj.write(chunk)                            #write file
                offset = offset + len(chunk)
                proess = offset / int(self.filesize) * 100
                self.download_proess_signal.emit(int(proess))        #Sending signal
            #######################################################################
            self.fileobj.close()    #Close file
            self.exit(0)            #Close thread


        except Exception as e:
            print(e)

version = 'v5.4.0'

if __name__ == '__main__':
    try:
        os.mkdir(appdatadir.overlaydir)
    except FileExistsError:
        pass
    try:
        os.mkdir(appdatadir.jsondir)
    except FileExistsError:
        pass
    debugpath = os.path.join(appdatadir.overlaydir, "debug.log")
    print(debugpath)
    logStartPath = os.path.join(appdatadir.overlaydir, "startLogdate.txt")
    try:
        with open(logStartPath) as f:
            logStartDate = f.read()
            if logStartDate == '':
                saveCurrentLogDate(logStartPath)
            logStartDate = datetime.strptime(logStartDate, '%Y-%m-%d').date()
            r = date.today() - logStartDate
            r = r.days
            if r > 7:
                # clear log files every 7 days
                f = open(debugpath, "w")
                f.write('')
                f.close()
                saveCurrentLogDate(logStartPath)
                # update game ressouces every 7 days
                updateCDragon()
    except FileNotFoundError:
        saveCurrentLogDate(logStartPath)
        f = open(debugpath, "w")
        f.write('')
        f.close()
        updateCDragon()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(debugpath),
            logging.StreamHandler()
        ]
    )
    logging.debug('m0 overlay started! (0/4 startup, 0/5 entire run)')
    app = QApplication([])
    myappid = 'summonerTrackerOverlay'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    url, updated, newversion, notes = lookForUpdate()
    updating = False
    if url is not None:
        msgBox = QMessageBox()
        icon = QIcon(resource_path('./assets/trackerIcon.xpm'))
        msgBox.setWindowIcon(icon)
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("TrackerOverlay "+newversion+" is available.\nDo you want to update?")
        msgBox.setWindowTitle("Update available")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        r = msgBox.exec()
        if r == QMessageBox.Ok:
            #downloadNewVersion(url, updated)
            download = DownLoadWidget(url,updated, newversion,notes)
            download.start()
            updating = True
    if not updating:
        initCDragon()
        screen_resolution = app.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        setterWindow = SetterWindow(width, height)
        window = InformationWindow(width, height)
        startThreads()
    app.exec_()
