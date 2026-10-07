import pandas as pd
import mysql.connector

columns = ['STUDENT_ID', 'NAME', 'GENDER', 'COURSE', 'USERNAME', 'PASSWORD', 'SEMESTER', 'MOBILE_NO','BOOKS_ISSUED', 'EMAIL']
df = pd.read_excel('demodatastu18.xlsx', header=None, names=columns)

conn = mysql.connector.connect(
    host='localhost',           
    user='root',
    password='db_password',
    database='librarydb'
)

cur = conn.cursor()

for index, row in df.iterrows():
   
    sql = """
    INSERT INTO STUDENT
    (STUDENT_ID,NAME,GENDER,COURSE,USERNAME,PASSWORD,SEMESTER,MOBILE_NO,BOOKS_ISSUED,EMAIL)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
    """
    values = tuple(row)
    print(values)
    cur.execute(sql,values)

conn.commit()
cur.close()
conn.close()

print("All records inserted successfully.")
