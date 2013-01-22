################################### SIGNATURE ##################################
#                                      ,,                                      #
#                     db             `7MM                                      #
#                    ;MM:              MM                                      #
#                   ,V^MM.    ,pP"Ybd  MMpMMMb.  .gP"Ya `7Mb,od8               #
#                  ,M  `MM    8I   `"  MM    MM ,M'   Yb  MM' "'               #
#                  AbmmmqMA   `YMMMa.  MM    MM 8M""""""  MM                   #
#                 A'     VML  L.   I8  MM    MM YM.    ,  MM                   #
#               .AMA.   .AMMA.M9mmmP'.JMML  JMML.`Mbmmd'.JMML.                 #
#                                                                              #
#                                                                              #
#                                  ,,    ,,                                    #
#                      .g8"""bgd `7MM    db        `7MM                        #
#                    .dP'     `M   MM                MM                        #
#                    dM'       `   MM  `7MM  ,p6"bo  MM  ,MP'                  #
#                    MM            MM    MM 6M'  OO  MM ;Y                     #
#                    MM.    `7MMF' MM    MM 8M       MM;Mm                     #
#                    `Mb.     MM   MM    MM YM.    , MM `Mb.                   #
#                      `"bmmmdPY .JMML..JMML.YMbmd'.JMML. YA.                  #
#                                                                              #
################################################################################
#################################### LICENSE ###################################
# Copyright (c) 2012, Asher Glick                                              #
# All rights reserved.                                                         #
#                                                                              #
# Redistribution and use in source and binary forms, with or without           #
# modification, are permitted provided that the following conditions are met:  #
#                                                                              #
# * Redistributions of source code must retain the above copyright notice,     #
# this                                                                         #
#   list of conditions and the following disclaimer.                           #
# * Redistributions in binary form must reproduce the above copyright notice,  #
#   this list of conditions and the following disclaimer in the documentation  #
#   and/or other materials provided with the distribution.                     #
#                                                                              #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"  #
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE    #
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE   #
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE    #
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR          #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF         #
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS     #
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN      #
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)      #
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   #
# POSSIBILITY OF SUCH DAMAGE.                                                  #
################################################################################

import sys, serial, threading, random, Queue, time
import serial.tools.list_ports
from PyQt4 import QtGui, QtCore
#serialPort = "/dev/ttyACM0"
serialBaud = 9600

