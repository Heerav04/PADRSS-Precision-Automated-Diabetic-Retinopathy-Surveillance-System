import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "dr_project_db")
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM prediction_history")
    rows = cursor.fetchall()
    
    with open("prediction_history.md", "w") as f:
        f.write("# Prediction History (dr_project_db)\n\n")
        f.write("| ID | Patient Name | Image Path | Predicted Label | Class | Confidence | Created At |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['id']} | {r['patient_name']} | {r['image_path']} | {r['predicted_label']} | {r['predicted_class']} | {r['confidence']:.2f}% | {r['created_at']} |\n")
    print("Table successfully exported to prediction_history.md")
except Exception as e:
    print(f"Error: {e}")
