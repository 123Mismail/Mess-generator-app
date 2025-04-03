

import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
import os

# Define the custom page size (width, height)
CUSTOM_PAGE_SIZE = (11 * inch, 8.5 * inch)  # Custom size: 12.5 inches (width) x 8.5 inches (height)

# Store mess data
if "mess_data" not in st.session_state:
    st.session_state["mess_data"] = []

# Store total expenses
if "total_expenses" not in st.session_state:
    st.session_state["total_expenses"] = {}

def reset_data():
    """Reset all stored data."""
    st.session_state["mess_data"] = []
    st.session_state["total_expenses"] = {}

def generate_pdf(dataframe):
    """Generates a formatted PDF report with a centered table and note below."""
    pdf_file = "mess_sheet.pdf"
    c = canvas.Canvas(pdf_file, pagesize=CUSTOM_PAGE_SIZE)  # Use custom page size
    width, height = CUSTOM_PAGE_SIZE

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 50, "Monthly Mess Report")  # Centered title

    # Create a list of lists for the table data
    table_data = [dataframe.columns.tolist()]  # Header
    for index, row in dataframe.iterrows():
        table_data.append(row.tolist())

    # Create the table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Calculate table width and height
    table_width, table_height = table.wrapOn(c, width, height)

    # Calculate starting x and y positions to center the table
    x_offset = (width - table_width) / 2
    y_offset = height - 100 - table_height  # Adjust y_offset to leave space for the title

    # Draw the table on the canvas
    table.drawOn(c, x_offset, y_offset)

    # Add note message below the table
    note = "Note: Please ensure all payments are made by the 8th of the month."
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y_offset - 30, note)  # Position note below the table

    # Save PDF
    c.save()
    return pdf_file

st.title("🍽️ Monthly Mess Management System")

