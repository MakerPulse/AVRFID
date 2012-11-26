import sys, serial, threading, random, Queue, time
from PyQt4 import QtGui, QtCore
serialPort = "/dev/ttyACM0"
serialBaud = 9600

## this is the main window class, it handles setting up the widnow and menu bars and maintining a connection with the worker thread. It also has the main widget loded in it
class mainWindow(QtGui.QMainWindow):
	def __init__(self, queue, endcommand):
		super(mainWindow, self).__init__()

		self.queue = queue
		self.endcommand = endcommand

	## a function that sets up all of the uo elements needed for the GUI
	def initUI(self):
		initMenu()
		self.splitterWidget = mainWidget()
		self.setCentralWidget(self.splitterWidget)
		self.setGeometry(100,100,800,700)
		self.showWindowTitle('RFID READER SOFTWARE')

	## a function that sets up the menus and menu bars for the application
	def initMenu(self):
		# Exit the program button
		exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit Application')
		exitAction.triggered.connect(self.close)

		self.statusBar()

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAction)

		toolbar = self.addToolBar('Exit')
		toolbar.addAction(exitAction)

	## This fucntion reads the queue and reacts to the elements it contains
	def readQueue(self):
		while self.queue.qsize():
			try:
				tag = self.queue.get(0)
				handleTag(tag)
			except Queue.Empty:
				pass

	## this fucntion handles the tags and how to add them to the database it also handles how to add the tag to the lists contained within
	def handleTag(self,tag):
		item = QtGui.QListWidgetItem("Tag %s" % tag[0:-2])
		self.splitterWidget.tagListWidget.addItem(item)	


class mainWidget(QtGui.QWidget):
	def __init__(self):
		super(mainQWidget, self).__init__()
		self.initUI()

	## this function intilizes the UI for the main widget which currently involves seting up two lists that get written to
	def initUI(self):
		hbox = QtGui.QHBoxLayout(self)

		self.tagListWidget = QtGui.QListWidget()
		self.namelistWidget = QtGui.QListWidget()

		splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
		splitter.addWidget(self.tagListWidget)
		splitter.addWidget(self.namelistWidget)

		hbox.addWidget(splitter)
		self.setLayout(hbox)
		QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

	



## the threader parent class spaws a second thread to pass messages from containing the rfid tags ##
class ThreaderParent:
	def __init__(self):
		print "WTHAT HE HELL"
		# create a queue for message passing
		self.queue = Queue.Queue()

		print "CREATED QUEUE"
		#instanciate the gui
		self.gui = mainWindow(self.queue, self.endApplication)
		self.gui.show()
		print "CRATED GUI"
		# create a timer to periodicly check the queue to see if it has tags
		self.timer = QtCore.QTimer()
		QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.periodicCall)
		self.timer.start(100)
		print "CRATED TIMER"
		# Create a thread to read the serial port
		self.running = 1
		self.thread = threading.Thread(target=self.workerThread)
		self.thread.start()

	# this fucntion gets called using a QTimer. It checks to see if there is anything in the queue and deals with it if there is ##
	def periodicCall(self):
		self.gui.readQueue()
		if not self.running:
			root.quit()

	# a function to cause this program to exit when the qt class exits
	def endApplication(self):
		print "ENDING"
		self.running = 0

	def workerThread(self):
		#serialConnection = serial.Serial(port=serialPort, baudrate=serialBaud)
		print "STARTING WORKER THREAD"
		while self.running:
			tag = None#serialConnection.readline()
			if (tag): self.queue.put(tag)






## the main function ##
def main():
	app = QtGui.QApplication(sys.argv)
	display = ThreaderParent()
	app.exec_()
	print "DONE"
	display.running = False
	sys.exit()

## run the main function ##
if __name__ == '__main__':
	main()