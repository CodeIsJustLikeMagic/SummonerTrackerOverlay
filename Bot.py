# Bot.py
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
    setterChampion = pyqtSignal(int,str)
    settSpell = pyqtSignal(int,str)
    resetPos = pyqtSignal()
    move = pyqtSignal()
    unmovable = pyqtSignal()
    colorSet = pyqtSignal(int)
    colorUnset = pyqtSignal(int)
    exitC = pyqtSignal()
    hotkeyklicked = pyqtSignal()
    status = pyqtSignal(str)
    unsetAll = pyqtSignal()
    showmqtt = pyqtSignal()


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

        font = QFont('Serif', 11)
        font.setWeight(62)


        self.championLabels = []
        self.ult = []
        for x in range(5):
            champlbl = QLabel("player"+str(x+1))
            champlbl.setFont(font)
            champlbl.setStyleSheet("color: rgb(230,230,230)")
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            champlbl.setGraphicsEffect(effect)
            grid_layout.addWidget(champlbl, x*2, 0)
            self.championLabels.append(champlbl)
            champsult = QPushButton("ult")
            champsult.setFont(font)
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            champsult.setGraphicsEffect(effect)
            champsult.setStyleSheet(self.unSetStyle)
            grid_layout.addWidget(champsult, 1+(x*2), 0)
            self.ult.append(champsult)

        self.spellButtons = []
        self.minButtons = []
        for x in range(10):
            champs1 = QPushButton("spell")
            champs1.setFont(font)
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            champs1.setGraphicsEffect(effect)
            champs1.setStyleSheet("color: rgb(230,230,230); background-color: rgb(150,150,150)")
            grid_layout.addWidget(champs1, x, 1)
            self.spellButtons.append(champs1)
            minButton = QPushButton("-1 min")
            minButton.setFont(font)
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(0)
            effect.setColor(QColor(0, 0, 0, 255))
            effect.setOffset(1)
            minButton.setGraphicsEffect(effect)
            minButton.setStyleSheet(self.unSetStyle)
            grid_layout.addWidget(minButton,x,2)
            self.minButtons.append(minButton)
        self.moveLabel = QLabel('grab me!')
        self.moveLabel.setFont(font)
        self.moveLabel.setStyleSheet("border: 5px solid white; color: rgb(230,230,230); background-color: rgb(150,150,150)")
        grid_layout.addWidget(self.moveLabel,12,1)
        self.moveLabel.hide()

        self.spellButtons[0].clicked.connect(lambda: self.StartSpellTrack(0,7))
        self.spellButtons[1].clicked.connect(lambda: self.StartSpellTrack(1,7))
        self.spellButtons[2].clicked.connect(lambda: self.StartSpellTrack(2,7))
        self.spellButtons[3].clicked.connect(lambda: self.StartSpellTrack(3,7))
        self.spellButtons[4].clicked.connect(lambda: self.StartSpellTrack(4,7))
        self.spellButtons[5].clicked.connect(lambda: self.StartSpellTrack(5,7))
        self.spellButtons[6].clicked.connect(lambda: self.StartSpellTrack(6,7))
        self.spellButtons[7].clicked.connect(lambda: self.StartSpellTrack(7,7))
        self.spellButtons[8].clicked.connect(lambda: self.StartSpellTrack(8,7))
        self.spellButtons[9].clicked.connect(lambda: self.StartSpellTrack(9,7))

        self.minButtons[0].clicked.connect(lambda: self.StartSpellTrack(0,60))
        self.minButtons[1].clicked.connect(lambda: self.StartSpellTrack(1,60))
        self.minButtons[2].clicked.connect(lambda: self.StartSpellTrack(2,60))
        self.minButtons[3].clicked.connect(lambda: self.StartSpellTrack(3,60))
        self.minButtons[4].clicked.connect(lambda: self.StartSpellTrack(4,60))
        self.minButtons[5].clicked.connect(lambda: self.StartSpellTrack(5,60))
        self.minButtons[6].clicked.connect(lambda: self.StartSpellTrack(6,60))
        self.minButtons[7].clicked.connect(lambda: self.StartSpellTrack(7,60))
        self.minButtons[8].clicked.connect(lambda: self.StartSpellTrack(8,60))
        self.minButtons[9].clicked.connect(lambda: self.StartSpellTrack(9,60))

        self.ult[0].clicked.connect(lambda: self.StartSpellTrack(10,7))
        self.ult[1].clicked.connect(lambda: self.StartSpellTrack(11,7))
        self.ult[2].clicked.connect(lambda: self.StartSpellTrack(12,7))
        self.ult[3].clicked.connect(lambda: self.StartSpellTrack(13,7))
        self.ult[4].clicked.connect(lambda: self.StartSpellTrack(14,7))

        postxtdir = os.path.join(os.getenv('APPDATA'),"SummonerTrackerOverlay")
        self.postxtfilepath = os.path.join(postxtdir,"pos2.txt")
        try:
            os.mkdir(postxtdir)
        except FileExistsError:
            pass
        c.setterChampion.connect(lambda index, val: self.setchampionlabel(index,val))
        c.settSpell.connect(lambda index,val: self.setspelllabel(index,val))
        c.resetPos.connect(self.resetPos)
        c.move.connect(self.movable)
        c.colorSet.connect(lambda index: self.set(index))
        c.colorUnset.connect(lambda index: self.unset(index))
        c.exitC.connect(self.close)
        c.unmovable.connect(self.unmovable)
        c.hotkeyklicked.connect(self.showOnKeyboardPress)
        c.unsetAll.connect(self.clear)
        self.lastAction = time.time()
        self.show()
        try:
            with open(self.postxtfilepath) as f:
                pos = f.read()
                pos = pos.split(' ')
                if len(pos) == 2:
                    #print('moving overlay to position from appdata file')
                    self.move(int(int(pos[0]) / 2), int(int(pos[1]) / 2))
        except FileNotFoundError:
            pass
        self.hide()

    def showOnKeyboardPress(self):
        if self.isHidden():
            print('showing on keypress')
            self.lastAction = time.time()
            self.waitandSeeIfIdle()
            self.setHidden(False)
        else:
            self.hide()
        #show but dont steal focus on hotkeypressnnn
        #hide again if hotkey is pressed again
    def clear(self):
        for num, lbl in enumerate(self.championLabels,start = 1):
            lbl.setText('player'+str(num))
        for btn in self.spellButtons:
            btn.setText('spell')
            btn.setStyleSheet(self.unSetStyle)
        for btn in self.minButtons:
            btn.setStyleSheet(self.unSetStyle)
        for num,btn in enumerate(self.ult,start=0):
            btn.setStyleSheet(self.unSetStyle)
    def unset(self, index):
        if index >=10:
            self.ult[int(index)-10].setStyleSheet(self.unSetStyle)
            return
        self.spellButtons[index].setStyleSheet(self.unSetStyle)
        self.minButtons[index].setStyleSheet(self.unSetStyle)
    def set(self, index):
        if index >=10:
            self.ult[index-10].setStyleSheet(self.setStyle)
            return
        self.spellButtons[index].setStyleSheet(self.setStyle)
        self.minButtons[index].setStyleSheet(self.setStyle)

    def setchampionlabel(self,index,val):
        self.championLabels[index].setText(val)
    def setspelllabel(self,index,val):
        self.spellButtons[index].setText(val)

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

    def unmovable(self):
        self.ismovable = False
        self.moveLabel.hide()
        self.hide()

    def mousePressEvent(self, event):
        #print('mouse Press Event')
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if(self.ismovable):
                # adjust offset from clicked point to origin of widget
                currPos = self.mapToGlobal(self.pos())
                globalPos = event.globalPos()
                diff = globalPos - self.__mouseMovePos
                newPos = self.mapFromGlobal(currPos + diff)
                self.move(newPos)
                self.__mouseMovePos = globalPos

    def mouseReleaseEvent(self, event):
        self.unmovable()
        c.unmovable.emit()
        self.savePosition()
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

    def waitandSeeIfIdle(self):
       #print('waiting for idle')
        QTimer.singleShot(6000, self.checkStillIdle)
    def checkStillIdle(self):
        if time.time()-self.lastAction >= 5.8:
            #print('idle detected')
            self.hide()
    def StartSpellTrack(self,index,modifier):
        self.lastAction = time.time()
        self.waitandSeeIfIdle()
        spell = dataholder.getSpell(index)
        if spell == None:
            return
        trackentry = (TrackEntry(spell,modifier))
        old = dataholder.getTrack(index)
        if old is not None:
            if old.endTrack > gameTime.elapsed:
                mqttclient.send('r '+str(index))
                return
        mqttclient.send('a '+str(index)+' '+str(trackentry.endTrack))



