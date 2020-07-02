# Bot.py
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QVBoxLayout, QSystemTrayIcon, QMenu, QDesktopWidget, \
    QGraphicsDropShadowEffect, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
import paho.mqtt.client as mqtt
import threading
from numpy import unicode
import os, sys
import requests
import json
import time


class Communicate(QObject):
    text = pyqtSignal(str)
    initMove = pyqtSignal(int, int)
    setterChampion = pyqtSignal(int, str)
    settSpell = pyqtSignal(int, str)
    resetPos = pyqtSignal()
    move = pyqtSignal()
    unmovable = pyqtSignal()
    colorSet = pyqtSignal(int)
    colorUnset = pyqtSignal(int)
    exitC = pyqtSignal()
    hotkeyClicked = pyqtSignal()
    status = pyqtSignal(str)
    unsetAll = pyqtSignal()
    showmqtt = pyqtSignal()
    updateColors = pyqtSignal()
    block = pyqtSignal(int)
    toogleShow = pyqtSignal()


c = Communicate()


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


class SetterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)
        self.ismovable = False
        self.setStyle = "color: rgb(150,150,150); background-color: rgb(90,90,90)"
        self.unSetStyle = "color: rgb(230,230,230); background-color: rgb(150,150,150)"
        self.redStyle = "color: rgb(230,230,230); background-color: rgb(200,50,50)"

        font = QFont('Serif', 11)
        font.setWeight(62)

        self.championLabels = []
        self.ult = []
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
            champsult.setFont(font)
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            champsult.setGraphicsEffect(effect)
            champsult.setStyleSheet(self.unSetStyle)
            grid_layout.addWidget(champsult, 1 + (x * 2), 0)
            self.ult.append(champsult)

        self.spellButtons = []
        self.minButtons = []
        for x in range(10):
            spellButton = SpellButton("spell")
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
            minButton.setStyleSheet(self.unSetStyle)
            grid_layout.addWidget(minButton, x, 2)
            self.minButtons.append(minButton)
        self.moveLabel = QLabel('grab me!')
        self.moveLabel.setFont(font)
        self.moveLabel.setStyleSheet(
            "border: 5px solid white; color: rgb(230,230,230); background-color: rgb(150,150,150)")
        grid_layout.addWidget(self.moveLabel, 12, 1)
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

        self.ult[0].clicked.connect(lambda: self.StartSpellTrack(10, 7))
        self.ult[1].clicked.connect(lambda: self.StartSpellTrack(11, 7))
        self.ult[2].clicked.connect(lambda: self.StartSpellTrack(12, 7))
        self.ult[3].clicked.connect(lambda: self.StartSpellTrack(13, 7))
        self.ult[4].clicked.connect(lambda: self.StartSpellTrack(14, 7))

        for btn in self.spellButtons:
            btn.installEventFilter(self)
        for btn in self.ult:
            btn.installEventFilter(self)

        self.postxtfilepath = os.path.join(appdatadir.overlaydir, "pos2.txt")
        c.setterChampion.connect(lambda index, val: self.setchampionlabel(index, val))
        c.settSpell.connect(lambda index, val: self.setspelllabel(index, val))
        c.resetPos.connect(self.resetPos)
        c.move.connect(self.movable)
        c.colorSet.connect(lambda index: self.setColorButton(index))
        c.colorUnset.connect(lambda index: self.unsetColorButton(index))
        c.exitC.connect(self.close)
        c.unmovable.connect(self.unmovable)
        c.hotkeyClicked.connect(self.showOnKeyboardPress)
        c.unsetAll.connect(self.clearAllButtons)
        c.updateColors.connect(self.updateColors)
        c.block.connect(lambda index: self.blockButton(index))
        c.toogleShow.connect(lambda: self.toogleShow())
        self.lastAction = time.time()
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

    def getButton(self, index):
        if index >= 10:
            return self.ult[index - 10]
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
            spellbutton.setText('X')
            spellbutton.setStyleSheet(self.redStyle)
        print('enabled', index)

    def eventFilter(self, spellbutton, event):
        if event.type() == QtCore.QEvent.HoverEnter:
            self.waitandSeeIfIdle()
            if spellbutton.isEnabled() and spellbutton.set:
                spellbutton.setStyleSheet(self.redStyle)
                spellbutton.setText('X')
                return True
        if event.type() == QtCore.QEvent.HoverLeave:
            self.waitandSeeIfIdle()
            if spellbutton.set:
                spellbutton.setStyleSheet(self.setStyle)
                spellbutton.setText(spellbutton.spellName)
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
            btn.setStyleSheet(self.unSetStyle)
        for btn in self.minButtons:
            btn.setStyleSheet(self.unSetStyle)
        for num, btn in enumerate(self.ult, start=0):
            btn.setStyleSheet(self.unSetStyle)
            btn.set = False
            btn.justPressed = False

    def updateColors(self):
        for btn in self.spellButtons:
            btn.setStyleSheet(self.unSetStyle)
            btn.set = False
        for btn in self.ult:
            btn.setStyleSheet(self.unSetStyle)
            btn.set = False

        with datalock:
            for id, track in dataholder.tracks.items():
                if track.endTrack > gameTime.elapsed:
                    btnindex = dataholder.buttons.get(id)
                    self.setColorButton(btnindex)

    def unsetColorButton(self, index):
        btn = self.getButton(index)
        btn.setStyleSheet(self.unSetStyle)
        btn.set = False
        btn.setText(btn.spellName)

    def setColorButton(self, index):
        btn = self.getButton(index)
        btn.set = True
        if btn.justPressed:
            if btn.underMouse():
                btn.setText('X')
                btn.setStyleSheet(self.redStyle)
                return
        btn.setStyleSheet(self.setStyle)

        return

    def setchampionlabel(self, index, val):
        self.championLabels[index].setText(val)

    def setspelllabel(self, index, val):
        logging.debug('     gc* setting spell label ' + str(index) + ' ' + str(val))
        self.spellButtons[index].setText(val)
        if index < 10:
            self.spellButtons[index].spellName = val

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
^^
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
        if old is not None: # old exists
            if old.endTrack > gameTime.elapsed: # and is not elapsed
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
        self.set = False
        self.justPressed = False


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
    c.colorSet.emit(int(buttonIndex))
    logging.debug('st10 save track success')


