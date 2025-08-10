from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'secret'

# Load student data
df = pd.read_excel("students.xlsx")
df["rollNumber"] = df["rollNumber"].astype(str)
df = df.sort_values(by="rollNumber").reset_index(drop=True)

# File explorer base
BASE_DIR = os.path.abspath(".")

# Helper to calculate percentage
def calculate_percentage(student_data):
    marks = {}
    for sub in ["Data Structures", "Algorithms", "Database Systems", "Operating Systems", "Computer Networks"]:
        if sub in student_data:
            marks[sub] = student_data[sub]
    for col in df.columns:
        if col.startswith("sub_"):
            marks[col[4:]] = student_data[col]
    return round(sum(marks.values()) / len(marks)) if marks else 0

@app.route("/", methods=["GET", "POST"])
def index():
    student = None
    students_summary = []
    current_path = "."

    # File Explorer
    contents = []
    for f in os.listdir(current_path):
        contents.append({
            "name": f,
            "path": os.path.join(current_path, f).replace("\\", "/"),
            "is_dir": os.path.isdir(os.path.join(current_path, f))
        })

    # Handle POST Search
    if request.method == "POST":
        roll = request.form.get("rollNumber", "").strip()
        start_roll = request.form.get("startRollNumber", "").strip()
        end_roll = request.form.get("endRollNumber", "").strip()

        # Single Student
        if roll:
            session["current_roll"] = roll
            row = df[df["rollNumber"] == roll]
            if not row.empty:
                data = row.iloc[0].to_dict()
                marks = {}
                for sub in ["Data Structures", "Algorithms", "Database Systems", "Operating Systems", "Computer Networks"]:
                    if sub in data:
                        marks[sub] = data[sub]
                for col in df.columns:
                    if col.startswith("sub_"):
                        marks[col[4:]] = data[col]
                percentage = calculate_percentage(data)
                student = {
                    "rollNumber": data["rollNumber"],
                    "hallTicket": data["hallTicket"],
                    "firstName": data["firstName"],
                    "lastName": data["lastName"],
                    "phoneNumber": data["phoneNumber"],
                    "parentPhone": data["parentPhone"],
                    "city": data["city"],
                    "photo": url_for('static', filename=f'photos/{data.get("photo")}') if data.get("photo") else '',
                    "marks": marks,
                    "percentage": percentage
                }

        # Range Search
        elif start_roll and end_roll:
            students_range = df[(df["rollNumber"] >= start_roll) & (df["rollNumber"] <= end_roll)]
            for _, row in students_range.iterrows():
                students_summary.append({
                    "rollNumber": row["rollNumber"],
                    "firstName": row["firstName"],
                    "lastName": row["lastName"],
                    "percentage": calculate_percentage(row)
                })

    # Always show all students by default (if not using range)
    if not students_summary:
        for _, row in df.iterrows():
            students_summary.append({
                "rollNumber": row["rollNumber"],
                "firstName": row["firstName"],
                "lastName": row["lastName"],
                "percentage": calculate_percentage(row)
            })

    return render_template("quantum-student-portal.html",
                           student=student,
                           students=students_summary,
                           contents=contents,
                           current_path=current_path)

@app.route("/next")
def next_student():
    student = None
    current_path = "."
    contents = []
    for f in os.listdir(current_path):
        contents.append({
            "name": f,
            "path": os.path.join(current_path, f).replace("\\", "/"),
            "is_dir": os.path.isdir(os.path.join(current_path, f))
        })

    current_roll = session.get("current_roll")
    if current_roll:
        idx = df[df["rollNumber"] == current_roll].index
        if not idx.empty and idx[0] + 1 < len(df):
            next_row = df.iloc[idx[0] + 1]
            session["current_roll"] = next_row["rollNumber"]
            data = next_row.to_dict()
            marks = {}
            for sub in ["Data Structures", "Algorithms", "Database Systems", "Operating Systems", "Computer Networks"]:
                if sub in data:
                    marks[sub] = data[sub]
            for col in df.columns:
                if col.startswith("sub_"):
                    marks[col[4:]] = data[col]
            percentage = calculate_percentage(data)
            student = {
                "rollNumber": data["rollNumber"],
                "hallTicket": data["hallTicket"],
                "firstName": data["firstName"],
                "lastName": data["lastName"],
                "phoneNumber": data["phoneNumber"],
                "parentPhone": data["parentPhone"],
                "city": data["city"],
                "photo": url_for('static', filename=f'photos/{data.get("photo")}') if data.get("photo") else '',
                "marks": marks,
                "percentage": percentage
            }

    return render_template("quantum-student-portal.html",
                           student=student,
                           students=None,
                           contents=contents,
                           current_path=current_path)

@app.route("/browse/<path:req_path>")
def browse_files(req_path):
    abs_path = os.path.join(BASE_DIR, req_path)
    if not os.path.exists(abs_path):
        return "Path not found", 404

    files = os.listdir(abs_path)
    contents = []
    for f in files:
        full_path = os.path.join(abs_path, f)
        contents.append({
            "name": f,
            "path": os.path.join(req_path, f).replace("\\", "/"),
            "is_dir": os.path.isdir(full_path)
        })

    return render_template("quantum-student-portal.html",
                           contents=contents,
                           current_path=req_path,
                           student=None,
                           students=None)

if __name__ == "__main__":
    app.run(debug=True)