def SaveTrack(index, endTrack):
    trackentry = TrackEntry(dataholder.getSpell(int(index)),0)
    trackentry.endTrack = float(endTrack)
    dataholder.addTrack(index,trackentry)
    showTrackEntrys()
    c.colorSet.emit(int(index))

def RemoveTrack(index):
    track = dataholder.getTrack(int(index))
    if track is not None:
        dataholder.removeTrack(track)
        showTrackEntrys()
        c.colorUnset(int(index))

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
        effect.setColor(QColor(0,0,0,255))
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
        #print(resource_path('./assets/trackerIcon.xpm'))
        icon = QIcon(resource_path('./assets/trackerIcon.xpm'))
        trayIcon = QSystemTrayIcon(icon, self)
        self.setWindowIcon(icon)
        menu = QMenu()
        openHotKeyFileAction = menu.addAction("set Hotkey")
        global hotkeyFilePath
        openHotKeyFileAction.triggered.connect(lambda: os.startfile(hotkeyFilePath))
        moveAction = menu.addAction("Move")
        moveAction.triggered.connect(self.movable)
        resetPosAction = menu.addAction("Reset Position")
        resetPosAction.triggered.connect(self.resetPos)
        toggleSetterAction = menu.addAction("Toggle Setter Window")
        toggleSetterAction.triggered.connect(lambda: c.hotkeyklicked.emit())
        showmqttInfoAction= menu.addAction("show mqtt info")
        showmqttInfoAction.triggered.connect(self.showMQTTInfo)
        newConnection = menu.addAction('new Connection')
        newConnection.triggered.connect(mqttclient.renonnectmqtt)
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(self.close)
        #self.aboutToQuit(disconnectmqtt())
        c.unmovable.connect(self.unmovable)

        postxtdir = os.path.join(os.getenv('APPDATA'),"SummonerTrackerOverlay")
        self.postxtfilepath = os.path.join(postxtdir,"pos.txt")
        try:
            os.mkdir(postxtdir)
        except FileExistsError:
            pass

        import ctypes
        myappid = 'summonerTrackerOverlay'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        trayIcon.setContextMenu(menu)
        trayIcon.show()

        self.show()
        try:
            with open(self.postxtfilepath) as f:
                pos = f.read()
                pos = pos.split(' ')
                if len(pos) == 2:
                    #print('moving overlay to position from appdata file')
                    self.move(int(int(pos[0]) / 2), int(int(pos[1]) / 2))
        except FileNotFoundError:
            pass
            #print('no position file')
    def showMQTTInfo(self):
        c.status.emit(mqttclient.connectionInfo)
        timer = QTimer(self)
        timer.timeout.connect(lambda: c.status.emit(''))
        timer.start(10000)
    def showStatus(self,m):
        if len(m)==0:
            self.statuslbl.hide()
        else:
            self.statuslbl.setHidden(False)
            self.statuslbl.setText(m)
    def closeEvent(self, event) -> None:
        #print('close Overlay')
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

    def movable(self):
        c.move.emit()
        self.ismovable = True
        #print('moveable')
        self.setAttribute(Qt.WA_TranslucentBackground, on=False)
        self.setAutoFillBackground(False)
        self.l.setStyleSheet("border: 3px solid white; color: rgb(230,230,230)")

    def unmovable(self):
        #print('unmovable')
        self.ismovable = False
        self.l.setStyleSheet("border: none; color: rgb(230,230,230)")

    def visibleIfNoMouse(self):
        if self.l.underMouse() is False:
            self.l.setHidden(False)
            return
        QTimer.singleShot(400, self.visibleIfNoMouse)

    def mousePressEvent(self, event):
        #print('mouse Press Event')
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
        c.unmovable.emit()
        self.savePosition()
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

