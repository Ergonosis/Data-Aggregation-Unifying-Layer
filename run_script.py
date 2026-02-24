from datetime import date
from apps import DataExporter, get_records_dir

# This is the "Method Call" approach
def main():
    print("--- Starting Manual Data Pull ---")
    
    # Direct call to the method we built in apps.py
    results = DataExporter.run_export(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 2, 23),
        bank_filter="Chase",  # Can be "Chase", "Wells Fargo", or an Item ID
        account_filter=["Plaid Checking", "Plaid Saving"],  # Optional: one or many account names/keywords
        output_dir=get_records_dir()
    )

    if not results:
        print("No accounts matched the filter or no tokens found.")
    
    for res in results:
        print(f"Export successful! File created at: {res['file']}")

if __name__ == "__main__":
    main()
