import configparser
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from fractions import Fraction
import sys

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

    def analyze_budget(self, mint, mint_analysis):
        # READ CATEGORIES FILE AND SORT
        categories = pd.read_excel('budget_categories.xlsx', sheet_name='main', engine='openpyxl')
        categories.sort_values(by=['sort1', 'sort2', 'sort3'], inplace=True)
        categories.reset_index(drop=True, inplace=True)

        # SUM UP MINT DF FOR LATER USE
        mint = mint.groupby(by=['Category']).sum()

        # MERGE CATEGORIES AND MODIFIED MINT
        budget_temp = categories.merge(mint, how='left', left_on='category', right_on='Category')
        months_mint = ((datetime.today() - mint_analysis).days)/(365.25/12)

        # CREATE TEMPORARY AMT FIELDS FOR LATER ANALYSIS
        budget_temp['amt'] = round(budget_temp['amt']/months_mint, 2)
        budget_temp['amt2'] = budget_temp.groupby(['sub_group'])['amt'].transform('sum')
        budget_temp['amt3'] = budget_temp.groupby(['group'])['amt'].transform('sum')
        budget_temp.sort_values(by=['sort1', 'sort2', 'sort3'], inplace=True)

        # ANALYZE BUDGET WITH THIS LOOP
        # MAYBE MAKE IT MORE EFFICIENT IN THE FUTURE
        budget_analysis = pd.DataFrame(columns=['category', 'amt'])
        prev_group = ''
        prev_sub = ''
        prev_cat = ''
        count = 0
        for index, row in budget_temp.iterrows():
            next_value = budget_temp.loc[index, 'group']
            if next_value == prev_group or not budget_temp.loc[index, 'show_group']:
                pass
            else:
                budget_analysis.loc[count, 'category'] = next_value
                budget_analysis.loc[count, 'amt'] = budget_temp.loc[index, 'amt3']
                prev_group = next_value
                count += 1
            next_value = budget_temp.loc[index, 'sub_group']
            if (
                next_value == prev_group or next_value == prev_sub
                or not budget_temp.loc[index, 'show_sub']
            ):
                pass
            else:
                budget_analysis.loc[count, 'category'] = next_value
                budget_analysis.loc[count, 'amt'] = budget_temp.loc[index, 'amt2']
                prev_sub = next_value
                count += 1
            next_value = budget_temp.loc[index, 'category']
            if (
                next_value == prev_group or next_value == prev_sub or next_value == prev_cat
                or not budget_temp.loc[index, 'show_cat']
            ):
                pass
            else:
                budget_analysis.loc[count, 'category'] = next_value
                budget_analysis.loc[count, 'amt'] = budget_temp.loc[index, 'amt']
                prev_cat = next_value
                count += 1

        # SELF VALUE
        self.budget_analysis = budget_analysis

    def generate_bill(self):
        # READ BILLS CSV AND CONVERT RECUR_DATE TO DATETIME
        bills = pd.read_csv('bills.csv')
        bills['recur_date'] = pd.to_datetime(bills['recur_date'])

        # MAKE SURE RECUR_DATE IS UP-TO-DATE
        for index, row in bills.iterrows():
            recur = bills.loc[index, 'recurrence']
            recur_date = bills.loc[index, 'recur_date']
            if recur == 'bi-weekly':
                temp_schedule = rrule(WEEKLY, dtstart=recur_date, count=52, interval=2)
            elif recur == 'monthly':
                temp_schedule = rrule(MONTHLY, dtstart=recur_date, count=24, interval=1)
            elif recur == 'yearly':
                temp_schedule = rrule(MONTHLY, dtstart=recur_date, count=4, interval=12)
            else:
                sys.exit('Recurrance type not defined')
            for each in temp_schedule:
                if each.date() >= (datetime.now() - timedelta(days=7)).date():
                    bills.loc[index, 'recur_date'] = each.date()
                    break
                else:
                    pass

        # UDPATE FILE
        bills.to_csv('bills.csv', index=False)

        # GENERATE EMPTY BILL SCHEDULE
        last_next_28 = rrule(
            DAILY, dtstart=(datetime.now() - timedelta(days=7)).date(), count=28, interval=1
        )
        last_7_df = pd.DataFrame(columns=['date', 'charges', 'amt'])
        next_21_df = pd.DataFrame(columns=['date', 'charges', 'amt'])
        for index, each in enumerate(last_next_28):
            if index <= 6:
                last_7_df.loc[index, 'date'] = each
                last_7_df.loc[index, 'charges'] = '|'
                last_7_df.loc[index, 'amt'] = 0
            else:
                next_21_df.loc[index - 7, 'date'] = each
                next_21_df.loc[index - 7, 'charges'] = '|'
                next_21_df.loc[index - 7, 'amt'] = 0
