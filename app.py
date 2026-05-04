import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
import mysql.connector as db_connector
import numpy as np
from PIL import Image

import os
from dotenv import load_dotenv

from model import predict

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "dr_project_db")
TABLE_NAME = "prediction_history"

DR_DESC = {
    "No DR": "Healthy retina. No visible diabetic retinopathy signs.",
    "Mild": "Early signs (microaneurysms) are present.",
    "Moderate": "More lesions are visible; progression is ongoing.",
    "Severe": "High-risk stage with significant vessel damage.",
    "Proliferative DR": "Advanced stage with neovascularization risk.",
}


class RetinaApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Automated Diabetic Retinopathy")
        self.root.geometry("980x620")
        self.root.configure(bg="#eef3f8")
        self.db_conn = None
        self.db_cursor = None
        self._init_db()
        self._build_ui()

    def _init_db(self):
        """Create database and prediction history table if missing."""
        try:
            admin_conn = db_connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            admin_cursor = admin_conn.cursor()
            admin_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
            admin_cursor.execute(f"USE `{DB_NAME}`")
            admin_cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
                    id INT NOT NULL AUTO_INCREMENT,
                    patient_name VARCHAR(120) NOT NULL,
                    image_path TEXT NOT NULL,
                    predicted_label VARCHAR(40) NOT NULL,
                    predicted_class INT NOT NULL,
                    confidence FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id)
                )
                """
            )
            admin_conn.commit()
            admin_cursor.close()
            admin_conn.close()

            self.db_conn = db_connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
            self.db_cursor = self.db_conn.cursor()
        except Exception as exc:
            messagebox.showwarning("Database", f"MySQL backend unavailable.\n{exc}")

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#005b96", height=82)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Automated Diabetic Retinopathy",
            fg="white",
            bg="#005b96",
            font=("Segoe UI", 20, "bold"),
        ).pack(expand=True)

        container = tk.Frame(self.root, bg="#eef3f8")
        container.pack(expand=True, fill="both", padx=18, pady=16)

        left = tk.Frame(container, bg="#eef3f8", width=330)
        left.pack(side="left", fill="y", padx=(0, 14))

        card = tk.Frame(left, bg="white", bd=1, relief="solid")
        card.pack(fill="x")
        tk.Label(
            card,
            text="Analyze Fundus Image",
            bg="white",
            font=("Segoe UI", 13, "bold"),
            pady=12,
        ).pack()
        tk.Label(card, text="Patient Name", bg="white", font=("Segoe UI", 9, "bold")).pack()
        self.patient_name_entry = ttk.Entry(card, width=34)
        self.patient_name_entry.pack(pady=(0, 8))
        ttk.Button(card, text="Upload and Analyze", command=self.analyze).pack(pady=10)
        tk.Label(
            card,
            text="Supported formats: PNG, JPG, JPEG",
            bg="white",
            fg="#4d4d4d",
            font=("Segoe UI", 9),
            pady=10,
        ).pack()

        self.result_box = tk.Text(left, height=14, width=42, wrap="word", bg="#fbfcfe")
        self.result_box.pack(fill="x", pady=12)
        self.result_box.insert("end", "Result will appear here after analysis.")
        self.result_box.config(state="disabled")

        right = tk.Frame(container, bg="white", bd=1, relief="solid")
        right.pack(side="right", expand=True, fill="both")
        tk.Label(
            right,
            text="Clinical Reference",
            bg="white",
            font=("Segoe UI", 13, "bold"),
            pady=10,
        ).pack()

        for stage, desc in DR_DESC.items():
            row = tk.Frame(right, bg="white")
            row.pack(fill="x", padx=12, pady=6)
            tk.Label(row, text=f"{stage}:", bg="white", width=18, anchor="w", font=("Segoe UI", 10, "bold")).pack(side="left")
            tk.Label(row, text=desc, bg="white", anchor="w", justify="left", wraplength=430, font=("Segoe UI", 10)).pack(side="left")

    def _set_result(self, text: str):
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", text)
        self.result_box.config(state="disabled")

    def analyze(self):
        patient_name = self.patient_name_entry.get().strip() or "Anonymous"
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not path:
            return

        try:
            value, label, confidence = predict(path)
            self._save_prediction(patient_name, path, value, label, confidence)
            details = (
                f"Patient: {patient_name}\n"
                f"Prediction: {label} (Class {value})\n"
                f"Confidence: {confidence:.2f}%\n\n"
                f"Medical note:\n{DR_DESC.get(label, 'No description available.')}"
            )
            self._set_result(details)
            self.show_plot(path, label, confidence)
        except Exception as exc:
            messagebox.showerror("Error", f"Inference failed:\n{exc}")

    def _save_prediction(self, patient_name: str, image_path: str, value: int, label: str, confidence: float):
        if self.db_cursor is None or self.db_conn is None:
            return
        self.db_cursor.execute(
            f"""
            INSERT INTO `{TABLE_NAME}` (
                patient_name, image_path, predicted_label, predicted_class, confidence
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (patient_name, image_path, label, value, confidence),
        )
        self.db_conn.commit()

    def show_plot(self, path: str, label: str, confidence: float):
        image = Image.open(path).convert("RGB")
        plt.figure(figsize=(8, 6))
        plt.imshow(np.array(image))
        plt.title(f"{label} ({confidence:.2f}%)", fontsize=14)
        plt.axis("off")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    app_root = tk.Tk()
    RetinaApp(app_root)
    app_root.mainloop()
