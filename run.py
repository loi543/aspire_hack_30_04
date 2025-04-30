from models import Goal 
import pandas as pd

dataset = pd.read_csv("simulated family savings contributions.csv")
members_list = ['Frank', 'Nancy', 'Mark', 'Abigail']
holiday_goal = Goal(800, 5, 'Family Holiday', members_list)

for index, row in dataset.iterrows():
    print(row)
    holiday_goal.contribute(row)
    holiday_goal.indiv_contribution(row)

