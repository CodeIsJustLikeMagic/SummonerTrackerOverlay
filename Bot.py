# Bot.py
import discord
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QVBoxLayout, QSystemTrayIcon, QMenu, QDesktopWidget, \
    QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer, QCoreApplication
import threading


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
        self.l.setStyleSheet("color: white")
        trayIcon = QSystemTrayIcon(QIcon("trackerIcon.xpm"), self)
        menu = QMenu()
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(lambda: QCoreApplication.exit())
        moveAction = menu.addAction("Move")
        moveAction.triggered.connect(lambda: self.movable())
        resetPosAction = menu.addAction("Reset Position")
        resetPosAction.triggered.connect(self.resetPos)
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


def connectBot():
    with open("secret.env") as f:
        secret = f.read()
    client = discord.Client()

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
        c.text.emit('connected')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if str(message.channel) == 'summonertracker':
            # display the content of the message in overlay
            # await message.channel.send("I'm a bot");
            message = message.content.replace(', ', '\n')
            message = message.replace(',', '')
            c.text.emit(message)

    t = threading.Thread(target=lambda: client.run(secret))
    t.setDaemon(True)
    t.start()


if __name__ == '__main__':
    connectBot()
    app = QApplication([])
    window = MainWindow()
    app.exec_()
