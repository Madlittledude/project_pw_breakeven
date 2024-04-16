import streamlit as st
import json
import math
import math

class BreakEvenCalculator:
    def __init__(self, cost_items, include_in_calculation, priority_order, months=12, average_price_per_gig=300, number_of_doors_hit=120, percentage_of_door_yes=13):
        self.cost_items = cost_items
        self.include_in_calculation = include_in_calculation
        self.priority_order = priority_order
        self.months = months
        self.average_price_per_gig = average_price_per_gig
        self.number_of_doors_hit = number_of_doors_hit
        self.percentage_of_door_yes = percentage_of_door_yes
        self.initialize_costs()

    def initialize_costs(self):
        self.monthly_costs = {item: self.cost_items[item] for item, (included, frequency) in self.include_in_calculation.items() if included and frequency == 'Monthly'}
        self.single_costs = {item: self.cost_items[item] for item in self.priority_order if item in self.cost_items and self.include_in_calculation[item][0] and self.include_in_calculation[item][1] == 'Single'}
        self.covered_single_costs = set()

    def calculate_revenue(self):
        number_of_yes = math.ceil((self.percentage_of_door_yes / 100) * self.number_of_doors_hit)
        monthly_revenue = number_of_yes * self.average_price_per_gig
        return monthly_revenue, number_of_yes

    def calculate_costs_and_coverage(self):
        total_monthly_costs = sum(self.monthly_costs.values()) * self.months
        total_single_costs = sum([cost for item, cost in self.single_costs.items() if item not in self.covered_single_costs])
        total_cost_to_break = total_monthly_costs + total_single_costs

        monthly_revenue, gigs_per_month = self.calculate_revenue()
        remaining_revenue = 0
        covered_expenses = []
        monthly_coverages = {month: [] for month in range(1, self.months + 1)}

        for month in range(1, self.months + 1):
            current_month_revenue = monthly_revenue + remaining_revenue
            for item, cost in self.monthly_costs.items():
                if current_month_revenue >= cost:
                    covered_expenses.append((item, cost, month, 'monthly'))
                    monthly_coverages[month].append((item, cost, 'monthly'))
                    current_month_revenue -= cost

            for item in self.priority_order:
                if item in self.single_costs and item not in self.covered_single_costs:
                    if current_month_revenue >= self.single_costs[item]:
                        covered_expenses.append((item, self.single_costs[item], month, 'single'))
                        monthly_coverages[month].append((item, self.single_costs[item], 'single'))
                        current_month_revenue -= self.single_costs[item]
                        self.covered_single_costs.add(item)

            monthly_coverages[month].append(('Remaining Revenue', current_month_revenue))
            remaining_revenue = current_month_revenue

        gigs_needed = math.ceil(total_cost_to_break / self.average_price_per_gig)
        gig_shortfall = gigs_needed - gigs_per_month * self.months

        return total_cost_to_break, monthly_revenue * self.months, gigs_needed, gig_shortfall, covered_expenses, monthly_coverages, gigs_per_month
    
    def get_financial_report(self):
        report = []
        total_cost_to_break, total_revenue, gigs_needed, gig_shortfall, covered_expenses, monthly_coverages, gigs_per_month = self.calculate_costs_and_coverage()
    
        report.append(f"Total Cost to Break Even: {total_cost_to_break}")
        report.append(f"Total Revenue: {total_revenue}")
        report.append(f"Gigs Needed: {gigs_needed}")
        report.append(f"Gig Shortfall: {gig_shortfall}\n")
    
        previous_revenue_rollover = 0
        for month in sorted(monthly_coverages):
            revenue_for_month = self.calculate_revenue()[0]
            report.append("----------")
            report.append(f"\nMonth {month}")
            report.append(f"Revenue This Month: {revenue_for_month}")
            report.append(f"Rollover Addition: {previous_revenue_rollover}")
            report.append(f"Revenue to Work with: {revenue_for_month + previous_revenue_rollover}\n")
            report.append(f"Number of Gigs this Month: {gigs_per_month}")
            total_monthly = 0
            total_single = 0
            for entry in monthly_coverages[month]:
                if len(entry) == 3:
                    item, cost, type = entry
                    if type == 'monthly':
                        total_monthly += cost
                    elif type == 'single':
                        total_single += cost
                    report.append(f"\t - {item} (${cost}), {type}")
                elif len(entry) == 2:
                    item, value = entry
                    if item == 'Remaining Revenue':
                        previous_revenue_rollover = value
                        report.append(f"{item}: ${value}")
    
            report.append(f"\nTotal Costs Covered: ${total_monthly + total_single}")
            report.append(f"\tTotal Monthly Costs Covered: ${total_monthly}")
            report.append(f"\tTotal Single Costs Covered: ${total_single}")
            report.append("----------")
    
        return "\n".join(report)




# Example usage:
cost_items = {
    'gas': 150, 'groceries': 350, 'power_washer': 1500, 'chemicals': 150, 'insurance': 100,
    'storage': 150, 'surface_cleaner_attachment': 150, 'x_jet_chem_applier': 160, 'ladder': 300,
    'gutter_wand': 80, 'uniforms': 120, 'gloves': 50, 'shoes': 200, 'hose': 120,
    'laptop': 2200,  'rent': 2300, 
}

include_in_calculation = {
    'gas': (True, 'Monthly'), 'groceries': (True, 'Monthly'), 'power_washer': (True, 'Single'),
    'chemicals': (True, 'Monthly'), 'insurance': (True, 'Monthly'), 'storage': (True, 'Single'),
    'surface_cleaner_attachment': (True, 'Single'), 'x_jet_chem_applier': (True, 'Single'),
    'ladder': (True, 'Single'), 'gutter_wand': (True, 'Single'), 'uniforms': (True, 'Single'),
    'gloves': (True, 'Single'), 'shoes': (True, 'Single'), 'hose': (True, 'Single'),
    'laptop': (True, 'Single'), 'rent': (True, 'Monthly'),
}

priority_order = ['gas', 'rent', 'groceries', 'power_washer', 'hose', 'chemicals', 'storage', 'insurance', 'surface_cleaner_attachment', 'x_jet_chem_applier', 'ladder', 'gutter_wand', 'uniforms', 'gloves', 'shoes', 'laptop']



# Streamlit application start
st.title('Break-Even Calculator App')

# User inputs for the calculator parameters
months = st.slider("Select number of months:", min_value=1, max_value=24, value=12)
average_price_per_gig = st.slider("Average price per gig ($):", min_value=100, max_value=1000, value=300)
number_of_doors_hit = st.slider("Number of doors to hit:", min_value=50, max_value=500, value=120)
percentage_of_door_yes = st.slider("Percentage of door yes (%):", min_value=1, max_value=100, value=13)

# JSON input for costs and inclusion in calculation
cost_items_input = st.text_area("Enter cost items in JSON format:", value=json.dumps(cost_items, indent=4))
include_in_calculation_input = st.text_area("Enter items to include in calculation in JSON format:", value=json.dumps(include_in_calculation, indent=4))

# Convert JSON input to Python dictionary
cost_items = json.loads(cost_items_input)
include_in_calculation = json.loads(include_in_calculation_input)

# Initialize the calculator with the user input
calculator = BreakEvenCalculator(cost_items, include_in_calculation, priority_order, months, average_price_per_gig, number_of_doors_hit, percentage_of_door_yes)


# Display the financial report in a text box
if st.button('Calculate Break-Even'):
    report = calculator.get_financial_report()
    st.text_area("Financial Report", value=report, height=1000)
