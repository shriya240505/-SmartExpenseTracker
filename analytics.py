
def calculate_total(expenses):
    """Calculate the total amount spent."""
    return sum(expense["amount"] for expense in expenses)


def category_summary(expenses):
    """Calculate total spending for each category."""
    summary = {}

    for expense in expenses:
        category = expense["category"].strip().title()
        amount = expense["amount"]

        if category in summary:
            summary[category] += amount
        else:
            summary[category] = amount

    return summary
