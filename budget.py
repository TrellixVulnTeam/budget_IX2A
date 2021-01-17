import configparser
from datetime import datetime, timedelta
from fractions import Fraction

import pandas as pd


class Budget:
    def __init__(self):
        pass

    def read_config(self):
        # READ CONFIG FILE
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.last_paid = datetime.strptime(config['DEFAULT']['last_paid'], '%Y-%m-%d')
        self.mint_analysis = datetime.strptime(config['DEFAULT']['mint_analysis'], '%Y-%m-%d')
        self.income_bk = round(
            float(config['BUDGET']['income_bk_raw'])
            *
            float(Fraction(config['BUDGET']['income_bk_mult'])), 2)

    def read_csv(self, last_paid, mint_analysis):
        # READ CSV FILES AND CONVERT TO DATAFRAMES
        chase = pd.read_csv('ChaseCC.csv')
        citi = pd.read_csv('CitiCC.csv')
        mint = pd.read_csv('Mint.csv')

        # CREATE TRANS_DATE FROM VARIOUS DATE FIELDS
        chase['trans_date'] = pd.to_datetime(chase['Transaction Date'])
        citi['trans_date'] = pd.to_datetime(citi['Date'])
        mint['trans_date'] = pd.to_datetime(mint['Date'])

        # FILTER OUT DATA
        chase = chase[chase['trans_date'] > last_paid]
        chase = chase[chase['Type'] != 'Payment']
        citi = citi[citi['trans_date'] > last_paid]
        citi = citi[~citi['Description'].str.contains('PAYMENT, THANK YOU')]
        mint = mint[mint['trans_date'] > mint_analysis]

        # CREATE AMT FIELDS
        chase['amt'] = chase['Amount'] * -1
        citi.loc[(citi['Debit'].notnull()), 'amt'] = citi['Debit']
        citi.loc[(citi['Credit'].notnull()), 'amt'] = citi['Credit']
        mint.loc[(mint['Transaction Type'] == 'debit'), 'amt'] = mint['Amount']
        mint.loc[(mint['Transaction Type'] == 'credit'), 'amt'] = mint['Amount'] * -1

        # CREATE NEW SELF DATAFRAMES
        self.chase = chase[['trans_date', 'amt', 'Description']]
        self.citi = citi[['trans_date', 'amt', 'Description']]
        self.mint = mint[['trans_date', 'amt', 'Category', 'Description', 'Original Description']]
