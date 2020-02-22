from PyQt5.QtWidgets import (
    QDialog,
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)

from PyQt5.QtGui import (
    QPixmap,
)

from PyQt5.QtCore import (
    Qt,
)

class CaptchaDialog(QDialog):
    def __init__(self, captchaImageData):
        super().__init__()

        #####################
        pixmap = QPixmap()
        pixmap.loadFromData(captchaImageData)
        pixmap = pixmap.scaled(pixmap.width() * 3, pixmap.height() * 3)

        self.label = QLabel()
        self.label.setPixmap(pixmap)

        #####################
        self.lineEdit = QLineEdit()
        self.lineEdit.textChanged.connect(self.lineEditTextChanged)

        #####################
        self.okButton = QPushButton("Ok")
        self.okButton.clicked.connect(self.accept)
        self.okButton.setEnabled(False)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)

        ######################
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.lineEdit)
        self.mainLayout.addLayout(self.buttonLayout)

        ######################
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Captcha")
        # self.resize(500, 500)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

    def lineEditTextChanged(self):
        self.okButton.setEnabled(len(self.lineEdit.text()) > 0)

    def getResult(self):
        return self.lineEdit.text()

def textFromCaptchaImage(captchaImageData):
    app = QApplication([])
    dialog = CaptchaDialog(captchaImageData)
    result = None
    while True:
        returnCode = dialog.exec()
        if returnCode == QDialog.Accepted:  
            result = dialog.getResult()
            break;
    return result