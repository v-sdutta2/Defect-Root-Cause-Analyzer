from flask import Flask, request, render_template, send_file, url_for
import pandas as pd
from openai import AzureOpenAI
import time
import threading
import os

app = Flask(__name__)

# setup Azure OpenAI Client
endpoint= os.getenv("ENDPOINT_URL", "https://ado-analysis-pipelines.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "ADO-Pipeline-Analysis-Model")
api_key = os.getenv("api_key", "1e62295240bd4c829fc884a6348efbd4")
client = AzureOpenAI(api_key=api_key, api_version="2024-05-01-preview",azure_endpoint=endpoint)

# Global variable to store the progress and error message
progress = 0
error_message = None

def generate_root_cause(description, close_description):
    prompt = f"Based on the following defect details, generate the most probable root cause in one or two sentences:\n\nDescription: {description}\nClose Description: {close_description}\n\nRoot Cause:"
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error generating root cause"


def process_defects(file_path, priority):
    global progress, error_message
    error_message = None  # Reset error message

    # Read the Excel file
    df = pd.read_excel(file_path)

    # Filter defects based on priority
    if priority != 'All':
        df = df[df['Priority'] == int(priority)]

    # Check if there are no matching defects
    if df.empty:
        error_message = f"No defects found with priority {priority}."
        return None

    # Simulate processing time and generate root cause analysis using Azure OpenAI
    total_defects = len(df)
    for i in range(total_defects):
        time.sleep(0.1)  # Simulate time taken to process each defect
        description = df.iloc[i]['Description']
        close_description = df.iloc[i]['CloseDescription']
        root_cause = generate_root_cause(description, close_description)
        df.at[i, 'Root Cause'] = root_cause
        progress = int((i + 1) / total_defects * 100)

    # Save the result to a new Excel file
    output_file = 'processed_defects.xlsx'
    df.to_excel(output_file, index=False)

    return output_file


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    global progress, error_message
    progress = 0

    # Get the uploaded file and priority
    file = request.files['file']
    priority = request.form['priority']

    # Save the uploaded file
    file_path = 'uploaded_defects.xlsx'
    file.save(file_path)

    # Start processing in a separate thread
    thread = threading.Thread(target=process_defects, args=(file_path, priority))
    thread.start()

    return render_template('progress.html')


@app.route('/progress')
def get_progress():
    global error_message
    if error_message:
        return {'progress': -1, 'error': error_message}

    messages = [
        "Processing defect details...",
        "Analyzing descriptions...",
        "Generating root causes...",
        "Almost there...",
        "Finalizing results..."
    ]
    message_index = min(progress // 20, 4)
    return {'progress': progress, 'message': messages[message_index]}


@app.route('/download')
def download_file():
    return send_file('processed_defects.xlsx', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)