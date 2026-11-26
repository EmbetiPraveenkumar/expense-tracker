
import csv
import os
from datetime import datetime
from collections import defaultdict

FILE = "expenses.csv"

def initialize():
    if not os.path.exists(FILE):
        with open(FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Description", "Amount"])

def add_expense():
    Category = input("Enter category: ")
    description = input("Enter description: ")

    try:
        amount = float(input("Enter amount: "))
        if amount <= 0:
            print("Amount must be greater than zero.")
            return
    except ValueError:
        print("Enter a valid amount.")
        return

#  date

    date = datetime.now().strftime("%Y-%m-%d")

# adding to csv file
    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, description, amount])

    print("Expense added successfully!")

# view expenses
def view_expenses():
    with open(FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            print(" | ".join(row))

def total_expenses():
    total = 0

    with open(FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += float(row["amount"])

    print("Total expenses: Rs.", round(total, 2))

def category_report():
    totals = defaultdict(float)

    with open(FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            totals[row["category"]] += float(row["amount"])

    print("\nCategory-wise expenses:")
    for category, amount in totals.items():
        print(category, ":", round(amount, 2))

def budget_check():
    try:
        budget = float(input("Enter monthly budget: "))
    except ValueError:
        print("Enter a valid budget.")
        return

    month = datetime.now().strftime("%Y-%m")
    total = 0

    with open(FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date"].startswith(month):
                total += float(row["amount"])

    print("This month's spending:", round(total, 2))

    if total > budget:
        print("Warning! You exceeded your monthly budget.")
    else:
        print("You are within your budget.")

def main():
    initialize()

    while True:
        print("\n===== SMART EXPENSE TRACKER =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Total Expenses")
        print("4. Category Report")
        print("5. Check Monthly Budget")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            total_expenses()
        elif choice == "4":
            category_report()
        elif choice == "5":
            budget_check()
        elif choice == "6":
            print("Thank you for using Expense Tracker!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
