# TO-DO

import configparser
from datetime import datetime, timedelta
from fractions import Fraction

import pandas as pd
import PyQt5.QtWidgets as qtw

class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()

        # initial calculations
        self.calculations()
        
        # set window
        qt_rectangle = self.frameGeometry()
        center_point = qtw.QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        self.setWindowTitle('Budget')
        self.setLayout(qtw.QVBoxLayout())
        self.main_menu()

        self.show()

    def calculations(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        last_paid = datetime.strptime(config['DEFAULT']['last_paid'], '%Y-%m-%d')
        mint_analysis = datetime.strptime(config['DEFAULT']['mint_analysis'], '%Y-%m-%d')
        income_bk = round(float(config['BUDGET']['income_bk_raw']) * float(Fraction(config['BUDGET']['income_bk_mult'])),2)
        cash = float(config['DEFAULT']['cash'])
        chase = pd.read_csv('ChaseCC.csv')
        citi = pd.read_csv('CitiCC.csv')
        mint = pd.read_csv('Mint.csv')
        chase['trans_date'] = pd.to_datetime(chase['Transaction Date'])
        citi['trans_date'] = pd.to_datetime(citi['Date'])
        mint['trans_date'] = pd.to_datetime(mint['Date'])
        chase = chase[chase['trans_date'] > last_paid]
        chase = chase[chase['Type'] != 'Payment']
        citi = citi[citi['trans_date'] > last_paid]
        citi = citi[~citi['Description'].str.contains('PAYMENT, THANK YOU')]
        mint = mint[mint['trans_date'] > mint_analysis]
        chase['amt'] = chase['Amount'] * -1
        citi.loc[(citi['Debit'].notnull()), 'amt'] = citi['Debit']
        citi.loc[(citi['Credit'].notnull()), 'amt'] = citi['Credit']
        mint.loc[(mint['Transaction Type'] == 'debit'), 'amt'] = mint['Amount']
        mint.loc[(mint['Transaction Type'] == 'credit'), 'amt'] = mint['Amount'] * -1
        chase = chase[['trans_date', 'amt', 'Description']]
        citi = citi[['trans_date', 'amt', 'Description']]
        mint = mint[['trans_date', 'amt', 'Category', 'Description', 'Original Description']]
        self.cash = cash
        self.chase = chase
        self.citi = citi
        self.last_paid = last_paid

    def main_menu(self):
        container = qtw.QWidget()
        container.setLayout(qtw.QGridLayout())

        btn1 = qtw.QPushButton('Click Me!')
        label_cash = qtw.QLabel('Cash: ')
        label_cash_amt = qtw.QLabel('${:,.2f}'.format(self.cash))
        label_chase = qtw.QLabel('Chase: ')
        label_chase_amt = qtw.QLabel('${:,.2f}'.format(round(self.chase['amt'].sum(),2)))
        label_citi = qtw.QLabel('Citi: ')
        label_citi_amt = qtw.QLabel('${:,.2f}'.format(round(self.citi['amt'].sum(),2)))
        label_last_cc = qtw.QLabel('Last CC Paid: ')
        label_last_cc_date = qtw.QLabel(self.last_paid.strftime("%m/%d/%Y"))
        btn_quit = qtw.QPushButton('Quit', self)

        container.layout().addWidget(btn1, 0, 0, 1, 2)
        container.layout().addWidget(label_cash, 1, 0)
        container.layout().addWidget(label_cash_amt, 1, 1)
        container.layout().addWidget(label_chase, 2, 0)
        container.layout().addWidget(label_chase_amt, 2, 1)
        container.layout().addWidget(label_citi, 3, 0)
        container.layout().addWidget(label_citi_amt, 3, 1)
        container.layout().addWidget(label_last_cc, 4, 0)
        container.layout().addWidget(label_last_cc_date, 4, 1)
        container.layout().addWidget(btn_quit, 5, 0, 1, 2)

        btn1.clicked.connect(self.test_click)
        btn_quit.clicked.connect(qtw.QApplication.instance().quit)

        self.label_cash_amt = label_cash_amt

        self.layout().addWidget(container)

    def test_click(self, event):
        self.label_cash_amt.setText('${:,.2f}'.format(1000000))

app = qtw.QApplication([])
mw = MainWindow()
app.exec_()