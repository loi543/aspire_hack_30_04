from models import Goal 


holiday_goal = Goal(800, 5, 'Family Holiday')

for row in dataset:
    holiday_goal.contribute(row)
    holiday_goal.indiv_contribution(row)