################################ MAIN QT WINDOW ################################
# This is the main window class it handles setting up the window and menu      #
# bars and maintaining a connectino with teh worker thread. It also is in      #
# charge of loading the main widget inside of itself                           #
################################################################################
class mainWindow(QtGui.QMainWindow):
	def __init__(self, queue, endcommand):
		super(mainWindow, self).__init__()

		self.queue = queue
		self.endcommand = endcommand

		self.sheetModified = False

		self.initUI()

		

	#################################### INIT UI ###################################
	# A wraper function for init menu that also sets the main widget of the        #
	# QMainWindow and sizes window itself                                          #
	################################################################################
	def initUI(self):
		self.initMenu()
		self.splitterWidget = mainWidget()
		self.setCentralWidget(self.splitterWidget)
		self.setGeometry(100,100,800,700)
		self.setWindowTitle('RPI-RFID Interface')

	################################### INIT MENU ##################################
	# This function initilizes the menu by creating all of the buttons and then    #
	# adding them to the menu bar and the toolbar                                  #
	################################################################################
	def initMenu(self):
		# Exit the program button
		exitAction = QtGui.QAction(QtGui.QIcon('window-close.png'), 'Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit Application')
		exitAction.triggered.connect(self.closeApp)

		newContactAction = QtGui.QAction(QtGui.QIcon('contact-new-3.png'), 'New Person', self)
		newContactAction.setShortcut('Ctrl+M')
		newContactAction.setStatusTip('Create a new Person')
		newContactAction.triggered.connect(self.newPerson)

		openAttendanceAction = QtGui.QAction(QtGui.QIcon('document-open-recent-2.png'),'Open Attendace',self)
		openAttendanceAction.setShortcut('Ctrl+O')
		openAttendanceAction.setStatusTip('Open a previous attendance document')
		openAttendanceAction.triggered.connect(self.openAttendanceSheet)

		newAttendanceAction = QtGui.QAction(QtGui.QIcon('new-attendance.png'),'New Attendace',self)
		newAttendanceAction.setShortcut('Ctrl+N')
		newAttendanceAction.setStatusTip('Creates a new attendance document')
		newAttendanceAction.triggered.connect(self.newAttendanceSheet)

		saveAttendance = QtGui.QAction(QtGui.QIcon('document-save-2.png'),'Save Attendace',self)
		saveAttendance.setShortcut('Ctrl+S')
		saveAttendance.setStatusTip('Saves the attendance document')
		saveAttendance.triggered.connect(self.saveAttendanceSheet)


		self.statusBar()

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAction)
		fileMenu.addAction(newContactAction)
		fileMenu.addAction(openAttendanceAction)
		fileMenu.addAction(newAttendanceAction)
		fileMenu.addAction(saveAttendance)

		toolbar = self.addToolBar('Commands')
		toolbar.addAction(exitAction)
		toolbar.addAction(newContactAction)
		toolbar.addAction(openAttendanceAction)
		toolbar.addAction(newAttendanceAction)
		toolbar.addAction(saveAttendance)

	############################### CLOSE APPLICATION ##############################
	# This function prompts the user if they would like to exit the program and    #
	# if they click yes then the entire program exits, not just the selected       #
	# window                                                                       #
	################################################################################
	def closeApp(self):
		reallyQuit =  QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
		if reallyQuit == QtGui.QMessageBox.Yes:
			QtCore.QCoreApplication.instance().quit()

	############################### NEW PERSON POPUP ###############################
	# The new person function creates a new person window and allows the user to   #
	# add the new person to the database                                           #
	################################################################################
	def newPerson(self):
		#self.move(self.x(), self.y())
		self.nperson = newPersonWidget(self)
		self.nperson.show()
	# This function will open a previously created attendance document
	
	def openAttendanceSheet(self):
		if self.sheetModified == True:
			# Prompt the user if they are sure they would like to delete the current sheet and start another
			deleteSheetResponce =  QtGui.QMessageBox.question(self, 'Message', "Are you sure to delete the current attendance sheet and start a new one?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			# call the subclass's action to clear the attendance
			if deleteSheetResponce == QtGui.QMessageBox.No:
				return
		
		filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", "", "")
		if filename == "":
			return
		self.splitterWidget.loadTagTable(filename)
		
	def saveAttendanceSheet(self):
		filename = QtGui.QFileDialog.getSaveFileName(self, "Save File", "todays date", ".rfid")
		# check to see if the user did not specify a file to save
		if filename == "":
			return
		self.modified = False
		
		self.splitterWidget.saveTagTable(filename)

	def newAttendanceSheet(self):
		if self.sheetModified == True:
			# Prompt the user if they are sure they would like to delete the current sheet and start another
			deleteSheetResponce =  QtGui.QMessageBox.question(self, 'Message', "Are you sure to delete the current attendance sheet and start a new one?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			# call the subclass's action to clear the attendance
			if deleteSheetResponce == QtGui.QMessageBox.No:
				return
		self.splitterWidget.newTagTable()
		self.splitterWidget.updateTagTable()
		self.sheetModified = False

	################################ READ TAG QUEUE ################################
	# The read queue function attemts to read anythin in the queue until it is     #
	# empty. Each itereation that a tag is removed from the queue it is passed to  #
	# the handle tag function to add it to the current attendance document         #
	################################################################################
	def readQueue(self):
		while self.queue.qsize():
			try:
				tag = self.queue.get(0)
				self.handleTag(tag)
			except Queue.Empty:
				pass

	## this fucntion handles the tags and how to add them to the database it also handles how to add the tag to the lists contained within
	def handleTag(self,tag):
		#item = QtGui.QListWidgetItem("Tag %s" % tag[0:-2])
		#self.splitterWidget.tagListWidget.addItem(item)

		self.splitterWidget.tagList.append(tag)
		self.splitterWidget.updateTagTable()

		self.sheetModified = True

	


class newPersonWidget(QtGui.QWidget):
	def __init__(self,parent):
		super(newPersonWidget, self).__init__()

		self.parentWindow = parent

		self.setWindowTitle('Add User')
		y = (parent.geometry().height()-250)/2+parent.geometry().y()
		x = (parent.geometry().width()-400)/2+parent.geometry().x()
		self.setGeometry(x, y, 400, 250)

		
		formLayout = QtGui.QFormLayout()
		self.username = QtGui.QLineEdit("",self)
		formLayout.addRow("&Name", self.username)
		self.rfidTag = QtGui.QLineEdit("",self)
		formLayout.addRow("&RFID:", self.rfidTag)
		self.metadata = QtGui.QTextEdit("",self)
		formLayout.addRow("&Metadata", self.metadata)
		groupBox = QtGui.QGroupBox("Add User");
		groupBox.setLayout(formLayout);

		buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.save)
		buttonBox.rejected.connect(self.close)
		
		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(groupBox)
		mainLayout.addWidget(buttonBox)
		self.setLayout(mainLayout)

		

	def save(self):
		# TODO save the new user in the database
		# print "pretending to save"
		rfid = str(self.rfidTag.text())
		name = str(self.username.text())

		print rfid, name

		self.parentWindow.splitterWidget.IDRelation[rfid] = name
		self.parentWindow.splitterWidget.updateNameTable()
		self.parentWindow.splitterWidget.updateTagTable()
		self.parentWindow.splitterWidget.saveDatabase()
		# then close
		self.close()
		
################################ MAIN QT WIDGET ################################
# The main qt widget handles all of the ui inside of the main window. This     #
# mainly includes the two list views displaying all of the students as well    #
# as just the students selected. Allong with the ability to search those lists #
################################################################################
class mainWidget(QtGui.QWidget):
	def __init__(self):
		super(mainWidget, self).__init__()
		self.initUI()
		self.loadDatabase()

	## this function intilizes the UI for the main widget which currently involves seting up two lists that get written to
	def initUI(self):
		hbox = QtGui.QHBoxLayout(self)

		self.tagListWidget = QtGui.QListWidget()

		

		self.namelistWidget = QtGui.QListWidget()
		self.namelist = QtGui.QLineEdit("",self)
		self.namelist.setPlaceholderText("Search Names ...")
		groupBox = QtGui.QVBoxLayout(self)
		groupBox.addWidget(self.namelist)
		groupBox.addWidget(self.namelistWidget)
		groupBox.setMargin(0)
		groupBoxWidget = QtGui.QWidget()
		groupBoxWidget.setLayout(groupBox)

		splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
		splitter.addWidget(self.tagListWidget)
		splitter.addWidget(groupBoxWidget)

		hbox.addWidget(splitter)
		self.setLayout(hbox)
		QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

	IDRelation = {}
	def loadDatabase(self):
		self.namelist.textChanged.connect(self.updateNameTable)
		f = open("Sample_Database")
		for line in f:
			splitline = line.split(',')
			rfid = splitline[0]
			name = splitline[1]
			#item = QtGui.QListWidgetItem("%s\t%s"%(rfid,name))
			#self.splitterWidget.namelistWidget.addItem(item)
			self.IDRelation[rfid] = name[:-1]
		self.updateNameTable("")
	
	def saveDatabase(self):
		savefile = open("Sample_Database",'w')
		for tag in self.IDRelation:
			csvLine = tag + "," + self.IDRelation[tag] 
			savefile.write(csvLine+'\n')
		savefile.close()

	############################### UPDATE NAME TABLE ##############################
	# THis function updates the the the contents of the list view containing the   #
	# name table. If the variable QText is specified then only elements of the     #
	# original list that contain that text will be included in the displayed       #
	# list. If the variable is not set then it will be set equal to the contents   #
	# of the text box above the list                                               #
	################################################################################
	def updateNameTable(self,QText=None):
		if QText == None:
			QText = str(self.namelist.text())
		text = str(QText)
		firstOrder = []
		secondOrder = []
		thirdOrder = []
		for rfid in self.IDRelation:
			name = self.IDRelation[rfid]
			if text.lower() in name.lower():
				thirdOrder.append(name)

		self.namelistWidget.clear()

		for name in thirdOrder:
			#item = QtGui.QListWidgetItem("%s\t%s"%(rfid,name))
			item = QtGui.QListWidgetItem("%s"%(name))
			self.namelistWidget.addItem(item)

	# The tag list stores the list of tags that have been swiped in durring this session
	tagList = []
	def loadTagTable (self, filename):
		print "Tried to open file", filename
		self.newTagTable()
		loadFile = open(filename)
		for line in loadFile:
			line = line.rstrip().lstrip()
			splitline = line.split(',')
			self.tagList.append(splitline[0]) #add only the rfid tag to the tag list, all the other data will be collected from the database
		loadFile.close()
		self.updateTagTable()

	def saveTagTable (self, filename):
		print "Tried to save file", filename
		savefile = open(filename,'w')
		for tag in self.tagList:
			csvLine = tag
			if tag in self.IDRelation:
				# for all the other attribtes of the relation will be added to the csv here too
				csvLine += ","+self.IDRelation[tag]
			savefile.write(csvLine+'\n')
		savefile.close()

	def newTagTable (self):
		self.tagList = []

	def updateTagTable(self, QText=None):
		# QText will be used to sort the tag table, but for now it will not be used

		self.tagListWidget.clear()
		for i in self.tagList:
			if (i in self.IDRelation):
				i = self.IDRelation[i]
			else:
				i = "Unknown Tag "+i
			item = QtGui.QListWidgetItem("%s"%(i))
			self.tagListWidget.addItem(item)

############################# THREADER PARENT CLASS ############################
# The threader parent class spawns a second thread to pass messages from the   #
# rfid reader over the serial port to a queue which is read by the main qt     #
# thread                                                                       #
################################################################################
class ThreaderParent:
	
	############################# INIT THREADER PARENT #############################
	# THe initilization function creates the queue, calls the QT main window       #
	# generation class to generate the QT window, and then creates the thread for  #
	# the serial port to read from                                                 #
	################################################################################
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
		self.openPorts = serial.tools.list_ports.comports()
		self.thread = []
		
	################################# PERIODIC CALL ################################
	# THis function is called periodoicly by the QT timer to tell the Main QT      #
	# Window to read data from the queue and update the display accordingly        #
	################################################################################
	def periodicCall(self):
		self.gui.readQueue()
		if not self.running:
			root.quit()
		else:
			# get the current list of serial divices
			currentPorts = list(serial.tools.list_ports.comports())
			###print "STARTING PERIODIC CALL"

			###print "LENGTH OF CURRENT PORTS", len(currentPorts)
			#for port in currentPorts:
			#	print port

			# find all new ports
			###print "LOOKING FOR NEW PORTS"
			newPorts = []
			for port in currentPorts:
				if port not in self.openPorts:
					newPorts.append(port)
					print "NEW PORT:", port
					self.thread.append(threading.Thread(target=self.workerThread,args=(port)))
					self.thread[-1].start()
			
			# find all removed ports
			###print "LOOKING FOR CLOSED PORTS"
			closedPorts = []
			for port in self.openPorts:
				if port not in currentPorts:
					closedPorts.append(port)
					print "CLOSED PORT:", port

			# set the current ports to the open ports
			###print "RESETTING PORTS"
			self.openPorts = currentPorts
			###print "RESET PORTS"
			###print "LENGTH OF CURRENT PORTS", len(currentPorts)
			###for port in currentPorts:
			###	print port

			###print "FUNCTION DONE"

	################################ END APPLICATION ###############################
	# This function should be called by the QT main window class when the QT       #
	# process ends, it sets the variable running to 0 so that the worker thread    #
	# can quit when the main thread does                                           #
	################################################################################
	def endApplication(self):
		print "ENDING"
		self.running = 0

	################################# WORKER THREAD ################################
	# The worker thread function is the function that is called to run inside the  #
	# spawned thread. It handles reading from the serial connection, if it reads   #
	# a valid tag then it puts it into a queue from wich the main thread can       #
	# handle it                                                                    #
	################################################################################
	def workerThread(self,serialPort,serialName, serialVIN):
		try:
			serialConnection = serial.Serial(port=serialPort, baudrate=serialBaud, timeout=0)
		except:
			print "ERROR INITILIZING THE CONNECTION TO", serialPort, "CLOSING THREAD"
			return


		print "STARTING WORKER THREAD:"
		print " WORKER PORT:", serialPort
		print " WORKER NAME:", serialName
		print " WORKER VIN:", serialVIN
		fulltag = ""
		while self.running:
			try:
				tag = serialConnection.read()
			except:
				print "ERROR READING FROM ", serialPort, "CLOSING THREAD"
				return
			if (tag == '\n'):
				self.queue.put(fulltag)
				fulltag = ""
				#print 'read tag'
				continue
			if (tag == '\r'):
				continue
			fulltag += tag

## the main function ##
def main():
	app = QtGui.QApplication(sys.argv)
	display = ThreaderParent()
	app.exec_()
	print "DONE"
	#display.thread.terminate()
	display.running = False
	#sys.exit()
	exit()

## run the main function ##
if __name__ == '__main__':
	main()