# Step 1: Enter total expenses
st.subheader("💰 Enter Total Monthly Expenses")
with st.form("expenses_form"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_meal_expense = st.number_input("Total Meal Expense", min_value=0.0, format="%.2f")
    with col2:
        total_utility = st.number_input("Total Utility Expense", min_value=0.0, format="%.2f")
    with col3:
        total_rent = st.number_input("Total Rent Expense", min_value=0.0, format="%.2f")
    with col4:
        total_cook_salary = st.number_input("Total Cook Salary", min_value=0.0, format="%.2f")  # Added Cook Salary
    submitted = st.form_submit_button("Save Expenses")
    if submitted:
        st.session_state["total_expenses"] = {
            "Total Meal Expense": total_meal_expense,
            "Total Utility": total_utility,
            "Total Rent": total_rent,
            "Total Cook Salary": total_cook_salary  # Added Cook Salary
        }
        st.success("✅ Expenses saved! Now add members.")

# Step 2: Add members
st.subheader("👤 Add Members to Mess")
with st.form("members_form"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        name = st.text_input("Name")
        fine = st.number_input("Fine", min_value=0.0, format="%.2f")
        advance = st.number_input("Advance Paid", min_value=0.0, format="%.2f")
    with col2:
        previous = st.number_input("Previous Balance", min_value=0.0, format="%.2f")
        admission = st.number_input("Admission Fee", min_value=0.0, format="%.2f")
        total_meal_times = st.number_input("Total Meal Times", min_value=0, step=1)
    with col3:
        fund = st.number_input("Fund", min_value=0.0, format="%.2f")  # Added Fund field
        meal_checked = st.checkbox("Participated in Meal", value=True)
        rent_checked = st.checkbox("Participated in Rent", value=True)
    with col4:
        utility_checked = st.checkbox("Participated in Utility", value=True)
        fund_checked = st.checkbox("Participated in Fund", value=True)  # Added Fund checkbox
        cook_salary_checked = st.checkbox("Participated in Cook Salary", value=True)  # Added Cook Salary checkbox
    
    add_member = st.form_submit_button("➕ Add Member")
    if add_member:
        if name:
            st.session_state["mess_data"].append({
                "Name": name,
                "Fine": fine,
                "Advance": advance,
                "Previous Balance": previous,
                "Admission": admission,
                "Total Meal Times": total_meal_times,
                "Fund": fund,  # Added Fund field
                "Meal Checked": meal_checked,
                "Rent Checked": rent_checked,
                "Utility Checked": utility_checked,
                "Fund Checked": fund_checked,  # Added Fund checkbox
                "Cook Salary Checked": cook_salary_checked  # Added Cook Salary checkbox
            })
            st.success(f"✅ Member {name} added!")
        else:
            st.warning("⚠️ Please enter a name!")

# Display members list and generate report
if st.session_state["mess_data"]:
    st.subheader("📋 Members List")
    df_members = pd.DataFrame(st.session_state["mess_data"])
    st.dataframe(df_members)

if st.session_state["mess_data"] and st.session_state["total_expenses"]:
    if st.button("📜 Generate Mess Sheet"):
        # Calculate total meal times for members who participated in meals
        total_meal_times = sum(
            member["Total Meal Times"] for member in st.session_state["mess_data"] if member["Meal Checked"]
        )
        
        # Calculate total members who participated in rent, utility, fund, and cook salary
        total_rent_members = sum(1 for member in st.session_state["mess_data"] if member["Rent Checked"])
        total_utility_members = sum(1 for member in st.session_state["mess_data"] if member["Utility Checked"])
        total_fund_members = sum(1 for member in st.session_state["mess_data"] if member["Fund Checked"])  # Added Fund
        total_cook_salary_members = sum(1 for member in st.session_state["mess_data"] if member["Cook Salary Checked"])  # Added Cook Salary

        # Calculate costs per person
        meal_cost = (st.session_state["total_expenses"]["Total Meal Expense"] / total_meal_times) if total_meal_times else 0
        rent_per_member = (st.session_state["total_expenses"]["Total Rent"] / total_rent_members) if total_rent_members else 0
        utility_per_member = (st.session_state["total_expenses"]["Total Utility"] / total_utility_members) if total_utility_members else 0
        fund_per_member = (st.session_state["total_expenses"].get("Total Fund", 0) / total_fund_members) if total_fund_members else 0  # Added Fund
        cook_salary_per_member = (st.session_state["total_expenses"]["Total Cook Salary"] / total_cook_salary_members) if total_cook_salary_members else 0  # Added Cook Salary

        report_data = []
        for member in st.session_state["mess_data"]:
            # Calculate individual meal cost if participated in meals
            individual_meal_cost = meal_cost * member["Total Meal Times"] if member["Meal Checked"] else 0
            
            # Calculate rent, utility, fund, and cook salary costs if participated
            rent_cost = rent_per_member if member["Rent Checked"] else 0
            utility_cost = utility_per_member if member["Utility Checked"] else 0
            fund_cost = fund_per_member if member["Fund Checked"] else 0  # Added Fund
            cook_salary_cost = cook_salary_per_member if member["Cook Salary Checked"] else 0  # Added Cook Salary

            # Calculate subtotal and final total
            subtotal = individual_meal_cost + member["Fine"] + member["Admission"] + rent_cost + utility_cost + fund_cost + cook_salary_cost + member["Fund"]
            final_total = subtotal - member["Advance"] + member["Previous Balance"]
            
            report_data.append({
                "Name": member["Name"],
                "Rent": round(rent_cost, 2),
                "Meal Cost": round(individual_meal_cost, 2),
                "Utility": round(utility_cost, 2),
                "Fine": round(member["Fine"], 2),
                "Admission": round(member["Admission"], 2),
                "Fund": round(member["Fund"], 2),  # Added Fund field
                "Cook Salary": round(cook_salary_cost, 2),  # Added Cook Salary
                "Advance": round(member["Advance"], 2),
                "Prev Bal": round(member["Previous Balance"], 2),
                "Subtotal": round(subtotal, 2),
                "Total": round(final_total, 2)
            })

        df_report = pd.DataFrame(report_data)

        totals = {
            "Name": "TOTAL",
            "Meal Cost": round(df_report["Meal Cost"].sum(), 2),
            "Fine": round(df_report["Fine"].sum(), 2),
            "Admission": round(df_report["Admission"].sum(), 2),
            "Rent": round(df_report["Rent"].sum(), 2),
            "Utility": round(df_report["Utility"].sum(), 2),
            "Fund": round(df_report["Fund"].sum(), 2),  # Added Fund field
            "Cook Salary": round(df_report["Cook Salary"].sum(), 2),  # Added Cook Salary
            "Advance": round(df_report["Advance"].sum(), 2),
            "Prev Bal": round(df_report["Prev Bal"].sum(), 2),
            "Subtotal": round(df_report["Subtotal"].sum(), 2),
            "Total": round(df_report["Total"].sum(), 2),
        }

        df_totals = pd.DataFrame([totals])
        df_report = pd.concat([df_report, df_totals], ignore_index=True)

        st.subheader("📊 Monthly Mess Sheet")
        st.dataframe(df_report)

        csv = df_report.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Mess Sheet (CSV)", csv, "mess_sheet.csv", "text/csv")

        pdf_path = generate_pdf(df_report)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button("📄 Download Mess Sheet (PDF)", pdf_file, file_name="mess_sheet.pdf", mime="application/pdf")

if st.button("🔄 Reset Data"):
    reset_data()
    st.success("✅ Data reset successfully! Start fresh.")