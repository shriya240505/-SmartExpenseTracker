
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



from database import (
    add_expense,
    get_expenses,
    initialize_database,
    update_expense,
    delete_expense,
    set_monthly_budget,
    get_monthly_budget,
    get_monthly_expense_total
)


from analytics import calculate_total, category_summary


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Expense Tracker")
app.geometry("750x950")
app.resizable(True, True)
initialize_database()


def clear_fields():
    date_entry.delete(0, "end")
    category_entry.delete(0, "end")
    amount_entry.delete(0, "end")
    description_entry.delete(0, "end")


from datetime import date


def refresh_budget_status():
    current_month = date.today().strftime("%Y-%m")

    budget = get_monthly_budget(current_month)
    spent = get_monthly_expense_total(current_month)

    if budget is None:
        budget_status.configure(
            text=(
                f"Month: {current_month}\n"
                f"Total spent: ₹{spent:.2f}\n"
                "Set a budget to track your spending."
            )
        )
        return

    remaining = budget - spent
    usage = (spent / budget) * 100

    if usage >= 100:
        alert = "\n⚠️ Monthly budget exceeded!"
    elif usage >= 80:
        alert = "\n⚠️ You have used at least 80% of your budget."
    else:
        alert = ""

    budget_status.configure(
        text=(
            f"Month: {current_month}\n"
            f"Monthly Budget: ₹{budget:.2f}\n"
            f"Total Spent: ₹{spent:.2f}\n"
            f"Remaining: ₹{remaining:.2f}\n"
            f"Budget Used: {usage:.1f}%"
            f"{alert}"
        )
    )


def save_budget():
    current_month = date.today().strftime("%Y-%m")
    amount_text = budget_entry.get().strip()

    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Budget",
            "Please enter a valid budget greater than zero.",
            parent=app
        )
        return

    set_monthly_budget(current_month, amount)

    messagebox.showinfo(
        "Success",
        f"Monthly budget set to ₹{amount:.2f}.",
        parent=app
    )

    budget_entry.delete(0, "end")
    refresh_budget_status()


def add_new_expense():
    date = date_entry.get().strip()
    category = category_entry.get().strip()
    amount_text = amount_entry.get().strip()
    description = description_entry.get().strip()

    if not date or not category or not amount_text:
        messagebox.showerror(
            "Missing Information",
            "Please enter date, category and amount."
        )
        return

    try:
        amount = float(amount_text)

        if amount <= 0:
            messagebox.showerror(
                "Invalid Amount",
                "Amount must be greater than zero."
            )
            return

    except ValueError:
        messagebox.showerror(
            "Invalid Amount",
            "Please enter a valid numeric amount."
        )
        return

    add_expense(date, category, amount, description)

    messagebox.showinfo("Success", "Expense added successfully!")
    clear_fields()
    refresh_budget_status()