def RemoveTrack(id):
    logging.debug('st3 attempting to remove track (mqtt)')
    track = dataholder.getTrack(id)
    if track is not None:
        dataholder.removeTrack(track)
        showTrackEntrys()
    logging.debug('st8 remove track success')


def modifyTrack(id, endTrack):
    track = dataholder.getTrack(id)
    if track is not None:
        track.updateEndTrack(float(endTrack))
        dataholder.addTrack(id, track)
        showTrackEntrys()


class OverlayWindow(QDialog):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
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
        layout.addWidget(self.l)
        layout.addWidget(self.statuslbl)
        self.setFocusPolicy(Qt.NoFocus)
        self.ismovable = False

        # Translate asset paths to useable format for PyInstaller
        icon = QIcon(resource_path('./assets/trackerIcon.xpm'))
        trayIcon = QSystemTrayIcon(icon, self)
        self.setWindowIcon(icon)
        menu = QMenu()
        openHotKeyFileAction = menu.addAction("Set Hotkey")
        global hotkeyFilePath
        openHotKeyFileAction.triggered.connect(lambda: os.startfile(hotkeyFilePath))
        moveAction = menu.addAction("Move")
        moveAction.triggered.connect(self.toggleMovable)
        resetPosAction = menu.addAction("Reset Position")
        resetPosAction.triggered.connect(self.resetPos)
        toggleSetterAction = menu.addAction("Toggle allays show Setter Window")
        toggleSetterAction.triggered.connect(lambda: c.toogleShow.emit())
        showmqttInfoAction = menu.addAction("Show mqtt info")
        showmqttInfoAction.triggered.connect(self.showMQTTInfo)
        newConnection = menu.addAction('Reload')
        newConnection.triggered.connect(mqttclient.renonnectmqtt)
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(self.close)
        # self.aboutToQuit(disconnectmqtt())
        c.unmovable.connect(self.unmovable)

        self.postxtfilepath = os.path.join(appdatadir.overlaydir, "pos.txt")

        import ctypes
        myappid = 'summonerTrackerOverlay'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        trayIcon.setContextMenu(menu)
        trayIcon.show()
        self.timer = QTimer()
        self.timer.timeout.connect(self.clearStatus)
        self.timer.setSingleShot(True)
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

    def showMQTTInfo(self):
        c.status.emit(mqttclient.connectionInfo)

        self.timer.start(10000)

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
        self.setAttribute(Qt.WA_TranslucentBackground, on=False)
        self.setAutoFillBackground(False)
        self.l.setStyleSheet("border: 3px solid white; color: rgb(230,230,230)")

    def unmovable(self):
        self.ismovable = False
        self.l.setStyleSheet("border: none; color: rgb(230,230,230)")

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
    def __init__(self, shortName, cd):
        self.shortName = shortName
        self.cd = cd

def calculateCD(spell):
    gtcdr = dataholder.getgameTypeCdr()
    if gtcdr == spellDatabase.get("ARAM"):
        cd = spell.cd * (1.0 - (spell.runecdr / 100.0))
        cdr = gtcdr + getItemCDR(spell)
        return cd * (1.0 - ((gtcdr + getItemCDR(spell)) / 100.0))
    else:
        return spell.cd * (1.0 - ((getItemCDR(spell) + spell.runecdr) / 100.0))

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
    def __init__(self, cham, spellname, mqttdesc, runecdr):
        self.champion = cham
        self.runecdr = runecdr
        if spellDatabase.get(spellname) is None:
            logging.debug('     gc6 ssError spell ' + spellname + ' doesnt exist in database')
        self.spellname = spellDatabase.get(spellname).shortName
        self.cd = spellDatabase.get(spellname).cd
        self.mqttdesc = mqttdesc
        logging.debug('     gc6 ss0 created summonerspell ' + self.spellname + ' ' + str(self.cd) + ' ' + str(
            self.mqttdesc) + '(0/1)')

