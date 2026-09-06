# 💰 Personal Budget Tracker

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)

A clean, beginner-friendly **desktop application** for tracking personal income and expenses — built with **Python**, **Tkinter**, and **Matplotlib**.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Add Transactions** | Log income or expenses with category, amount, date & description |
| **Transaction Table** | Sortable table with colour-coded Income (green) / Expense (red) rows |
| **Summary Panel** | Live totals for Income, Expenses, Balance & Transaction count |
| **Pie Chart** | Expenses broken down by category using Matplotlib |
| **Persistent Storage** | All data saved to `budget_data.csv` — survives restarts |
| **Validation** | Checks for empty fields, invalid amounts, and bad date formats |
| **Delete / Clear** | Remove a selected row or wipe all data with confirmation dialogs |

---

## 📁 Project Structure

```
Personal_Budget_Tracker/
├── main.py           # Application entry point
├── budget_data.csv   # Auto-created; stores all transactions
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## 🚀 Getting Started

### 1 — Prerequisites

- Python **3.10+** (tkinter ships with Python by default)
- pip

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

> Only **matplotlib** is required; tkinter and csv are part of the Python standard library.

### 3 — Run the application

```bash
python main.py
```

---

## 🖥️ How to Use

### Adding a Transaction
1. Choose **Expense** or **Income** using the radio buttons.
2. Select a **Category** from the dropdown (list changes with transaction type).
3. Enter the **Amount** as a positive number (e.g. `1500` or `99.50`).
4. Set the **Date** in `YYYY-MM-DD` format (today's date is pre-filled).
5. Write a short **Description**.
6. Click **✚ Add Transaction**.

### Deleting a Transaction
- Click a row in the table to select it, then click **🗑 Delete Selected**.
- Confirm the prompt — the row is removed from both the table and the CSV.

### Clearing All Data
- Click **🧹 Clear All Transactions**.
- Confirm the prompt to permanently delete every record.

### Sorting the Table
- Click any **column header** to sort by that column.

---

## 📊 Categories

| Income | Expense |
|---|---|
| Salary | Food |
| Freelance | Rent |
| Investment | Utilities |
| Gift | Transport |
| Bonus | Healthcare |
| Other Income | Entertainment |
| | Shopping |
| | Education |
| | Savings |
| | Other Expense |

---

## 💾 Data Format (`budget_data.csv`)

```
type,category,amount,date,description
Expense,Food,250.00,2025-06-15,Weekly groceries
Income,Salary,50000.00,2025-06-01,Monthly salary
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Tkinter** — GUI framework (standard library)
- **csv** — Data persistence (standard library)
- **Matplotlib** — Pie chart visualisation

---

## 📝 License

This project is open-source and free to use for personal or educational purposes.