class Spell():
    def __init__(self,shortName, cd):
        self.shortName = shortName
        self.cd = cd
spellDatabase = {
    'Heal':Spell('h',240),
    'Ghost':Spell('ghost', 180),
    'Barrier': Spell('barr', 180),
    'Exhaust': Spell('exh', 210),
    'Clarity': Spell('clarity',240),
    'Flash':Spell('f',300),
    'Teleport': Spell('tp',240),
    'Smite':Spell('smite',15),
    'Cleanse': Spell('cleanse', 210),
    'Ignite':Spell('ign', 180)
}

class TrackEntry():
    def __init__(self,spell,modifier):
        now = gameTime.elapsed
        self.endTrack = now + spell.cd - modifier
        self.endTrackMins = time.strftime("%M:%S", time.gmtime(self.endTrack))
        self.spell = spell
        self.desc = spell.champion + ' ' + spell.spellname+' '+self.endTrackMins

class SummonerSpell():
    def __init__(self, cham,spellname, buttonindex):
        self.champion = cham
        self.spellname = spellDatabase.get(spellname).shortName
        self.cd = spellDatabase.get(spellname).cd
        self.index = buttonindex
class UltSpell():
    def __init__(self,cham,cd,buttonindex):
        self.champion = cham
        self.spellname = 'ult'
        self.cd = cd
        self.index = buttonindex

