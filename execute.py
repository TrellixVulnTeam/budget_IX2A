from budget import Budget

budget = Budget()
budget.read_config()
last_paid = budget.last_paid
mint_analysis = budget.mint_analysis
budget.read_csv(last_paid=last_paid, mint_analysis=mint_analysis)

print(budget.chase)
print(budget.income_bk)
