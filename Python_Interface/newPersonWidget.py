from PyQt4 import QtGui, QtCore
############################### NEW PERSON WIDGET ##############################
# This class handles the new person widget, which is a popup windows that      #
# allows a new person to be added to the database of users.                    #
################################################################################
class newPersonWidget(QtGui.QWidget):
    ############################ NEW PERSON WIDGIT INIT ############################
    # The intilization of the new user widget takes in the parent widget and the   #
    # optional parameter of a tag. If the tag is given then when the widget        #
    # apears the RFID tag field will allready be filled in                         #
    ################################################################################
    def __init__(self, parent, tag="", name="", metadata=[], metadataSlots=[]):
        super(newPersonWidget, self).__init__()

        self.parentWindow = parent

        self.setWindowTitle('Add User')
        y = (parent.geometry().height()-250)/2+parent.geometry().y()
        x = (parent.geometry().width()-400)/2+parent.geometry().x()
        self.setGeometry(x, y, 400, 250)

        formLayout = QtGui.QFormLayout()
        self.username = QtGui.QLineEdit(name, self)
        formLayout.addRow("&Name", self.username)
        self.rfidTag = QtGui.QLineEdit(tag, self)
        formLayout.addRow("&RFID:", self.rfidTag)

        if tag != "":
            self.rfidTag.setEnabled(False)

        for metadata in metadataSlots:
            metadataWidget = QtGui.QTextEdit("", self)
            formLayout.addRow("&"+metadata, metadataWidget)

        groupBox = QtGui.QGroupBox("Add User")
        groupBox.setLayout(formLayout)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.save)
        buttonBox.rejected.connect(self.close)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(groupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

    ##################################### SAVE #####################################
    # The save new tag function takes all the data presented in the new user       #
    # widgit and saves it to the databse.                                          #
    ################################################################################
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