class UltSpell():
    def __init__(self, cham, cd, mqttdesc,runecdr):
        self.champion = cham
        self.runecdr = runecdr
        self.spellname = 'ult'
        self.cd = cd
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
        dataholder.clear()
        c.text.emit('')
        c.unsetAll.emit()


def showTrackEntrys():
    show = ''
    with datalock:
        for id, track in dataholder.tracks.items():
            if track.endTrack > gameTime.elapsed:
                show = show + track.desc + '\n'
            else:
                btnindex = dataholder.buttons.get(id)
                c.colorUnset.emit(btnindex)
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
            self.items = {}
            self.buttons = {}
            self.gtcdr = 0.0
    def setgameTypeCdr(self,cdr):
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
            self.items = {}
            self.gtcdr = 0.0

    def setItems(self, champion, j):
        with datalock:
            self.items[champion] = j

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

    def getItem(self, champion):
        with datalock:
            ret = self.items.get(champion)
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


def getItemCDR(spell):
    items = dataholder.getItem(spell.champion)
    if isinstance(spell, SummonerSpell):
        scdr = 0.0
        for item in items:
            name = item.get("displayName")
            r = spellDatabase.get(name)
            if r is None:
                r = 0.0
            scdr = scdr + r
        return scdr
    return 0.0


def loadLevelsAndItems():
    logging.debug('gc* ll0 attempting to load levels (0/1)')
    try:
        r = requests.get("https://127.0.0.1:2999/liveclientdata/playerlist", verify=False)
    except Exception as e:
        return
    j = json.loads(r.content)
    for player in j:
        if player.get("team", "") != myteam:
            champ = player.get("championName", "")
            lvl = player.get("level", "")
            dataholder.setLvl(champ, lvl)
            items = player.get("items")
            dataholder.setItems(champ, items)

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

            dataholder.addSpell(champ + 'Spell1', SummonerSpell(champ, sp1, index, runecdr))
            dataholder.addButton(champ + 'Spell1', index)
            temp = c
            c.settSpell.emit(index, sp1)
            index = index + 1

            logging.debug(' gc6_1 enemy ' + name + ' ' + champ + ' ' + sp2)
            dataholder.addSpell(champ + 'Spell2', SummonerSpell(champ, sp2, index, runecdr))
            dataholder.addButton(champ + 'Spell2', index)
            c.settSpell.emit(index, sp2)
            index = index + 1
            dataholder.addSpell(champ + 'Ult', UltSpell(champ, 110, ultindex, runecdr))
            dataholder.addButton(champ + 'Ult', ultindex)
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
        c.showmqtt.emit()
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


import keyboard

hotkeyFilePath = ''


def loadHotkey():
    global hotkeyFilePath
    hotkeyFilePath = os.path.join(appdatadir.overlaydir, "hotkey.txt")
    keys = '^'

    try:
        with open(hotkeyFilePath) as f:
            keys = f.read()
    except FileNotFoundError:
        f = open(hotkeyFilePath, "w")
        f.write(keys)
        f.close()
    keyboard.add_hotkey(keys, reactToHotKey)


def reactToHotKey():
    global activeGameFound
    if activeGameFound:
        c.hotkeyClicked.emit()


class AppDataDir():
    def __init__(self):
        self.overlaydir = os.path.join(os.getenv('APPDATA'), "SummonerTrackerOverlay")


appdatadir = AppDataDir()
from datetime import datetime
from datetime import date


def saveCurrentLogDate(path):
    f = open(path, "w")
    f.write(str(date.today()))
    f.close()


spellDatabase = {
    'Heal': Spell('h', 240),
    'Ghost': Spell('ghost', 210),
    'Barrier': Spell('barr', 180),
    'Exhaust': Spell('exh', 210),
    'Clarity': Spell('clarity', 240),
    'Flash': Spell('f', 300),
    'HexFlash': Spell('f', 300),
    'Teleport': Spell('tp', 240),
    'Smite': Spell('smite', 15),
    'Cleanse': Spell('cleanse', 210),
    'Ignite': Spell('ign', 180),
    'Mark': Spell('mark', 80),
    'Dash': Spell('mark', 80),
    'Challenging Smite': Spell('smite', 15),
    'Chilling Smite': Spell('smite', 15),
    'Poro Toss': Spell('p-mark', 80),
    'Poro Dash': Spell('p-dash', 80),
    'To the King!': Spell('king', 10),
    'Resuscitate': Spell('rev', 100),
    'Warp': Spell('warp', 15),
    'Ionial Boots of Lucidity': 10.0,
    'ARAM': 40.0,
    'Inspiration': 5.0
}

if __name__ == '__main__':
    import logging

    try:
        os.mkdir(appdatadir.overlaydir)
    except FileExistsError:
        pass
    debugpath = os.path.join(appdatadir.overlaydir, "debug.log")
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
    except FileNotFoundError:
        saveCurrentLogDate(logStartPath)
        f = open(debugpath, "w")
        f.write('')
        f.close()

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
    setterWindow = SetterWindow()
    window = OverlayWindow()
    startThreads()
    app.exec_()
