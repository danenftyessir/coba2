import mysql.connector

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="danen332",
        database="kaggle_resumes",
        port=3306,
        connection_timeout=5
    )
    print("✅ TERHUBUNG KE DATABASE!")
except mysql.connector.Error as err:
    print("❌ GAGAL CONNECT:", err)