def view_all_expenses():
    expenses = get_expenses()

    if not expenses:
        messagebox.showinfo("Expenses", "No expenses found.")
        return

    window = ctk.CTkToplevel(app)
    window.title("Manage Expenses")
    window.geometry("750x550")

    heading = ctk.CTkLabel(
        window,
        text="Manage Your Expenses",
        font=("Arial", 22, "bold")
    )
    heading.pack(pady=15)

    
    # Search and filter controls
    filter_frame = ctk.CTkFrame(window)
    filter_frame.pack(fill="x", padx=15, pady=8)

    search_entry = ctk.CTkEntry(
        filter_frame,
        placeholder_text="Search category or description...",
        width=260
    )
    search_entry.grid(row=0, column=0, padx=8, pady=8)

    category_options = sorted({
        expense["category"].strip().title()
        for expense in expenses
        if expense["category"].strip()
    })

    category_menu = ctk.CTkOptionMenu(
        filter_frame,
        values=["All Categories"] + category_options,
        width=170
    )
    category_menu.grid(row=0, column=1, padx=8, pady=8)

    date_entry = ctk.CTkEntry(
        filter_frame,
        placeholder_text="Date (DD-MM-YYYY)",
        width=170
    )
    date_entry.grid(row=1, column=0, padx=8, pady=8)

    scroll_frame = ctk.CTkScrollableFrame(
        window,
        width=690,
        height=340
    )
    scroll_frame.pack(padx=15, pady=8, fill="both", expand=True)


    def refresh_expenses():
        window.destroy()
        view_all_expenses()

    def edit_expense(expense):
        edit_window = ctk.CTkToplevel(window)
        edit_window.title("Edit Expense")
        edit_window.geometry("400x430")
        edit_window.transient(window)
        edit_window.grab_set()

        ctk.CTkLabel(
            edit_window,
            text="Update Expense",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        date_field = ctk.CTkEntry(
            edit_window, width=300, placeholder_text="Date"
        )
        date_field.pack(pady=8)
        date_field.insert(0, expense["date"])

        category_field = ctk.CTkEntry(
            edit_window, width=300, placeholder_text="Category"
        )
        category_field.pack(pady=8)
        category_field.insert(0, expense["category"])

        amount_field = ctk.CTkEntry(
            edit_window, width=300, placeholder_text="Amount"
        )
        amount_field.pack(pady=8)
        amount_field.insert(0, str(expense["amount"]))

        description_field = ctk.CTkEntry(
            edit_window, width=300, placeholder_text="Description"
        )
        description_field.pack(pady=8)
        description_field.insert(0, expense["description"] or "")

        def save_changes():
            date = date_field.get().strip()
            category = category_field.get().strip()
            amount_text = amount_field.get().strip()
            description = description_field.get().strip()

            if not date or not category or not amount_text:
                messagebox.showerror(
                    "Missing Information",
                    "Date, category and amount are required.",
                    parent=edit_window
                )
                return

            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid Amount",
                    "Enter an amount greater than zero.",
                    parent=edit_window
                )
                return

            updated = update_expense(
                expense["id"],
                date,
                category,
                amount,
                description
            )

            if updated:
                messagebox.showinfo(
                    "Success",
                    "Expense updated successfully!",
                    parent=edit_window
                )
                edit_window.destroy()
                refresh_expenses()
                refresh_budget_status()
            else:
                messagebox.showerror(
                    "Error",
                    "Expense could not be found.",
                    parent=edit_window
                )

        ctk.CTkButton(
            edit_window,
            text="Save Changes",
            command=save_changes,
            width=200
        ).pack(pady=15)

    def confirm_delete(expense):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {expense['category']} expense of "
            f"₹{expense['amount']:.2f}?",
            parent=window
        )

        if confirm:
            deleted = delete_expense(expense["id"])

            if deleted:
                messagebox.showinfo(
                    "Success",
                    "Expense deleted successfully!",
                    parent=window
                )
                refresh_expenses()
                refresh_budget_status()
            else:
                messagebox.showerror(
                    "Error",
                    "Expense could not be found.",
                    parent=window
                )

    
    def render_expenses():
        # Clear the currently displayed expense cards
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        search_text = search_entry.get().strip().lower()
        selected_category = category_menu.get()
        selected_date = date_entry.get().strip()

        filtered_expenses = []

        for expense in expenses:
            category = expense["category"].strip().title()
            description = expense["description"] or ""

            # Search by category or description
            if search_text and (
                search_text not in category.lower()
                and search_text not in description.lower()
            ):
                continue

            # Filter by category
            if (
                selected_category != "All Categories"
                and category != selected_category
            ):
                continue

            # Filter by exact date
            if selected_date and expense["date"].strip() != selected_date:
                continue

            filtered_expenses.append(expense)

        if not filtered_expenses:
            ctk.CTkLabel(
                scroll_frame,
                text="No matching expenses found.",
                font=("Arial", 16)
            ).pack(pady=25)
            return

        for expense in filtered_expenses:
            row = ctk.CTkFrame(scroll_frame)
            row.pack(fill="x", padx=5, pady=6)

            details = (
                f"ID: {expense['id']}  |  {expense['date']}  |  "
                f"{expense['category']}  |  "
                f"₹{expense['amount']:.2f}\n"
                f"{expense['description'] or 'No description'}"
            )

            ctk.CTkLabel(
                row,
                text=details,
                justify="left",
                anchor="w",
                wraplength=400
            ).pack(
                side="left",
                padx=10,
                pady=12,
                fill="x",
                expand=True
            )

            ctk.CTkButton(
                row,
                text="Edit",
                width=75,
                command=lambda e=expense: edit_expense(e)
            ).pack(side="left", padx=5, pady=10)

            ctk.CTkButton(
                row,
                text="Delete",
                width=75,
                fg_color="#B22222",
                hover_color="#8B0000",
                command=lambda e=expense: confirm_delete(e)
            ).pack(side="left", padx=5, pady=10)

    def reset_filters():
        search_entry.delete(0, "end")
        category_menu.set("All Categories")
        date_entry.delete(0, "end")
        render_expenses()

    ctk.CTkButton(
        filter_frame,
        text="Search / Apply Filters",
        command=render_expenses,
        width=170
    ).grid(row=1, column=2, padx=8, pady=8)

    ctk.CTkButton(
        filter_frame,
        text="Reset Filters",
        command=reset_filters,
        width=170
    ).grid(row=2, column=0, columnspan=2, padx=8, pady=8)

    render_expenses()



