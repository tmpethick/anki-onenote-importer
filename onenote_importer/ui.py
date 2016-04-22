# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'anki_importer/importing.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MHTImportDialog(object):
    def setupUi(self, MHTImportDialog):
        MHTImportDialog.setObjectName(_fromUtf8("MHTImportDialog"))
        MHTImportDialog.resize(400, 150)
        self.vboxlayout = QtGui.QVBoxLayout(MHTImportDialog)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.groupBox = QtGui.QGroupBox(MHTImportDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.toplayout = QtGui.QVBoxLayout(self.groupBox)
        self.toplayout.setObjectName(_fromUtf8("toplayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.deckArea = QtGui.QWidget(self.groupBox)
        self.deckArea.setObjectName(_fromUtf8("deckArea"))
        self.gridLayout_2.addWidget(self.deckArea, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.toplayout.addLayout(self.gridLayout_2)
        self.vboxlayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(MHTImportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(MHTImportDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MHTImportDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MHTImportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MHTImportDialog)

    def retranslateUi(self, MHTImportDialog):
        MHTImportDialog.setWindowTitle(_translate("MHTImportDialog", "Import", None))
        self.groupBox.setTitle(_translate("MHTImportDialog", "Import options", None))
        self.label_2.setText(_translate("MHTImportDialog", "Deck", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MHTImportDialog = QtGui.QDialog()
    ui = Ui_MHTImportDialog()
    ui.setupUi(MHTImportDialog)
    MHTImportDialog.show()
    sys.exit(app.exec_())

