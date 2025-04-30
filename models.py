class Goal:
    def __init__(self, target, target_months, goal_name, members_list):
        self.target_date = target_months
        self.target = target
        self.goal_name = goal_name
        self.curr_amt = 0 
        self.members_list = members_list
        self.indiv_cotri_dict = {}
        indiv_monthly_targets = target/(len(members_list)*target_months)
        self.indiv_targets = {}

        for member in self.members_list:
            self.indiv_targets[member] = indiv_monthly_targets
    
    def get_remaining_goal(self):
        return self.target - self.curr_amt
    
    def get_individual_contributions(self):
        return self.indiv_cotri_dict

    def set_indiv_targets(self, name, target_amount):
        self.indiv_targets[name] = target_amount

    def contribute(self, row):
        self.curr_amt += row['amount']

    def indiv_contribution(self, row):
        if row['name'] in self.indiv_cotri_dict:
            self.indiv_cotri_dict[row['name']] += row['amount']
        else: 
            self.indiv_cotri_dict[row['name']] = row['amount']

    
        
    



    