def show_expense_summary():
    expenses = get_expenses()

    if not expenses:
        messagebox.showinfo("Summary", "No expenses found.")
        return

    total = calculate_total(expenses)
    categories = category_summary(expenses)

    summary = f"Total Expenses: ₹{total:.2f}\n\n"
    summary += "Category-wise Spending:\n"

    for category, amount in sorted(categories.items()):
        summary += f"{category}: ₹{amount:.2f}\n"

    messagebox.showinfo("Expense Summary", summary)
    

def open_dashboard():
    dashboard = ctk.CTkToplevel(app)
    dashboard.title("Expense Tracker - Dashboard")
    dashboard.geometry("900x700")
    dashboard.minsize(750, 600)

    dashboard_heading = ctk.CTkLabel(
        dashboard,
        text="Expense Dashboard",
        font=("Arial", 26, "bold")
    )
    dashboard_heading.pack(pady=(20, 15))

    expenses = get_expenses()
    total_spending = calculate_total(expenses)

    current_month = date.today().strftime("%Y-%m")
    monthly_spending = get_monthly_expense_total(current_month)
    monthly_budget = get_monthly_budget(current_month)

    remaining = monthly_budget - monthly_spending
    budget_usage = (
        (monthly_spending / monthly_budget) * 100
        if monthly_budget > 0 else 0
    )

    
    # KPI Cards Section
    kpi_frame = ctk.CTkFrame(
        dashboard,
        fg_color="transparent"
    )
    kpi_frame.pack(fill="x", padx=20, pady=12)

    # Calculate budget values safely
    remaining = monthly_budget - monthly_spending
    budget_usage = (
        (monthly_spending / monthly_budget) * 100
        if monthly_budget > 0 else 0
    )

    # Card 1: Total Expenses
    total_card = ctk.CTkFrame(
        kpi_frame,
        fg_color="#303030",
        corner_radius=12
    )
    total_card.grid(
        row=0, column=0, padx=6, pady=6,
        sticky="nsew"
    )

    ctk.CTkLabel(
        total_card,
        text="Total Expenses",
        text_color="#D1D5DB",
        font=("Arial", 13)
    ).pack(pady=(16, 6))

    ctk.CTkLabel(
        total_card,
        text=f"₹{total_spending:,.2f}",
        text_color="#FFFFFF",
        font=("Arial", 21, "bold")
    ).pack(pady=(0, 16))

    # Card 2: Current Month
    month_card = ctk.CTkFrame(
        kpi_frame,
        fg_color="#303030",
        corner_radius=12
    )
    month_card.grid(
        row=0, column=1, padx=6, pady=6,
        sticky="nsew"
    )

    ctk.CTkLabel(
        month_card,
        text="This Month",
        text_color="#D1D5DB",
        font=("Arial", 13)
    ).pack(pady=(16, 6))

    ctk.CTkLabel(
        month_card,
        text=f"₹{monthly_spending:,.2f}",
        text_color="#FFFFFF",
        font=("Arial", 21, "bold")
    ).pack(pady=(0, 16))

    # Card 3: Budget Remaining
    remaining_card = ctk.CTkFrame(
        kpi_frame,
        fg_color="#303030",
        corner_radius=12
    )
    remaining_card.grid(
        row=0, column=2, padx=6, pady=6,
        sticky="nsew"
    )

    ctk.CTkLabel(
        remaining_card,
        text="Budget Remaining",
        text_color="#D1D5DB",
        font=("Arial", 13)
    ).pack(pady=(16, 6))

    remaining_color = (
        "#F87171" if remaining < 0 else "#4ADE80"
    )

    ctk.CTkLabel(
        remaining_card,
        text=f"₹{remaining:,.2f}",
        text_color=remaining_color,
        font=("Arial", 21, "bold")
    ).pack(pady=(0, 16))

    # Card 4: Budget Used
    usage_card = ctk.CTkFrame(
        kpi_frame,
        fg_color="#303030",
        corner_radius=12
    )
    usage_card.grid(
        row=0, column=3, padx=6, pady=6,
        sticky="nsew"
    )

    ctk.CTkLabel(
        usage_card,
        text="Budget Used",
        text_color="#D1D5DB",
        font=("Arial", 13)
    ).pack(pady=(16, 6))

    ctk.CTkLabel(
        usage_card,
        text=f"{budget_usage:.1f}%",
        text_color=(
            "#F87171" if budget_usage >= 100
            else "#4ADE80"
        ),
        font=("Arial", 21, "bold")
    ).pack(pady=(0, 8))

    budget_progress = ctk.CTkProgressBar(
        usage_card,
        width=130,
        height=8,
        progress_color=(
            "#F87171" if budget_usage >= 100
            else "#22C55E"
        ),
        fg_color="#454545"
    )
    budget_progress.pack(padx=12, pady=(0, 16))

    budget_progress.set(
        min(max(budget_usage / 100, 0), 1)
    )

    # Give all four cards equal width
    for column in range(4):
        kpi_frame.grid_columnconfigure(
            column, weight=1, uniform="kpi"
        )

    
    

    category_data = category_summary(expenses)

    if category_data:
        figure, axis = plt.subplots(
            figsize=(9, 4.5),
            facecolor="#242424"
        )
        axis.set_facecolor("#242424")

        bars = axis.bar(
            category_data.keys(),
            category_data.values(),
            color="#3B82F6",
            width=0.6
        )

        axis.set_title(
            "Category-wise Spending",
            color="white",
            fontsize=16,
            fontweight="bold",
            pad=15
        )
        axis.set_xlabel(
            "Category",
            color="#D1D5DB",
            fontsize=11
        )
        axis.set_ylabel(
            "Amount (₹)",
            color="#D1D5DB",
            fontsize=11
        )

        axis.tick_params(
            axis="x",
            colors="#E5E7EB",
            rotation=25
        )
        axis.tick_params(
            axis="y",
            colors="#E5E7EB"
        )

        axis.grid(
            axis="y",
            linestyle="--",
            alpha=0.2,
            color="white"
        )
        axis.set_axisbelow(True)

        for spine in axis.spines.values():
            spine.set_color("#4B5563")

        axis.bar_label(
            bars,
            labels=[
                f"₹{value:,.0f}"
                for value in category_data.values()
            ],
            padding=4,
            color="white",
            fontsize=9
        )

        figure.tight_layout()

        chart_canvas = FigureCanvasTkAgg(
            figure,
            master=dashboard
        )
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        plt.close(figure)

    else:
        ctk.CTkLabel(
            dashboard,
            text="No expenses available to display in the chart."
        ).pack(pady=30)




