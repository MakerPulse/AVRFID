"""
This recipe opens a simple window in PyQt to poll the serial port for 
data and print it out. Uses threads and a queue.

DON'T FORGET TO SET SERIALPORT BEFORE RUNNING THIS CODE

Here is an Arduino Sketch to use:
    ***********
void setup() {
  Serial.begin(115200);
}
void loop() {
  Serial.println("I blinked");
  delay(1000);
}
    ***********
This recipe depends on PyQt and pySerial. Qt 4 is world class code 
and I like how it looks. PyQt is not completely open source, 
but I think PySide is. Tested on Qt4.6 / Win 7 / Duemilanove

Author: Dirk Swart, Ithaca, NY. 2011-05-20. www.wickeddevice.com

Based on threads recipe by Jacob Hallen, AB Strakt, Sweden. 2001-10-17
As adapted by Boudewijn Rempt, Netherlands. 2002-04-15

PS: This code is provided with no warranty, express or implied. It is 
meant to demonstrate a concept only, not for actual use. 
Code is in the public domain.
"""
__author__ = 'Dirk Swart, Doudewijn Rempt, Jacob Hallen'

import sys, time, threading, random, Queue
from PyQt4 import QtGui, QtCore as qt
import serial

SERIALPORT = '/dev/ttyACM0'

class GuiPart(QtGui.QMainWindow):

    def __init__(self, queue, endcommand, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.setWindowTitle('Arduino Serial Demo')
        self.queue = queue
        # We show the result of the thread in the gui, instead of the console
        self.editor = QtGui.QTextEdit(self)
        self.setCentralWidget(self.editor)
        self.endcommand = endcommand    
        
    def closeEvent(self, ev):
        self.endcommand()

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.editor.insertPlainText(str(msg))
            except Queue.Empty:
                pass

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
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

#rand = random.Random()
root = QtGui.QApplication(sys.argv)
client = ThreadedClient()
sys.exit(root.exec_())