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
    'car': 5000,
    'rent': 2300,
    'van': 15000,
}

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
    'car': (True, 'Single'),
    'rent': (True, 'Monthly'),
    'van': (True, 'Single'),
}



def print_financial_report(total_cost_to_break, total_revenue, gigs_needed, gig_shortfall, covered_expenses, months, monthly_costs, monthly_shortfall):
    report = []

    report.append("### Executive Financial Summary")
    report.append(f"* Total cost to break even over {months} months: **${total_cost_to_break:,.2f}**")
    report.append(f"* Total projected revenue for {months} months: **${total_revenue:,.2f}**")
    report.append(f"* Total gigs needed to break even: **{gigs_needed:,}**")
    report.append(f"* Projected shortfall of gigs: **{gig_shortfall:,}** (additional gigs needed)" if gig_shortfall > 0 else "Sufficient gigs projected to meet or exceed break-even requirements.")

    report.append("\n### Detailed Expense Coverage Report")
    last_month = 0
    for month in range(1, months + 1):
        if month != last_month:
            report.append("------------")
            report.append(f"\n#### Month {month}:")
            last_month = month

        for item, cost in monthly_costs.items():
            covered = any(expense[0] == item and expense[2] == month for expense in covered_expenses if expense[3] == 'monthly')
            if covered:
                report.append(f"* Covered monthly '{item}' costing **${cost:,.2f}**")
            else:
                shortfall = monthly_shortfall.get(item, (0, ))[0]
                report.append(f"* Not covered monthly '{item}' (Shortfall: **${shortfall:,.2f}**)")

        for expense in covered_expenses:
            if expense[2] == month and expense[3] == 'single':
                report.append(f"* Covered single '{expense[0]}' costing **${expense[1]:,.2f}**")

    report.append("\n### Analysis & Recommendations")
    report.append("Recommendation: Increase the number of gigs or optimize cost structures to meet financial targets." if gig_shortfall > 0 else "Financial strategy is on track. Maintain current operations and continue monitoring expenses.")

    return "\n".join(report)




def calculate_break_even(cost_items, include_in_calculation, priority_order, months=1, average_price_per_gig=300, number_of_doors_hit=120, percentage_of_door_yes=13):
    try:
        monthly_costs = {item: cost_items[item] for item, (included, frequency) in include_in_calculation.items() if included and frequency == 'Monthly'}
        single_costs = {item: cost_items[item] for item in priority_order if item in cost_items and include_in_calculation[item][0] and include_in_calculation[item][1] == 'Single'}

        number_of_yes = math.ceil((percentage_of_door_yes / 100) * number_of_doors_hit)
        monthly_revenue = number_of_yes * average_price_per_gig

        total_monthly_costs = sum(monthly_costs.values()) * months
        total_single_costs = sum(single_costs.values())
        total_cost_to_break = total_monthly_costs + total_single_costs

        remaining_revenue = 0
        covered_expenses = []
        monthly_shortfall = {}

        for month in range(1, months + 1):
            current_month_revenue = monthly_revenue + remaining_revenue

            for item, cost in monthly_costs.items():
                if current_month_revenue >= cost:
                    covered_expenses.append((item, cost, month, 'monthly'))
                    current_month_revenue -= cost
                else:
                    shortfall = cost - current_month_revenue
                    monthly_shortfall[item] = (shortfall, month)
                    current_month_revenue = 0  # Allocate all remaining revenue to this cost

            if not monthly_shortfall and current_month_revenue > 0:
                for item in priority_order:
                    if item in single_costs and current_month_revenue >= single_costs[item]:
                        covered_expenses.append((item, single_costs[item], month, 'single'))
                        current_month_revenue -= single_costs[item]

            remaining_revenue = current_month_revenue

        gigs_needed = math.ceil(total_cost_to_break / average_price_per_gig)
        gig_shortfall = gigs_needed - number_of_yes * months

        return total_cost_to_break, monthly_revenue, gigs_needed, gig_shortfall, covered_expenses, months, monthly_costs, monthly_shortfall
    except Exception as e:
        st.error(f"Failed to calculate: {str(e)}")
        return 0, 0, 0, 0, [], months, {}, {}



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



def app():
    priority_order = ['gas', 'rent', 'groceries', 'power_washer', 'hose','chemicals','storage','insurance',  'surface_cleaner_attachment', 'x_jet_chem_applier', 'ladder', 'gutter_wand', 'uniforms', 'gloves', 'shoes',  'laptop', 'car', 'van']

    st.title('Financial Break-Even Analysis Tool')

    # Configuration for cost items
    st.sidebar.header('Cost Items Configuration')
    modified_cost_items = {}
    for item, cost in cost_items.items():
        modified_cost_items[item] = st.sidebar.number_input(f'Cost for {item}', value=cost, min_value=0)

    # Configuration for priority order
    st.sidebar.header('Adjust Priority Order')
    all_items = list(modified_cost_items.keys())
    selected_priority_order = st.sidebar.multiselect('Set Priority Order (top to bottom):', options=all_items, default=priority_order)

    # Main configuration inputs
    month_scope = st.number_input('Months Scope', value=12, min_value=1)
    doors = st.number_input('Number of Doors Hit', value=300, min_value=1)
    yield_percent = st.number_input('Yield Percent', value=13, min_value=0, max_value=100)
    estimated_average_price_per_gig = st.number_input('Estimated Average Price per Gig', value=300, min_value=0)

    if st.button('Calculate Break Even'):
        results = calculate_break_even(modified_cost_items, include_in_calculation, selected_priority_order, month_scope, estimated_average_price_per_gig, doors, yield_percent)
        if results:
            report = print_financial_report(*results)
            st.markdown(report, unsafe_allow_html=True)
        else:
            st.error("Error in calculation.")


    # Display history of runs
    if 'history' in st.session_state and st.session_state['history']:
        run = st.selectbox('Select a run to view results:', range(len(st.session_state['history'])), format_func=lambda x: f"Run {x + 1}")
        st.json(st.session_state['history'][run])  # Display the results as JSON for clarity

if __name__ == "__main__":
    app()