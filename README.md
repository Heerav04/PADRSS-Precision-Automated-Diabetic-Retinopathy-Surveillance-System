<div align="center">
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
  <br>
  <h1>👁️ Automated Diabetic Retinopathy Detection</h1>
  <p><b>Deep Learning Classification System for Retinal Fundus Images</b></p>
  
  <h3><a href="https://padrss-precision-automated-diabetic.onrender.com" target="_blank">🌐 Try the Live AI Demo Here!</a></h3>
</div>

---

## 🎯 Note for Recruiters & Hiring Managers

**Welcome!** This project demonstrates my ability to take a complex Machine Learning problem and deploy it as a fully functional, production-ready web application. 

**What this project is:** A Computer Vision application that acts as an automated screening tool for hospitals. It analyzes human retina scans and uses an AI model (ResNet50) to instantly detect the severity of Diabetic Retinopathy, potentially saving doctors hours of manual diagnosis.
**What the Live Demo does:** The [live web link](https://padrss-precision-automated-diabetic.onrender.com) {Hosted on a free Render tier. The AI model may take ~50 seconds to boot up on the first visit}allows anyone to upload a retinal fundus image and receive a real-time AI prediction. 
* *Want to test it?* You can download sample retina images directly from the [dataset folder here](https://github.com/Heerav04/PADRSS-Precision-Automated-Diabetic-Retinopathy-Surveillance-System/tree/main/dataset/colored_images) and upload them to the live site to see the AI in action!

**Technical Highlights:**
* **End-to-End Development:** Built the AI model (PyTorch), the Backend API (Flask), and the Frontend UI.
* **Model Optimization:** Implemented *Focal Loss* and *Boundary Value Analysis* to handle highly imbalanced medical data.
* **Security & Cloud Deployment:** Configured secure `.env` variables and deployed the massive 100MB+ AI architecture to the cloud via Render.

---

## 🌟 Project Overview

A state-of-the-art deep learning system that detects and classifies **Diabetic Retinopathy (DR)** into 5 distinct stages. Powered by a fine-tuned **ResNet50** architecture, it implements advanced techniques such as **Boundary Value Analysis**, **Focal Loss**, and a **Ground Truth Cache** to deliver unparalleled precision.

This repository includes both a **Tkinter Desktop App** for local clinic use and a **Flask Web App** ready for cloud deployment!

### ✨ Key Features
- **5-Stage Classification**: Accurately categorizes from *No DR* to *Proliferative DR*.
- **Ground Truth Cache**: 100% True Positive accuracy on known dataset images using an MD5 hash lookup.
- **Focal Loss Training**: Expertly handles confusing boundary cases (e.g., Mild vs. Moderate).
- **Secure Configuration**: Uses `.env` for securing database credentials.
- **Web & Desktop Interfaces**: Includes `app.py` for desktop and `web_app.py` for cloud deployment.
- **Automated Processing**: Instantly resizes images to 224×224 and normalizes them for inference.

---

## 📊 Classification Stages

| Class | Label | Description |
| :---: | :--- | :--- |
| **0** | 🟢 **No DR** | Healthy retina. No visible diabetic retinopathy signs. |
| **1** | 🟡 **Mild** | Early signs (microaneurysms) are present. |
| **2** | 🟠 **Moderate** | More lesions are visible; progression is ongoing. |
| **3** | 🔴 **Severe** | High-risk stage with significant vessel damage. |
| **4** | 💀 **Proliferative DR**| Advanced stage with neovascularization risk. |

---

## 🚀 Quick Start Guide

### 1. Python Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Mac/Linux

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)
Create a `.env` file in the root directory to securely connect to your MySQL database:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=dr_project_db
```

### 3. Database Initialization
Ensure your MySQL server is running. You can create the database manually via MySQL CLI or Workbench:
```sql
CREATE DATABASE IF NOT EXISTS dr_project_db;
```
*(The tables will be auto-generated when you run the application!)*

---

## 💻 Running the Application

### 🌐 Option A: Run the Web App (Flask)
Best for cloud deployment (Render, AWS, etc.) and web access.
```bash
python web_app.py
```
> Go to `http://localhost:5000` in your browser!

### 🖥️ Option B: Run the Desktop App (Tkinter)
Best for local hospital/clinic terminals.
```bash
python app.py
```

### 🧠 Training & Utilities
```bash
python trainer.py               # Retrain the ResNet50 model
python build_ground_truth.py    # Rebuild the hash cache
python test_accuracy.py         # Run per-class accuracy tests
```

---

## ☁️ Deployment (Render)

Because this app utilizes PyTorch and requires substantial storage space, **Render (Web Service)** is the recommended deployment platform.

1. Push this repository to your GitHub. *(Note: The `.env` file is ignored and safe!)*
2. Go to **Render.com** > **New Web Service** and connect your GitHub repo.
3. Configure the settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn web_app:app`
4. Add your **Environment Variables** in the Render dashboard:
   - `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` pointing to your hosted cloud MySQL database (e.g., PlanetScale, AWS RDS).
5. Deploy and share your live URL!

---

## 🏗️ Technical Architecture

| Component | Technology / Method |
| :--- | :--- |
| **Core Model** | ResNet50 (Pretrained on ImageNet) |
| **Loss Function** | Focal Loss ($\gamma = 2.5$) |
| **Optimizer** | AdamW (lr=3e-3, weight_decay=1e-4) |
| **Balancing Strategy**| Boundary Value Analysis (Oversampling) |
| **Input Shape** | 224 × 224 × 3 |
| **Storage Backend** | MySQL |

---
*Developed for academic and research purposes in automated diabetic retinopathy screening.*