class GameTime():
    def __init__(self):
        self.gameStart = time.time()
        self.elapsed = time.time()-self.gameStart
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
def advanceGameTime():
    global activeGameFound
    print('activeGameFOund',activeGameFound)
    if activeGameFound:
        gameTime.advanceGameTime()
        print('advancing gametime')
        showTrackEntrys()
        time.sleep(1)
        advanceGameTime()
    else:
        dataholder.clear()
        c.text.emit('')
        c.unsetAll.emit()
def showTrackEntrys():
    show = ''
    with datalock:
        for key,track in dataholder.tracks.items():
            if track.endTrack > gameTime.elapsed:
                show = show + track.desc + '\n'
            else:
                c.colorUnset.emit(key)
    if len(show) > 0:
        show = gameTime.gameTimeMins + '\n\n' + show
    c.text.emit(show)

datalock = threading.Lock()
class Dataholder():
    def __init__(self):
        with datalock:
            self.spells={}
            self.lvls={}
            self.tracks={}
    def clear(self):
        with datalock:
            print('clearing data')
            self.spells={}
            self.lvls={}
            self.tracks = {}
    def addSpell(self,index, spell):
        with datalock:
            self.spells[index] = spell
            print(self.spells[index])
    def setLvl(self, champion, lvl):
        with datalock:
            self.lvls[champion] = lvl
    def addTrack(self, index, trackentry):
        with datalock:
            print('add track')
            dataholder.tracks[int(index)] = trackentry
            sortTracks()
    def removeTrack(self, track):
        with datalock:
            track.endTrack = float(0)
            sortTracks()
    def getSpell(self, index):
        with datalock:
            ret = self.spells.get(index)
        return ret
    def getTrack(self,index):
        with datalock:
            ret = self.tracks.get(index)
        return ret

def sortTracks(): # called while thread is locked
    dataholder.tracks = dict(sorted(dataholder.tracks.items(), key=lambda x: x[1].endTrack))

dataholder = Dataholder()
def loadLevels():
    try:
        r = requests.get("https://127.0.0.1:2999/liveclientdata/playerlist",verify = False)
    except Exception as e:
        return
    j = json.loads(r.content)
    for player in j:
        if player.get("team", "") != myteam:
            champ = player.get("championName","")
            lvl = player.get("level","")
            dataholder.setLvl(champ,lvl)

myteam = "empty"
def loadWithApi():
    # api_connection_data = lcu.connect("D:/Program/RiotGames/LeagueOfLegends")
    try:
        r = requests.get("https://127.0.0.1:2999/liveclientdata/playerlist", verify=False)
    except Exception as e:
        return None,None
    activeplayer = requests.get("https://127.0.0.1:2999/liveclientdata/activeplayername", verify = False)
    activeplayer = json.loads(activeplayer.content)
    j = json.loads(r.content)
    li = []
    global myteam
    for player in j:
        name = player.get("summonerName", "")
        if name == activeplayer:
            myteam = player.get("team", "")
        li.append(player.get("summonerName",""))
    li.append(myteam)
    index = 0
    ultindex = 10
    for player in j:
        if player.get("team","") != myteam:
            name = player.get("summonerName","")
            champ = player.get("championName","")
            sp1 = player.get("summonerSpells").get("summonerSpellOne").get("displayName")
            dataholder.addSpell(index, SummonerSpell(champ,sp1,index))
            c.settSpell.emit(index,sp1)
            index = index +1
            sp2 = player.get("summonerSpells").get("summonerSpellTwo").get("displayName")
            dataholder.addSpell(index, SummonerSpell(champ, sp2, index))
            c.settSpell.emit(index,sp2)
            index = index +1
            dataholder.addSpell(ultindex,UltSpell(champ,110,ultindex))
            lvl = player.get("level","")
            dataholder.setLvl(champ, lvl)
            #set sp1, sp2, champName in window (create new setterWindow with list of champions and spells)
            c.setterChampion.emit(ultindex-10,champ)
            ultindex = ultindex + 1
    print('done loading')
    topic = str(hashNames(li))
    return topic, str(java_string_hashcode(activeplayer))
