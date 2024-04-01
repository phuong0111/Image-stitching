import shutil
from flask import Flask, render_template, request, redirect, send_file, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import zipfile
import sys
from stitched import stitched
from overlay import overlay

app = Flask(__name__)
CORS(app)

# Configure upload folders
XRAY_FOLDER = "Data/Xray-image"
OPTICAL_FOLDER = "Data/Optical-image"
OUTPUT_FINAL_FOLDER = "Output/Final"
OUTPUT_STITCHED_FOLDER = "Output/SIFT"
DATASET_NAME = "Test-1"
DOWNLOAD_ZIP = "Download-zip"
XRAY_STITCHING = f"{DOWNLOAD_ZIP}/xray-stitching"
FINAL_OVERLAY = f"{DOWNLOAD_ZIP}/final-overlay"
ALLOWED_EXTENSIONS = {"zip", "rar"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def list_dataset_name():
    return [_ for _ in os.listdir(OPTICAL_FOLDER) if _ != ".DS_Store"]


@app.route("/", methods=["GET", "POST"])
def root():
    return render_template("index.html")

@app.route("/uploads-file", methods=["GET", "POST"])
def upload_file():
    xray_message = ""
    optical_message = ""
    if request.method == "POST":
        # X-ray Upload
        if "xray_file" in request.files:
            xray_file = request.files["xray_file"]
            if xray_file and allowed_file(xray_file.filename):
                filename = secure_filename(xray_file.filename)
                filepath = os.path.join(app.config["XRAY_FOLDER"], filename)
                xray_file.save(filepath)
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(app.config['XRAY_FOLDER']))
                    os.remove(filepath)  # Remove zip file
                xray_message = f'File "{filename}" uploaded and extracted!'
            else:
                xray_message = (
                    "Invalid X-ray file format. Allowed extensions: "
                    + ", ".join(ALLOWED_EXTENSIONS)
                )

        # Optical Upload
        if "optical_file" in request.files:
            optical_file = request.files["optical_file"]
            if optical_file and allowed_file(optical_file.filename):
                filename = secure_filename(optical_file.filename)
                filepath = os.path.join(app.config["OPTICAL_FOLDER"], filename)
                optical_file.save(filepath)
                with zipfile.ZipFile(filepath, "r") as zip_ref:
                    zip_ref.extractall(os.path.join(app.config["OPTICAL_FOLDER"]))
                    os.remove(filepath)  # Remove zip file
                optical_message = f'File "{filename}" uploaded and extracted!'
            else:
                optical_message = (
                    "Invalid Optical file format. Allowed extensions: "
                    + ", ".join(ALLOWED_EXTENSIONS)
                )

    return render_template(
        "upload.html", xray_message=xray_message, optical_message=optical_message
    )


# @app.route("/process-image", methods=["GET", "POST"])
# def process_images():
#     if request.method == 'GET':
#         print("abbcbcb")
#         return render_template("process.html", datasets=list_dataset_name())  # Pass datasets to template
#     if request.method == "POST":
#         if 'dataset' in request.form:
#             stitched(request.form['dataset'])
#             overlay(request.form["dataset"], 0.2, 0.8)
#         return render_template("process.html", datasets=list_dataset_name())


@app.route("/process-image", methods=["GET", "POST"])
def process_images():
    if request.method == "GET":
        print("abbcbcb")
        return render_template(
            "process.html", datasets=list_dataset_name()
        )  # Pass datasets to template
    if request.method == "POST":
        if "dataset" in request.form:
            try:
                dataset = request.form["dataset"]
                stitched(dataset)
                overlay(dataset, 0.2, 0.8)
                if os.path.exists("result.zip"):
                    os.remove(f"result.zip")
                if os.path.exists(XRAY_STITCHING) == False:
                    os.mkdir(XRAY_STITCHING)
                if os.path.exists(FINAL_OVERLAY) == False:
                    os.mkdir(FINAL_OVERLAY)
                shutil.copytree(f"{OUTPUT_FINAL_FOLDER}/{DATASET_NAME}", f"{FINAL_OVERLAY}/{DATASET_NAME}")
                shutil.copytree(f"{OUTPUT_STITCHED_FOLDER}/{DATASET_NAME}", f"{XRAY_STITCHING}/{DATASET_NAME}")
                shutil.make_archive("result", "zip", DOWNLOAD_ZIP)
                shutil.rmtree(f"{XRAY_STITCHING}")
                shutil.rmtree(f"{FINAL_OVERLAY}")

                return send_file(
                    "result.zip",
                    as_attachment=True,
                    mimetype="image/jpeg",
                )  # Download as JPEG
            except Exception:
                return render_template(
                    "process.html",
                    datasets=list_dataset_name(),
                    error_message="Image processing failed.",
                )
        else:
            return render_template(
                "process.html",
                datasets=list_dataset_name(),
                error_message="Missing dataset selection.",
            )


if __name__ == "__main__":
    # Create upload folders if they don't exist
    os.makedirs(XRAY_FOLDER, exist_ok=True)
    os.makedirs(OPTICAL_FOLDER, exist_ok=True)
    app.config["XRAY_FOLDER"] = XRAY_FOLDER
    app.config["OPTICAL_FOLDER"] = OPTICAL_FOLDER
    app.config["CORS_HEADERS"] = 'Content-Type'
    app.secret_key = "xuanphuong"
    app.run(debug=True)
