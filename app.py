import streamlit as st
import pandas as pd
import math



import math




# Example usage
cost_items = {
    'gas': 150,
    'groceries': 350,
    'power_washer': 1500,
    'chemicals': 150,
    'insurance': 100,
    'storage': 150,
    'surface_cleaner_attachment': 150,
    'x_jet_chem_applier': 160,
    'ladder': 300,
    'gutter_wand': 80,
    'uniforms': 120,
    'gloves': 50,
    'shoes': 200,
    'hose': 120,
    'laptop': 2200,

    'rent': 2300,
 
}
   # 'van': 15000,
    # 'car': 5000,

include_in_calculation = {
    'gas': (True, 'Monthly'),
    'groceries': (True, 'Monthly'),
    'power_washer': (True, 'Single'),
    'chemicals': (True, 'Monthly'),
    'insurance': (True, 'Monthly'),
    'storage': (True, 'Single'),
    'surface_cleaner_attachment': (True, 'Single'),
    'x_jet_chem_applier': (True, 'Single'),
    'ladder': (True, 'Single'),
    'gutter_wand': (True, 'Single'),
    'uniforms': (True, 'Single'),
    'gloves': (True, 'Single'),
    'shoes': (True, 'Single'),
    'hose': (True, 'Single'),
    'laptop': (True, 'Single'),
  
    'rent': (True, 'Monthly'),
   
}
 #  'car': (True, 'Single'),
 # 'van': (True, 'Single'),


def print_financial_report(total_cost_to_break, total_revenue, gigs_needed, gig_shortfall, covered_expenses, months, monthly_costs, monthly_shortfall, monthly_revenue_details, doors_hit_per_month, remaining_revenue_each_month):
    report = []
    covered_single_items = set()  # Set to keep track of covered single items

    report.append("### Executive Financial Summary")
    report.append(f"* Total cost to break even over {months} months: **${total_cost_to_break:,.2f}**")
    report.append(f"* Total projected revenue for {months} months: **${total_revenue:,.2f}**")
    report.append(f"* Total gigs needed to break even: **{gigs_needed:,}**")
    report.append(f"* Projected shortfall of gigs: **{gig_shortfall:,}** (additional gigs needed)" if gig_shortfall > 0 else "Sufficient gigs projected to meet or exceed break-even requirements.")

    report.append("\n### Detailed Expense Coverage Report")
    cumulative_remaining_revenue = 0
    for month in range(1, months + 1):
        report.append("------------")
        report.append(f"\n#### Month {month}:")
        report.append(f"* Revenue this month: **${monthly_revenue_details[month-1]:,.2f}**")
        report.append(f"* Doors hit this month: **{doors_hit_per_month[month-1]}**")

        for item, cost in monthly_costs.items():
            covered = any(expense[0] == item and expense[2] == month for expense in covered_expenses if expense[3] == 'monthly')
            if covered:
                report.append(f"* Covered monthly '{item}' costing **${cost:,.2f}**")
            else:
                shortfall = monthly_shortfall.get(item, (0, ))[0]
                report.append(f"* Not covered monthly '{item}' (Shortfall: **${shortfall:,.2f}**)")

        for expense in covered_expenses:
            if expense[2] == month and expense[3] == 'single' and expense[0] not in covered_single_items:
                report.append(f"* Covered single '{expense[0]}' costing **${expense[1]:,.2f}**")
                covered_single_items.add(expense[0])  # Mark this item as covered once

        # Track remaining revenue for each month
        remaining_revenue = remaining_revenue_each_month[month - 1]
        cumulative_remaining_revenue += remaining_revenue
        report.append(f"* Remaining revenue after expenses: **${remaining_revenue:,.2f}**")

    report.append("\n### Cumulative Remaining Revenue")
    report.append(f"* Total remaining revenue after all expenses over {months} months: **${cumulative_remaining_revenue:,.2f}**")

    report.append("\n### Analysis & Recommendations")
    report.append("Recommendation: Increase the number of gigs or optimize cost structures to meet financial targets." if gig_shortfall > 0 else "Financial strategy is on track. Maintain current operations and continue monitoring expenses.")

    return "\n".join(report)







import math

class BreakEvenCalculator:
    def __init__(self, cost_items, include_in_calculation, priority_order):
        self.cost_items = cost_items
        self.include_in_calculation = include_in_calculation
        self.priority_order = priority_order
        self.covered_expenses = []  # Track covered expenses
        self.monthly_shortfall = {}  # Track shortfalls
        self.monthly_revenue_details = []  # Revenue per month
        self.doors_hit_per_month = []  # Doors hit per month

    def calculate_monthly_revenue(self, number_of_doors_hit, percentage_of_door_yes, average_price_per_gig):
        number_of_yes = math.ceil((percentage_of_door_yes / 100) * number_of_doors_hit)
        self.doors_hit_per_month.append(number_of_yes)
        return number_of_yes * average_price_per_gig

    def simulate_month(self, month, monthly_revenue, monthly_costs, single_costs):
        covered_this_month = []
        shortfall_this_month = {}
        for item, cost in monthly_costs.items():
            if monthly_revenue >= cost:
                monthly_revenue -= cost
                covered_this_month.append((item, cost, month, 'monthly'))
            else:
                shortfall_this_month[item] = cost - monthly_revenue
                monthly_revenue = 0

        for item in self.priority_order:
            if item in single_costs and monthly_revenue >= single_costs[item] and (item, month) not in self.covered_expenses:
                monthly_revenue -= single_costs[item]
                covered_this_month.append((item, single_costs[item], month, 'single'))

        self.covered_expenses.extend(covered_this_month)
        self.monthly_shortfall[month] = shortfall_this_month
        self.monthly_revenue_details.append(monthly_revenue)
        return monthly_revenue

    def calculate_break_even(self, months, average_price_per_gig, number_of_doors_hit, percentage_of_door_yes):
        monthly_costs = self.calculate_monthly_costs()
        single_costs = self.calculate_single_costs()
        remaining_revenue_each_month = []

        for month in range(1, months + 1):
            monthly_revenue = self.calculate_monthly_revenue(number_of_doors_hit, percentage_of_door_yes, average_price_per_gig)
            remaining_revenue = self.simulate_month(month, monthly_revenue, monthly_costs, single_costs)
            remaining_revenue_each_month.append(remaining_revenue)

        total_cost_to_break = sum(monthly_costs.values()) * months + sum(single_costs.values()) - sum(single_costs[item] for item in set(expense[0] for expense in self.covered_expenses if expense[3] == 'single'))
        gigs_needed = math.ceil(total_cost_to_break / average_price_per_gig)
        total_revenue = average_price_per_gig * sum(self.doors_hit_per_month)
        gig_shortfall = gigs_needed - sum(self.doors_hit_per_month)

        return total_cost_to_break, total_revenue, gigs_needed, gig_shortfall, self.covered_expenses, months, monthly_costs, self.monthly_shortfall, self.monthly_revenue_details, self.doors_hit_per_month, remaining_revenue_each_month