def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    #print('message', msg)
    msg = msg.split(' ')
    if msg[0] == 'a':
        #index added
        #print(msg[1])
        SaveTrack(msg[1], msg[2])
        return
    if msg[0] == 'r':
        RemoveTrack(msg[1])
        return
    return
class Mqttclient():
    def __init__(self):
        self.clientHolder = None
        self.connectionInfo = 'will connect once game starts'
    def connect(self):
        #print('connecting mqtt client')
        topicsuffix,clientIdSuffix = loadWithApi()
        if topicsuffix is None:
            topicsuffix = "0"
            clientIdSuffix = "000"
        broker_address="mqtt.eclipse.org"
        self.clientID = "observer"+clientIdSuffix
        self.topic = "SpellTracker2/Match" + topicsuffix
        client = mqtt.Client(self.clientID)
        client.on_message = on_message
        #print(clientID,topic)
        client.connect(broker_address)
        self.connectionInfo = 'connected\n'+'topic ' + self.topic + '\nclient id '+self.clientID
        c.showmqtt.emit()
        #print('mqtt connected.')
        client.subscribe(self.topic)
        client.loop_start()
        self.clientHolder = client
    def send(self,msg):
        #print('sending', msg)
        if self.clientHolder is not None:
            self.clientHolder.publish(self.topic, msg)
    def disconnectmqtt(self):
        if self.clientHolder is not None:
            self.clientHolder.disconnect()
    def renonnectmqtt(self):
        self.disconnectmqtt()
        self.connect()
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
    #print('hashNames', li)
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
    #print(activeGameFound)
    global tries
    try:
        r = s.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify = False)
        if r.status_code !=200:
            return
        if activeGameFound is False:
            activeGameFound = True
            j = json.loads(r.content)
            currentTime = j.get("gameTime")
            gameTime.setGameTime(currentTime)
            loadLevels()
            mqttclient.connect()
            tries = 1
            startShowTrackThread()
            return
        j = json.loads(r.content)
        currentTime = j.get("gameTime")
        gameTime.setGameTime(currentTime)
        loadLevels()
        return
    except Exception as e:
        #print(tries)
        if tries == 3 :
            #print(tries, 1)
            #print('clear text. to many tries')
            c.status.emit('')
            tries = tries +1
        elif tries == 2:
            c.status.emit('Will keep looking even when hiding')
            tries = tries + 1
        elif tries  ==1:
            #print(tries, 'no active game')
            c.status.emit('Looking for active game...')
            tries = tries + 1
        if activeGameFound:
            #print('disconnect previous mqtt connection')
            mqttclient.disconnectmqtt()
        activeGameFound = False
        return
def gameCheck(s):
    testConnection(s)
    time.sleep(10)
    gameCheck(s)
def startThreads():
    s = requests.Session()
    t = threading.Thread(name='activeGameSearch', target = lambda: gameCheck(s))
    t.setDaemon(True)
    t.start()
    t3 = threading.Thread(name='hotkey', target= loadHotkey)
    t3.setDaemon(True)
    t3.start()
def startShowTrackThread():
    t2 = threading.Thread(name='advanceTime', target = advanceGameTime)
    t2.setDaemon(True)
    t2.start()
import keyboard
hotkeyFilePath = ''
def loadHotkey():
    global hotkeyFilePath
    postxtdir = os.path.join(os.getenv('APPDATA'), "SummonerTrackerOverlay")
    hotkeyFilePath = os.path.join(postxtdir, "hotkey.txt")
    keys = '^'
    try:
        os.mkdir(postxtdir)
    except FileExistsError:
        pass
    try:
        with open(hotkeyFilePath) as f:
            keys = f.read()
    except FileNotFoundError:
        f = open(hotkeyFilePath, "w")
        f.write(keys)
        f.close()
    keyboard.add_hotkey(keys,reactToHotKey)
def reactToHotKey():
    global activeGameFound
    if activeGameFound:
        c.hotkeyklicked.emit()

if __name__ == '__main__':
    startThreads()
    app = QApplication([])
    setterWindow = SetterWindow()
    window = OverlayWindow()
    app.exec_()