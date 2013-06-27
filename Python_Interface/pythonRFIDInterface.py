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

import sys
import serial
import threading
import random
import Queue
import time
import pyaudio
import wave
import signal
import datetime
import platform
import itertools
#import serial.tools.list_ports
import glob
from PyQt4 import QtGui, QtCore

from newPersonWidget import newPersonWidget


#serialPort = "/dev/ttyACM0"
serialBaud = 9600

metadataSlots = ["Metadata", "More Metadata"]


class aboutWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(aboutWidget, self).__init__()
        self.setWindowTitle('About AVRFID')
        y = (parent.geometry().height()-250)/2+parent.geometry().y()
        x = (parent.geometry().width()-400)/2+parent.geometry().x()
        self.setGeometry(x, y, 400, 250)

        # create centered text
        self.inputhlayout = QtGui.QHBoxLayout()
        self.inputhlayout.addStretch(1)
        self.inputvlayout = QtGui.QVBoxLayout()
        self.inputvlayout.addStretch(1)

        # Create the domain text box
        lbl1 = QtGui.QLabel('<qt><b style="font-size:40px">AVRFID Client</b><br><i>Copyright \xa9 2012-2013 MakerPulse</i><br></qt>', self)
        lbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.inputvlayout.addWidget(lbl1)

        # Create the password text box
        lbl2 = QtGui.QLabel('<qt>Written by Asher Glick (aglick@aglick.com)<br/>The AVRFID client is a computer client<br>used to assist with the use of the<br>MakerPulse AVRFID RFID unit<br><a href="http://www.makerpulse.com/avrfid">Website</a></qt>', self)
        lbl2.setAlignment(QtCore.Qt.AlignCenter)
        lbl2.setOpenExternalLinks(True)
        self.inputvlayout.addWidget(lbl2)

        # Finish configuring the layput
        self.inputvlayout.addStretch(1)
        self.inputhlayout.addLayout(self.inputvlayout)
        self.inputhlayout.addStretch(1)
        # Set the layout to the hlayout
        self.setLayout(self.inputhlayout)


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
        self.splitterWidget = mainWidget(self)
        self.setCentralWidget(self.splitterWidget)
        self.setGeometry(100, 100, 800, 700)
        self.setWindowTitle('RPI-RFID Interface')

    ################################### INIT MENU ##################################
    # This function initilizes the menu by creating all of the buttons and then    #
    # adding them to the menu bar and the toolbar                                  #
    ################################################################################
    def initMenu(self):

        # FILE MENU OPTIONS
        # Exit the program button
        exitAction = QtGui.QAction(QtGui.QIcon('icons/window-close.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit Application')
        exitAction.triggered.connect(self.closeApp)

        newContactAction = QtGui.QAction(QtGui.QIcon('icons/add_user.png'), 'New Person', self)
        newContactAction.setShortcut('Ctrl+M')
        newContactAction.setStatusTip('Create a new Person')
        newContactAction.triggered.connect(self.newPerson)

        openAttendanceAction = QtGui.QAction(QtGui.QIcon('icons/folder.png'), 'Open Attendace', self)
        openAttendanceAction.setShortcut('Ctrl+O')
        openAttendanceAction.setStatusTip('Open a previous attendance document')
        openAttendanceAction.triggered.connect(self.openAttendanceSheet)

        newAttendanceAction = QtGui.QAction(QtGui.QIcon('icons/add_page.png'), 'New Attendace', self)
        newAttendanceAction.setShortcut('Ctrl+N')
        newAttendanceAction.setStatusTip('Creates a new attendance document')
        newAttendanceAction.triggered.connect(self.newAttendanceSheet)

        saveAttendance = QtGui.QAction(QtGui.QIcon('icons/download_page.png'), 'Save Attendace', self)
        saveAttendance.setShortcut('Ctrl+S')
        saveAttendance.setStatusTip('Saves the attendance document')
        saveAttendance.triggered.connect(self.saveAttendanceSheet)

        # DATABASE READER OPTIONS
        changeDatabase = QtGui.QAction(QtGui.QIcon(""), 'Open New Database', self)
        changeDatabase.setShortcut("Ctrl+D")
        changeDatabase.setStatusTip('Open a different default databse file')

        exportDatabse = QtGui.QAction(QtGui.QIcon(""), 'Export Database', self)
        exportDatabse.setShortcut("Ctrl+E")
        exportDatabse.setStatusTip('Export the database to another location')

        importDatabase = QtGui.QAction(QtGui.QIcon(""), 'Import Database', self)
        importDatabase.setShortcut("Ctrl+I")
        importDatabase.setStatusTip('import another database into your current database')

        allowRFIDModification = QtGui.QAction(QtGui.QIcon(""), "Allow RFID Modification", self)
        allowRFIDModification.setStatusTip('Allow the user to modify the RFID tag of database element')

        deleteDatabaseElement = QtGui.QAction(QtGui.QIcon(""), "Delete Databse Element", self)
        deleteDatabaseElement.setStatusTip('Delete a single element of the database')

        # Reader Options
        readerAutoConnect = QtGui.QAction(QtGui.QIcon(""), 'Enable Auto Connect', self)
        #readerAutoConnect.setShortcut("")
        readerAutoConnect.setStatusTip('Enable the program to auto detect and connect to a reader')


        # HELP MENU OPTIONS
        viewOnlineHelp = QtGui.QAction(QtGui.QIcon(""),'View Online Help', self)
        aboutAvrfid = QtGui.QAction(QtGui.QIcon(""), 'About...', self)
        aboutAvrfid.triggered.connect(self.openHelp)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(newContactAction)
        fileMenu.addAction(openAttendanceAction)
        fileMenu.addAction(newAttendanceAction)
        fileMenu.addAction(saveAttendance)

        databaseMenu = menubar.addMenu('&Database')
        databaseMenu.addAction(changeDatabase)
        databaseMenu.addAction(exportDatabse)
        databaseMenu.addAction(importDatabase)
        databaseMenu.addAction(allowRFIDModification)
        databaseMenu.addAction(deleteDatabaseElement)

        self.rfidReaderMenu = menubar.addMenu("&Reader")
        self.rfidReaderMenu.addAction(readerAutoConnect)
        self.rfidReaderList = self.rfidReaderMenu.addMenu("&Manual Connect")

        helpMenu = menubar.addMenu("&Help")
        helpMenu.addAction(viewOnlineHelp)
        helpMenu.addAction(aboutAvrfid)

        toolbar = self.addToolBar('Commands')
        #toolbar.addAction(exitAction)
        toolbar.addAction(newContactAction)
        toolbar.addAction(openAttendanceAction)
        toolbar.addAction(newAttendanceAction)
        toolbar.addAction(saveAttendance)

    def openHelp(self):
        self.aboutWindow = aboutWidget(self)
        self.aboutWindow.show()
    ############################### CLOSE APPLICATION ##############################
    # This function prompts the user if they would like to exit the program and    #
    # if they click yes then the entire program exits, not just the selected       #
    # window                                                                       #
    ################################################################################
    def closeApp(self):
        reallyQuit = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reallyQuit == QtGui.QMessageBox.Yes:
            QtCore.QCoreApplication.instance().quit()

    ############################### NEW PERSON POPUP ###############################
    # The new person function creates a new person window and allows the user to   #
    # add the new person to the database                                           #
    ################################################################################
    def newPerson(self):
        #self.move(self.x(), self.y())
        self.nperson = newPersonWidget(self,metadataSlots=metadataSlots)
        self.nperson.show()

    ############################# OPEN ATTENDANCE SHEET ############################
    # THis function opens a file dialog to search for a document to open. If a     #
    # file is selected then it is opened. If the current file is modified then a   #
    # message box prompt is also shown to ask the user if they want to delete the  #
    # current unsaved attendance sheet                                             #
    ################################################################################
    def openAttendanceSheet(self):
        if self.sheetModified:
            # Prompt the user if they are sure they would like to delete the current sheet and start another
            deleteSheetResponce = QtGui.QMessageBox.question(self, 'Message', "Are you sure to delete the current attendance sheet and start a new one?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            # call the subclass's action to clear the attendance
            if deleteSheetResponce == QtGui.QMessageBox.No:
                return

        filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", "", "")
        if filename == "":
            return
        self.splitterWidget.loadTagTable(filename)

    ############################# SAVE ATTENDANCE SHEET ############################
    # This function will save the current attendance sheet. The default name for   #
    # the saved file is set to todays date. If the file is saved then the global   #
    # 'modified' variable is set to false                                          #
    ################################################################################
    def saveAttendanceSheet(self):
        now = datetime.datetime.now()
        months = ["January", "Febuary", "March", "April", "May", "June", "July", "Augest", "September", "October", "November", "December"]
        todaysDate = months[now.month-1]+"-"+str(now.day)+"-"+str(now.year)
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save File", "Attendance-"+todaysDate+".rfid", ".rfid")
        # check to see if the user did not specify a file to save
        if filename == "":
            return
        self.modified = False

        self.splitterWidget.saveTagTable(filename)

    ############################# NEW ATTENDANCE SHEET #############################
    # The new attendance sheet function will clear the current attendance list     #
    # resulting in a blank new list. If the current list has been modified since   #
    # it was last saved then a message box will pop up confirming that the user    #
    # wants to delete the current sheet                                            #
    ################################################################################
    def newAttendanceSheet(self):
        if self.sheetModified:
            # Prompt the user if they are sure they would like to delete the current sheet and start another
            deleteSheetResponce = QtGui.QMessageBox.question(self, 'Message', "Are you sure to delete the current attendance sheet and start a new one?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
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

    ################################## HANDLE TAG ##################################
    # This function handles adding the new tag to the tag list. It also changes    #
    # the current status of the attendance sheet to modified. Lastly it plays a    #
    # notification noise to indicate the tag has been read                         #
    ################################################################################
    def handleTag(self, tag):
        self.splitterWidget.tagList.append(tag)
        self.splitterWidget.updateTagTable()

        self.sheetModified = True
        playNoise()


################################ MAIN QT WIDGET ################################
# The main qt widget handles all of the ui inside of the main window. This     #
# mainly includes the two list views displaying all of the students as well    #
# as just the students selected. Allong with the ability to search those lists #
################################################################################
class mainWidget(QtGui.QWidget):
    ############################### INIT MAIN WIDGET ###############################
    # The main widget initilization takes in a parent widget or windows. It is in  #
    # charge of setting up the display functionality                               #
    ################################################################################
    def __init__(self, parent):
        super(mainWidget, self).__init__()
        self.parent = parent
        self.IDRelation = {}
        self.tagList = []
        self.initUI()
        self.loadDatabase()

    #################################### INIT UI ###################################
    # This function initilizes the UI for the main widget, involving the two       #
    # lists that get displayed to the user and the search bar for users.           #
    ################################################################################
    def initUI(self):
        hbox = QtGui.QHBoxLayout(self)

        self.tagListWidget = QtGui.QListWidget()

        self.namelistWidget = QtGui.QListWidget()
        self.namelist = QtGui.QLineEdit("", self)
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

        self.tagListWidget.itemDoubleClicked.connect(self.editTag)
        self.namelistWidget.itemDoubleClicked.connect(self.editTag)

    ################################# LOAD DATABASE ################################
    # The load databse funciton reads the databse file into memory and puts all    #
    # the entries into the databse relation table. It is run when the program      #
    # starts up and does not need to be run by the user.                           #
    ################################################################################
    def loadDatabase(self):
        self.namelist.textChanged.connect(self.updateNameTable)
        try:
            f = open("Sample_Database")
            for line in f:
                splitline = line.split(',')
                rfid = splitline[0]
                name = splitline[1]
                #item = QtGui.QListWidgetItem("%s\t%s"%(rfid,name))
                #self.splitterWidget.namelistWidget.addItem(item)
                self.IDRelation[rfid] = name[:-1]
        except IOError:
            pass
        self.updateNameTable("")

    ################################# SAVE DATABASE ################################
    # The save database function reads the data from the ID relation and converts  #
    # it back into a CSV file and saves it to the database file                    #
    ################################################################################
    def saveDatabase(self):
        savefile = open("Sample_Database", 'w')
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
    def updateNameTable(self, QText=None):
        if QText is None:
            QText = str(self.namelist.text())
        text = str(QText)
        firstOrder = []
        secondOrder = []
        thirdOrder = []
        for rfid in self.IDRelation:
            name = self.IDRelation[rfid]
            if text.lower() in name.lower():
                thirdOrder.append((name, rfid))

        self.namelistWidget.clear()

        for (name, rfid) in thirdOrder:
            item = QtGui.QListWidgetItem("%s" % (name))
            item.rfidTag = rfid
            self.namelistWidget.addItem(item)

    ################################ LOAD TAG TABLE ################################
    # Load tag table is the function that is called when a previous attendance     #
    # sheet is trying to be accessed. It opens a file and writes the contents to   #
    # the current tag list                                                         #
    ################################################################################
    def loadTagTable(self, filename):
        print "Tried to open file", filename
        self.newTagTable()
        loadFile = open(filename)
        for line in loadFile:
            line = line.rstrip().lstrip()
            splitline = line.split(',')
            self.tagList.append(splitline[0])  # add only the rfid tag to the tag list, all the other data will be collected from the database
        loadFile.close()
        self.updateTagTable()

    ################################ SAVE TAG TABLE ################################
    # The save tag table converts the current attendance sheet into a CSV file     #
    # and saves it to a user specified location                                    #
    ################################################################################
    def saveTagTable(self, filename):
        print "Tried to save file", filename
        savefile = open(filename, 'w')
        for tag in self.tagList:
            csvLine = tag
            if tag in self.IDRelation:
                # for all the other attribtes of the relation will be added to the csv here too
                csvLine += ","+self.IDRelation[tag]
            savefile.write(csvLine+'\n')
        savefile.close()

    ################################# NEW TAG TABLE ################################
    # The new tag table clears the current tag list making it blank once more      #
    ################################################################################
    def newTagTable(self):
        self.tagList = []

    ############################### UPDATE TAG TABLE ###############################
    # The update tag table function iterates through all of the tags in the tag    #
    # list if the tag exists in the database then the name associated with the     #
    # tag is displayued. If there is no name then 'Unknown Tag' is displayed with  #
    # the tag that was scanned                                                     #
    ################################################################################
    def updateTagTable(self, QText=None):
        # QText will be used to sort the tag table, but for now it will not be used

        self.tagListWidget.clear()
        for tag in reversed(self.tagList):
            name = ""
            if (tag in self.IDRelation):
                name = self.IDRelation[tag]
            else:
                name = "Unknown Tag "+i
            item = QtGui.QListWidgetItem("%s" % (name))
            item.rfidTag = tag
            self.tagListWidget.addItem(item)

    def editTag(self, listItem):
        tagToModify = str(listItem.text())
        if tagToModify[0:12] == "Unknown Tag ":
            print "UNKNOWN TAG"
            tag = tagToModify[12:]
            # Call edit function with just the RFID Tag
            self.nperson = newPersonWidget(self.parent, tag=tag, metadataSlots=metadataSlots)
            self.nperson.show()
        else:
            tag = listItem.rfidTag
            print tag + "!!!"
            self.nperson = newPersonWidget(self.parent, tag=tag, name=str(listItem.text()), metadata=[], metadataSlots=metadataSlots)
            self.nperson.show()


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
        self.tagqueue = Queue.Queue()
        print "CREATED QUEUE"
        #instanciate the gui
        self.gui = mainWindow(self.tagqueue, self.endApplication)
        self.gui.show()
        print "CRATED GUI"
        # create a timer to periodicly check the queue to see if it has tags
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.periodicCall)
        self.timer.start(100)
        print "CRATED TIMER"
        # Create a thread to read the serial port
        self.running = 1
        self.openPorts = scanPorts()
        self.refreshSerialList(self.openPorts, ["/dev/ttyS4"])
        self.thread = []

        self.workerqueue = Queue.Queue()

    def refreshSerialList(self, portList, connectedList):
        self.gui.rfidReaderList.clear()
        for (index, port) in enumerate(self.openPorts):
            menuItemName = "Connect To " + port
            menuItemIcon = "icons/unchecked.png"
            if port in connectedList:
                menuItemName = "Disconnect From " + port
                menuItemIcon = "icons/checked.png"

            serialPort = QtGui.QAction(QtGui.QIcon(menuItemIcon), menuItemName, self.gui)
            #if index < 10:
            #    serialPort.setShortcut("Ctrl+"+str(index))
            self.gui.rfidReaderList.addAction(serialPort)

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
            currentPorts = scanPorts()

            # find all new ports
            newPorts = []
            for port in currentPorts:
                if port not in self.openPorts:
                    newPorts.append(port)
                    print "NEW PORT:", port
                    self.thread.append(threading.Thread(target=self.workerThread, args=(port,)))
                    self.thread[-1].start()

            # find all removed ports
            closedPorts = []
            for port in self.openPorts:
                if port not in currentPorts:
                    closedPorts.append(port)
                    print "CLOSED PORT:", port

            # set the current ports to the open ports
            if self.openPorts != currentPorts:
                self.openPorts = currentPorts
                self.refreshSerialList(currentPorts, ["/dev/ttyS4"])

            # Cycle through the queue
            while not self.workerqueue.empty():
                print self.workerqueue.get()

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
    def workerThread(self, serialPort, serialName="", serialVIN=""):
        try:
            serialConnection = serial.Serial(port=serialPort, baudrate=serialBaud, timeout=0)
        except Exception:
            print Exception
            print "ERROR INITILIZING THE CONNECTION TO", serialPort, "CLOSING THREAD"
            return

        self.workerqueue.put("Starting Worker For:"+serialPort)

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
                break
            if (tag == '\n'):
                self.tagqueue.put(fulltag)
                fulltag = ""
                #print 'read tag'
                continue
            if (tag == '\r'):
                continue
            fulltag += tag

        self.workerqueue.put("Ending Worker For:"+serialPort)

## the main function ##

CHUNK = 1024
p = None
stream = None
data = None

def scanPorts():
    systemName = platform.system()
    if systemName == "Windows":
        ### UNTESTED WINDOWS CODE ###
        ### NEEDS TESTING!!!!!!!! ###
        import _winreg as winreg
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        ports = []
        for i in itertools.count():
            try:
                val = winreg.EnumValue(key, i)
                ports.append(str(val[1]))
            except EnvironmentError:
                break
        return sorted(ports)
    elif systemName == "Darwin":
        # mac system, not tested but not much different from *nix solution
        return glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
    else:
        # assume *nix
        return list(glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'))

def playNoise():

    thread = threading.Thread(target=playNoise_Thread)
    thread.start()


def playNoise_Thread():
    stream.start_stream()

    wf = wave.open("ping.wav", 'rb')
    data = wf.readframes(CHUNK)
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    wf.close()
    stream.stop_stream()


def loadNoise():
    global p
    global stream

    wf = wave.open("ping.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    wf.close()


def endNoise():
    stream.close()
    p.terminate()

def sigintHandler(*args):
    sys.stderr.write('\r')
    print args
    # if QtGui.QMessageBox.question(None, '', "Are you sure you want to quit?",
    #                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
    #                         QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
    #     return
    QtGui.QApplication.quit()

def main():
    loadNoise()

    signal.signal(signal.SIGINT, sigintHandler)
    app = QtGui.QApplication(sys.argv)
    display = ThreaderParent()
    app.exec_()
    print "DONE"
    #display.thread.terminate()
    display.running = False
    #sys.exit()
    endNoise()
    exit()

## run the main function ##
if __name__ == '__main__':
    main()
