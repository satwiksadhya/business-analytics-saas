from flask import Flask, request, jsonify
from ml_engine import validate_and_clean_csv, run_forecasting_pipeline
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Business Analytics SaaS Backend Running"

@app.route("/upload", methods=["POST"])
def upload_file():
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    df, message = validate_and_clean_csv(file_path)
    
    if df is None:
        return jsonify({"error": message}), 400
    
    results = run_forecasting_pipeline(df)
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)