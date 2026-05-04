import os
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import mysql.connector

from model import predict

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database connection details from .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "dr_project_db")
TABLE_NAME = "prediction_history"

def save_prediction_db(patient_name, image_path, value, label, confidence):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO `{TABLE_NAME}` (
                patient_name, image_path, predicted_label, predicted_class, confidence
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (patient_name, image_path, label, value, confidence)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database error:", e)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Automated Diabetic Retinopathy</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #eef3f8; margin: 0; }
        .header { background-color: #005b96; color: white; padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: 30px auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input[type="text"], input[type="file"] { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background-color: #005b96; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; font-size: 16px; }
        button:hover { background-color: #003f69; }
        .result { margin-top: 20px; padding: 15px; background: #fbfcfe; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Automated Diabetic Retinopathy Analysis</h1>
    </div>
    <div class="container">
        <form action="/predict" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label>Patient Name:</label>
                <input type="text" name="patient_name" placeholder="Anonymous" />
            </div>
            <div class="form-group">
                <label>Upload Fundus Image (PNG/JPG/JPEG):</label>
                <input type="file" name="file" required accept="image/png, image/jpeg, image/jpg"/>
            </div>
            <button type="submit">Upload and Analyze</button>
        </form>
        
        {% if prediction %}
        <div class="result">
            <h3>Analysis Result:</h3>
            <p><strong>Patient:</strong> {{ patient }}</p>
            <p><strong>Prediction:</strong> {{ prediction }} (Class {{ value }})</p>
            <p><strong>Confidence:</strong> {{ confidence }}%</p>
        </div>
        {% endif %}
        
        {% if error %}
        <div class="result" style="color: red;">
            <p><strong>Error:</strong> {{ error }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/predict', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return render_template_string(HTML_TEMPLATE, error="No file part")
    file = request.files['file']
    if file.filename == '':
        return render_template_string(HTML_TEMPLATE, error="No selected file")
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        patient_name = request.form.get('patient_name', 'Anonymous').strip() or 'Anonymous'
        
        try:
            value, label, confidence = predict(filepath)
            save_prediction_db(patient_name, filepath, value, label, confidence)
            return render_template_string(
                HTML_TEMPLATE, 
                prediction=label, 
                value=value, 
                confidence=round(confidence, 2),
                patient=patient_name
            )
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
