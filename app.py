import streamlit as st
import json
import math
import math

class BreakEvenCalculator:
    def __init__(self, cost_items, include_in_calculation, priority_order, months=12, average_price_per_gig=300, number_of_doors_hit=120, percentage_of_door_yes=13, monthly_growth_rate=0.0):
        self.cost_items = cost_items
        self.include_in_calculation = include_in_calculation
        self.priority_order = priority_order
        self.months = months
        self.average_price_per_gig = average_price_per_gig
        self.number_of_doors_hit = number_of_doors_hit
        self.percentage_of_door_yes = percentage_of_door_yes
        self.monthly_growth_rate = monthly_growth_rate / 100  # Convert percentage to decimal
        self.initialize_costs()

    def initialize_costs(self):
        self.monthly_costs = {item: self.cost_items[item] for item, (included, frequency) in self.include_in_calculation.items() if included and frequency == 'Monthly'}
        self.single_costs = {item: self.cost_items[item] for item in self.priority_order if item in self.cost_items and self.include_in_calculation[item][0] and self.include_in_calculation[item][1] == 'Single'}
        self.covered_single_costs = set()

    def calculate_revenue(self):
        revenues = []
        gigs_per_month = []
        current_doors_hit = self.number_of_doors_hit
    
        for month in range(1, self.months + 1):
            number_of_yes = math.ceil((self.percentage_of_door_yes / 100) * current_doors_hit)
            monthly_revenue = number_of_yes * self.average_price_per_gig
            revenues.append(monthly_revenue)
            gigs_per_month.append(number_of_yes)
    
            # Update the number of doors hit for the next month
            current_doors_hit *= (1 + self.monthly_growth_rate)  # Increase by the growth rate
            current_doors_hit = math.ceil(current_doors_hit)  # Round to the nearest whole number
            
            # Apply the growth rate directly to the number of gigs (number_of_yes)
            if month < self.months:  # Only apply growth if there are more months to process
                number_of_yes = math.ceil(number_of_yes * (1 + self.monthly_growth_rate))
        
        return revenues, gigs_per_month
    



    def calculate_costs_and_coverage(self):
        total_monthly_costs = sum(self.monthly_costs.values()) * self.months
        total_single_costs = sum([cost for item, cost in self.single_costs.items() if item not in self.covered_single_costs])
        total_cost_to_break = total_monthly_costs + total_single_costs
        
        monthly_revenues, gigs_per_month_list = self.calculate_revenue()
        remaining_revenue = 0
        covered_expenses = []
        monthly_coverages = {month: [] for month in range(1, self.months + 1)}
        rolled_over_deficits = 0
        
        for month in range(1, self.months + 1):
            monthly_revenue = monthly_revenues[month - 1]
            current_month_revenue = monthly_revenue + remaining_revenue - rolled_over_deficits

            # Handle monthly recurring costs
            monthly_cost_total = 0  # Track total monthly costs for the current month
            for item, cost in self.monthly_costs.items():
                monthly_cost_total += cost
                if current_month_revenue >= cost:
                    covered_expenses.append((item, cost, month, 'monthly'))
                    monthly_coverages[month].append((item, cost, 'monthly'))
                    current_month_revenue -= cost
                else:
                    # Not enough revenue to cover this cost
                    deficit = cost - current_month_revenue
                    current_month_revenue = 0  # Update to zero since we're in deficit
                    monthly_coverages[month].append((item, cost - deficit, 'monthly (partial)'))
                    rolled_over_deficits += deficit  # Add remaining cost to the rolled over deficits
    
            # Handle single costs according to priority, but only if all monthly costs are fully paid
            if rolled_over_deficits == 0:
                for item in self.priority_order:
                    if item in self.single_costs and item not in self.covered_single_costs:
                        cost = self.single_costs[item]
                        if current_month_revenue >= cost:
                            covered_expenses.append((item, cost, month, 'single'))
                            monthly_coverages[month].append((item, cost, 'single'))
                            current_month_revenue -= cost
                            self.covered_single_costs.add(item)
                        else:
                            # Not enough revenue to cover single cost
                            monthly_coverages[month].append((item, 0, 'single (not covered)'))
                            break  # Stop attempting to cover single costs
    
            # Record remaining revenue for the month
            monthly_coverages[month].append(('Remaining Revenue', current_month_revenue))
            remaining_revenue = current_month_revenue  # Remaining revenue for the next month
            rolled_over_deficits = 0  # Reset deficits for the next month
    
        gigs_needed = math.ceil(total_cost_to_break / self.average_price_per_gig)
        total_gigs = sum(gigs_per_month_list)
        gig_shortfall = gigs_needed - total_gigs
    
        return total_cost_to_break, sum(monthly_revenues), gigs_needed, gig_shortfall, covered_expenses, monthly_coverages, gigs_per_month_list

    def get_financial_report(self):
        report = []
        total_cost_to_break, total_revenue, gigs_needed, gig_shortfall, covered_expenses, monthly_coverages, gigs_per_month_list = self.calculate_costs_and_coverage()
    
        # Format numbers with commas
        report.append(f"Total Cost to Break Even: {total_cost_to_break:,.2f}")
        report.append(f"Total Revenue: {total_revenue:,.2f}")
        report.append(f"Gigs Needed: {gigs_needed:,}")
        report.append(f"Gig Shortfall: {gig_shortfall:,}\n")
    
        monthly_revenues, _ = self.calculate_revenue()  # Fetch monthly revenues directly from the revenue calculation method
        previous_revenue_rollover = 0
        for month in sorted(monthly_coverages):
            revenue_for_month = monthly_revenues[month-1]  # Get revenue for the current month, adjusted for zero-index
            gigs_this_month = gigs_per_month_list[month-1]  # Correctly fetch the gigs for the current month
            
            report.append("----------")
            report.append(f"\nMonth {month}")
            report.append(f"Revenue This Month: {revenue_for_month:,.2f}")  # Properly formatted float
            report.append(f"Rollover Addition: {previous_revenue_rollover:,.2f}")
            report.append(f"Revenue to Work with: {revenue_for_month + previous_revenue_rollover:,.2f}\n")
            
            report.append(f"Number of Gigs this Month: {gigs_this_month:,}")  # Display gigs correctly
    
            total_monthly = 0
            total_single = 0
            for entry in monthly_coverages[month]:
                if len(entry) == 3:
                    item, cost, type = entry
                    if type == 'monthly':
                        total_monthly += cost
                    elif type == 'single':
                        total_single += cost
                    report.append(f"\t - {item} (${cost:,.2f}), {type}")
                elif len(entry) == 2:
                    item, value = entry
                    if item == 'Remaining Revenue':
                        previous_revenue_rollover = value
                        report.append('\n')
                        report.append(f"{item}: ${value:,.2f}")
    
            report.append(f"\nTotal Costs Covered: ${total_monthly + total_single:,.2f}")
            report.append(f"\tTotal Monthly Costs Covered: ${total_monthly:,.2f}")
            report.append(f"\tTotal Single Costs Covered: ${total_single:,.2f}")
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

priority_order = ['power_washer', 'hose', 'chemicals', 'storage', 'surface_cleaner_attachment', 'x_jet_chem_applier', 'ladder', 'gutter_wand', 'uniforms', 'gloves', 'shoes', 'laptop']



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


monthly_growth_rate = st.slider("Monthly growth rate (%):", min_value=0, max_value=50, value=0, step=1)
monthly_growth_rate /= 100.0  # Convert percentage to decimal
# Initialize the calculator with the user input
calculator = BreakEvenCalculator(cost_items, include_in_calculation, priority_order, months, average_price_per_gig, number_of_doors_hit, percentage_of_door_yes, monthly_growth_rate)



# Display the financial report in a text box
if st.button('Calculate Break-Even'):
    report = calculator.get_financial_report()
    st.text_area("Financial Report", value=report, height=1000)