title = ctk.CTkLabel(
    app,
    text="💰 Expense Tracker",
    font=("Arial", 28, "bold")
)
title.pack(pady=(30, 10))

subtitle = ctk.CTkLabel(
    app,
    text="Manage and analyze your spending",
    font=("Arial", 14)
)
subtitle.pack(pady=(0, 20))


# Monthly Budget Section
budget_frame = ctk.CTkFrame(app, corner_radius=12)
budget_frame.pack(fill="x", padx=35, pady=5)

budget_title = ctk.CTkLabel(
    budget_frame,
    text="📊 Monthly Budget",
    font=("Arial", 18, "bold")
)
budget_title.pack(pady=(12, 8))

budget_entry = ctk.CTkEntry(
    budget_frame,
    placeholder_text="Enter monthly budget in ₹",
    width=280,
    height=35
)
budget_entry.pack(pady=6)

budget_button = ctk.CTkButton(
    budget_frame,
    text="Set Monthly Budget",
    width=220,
    command=lambda: save_budget()
)
budget_button.pack(pady=6)

budget_status = ctk.CTkLabel(
    budget_frame,
    text="Your monthly spending details will appear here.",
    font=("Arial", 13),
    justify="center"
)
budget_status.pack(pady=(6, 12))


date_entry = ctk.CTkEntry(
    app,
    placeholder_text="Date (DD-MM-YYYY)",
    width=320,
    height=40
)
date_entry.pack(pady=6)

category_entry = ctk.CTkEntry(
    app,
    placeholder_text="Category (e.g. Food, Travel)",
    width=320,
    height=40
)
category_entry.pack(pady=6)

amount_entry = ctk.CTkEntry(
    app,
    placeholder_text="Amount in ₹",
    width=320,
    height=40
)
amount_entry.pack(pady=6)

description_entry = ctk.CTkEntry(
    app,
    placeholder_text="Description (optional)",
    width=320,
    height=40
)
description_entry.pack(pady=6)


# Buttons container
button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=(20, 10))

# Add Expense
add_button = ctk.CTkButton(
    button_frame,
    text="Add Expense",
    command=add_new_expense,
    width=250,
    height=42
)
add_button.grid(row=0, column=0, padx=8, pady=8)

# View All Expenses
view_button = ctk.CTkButton(
    button_frame,
    text="View All Expenses",
    command=view_all_expenses,
    width=250,
    height=42
)
view_button.grid(row=0, column=1, padx=8, pady=8)

# Expense Summary
summary_button = ctk.CTkButton(
    button_frame,
    text="Expense Summary",
    command=show_expense_summary,
    width=250,
    height=42
)
summary_button.grid(row=1, column=0, padx=8, pady=8)

# Open Dashboard
dashboard_button = ctk.CTkButton(
    button_frame,
    text="Open Dashboard",
    command=open_dashboard,
    width=250,
    height=42
)
dashboard_button.grid(row=1, column=1, padx=8, pady=8)

refresh_budget_status()

app.mainloop()
