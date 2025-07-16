from db_connector import fetch_data_from_mysql
from plot_mixer_data import plot_all_signals_db
import pandas as pd

def check_orphaned_ids():
    print("\n🔍 Checking for orphaned id_summary values in mix_detail...")
    query = """
    SELECT id_summary
    FROM mix_detail
    WHERE id_summary NOT IN (SELECT id FROM mix_summary)
    ORDER BY id_summary DESC
    LIMIT 10
    """
    df = fetch_data_from_mysql(query)
    if df.empty:
        print("✅ All id_summary values in mix_detail are valid.")
    else:
        print("❌ Found orphaned id_summary values (most recent):")
        print(df)


def preview_join():
    print("\n🔗 Previewing join between mix_detail and mix_summary...")
    query = """
    SELECT d.*, s.batch, s.program, s.date
    FROM mix_detail d
    JOIN mix_summary s ON d.id_summary = s.id
    ORDER BY d.id_summary DESC
    LIMIT 5
    """
    df = fetch_data_from_mysql(query)
    if df.empty:
        print("❌ No results found.")
    else:
        print("✅ Join preview successful:")
        print(df)

def plot_single_batch():
    try:
        batch_id = int(input("\nEnter a valid id_summary to plot: "))
    except ValueError:
        print("⚠️ Invalid input. Please enter a numeric id_summary.")
        return

    print(f"📊 Fetching data for batch ID {batch_id}...")
    query = f"""
    SELECT d.*, s.batch, s.program, s.date
    FROM mix_detail d
    JOIN mix_summary s ON d.id_summary = s.id
    WHERE d.id_summary = {batch_id}
    """
    df = fetch_data_from_mysql(query)

    if df.empty:
        print("❌ No data found for that id_summary.")
    else:
        print("✅ Plotting data...")
        print(df.head())
        print(df.columns)
        print(df[["elapsed_batch_time", "kw_actual"]].dropna().head())

        fig = plot_all_signals_db(df)
        fig.show()

def main():
    print("\n=== 🔧 Mixer Database Debug Tool ===")
    print("1. Check for orphaned id_summary in mix_detail")
    print("2. Preview joined data from mix_summary + mix_detail")
    print("3. Plot data for a single batch")
    print("0. Exit")

    while True:
        try:
            choice = int(input("\nSelect an option: "))
        except ValueError:
            print("⚠️ Invalid input. Enter a number.")
            continue

        if choice == 1:
            check_orphaned_ids()
        elif choice == 2:
            preview_join()
        elif choice == 3:
            plot_single_batch()
        elif choice == 0:
            print("👋 Exiting debug tool.")
            break
        else:
            print("⚠️ Invalid option. Try again.")

if __name__ == "__main__":
    main()
