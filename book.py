
import pandas as pd
from database import cur, con

# Load Excel
df = pd.read_excel("booklist.xlsx")

# Clean and prepare data
for index, row in df.iterrows():
    try:
        book_id = row["Book ID"]
        title = row["Book Name"]
        author = row["Author"]
        isbn = str(row["ISBN"])
        publisher = row["Publisher"] if not pd.isna(row["Publisher"]) else "Unknown"
        available = 5 if pd.isna(row["Available"]) or row["Available"] == "Undefined" else int(row["Available"])

        # Fixed/default values
        category = "General"
        year = 2020
        status = "AVAILABLE"
        out_of = available
        bdescription = ""

        # Insert query
        cur.execute("""
            INSERT INTO BOOKS 
            (BOOK_ID, TITLE, AUTHOR, ISBN, CATEGORY, YEAR, STATUS, PUBLISHER, AVAILABLE, OUT_OF, BDESCRIPTION)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (book_id, title, author, isbn, category, year, status, publisher, available, out_of, bdescription))

    except Exception as e:
        print(f"❌ Error inserting book at row {index}: {e}")

# Commit changes
con.commit()
print("✅ All valid books inserted successfully!")
