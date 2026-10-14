# 💰 Expense Tracker

A desktop-based Expense Tracker built with Python to help users record daily expenses, manage monthly budgets, and analyse their spending through a visual dashboard.

## ✨ Features

- **Expense Management:** Add, view, search, edit, and delete expenses.
- **Monthly Budget Tracking:** Set a monthly budget and monitor spending.
- **Budget Insights:** View remaining budget and budget usage percentage.
- **Analytics Dashboard:** Track total expenses and current-month spending.
- **Category-wise Visualisation:** Analyse spending across expense categories using charts.
- **Local Database:** Store expense records using SQLite.
- **Dark User Interface:** Built with CustomTkinter.

## 🛠️ Technologies Used

- Python
- CustomTkinter
- SQLite
- Matplotlib

## 📁 Project Structure

```text
expense_tracker/
├── main.py
├── database.py
├── analytics.py
├── migrate_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd expense_tracker
```

Replace `YOUR_REPOSITORY_URL` with your GitHub repository URL.

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Run the application

```bash
python main.py
```

## 💾 Data Storage

The application uses SQLite for local expense storage. Personal database and backup files are excluded from Git tracking.

## 🎯 Project Goal

The goal of this project is to make personal expense tracking easier through a simple desktop interface, monthly budget monitoring, and spending visualisation.

## 👩‍💻 Author

Developed as a Python project to practise desktop application development, database management, and data visualisation.
