# -*- coding: utf-8 -*-

"""The user interface for our app"""

import os,sys,codecs

# Import Qt modules
from PyQt4 import QtCore,QtGui,QtOpenGL
from PyQt4.phonon import Phonon

try:
    import enchant
    from spelltextedit import SpellTextEdit as EditorClass
    print 'Spellchecking enabled'
except ImportError:
    EditorClass=QtGui.QPlainTextEdit
    print 'Spellchecking disabled'

class animatedOpacity:
    def moveOpacity(self):
        if abs(abs(self.proxy.opacity())-abs(self.targetOpacity))<.1:
            self.proxy.setOpacity(self.targetOpacity)
            self.movingOp=False
        else:
            self.movingOp=True
            if self.proxy.opacity()<self.targetOpacity:
                self.proxy.setOpacity(self.proxy.opacity()+.1)
            else:
                self.proxy.setOpacity(self.proxy.opacity()-.1)
            QtCore.QTimer.singleShot(30,self.moveOpacity)

    def showChildren(self):
        for c in self.children:
            c.targetOpacity=.8
            c.moveOpacity()

    def hideChildren(self):
        for c in self.children:
            c.targetOpacity=0.
            c.moveOpacity()

class FunkyLabel(QtGui.QLabel, animatedOpacity):
    def __init__(self, text, scene,opacity=.3):
        QtGui.QLabel.__init__(self,text)
        self.baseOpacity=opacity
        self.proxy=scene.addWidget(self)
        self.proxy.setOpacity(opacity)
        self.movingOp=False
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.children=[]
        self.setStyleSheet("""background-color: transparent;
                              padding: 6px;
                              border: 2px solid #eeeeee;
                              text-align: right;
                           """)

