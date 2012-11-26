#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import serial
import time
# s = serial.Serial(port='/dev/ttyACM0', baudrate=9600)
# s.read()


class mainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(mainWindow, self).__init__()
        
        self.initUI()
        
    def initUI(self):               
        
        textEdit = QtGui.QTextEdit()
        #self.setCentralWidget(textEdit)
        # print textEdit
        # print mainQWidget
        self.splitEdit = mainQWidget()
        self.setCentralWidget(self.splitEdit)

        # Button to exit the program
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)
        
        self.setGeometry(100, 100, 800, 700)
        self.setWindowTitle('Main window')    
        self.show()

        self.serialPort = serial.Serial(port='/dev/ttyACM0', baudrate=9600)

        # timer settings, eventually for reading the RFID port
        #self.timer = QtCore.QBasicTimer()
        #self.timer.start(300,self)

        

    # def timerEvent(self, event):
    #     if event.timerId() == self.timer.timerId():
    #         tag = "h9999" #self.serialPort.readline()
    #         item = QtGui.QListWidgetItem("Item %s" % tag[0:-2])
    #         self.splitEdit.listWidget.addItem(item)
    #     else:
    #         QtGui.QFrame.timerEvent(self, event)

    # def start(self):
    #     item = QtGui.QListWidgetItem("Item %i" % 42)
    #     self.splitEdit.listWidget.addItem(item)

    # Read the messages that are waiting in the queue
    def processIncoming(self):
        while self.queue.qsize():
            try:
                tag = self.queue.get(0)
                item = QtGui.QListWidgetItem("Item %s" % tag[0:-2])
                self.splitEdit.listWidget.addItem(item)
            except Queue.Empty:
                pass



class mainQWidget(QtGui.QWidget):
    listWidget = None

    def __init__(self):
        super(mainQWidget, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        hbox = QtGui.QHBoxLayout(self)

        # topleft = QtGui.QFrame(self)
        # topleft.setFrameShape(QtGui.QFrame.StyledPanel)

        self.listWidget = QtGui.QListWidget() 

        for i in range(10):
            item = QtGui.QListWidgetItem("Item %i" % i)
            self.listWidget.addItem(item)

        listWidget2 = QtGui.QListWidget() 
        for i in range(10):
            item = QtGui.QListWidgetItem("Item %i" % i)
            listWidget2.addItem(item)



 
        # topright = QtGui.QFrame(self)
        # topright.setFrameShape(QtGui.QFrame.StyledPanel)

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.listWidget)
        splitter1.addWidget(listWidget2)

        hbox.addWidget(splitter1)
        self.setLayout(hbox)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        
        #self.setGeometry(300, 300, 300, 200)
        #self.setWindowTitle('QtGui.QSplitter')
        #self.show()

    def onChanged(self, text):
        
        self.lbl.setText(text)
        self.lbl.adjustSize()  
        


class ThreadedClient:
    def __init__(self):
        # Create the queue
        self.queue = Queue.Queue()

        # Set up the GUI part
        self.gui=GuiPart(self.queue, self.endApplication)
        self.gui.show()

        # A timer to periodically call periodicCall :-)
        self.timer = qt.QTimer()
        qt.QObject.connect(self.timer,
                           qt.SIGNAL("timeout()"),
                           self.periodicCall)
        # Start the timer -- this replaces the initial call to periodicCall
        self.timer.start(100)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            root.quit()

    def endApplication(self):
        self.running = 0

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. 
        Put your stuff here.
        """
        ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600)
        while self.running:
            #This is where we poll the Serial port. 
            #time.sleep(rand.random() * 0.3)
            #msg = rand.random()
            #self.queue.put(msg)
            
            msg = ser.readline();
            if (msg):
                self.queue.put(msg)
            else: pass  
            #ser.close()
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()