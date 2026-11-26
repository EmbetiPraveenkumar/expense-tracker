
import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime

FILE = "expenses.csv"
COLUMNS = ["Date", "Category", "Description", "Amount"]

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------- INITIALIZE CSV ----------------

def initialize():
    if not os.path.exists(FILE):
        with open(FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)

# ---------------- LOAD DATA ----------------

def load_data():
    initialize()

    df = pd.read_csv(FILE)

    # Normalize headers to avoid case/space mismatches
    df.columns = df.columns.str.strip().str.title()

    if list(df.columns) != COLUMNS:
        st.error("Incorrect CSV headers. Please check expenses.csv.")
        st.stop()

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Category"] = df["Category"].fillna("").astype(str).str.strip()
    df["Description"] = df["Description"].fillna("").astype(str)

    return df.dropna(subset=["Amount", "Date"])

# ---------------- SAVE EXPENSE ----------------

def save_expense(category, description, amount):
    date = datetime.now().strftime("%Y-%m-%d")

    with open(FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, description, amount])

# ---------------- DELETE EXPENSE ----------------

def delete_expense(index):
    df = load_data()

    if 0 <= index < len(df):
        df = df.drop(index=index).reset_index(drop=True)
        df.to_csv(FILE, index=False)

# ---------------- LOAD APPLICATION DATA ----------------

initialize()
df = load_data()

# ---------------- SIDEBAR NAVIGATION ----------------

st.title("💰 Smart Expense Tracker")

st.write("Manage your daily expenses and monthly budget in one place.")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Dashboard",
        "Add Expense",
        "Expense History",
        "Category Report",
        "Budget Tracker",
        "Delete Expense"
    ]
)

# ---------------- MONTHLY DATA ----------------

today = pd.Timestamp.today()

month_data = df[
    (df["Date"].dt.year == today.year) &
    (df["Date"].dt.month == today.month)
]

total = df["Amount"].sum()
monthly_total = month_data["Amount"].sum()

# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.subheader("📊 Expense Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Expenses", f"₹{total:.2f}")
    col2.metric("This Month", f"₹{monthly_total:.2f}")
    col3.metric("Total Transactions", len(df))

    st.subheader("🕒 Recent Expenses")

    if not df.empty:

        recent = df.sort_values("Date", ascending=False).head(10)

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("📊 Spending Overview")

        category_totals = df.groupby("Category")["Amount"].sum()

        st.bar_chart(category_totals)

    else:
        st.info("No expenses recorded yet.")

# ==================================================
# ADD EXPENSE
# ==================================================

elif page == "Add Expense":

    st.subheader("➕ Add a New Expense")

    with st.form("expense_form"):

        category = st.selectbox(
            "Select Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Education",
                "Entertainment",
                "Health",
                "Other"
            ]
        )

        description = st.text_input("Description")

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=10.0
        )

        submit = st.form_submit_button("Add Expense")

        if submit:

            if not description.strip():
                st.warning("Please enter a description.")

            elif amount <= 0:
                st.warning("Amount must be greater than zero.")

            else:
                save_expense(category, description.strip(), amount)

                st.success("Expense added successfully!")

                st.rerun()

# ==================================================
# EXPENSE HISTORY
# ==================================================

elif page == "Expense History":

    st.subheader("📋 All Expenses")

    if not df.empty:

        st.dataframe(
            df.sort_values("Date", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Expense Report",
            data=csv_data,
            file_name="expense_report.csv",
            mime="text/csv"
        )

    else:
        st.info("No expenses available.")

# ==================================================
# CATEGORY REPORT
# ==================================================

elif page == "Category Report":

    st.subheader("📈 Category-wise Expense Report")

    if not df.empty:

        report = df.groupby("Category")["Amount"].sum().sort_values(
            ascending=False
        )

        st.dataframe(
            report.reset_index(),
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(report)

    else:
        st.info("No expenses available yet.")

# ==================================================
# BUDGET TRACKER
# ==================================================

elif page == "Budget Tracker":

    st.subheader("💰 Monthly Budget Tracker")

    budget = st.number_input(
        "Enter Your Monthly Budget (₹)",
        min_value=1.0,
        value=5000.0,
        step=500.0
    )

    remaining = budget - monthly_total

    col1, col2, col3 = st.columns(3)

    col1.metric("Monthly Budget", f"₹{budget:.2f}")

    col2.metric("Amount Spent", f"₹{monthly_total:.2f}")

    col3.metric("Remaining", f"₹{remaining:.2f}")

    progress = min(monthly_total / budget, 1.0)

    st.progress(progress)

    if monthly_total > budget:

        st.error("⚠️ Warning! You exceeded your monthly budget.")

    else:

        st.success("✅ You are within your monthly budget.")

# ==================================================
# DELETE EXPENSE
# ==================================================

elif page == "Delete Expense":

    st.subheader("🗑️ Delete an Expense")

    if df.empty:

        st.info("No expenses available to delete.")

    else:

        # Create a unique selection label for each expense
        expense_options = {}

        for index, row in df.iterrows():

            label = (
                f"{index} | "
                f"{row['Date'].strftime('%Y-%m-%d')} | "
                f"{row['Category']} | "
                f"{row['Description']} | "
                f"₹{row['Amount']:.2f}"
            )

            expense_options[label] = index

        selected_expense = st.selectbox(
            "Select the expense you want to delete",
            list(expense_options.keys())
        )

        selected_index = expense_options[selected_expense]

        st.warning("This action permanently deletes the selected expense.")

        confirm = st.checkbox(
            "I confirm that I want to delete this expense."
        )

        if st.button("🗑️ Delete Selected Expense", type="primary"):

            if confirm:

                delete_expense(selected_index)

                st.success("Expense deleted successfully!")

                st.rerun()

            else:

                st.warning("Please confirm before deleting.")