class FunkyButton(QtGui.QPushButton, animatedOpacity):
    def __init__(self, text, scene,opacity=.3):
        QtGui.QPushButton.__init__(self,text)
        self.baseOpacity=opacity
        self.proxy=scene.addWidget(self)
        self.proxy.setOpacity(opacity)
        self.movingOp=False
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""
            border: 1px solid gray;
            border-radius: 3px;
            padding: 5px 4px 3px 4px;
        """)
        self.children=[]

class FunkyFontList(QtGui.QFontComboBox, animatedOpacity):
    def __init__(self, scene,opacity=.3):
        QtGui.QFontComboBox.__init__(self)
        self.baseOpacity=opacity
        self.proxy=scene.addWidget(self)
        self.proxy.setOpacity(opacity)
        self.movingOp=False
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.children=[]
        self.setStyleSheet("""
            padding: 5px 2px 4px 3px;
        """)
         

class FunkyEditor(EditorClass):
    def __init__(self, *args, **kwargs):
        EditorClass.__init__(self, *args, **kwargs)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.defSize=self.font().pointSize()
        self.docName=''

    def save(self):
        if not self.docName:
            self.saveas()
        else:
            f=codecs.open(self.docName,'w+','utf-8')
            f.truncate()
            f.write(unicode(self.toPlainText()))
            f.close()

    def saveas(self):
        fname=unicode(QtGui.QFileDialog.getSaveFileName())
        if fname:
            self.docName=fname
            self.save()

    def open(self):
        fname=unicode(QtGui.QFileDialog.getOpenFileName())
        if fname:
            self.docName=fname
            self.setPlainText(codecs.open(fname,'r','utf-8').read())

    def smaller(self):
        f=self.font()
        f.setPointSize(f.pointSize()-1)
        self.setFont(f)
        
    def larger(self):
        f=self.font()
        f.setPointSize(f.pointSize()+1)
        self.setFont(f)

    def default(self):
        f=self.font()
        f.setPointSize(self.defSize)
        self.setFont(f)

    def mouseMoveEvent(self, ev):
        self.parent().showButtons()
        self.parent().showCursor()
        return QtGui.QPlainTextEdit.mouseMoveEvent(self, ev)

class MainWidget (QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)
        
        self._scene=QtGui.QGraphicsScene()
        self.setScene(self._scene)

        self.editor=None
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setMouseTracking(True)
        self.currentBG=None
        self.bgcolor=None
        self.currentClick=None
        self.beep=None
        self.nextbg()
        self.nextclick()

        self.stations=[x.strip() for x in open('radios.txt').readlines()]
        self.currentStation=None

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setViewport(QtOpenGL.QGLWidget())

        # These are the positions for the elements of the screen
        # They are recalculated on resize
        
        self.editorX=100
        self.editorY=40
        self.editorH=400
        self.editorW=400

        self.editor=FunkyEditor(self)
        self.editor.show()
        self.editor.setMouseTracking(True)
        self.editor.setFrameStyle(QtGui.QFrame.NoFrame)
        self.editor.setStyleSheet("""background-color: transparent;
                                     color: black;
                                  """)

        self.editorBG=QtGui.QGraphicsRectItem(self.editorX-5,self.editorY-5,self.editorW+10,self.editorH+10)
        self.editorBG.setOpacity(.03)
        self.editorBG.setBrush(QtGui.QColor(1,1,1))
        self._scene.addItem(self.editorBG)

        self.fontButton=FunkyButton("FONT", self._scene, 0)
        self.sizeButton=FunkyButton("SIZE", self._scene, 0)
        self.fileButton=FunkyButton("FILE", self._scene, 0)
        self.bgButton=FunkyButton("BG", self._scene, 0)
        self.clickButton=FunkyButton("CLICK", self._scene, 0)
        self.musicButton=FunkyButton("MUSIC", self._scene, 0)
        self.quitButton=FunkyButton("QUIT", self._scene, 0)
        self.quitButton.clicked.connect(self.close)

        self.buttons=[self.fontButton, 
                      self.sizeButton, 
                      self.fileButton, 
                      self.bgButton, 
                      self.clickButton,
                      self.musicButton,
                      self.quitButton,
                      ]

        mainMenuLayout=QtGui.QGraphicsGridLayout()
        mainMenuLayout.setContentsMargins(20,0,0,0)
        for pos, button in enumerate(self.buttons):
            mainMenuLayout.addItem(button.proxy,pos,0)

        self.fontList=FunkyFontList(self._scene,0)
        self.fontList.currentFontChanged.connect(self.changeFont)
        self.fontColor=FunkyButton("COLOR", self._scene,0)
        self.fontColor.clicked.connect(self.setfontcolor)
        mainMenuLayout.addItem(self.fontList.proxy,0,2,1,2)
        mainMenuLayout.addItem(self.fontColor.proxy,0,1)
        self.fontButton.children+=[self.fontList,self.fontColor]

        self.size1=FunkyButton("-", self._scene,0)
        self.size2=FunkyButton("=", self._scene,0)
        self.size3=FunkyButton("+", self._scene,0)
        self.size1.clicked.connect(self.editor.smaller)
        self.size3.clicked.connect(self.editor.larger)
        self.size2.clicked.connect(self.editor.default)
        self.sizeButton.children+=[self.size1, self.size2, self.size3]

        mainMenuLayout.addItem(self.size1.proxy,1,1)
        mainMenuLayout.addItem(self.size2.proxy,1,2)
        mainMenuLayout.addItem(self.size3.proxy,1,3)

        self.file1=FunkyButton("OPEN", self._scene, 0)
        self.file2=FunkyButton("SAVE", self._scene, 0)
        self.file3=FunkyButton("SAVE AS", self._scene, 0)
        mainMenuLayout.addItem(self.file1.proxy,2,1)
        mainMenuLayout.addItem(self.file2.proxy,2,2)
        mainMenuLayout.addItem(self.file3.proxy,2,3)
        self.file1.clicked.connect(self.editor.open)
        self.file2.clicked.connect(self.editor.save)
        self.file3.clicked.connect(self.editor.saveas)
        self.fileButton.children+=[self.file1, self.file2, self.file3]

        self.bg1=FunkyButton("<", self._scene,0)
        self.bg2=FunkyButton(">", self._scene,0)
        self.bg3=FunkyButton("COLOR", self._scene,0)
        mainMenuLayout.addItem(self.bg1.proxy,3,1)
        mainMenuLayout.addItem(self.bg2.proxy,3,2)
        mainMenuLayout.addItem(self.bg3.proxy,3,3)
        self.bg1.clicked.connect(self.prevbg)
        self.bg2.clicked.connect(self.nextbg)
        self.bg3.clicked.connect(self.setbgcolor)
        self.bgButton.children+=[self.bg1, self.bg2, self.bg3]

        self.click1=FunkyButton("<", self._scene,0)
        self.click2=FunkyButton(">", self._scene,0)
        self.click3=FunkyButton("X", self._scene,0)
        mainMenuLayout.addItem(self.click1.proxy,4,1)
        mainMenuLayout.addItem(self.click2.proxy,4,2)
        mainMenuLayout.addItem(self.click3.proxy,4,3)
        self.click1.clicked.connect(self.prevclick)
        self.click2.clicked.connect(self.nextclick)
        self.click3.clicked.connect(self.noclick)
        self.clickButton.children+=[self.click1, self.click2, self.click3]
        
        self.music1=FunkyButton("<", self._scene,0)
        self.music2=FunkyButton(">", self._scene,0)
        self.music3=FunkyButton("X", self._scene,0)
        mainMenuLayout.addItem(self.music1.proxy,5,1)
        mainMenuLayout.addItem(self.music2.proxy,5,2)
        mainMenuLayout.addItem(self.music3.proxy,5,3)
        self.music1.clicked.connect(self.prevstation)
        self.music2.clicked.connect(self.nextstation)
        self.music3.clicked.connect(self.nomusic)
        self.musicButton.children+=[self.music1, self.music2, self.music3]

        self.mainMenu=QtGui.QGraphicsWidget()
        self.mainMenu.setLayout(mainMenuLayout)
        self.mainMenu.setPos(self.editorX+self.editorW+20,self.editorY)
        self._scene.addItem(self.mainMenu)
        self.editor.installEventFilter(self)
        for b in self.buttons:
            b.installEventFilter(self)

    def prevclick(self):
        clist=os.listdir('clicks')
        clist=[x for x in clist if not x.startswith('.')]
        clist.sort()
        try:
            idx=(clist.index(self.currentClick)-1)%len(clist)
        except ValueError:
            idx=-1
        self.currentClick=clist[idx]
        print '<< switching click to:', self.currentClick
        self.beep = Phonon.createPlayer(Phonon.NotificationCategory,
                                  Phonon.MediaSource(os.path.join('clicks',self.currentClick)))
        self.beep.play()

    def nextclick(self):
        clist=os.listdir('clicks')
        clist=[x for x in clist if not x.startswith('.')]
        clist.sort()
        try:
            idx=(clist.index(self.currentClick)+1)%len(clist)
        except ValueError:
            idx=-1
        self.currentClick=clist[idx]
        print '>> switching click to:', self.currentClick
        self.beep = Phonon.createPlayer(Phonon.NotificationCategory,
                                  Phonon.MediaSource(os.path.join('clicks',self.currentClick)))
        self.beep.play()

    def noclick(self):
        self.beep=None

    def prevstation(self):
        try:
            idx=(self.stations.index(self.currentStation)-1)%len(self.stations)
        except ValueError:
            idx=-1
        self.currentStation=self.stations[idx]
        print '<< switching music to:', self.currentStation
        self.music = Phonon.createPlayer(Phonon.MusicCategory,
                                  Phonon.MediaSource(self.currentStation))
        self.music.play()
        
    def nextstation(self):
        try:
            idx=(self.stations.index(self.currentStation)+1)%len(self.stations)
        except ValueError:
            idx=-1
        self.currentStation=self.stations[idx]
        print '>> switching music to:', self.currentStation
        self.music = Phonon.createPlayer(Phonon.MusicCategory,
                                  Phonon.MediaSource(self.currentStation))
        self.music.play()

    def nomusic(self):
        self.music.stop()
        
    def prevbg(self):
        bglist=os.listdir('backgrounds')
        bglist=[x for x in bglist if not x.startswith('.')]
        bglist.sort()
        try:
            idx=(bglist.index(self.currentBG)-1)%len(bglist)
        except ValueError:
            idx=-1
        self.currentBG=bglist[idx]
        print '<< switching bg to:', self.currentBG
        self.bg=QtGui.QImage(os.path.join('backgrounds',bglist[idx]))
        self.realBg=self.bg.scaled( self.size(), QtCore.Qt.KeepAspectRatioByExpanding)
        # FIXME: I can't find a way to force it to redraw the background nicely.
        self.hide()
        self.showFullScreen()
        
    def nextbg(self):
        bglist=os.listdir('backgrounds')
        bglist=[x for x in bglist if not x.startswith('.')]
        bglist.sort()
        try:
            idx=(bglist.index(self.currentBG)+1)%len(bglist)
        except ValueError:
            idx=0
        self.currentBG=bglist[idx]
        print '>> switching bg to:', self.currentBG
        self.bg=QtGui.QImage(os.path.join('backgrounds',bglist[idx]))
        self.realBg=self.bg.scaled( self.size(), QtCore.Qt.KeepAspectRatioByExpanding)
        # FIXME: I can't find a way to force it to redraw the background nicely.
        self.hide()
        self.showFullScreen()
        
    def setbgcolor(self):
        bgcolor=QtGui.QColorDialog.getColor()
        if bgcolor:
            self.bg=None
            self.realBG=None
            self.bgcolor=bgcolor
            # FIXME: I can't find a way to force it to redraw the background nicely.
            self.hide()
            self.showFullScreen()

    def setfontcolor(self):
        color=QtGui.QColorDialog.getColor()
        if color:
            self.editor.setStyleSheet("""background-color: transparent;
                                         color: %s;
                                      """%(unicode(color.name())))

        
    def eventFilter(self, obj, event):
        if obj==self.editor:
            if event.type()==QtCore.QEvent.KeyPress:
                if self.beep:
                    self.beep.play()
                self.hideCursor()
                self.hideButtons()
            elif isinstance(event, QtGui.QMoveEvent):
                self.showButtons()
        elif isinstance(event, QtGui.QHoverEvent):
            for b in self.buttons:
                if b != obj:
                    b.hideChildren()
                else:
                    b.showChildren()
                self.showButtons()
        return QtGui.QGraphicsView.eventFilter(self, obj, event)

    def keyEvent(self, ev):
        self.hideCursor()
        QtGui.QGraphicsView.keyEvent(self, ev)

    def mouseMoveEvent(self, ev):
        self.showCursor()
        self.showButtons()
        QtGui.QGraphicsView.mouseMoveEvent(self, ev)

    def changeFont(self, font):
        f=self.editor.font()
        f.setFamily(font.family())
        self.editor.setFont(f)

    def drawBackground(self, painter, rect):
        if self.bg:
            #Anchor the image's bottom-right corner, which is usually the most interesting ;-)
            dx=self.realBg.width()-self.width()
            dy=self.realBg.height()-self.height()
            source=QtCore.QRect(dx,dy,self.width(),self.height())
            painter.drawImage(self.geometry(), self.realBg, source)
        elif self.bgcolor:
            painter.fillRect(self.geometry(),self.bgcolor)

    def resizeEvent(self, ev):
        self._scene.setSceneRect(QtCore.QRectF(self.geometry()))
        if self.bg:
            self.realBg=self.bg.scaled( self.size(), QtCore.Qt.KeepAspectRatioByExpanding)
        
        # Try to guess a decent size for the editor window
        # Width: 80 characters
        # Height: 90% of the screen
        self.editorH=.9*self.height()
        self.editorW=self.fontMetrics().averageCharWidth()*80
        self.editorY=self.width()*.05
        self.editorX=self.width()*.1
        
        if self.editor:
            self.editor.setGeometry(self.editorX,self.editorY,self.editorW,self.editorH)
            print (self.editorX,self.editorY,self.editorW,self.editorH),self.editor.geometry()
            self.editorBG.setRect(self.editorX-5,self.editorY-5,self.editorW+10,self.editorH+10)
            self.mainMenu.setPos(self.editorX+self.editorW+20,self.editorY)

    def showButtons(self):
        for w in self.buttons:
            w.targetOpacity=.8
            w.moveOpacity()

    def hideButtons(self):
        for w in self.buttons:
            w.targetOpacity=0.
            w.moveOpacity()
            w.hideChildren()

    def hideCursor(self):
        QtCore.QCoreApplication.instance().setOverrideCursor(QtCore.Qt.BlankCursor)

    def showCursor(self):
        QtCore.QCoreApplication.instance().restoreOverrideCursor()

    def _show(self):
        self.show()
        self.showButtons()
        self.showFullScreen()

def main():
    # Again, this is boilerplate, it's going to be the same on
    # almost every app you write
    app = QtGui.QApplication(sys.argv)
    window=MainWidget()
    QtCore.QTimer.singleShot(0,window._show)
    
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()