import sys
from PyQt5.QtWidgets import (QApplication, QToolTip, QPushButton, QMessageBox,
                             QDesktopWidget, QMainWindow, qApp, QAction, QMenu)
from PyQt5.QtGui import (QIcon, QFont)


# create class with QWidget inheritance
class BudgetGui(QMainWindow):

    # init and call initUI
    def __init__(self):
        super().__init__()

        self.initUI()

    # defines basic GUI
    def initUI(self):

        # tool tips
        QToolTip.setFont(QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        # push button
        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)

        # exit button
        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(QApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 75)

        # status bar
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')

        # menu - new
        newAct = QAction('New', self)

        # sub menu - Import and Import Mail
        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self)
        impMenu.addAction(impAct)

        # menu - exit
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        # menu - checkbox - view
        viewStatAct = QAction('View statusbar', self, checkable=True)
        viewStatAct.setStatusTip('View statusbar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.toggleMenu)

        # create menu
        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(newAct)
        fileMenu.addMenu(impMenu)
        fileMenu.addAction(exitAct)

        viewMenu = menubar.addMenu('View')
        viewMenu.addAction(viewStatAct)

        # dimensions
        self.resize(250, 150)
        self.center()
        self.setWindowTitle('Budget')
        self.setWindowIcon(QIcon('doge.png'))

        self.show()

    # center window
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # checkbox method
    def toggleMenu(self, state):
        if state:
            self.statusbar.show()
        else:
            self.statusbar.hide()

    # message box when quitting
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message', 'Are you sure to quit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():

    app = QApplication(sys.argv)
    bgui = BudgetGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