# Sorted priority order by highest cost
priority_order = sorted(
    (item for item in include_in_calculation if include_in_calculation[item][0] and include_in_calculation[item][1] == 'Single'),
    key=lambda item: cost_items[item],
    reverse=True
)




    # # Final financial overview
    # print(f"Total cost to break even: ${total_cost_to_break}")
    # print(f"Total revenue for {months} months: ${monthly_revenue * months}")
    # print(f"You need a total of {gigs_needed} gigs to break even.")
    # print(f"Based on current estimates, you will organize {number_of_yes * months} gigs.")
    # if gig_shortfall > 0:
    #     print(f"You are short by {gig_shortfall} gigs.")

    # # Output covered expenses
    # if covered_expenses:
    #     print("With the total revenue, the following expenses were covered:")
    #     for item, cost, month in covered_expenses:
    #         print(f"- {item} (${cost}) in month {month}")
    # else:
    #     print("The total revenue was not sufficient to cover any of the prioritized expenses.")









def get_single_cost_items(include_in_calculation):
    return [item for item, (included, frequency) in include_in_calculation.items() if included and frequency == 'Single']



import streamlit as st
import math
from your_calculator_module import BreakEvenCalculator  # Adjust the import statement based on your file organization

def calculate_break_even(cost_items, include_in_calculation, priority_order, months, average_price_per_gig, number_of_doors_hit, percentage_of_door_yes):
    calculator = BreakEvenCalculator(cost_items, include_in_calculation, priority_order)
    return calculator.calculate_break_even(months, average_price_per_gig, number_of_doors_hit, percentage_of_door_yes)

def app():
    priority_order = ['gas', 'rent', 'groceries', 'power_washer', 'hose', 'chemicals', 'storage', 'insurance',  'surface_cleaner_attachment', 'x_jet_chem_applier', 'ladder', 'gutter_wand', 'uniforms', 'gloves', 'shoes',  'laptop']
    st.title('Financial Break-Even Analysis Tool')

    # Configuration for cost items
    st.sidebar.header('Cost Items Configuration')
    modified_cost_items = {}
    for idx, (item, cost) in enumerate(cost_items.items()):
        widget_key = f"cost_{item}_{idx}"  # Ensure unique widget keys
        modified_cost_items[item] = st.sidebar.number_input(f'Cost for {item}', value=cost, min_value=0, key=widget_key)

    # Configuration for priority order
    st.sidebar.header('Adjust Priority Order')
    all_items = list(modified_cost_items.keys())
    valid_priority_order = [item for item in priority_order if item in all_items]  # Validate default values
    selected_priority_order = st.sidebar.multiselect('Set Priority Order (top to bottom):', options=all_items, default=valid_priority_order)

    # Main configuration inputs
    month_scope = st.number_input('Months Scope', value=12, min_value=1)
    doors = st.number_input('Number of Doors Hit', value=300, min_value=1)
    yield_percent = st.number_input('Yield Percent', value=13, min_value=0, max_value=100)
    estimated_average_price_per_gig = st.number_input('Estimated Average Price per Gig', value=300, min_value=0)

    # Calculate doors yielded
    doors_yielded = math.ceil(doors * (yield_percent / 100))
    st.write(f'Number of doors yielded: {doors_yielded}')  # Displaying the number of doors that yielded

    if st.button('Calculate Break Even'):
        results = calculate_break_even(modified_cost_items, include_in_calculation, selected_priority_order, month_scope, estimated_average_price_per_gig, doors, yield_percent)
        total_cost_to_break, total_revenue, gigs_needed, gig_shortfall, covered_expenses, months, monthly_costs, monthly_shortfall, monthly_revenue_details, doors_hit_per_month, remaining_revenue_each_month = results
        report = print_financial_report(total_cost_to_break, total_revenue, gigs_needed, gig_shortfall, covered_expenses, months, monthly_costs, monthly_shortfall, monthly_revenue_details, doors_hit_per_month, remaining_revenue_each_month)
        st.markdown(report, unsafe_allow_html=True)
        # Verify clients count
        st.write(f"Based on the calculations, you will have {doors_yielded * month_scope} clients over {month_scope} months.")

    # Display history of runs
    if 'history' in st.session_state and st.session_state['history']:
        run = st.selectbox('Select a run to view results:', range(len(st.session_state['history'])), format_func=lambda x: f"Run {x + 1}")
        st.json(st.session_state['history'][run])  # Display the results as JSON for clarity

if __name__ == "__main__":
    app()



