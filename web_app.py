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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automated Diabetic Retinopathy | AI Diagnostic System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b1120;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
        }

        body { 
            font-family: 'Inter', sans-serif; 
            background: radial-gradient(circle at top left, #1e293b, var(--bg-color)); 
            color: var(--text-main);
            margin: 0; 
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .navbar {
            width: 100%;
            padding: 24px 0;
            text-align: center;
            background: rgba(11, 17, 32, 0.6);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--card-border);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .navbar h1 {
            margin: 0;
            font-weight: 800;
            font-size: 28px;
            letter-spacing: -0.5px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .navbar p {
            margin: 5px 0 0 0;
            font-size: 14px;
            color: var(--text-muted);
            font-weight: 300;
        }

        .container { 
            width: 100%;
            max-width: 600px; 
            margin: 50px 20px; 
            background: var(--card-bg); 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); 
            border: 1px solid var(--card-border);
            backdrop-filter: blur(20px);
            transition: transform 0.3s ease;
        }

        .container:hover {
            transform: translateY(-5px);
        }

        .form-group { margin-bottom: 25px; }
        
        label { 
            display: block; 
            font-weight: 600; 
            margin-bottom: 10px; 
            font-size: 14px;
            color: #e2e8f0;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        input[type="text"], input[type="file"] { 
            width: 100%; 
            padding: 14px 16px; 
            box-sizing: border-box; 
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            color: white;
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
        }

        input[type="file"] {
            padding: 10px;
            cursor: pointer;
        }

        input[type="file"]::file-selector-button {
            background: var(--card-border);
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin-right: 15px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            transition: background 0.2s;
        }

        input[type="file"]::file-selector-button:hover {
            background: rgba(255,255,255,0.15);
        }

        button { 
            width: 100%;
            background: linear-gradient(135deg, var(--accent), #2563eb); 
            color: white; 
            border: none; 
            padding: 16px 20px; 
            cursor: pointer; 
            border-radius: 10px; 
            font-size: 16px; 
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3);
            transition: all 0.3s ease;
        }

        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(56, 189, 248, 0.5);
        }

        button:active {
            transform: translateY(1px);
        }

        .sample-link {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 12px;
            display: inline-block;
        }

        .sample-link a {
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s;
        }

        .sample-link a:hover {
            color: white;
            text-decoration: underline;
        }

        .result { 
            margin-top: 30px; 
            padding: 25px; 
            background: rgba(15, 23, 42, 0.8); 
            border-radius: 12px;
            border-left: 5px solid var(--accent);
            animation: fadeIn 0.5s ease-out;
        }

        .result h3 {
            margin-top: 0;
            font-size: 18px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .result p {
            font-size: 16px;
            margin: 10px 0;
            line-height: 1.5;
        }

        .result strong {
            color: white;
            font-weight: 600;
        }
        
        .class-val {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 800;
            font-size: 14px;
            background: rgba(255,255,255,0.1);
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Dynamic Colors for Severity */
        .severity-0 { border-left-color: #22c55e; } /* Green */
        .severity-1 { border-left-color: #eab308; } /* Yellow */
        .severity-2 { border-left-color: #f97316; } /* Orange */
        .severity-3 { border-left-color: #ef4444; } /* Red */
        .severity-4 { border-left-color: #b91c1c; } /* Dark Red */

    </style>
</head>
<body>
    <div class="navbar">
        <h1>PADRSS AI</h1>
        <p>Precision Automated Diabetic Retinopathy Surveillance System</p>
    </div>

    <div class="container">
        <form action="/predict" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label>Patient ID / Name</label>
                <input type="text" name="patient_name" placeholder="Enter patient identifier..." autocomplete="off"/>
            </div>
            <div class="form-group">
                <label>Retinal Fundus Scan</label>
                <input type="file" name="file" required accept="image/png, image/jpeg, image/jpg"/>
                <span class="sample-link">
                    No scan available? <a href="https://github.com/Heerav04/PADRSS-Precision-Automated-Diabetic-Retinopathy-Surveillance-System/tree/main/dataset/colored_images" target="_blank">Download a test sample</a>.
                </span>
            </div>
            <button type="submit">Run Diagnostics</button>
        </form>
        
        {% if prediction %}
        <div class="result severity-{{ value }}">
            <h3>Diagnostic Report</h3>
            <p><strong>Patient:</strong> {{ patient }}</p>
            <p><strong>Assessment:</strong> <span class="class-val">{{ prediction }}</span> (Class {{ value }})</p>
            <p><strong>AI Confidence:</strong> {{ confidence }}%</p>
        </div>
        {% endif %}
        
        {% if error %}
        <div class="result" style="border-left-color: #ef4444;">
            <p style="color: #fca5a5;"><strong>System Error:</strong> {{ error }}</p>
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
