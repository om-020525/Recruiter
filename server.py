from flask import Flask, render_template, request, session, redirect, url_for
import json
from Test.api_calls_dummy import fetch_jobs_from_ashby, fetch_applications_from_ashby

app = Flask(__name__)

# Load secrets from file
def load_secrets():
    try:
        with open('secrets.json', 'r') as file:
            file_data = json.load(file)
            return file_data
    except FileNotFoundError:
        print("Warning: secrets.json file not found!")
        return {}

secrets = load_secrets()

# Set Flask secret key from secrets file
app.secret_key = secrets.get('flask_secret_key', 'fallback_secret_key_change_me')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ashby_token = request.form.get('ashby_token')
        google_token = request.form.get('google_token')
        
        print("=== RECEIVED TOKENS ===")
        print(f"Ashby Token: {ashby_token}")
        print(f"Google Token: {google_token}")
        print("=====================")
        
        # Store tokens in session
        session['ashby_token'] = ashby_token
        session['google_token'] = google_token
        
        # Redirect to resume downloader
        return redirect(url_for('resume_downloader'))
    
    return render_template('token_input.html', 
                         google_client_id=secrets.get('google_client_id', ''),
                         google_scopes=secrets.get('google_scopes', ''))

@app.route('/resume_downloader', methods=['GET', 'POST'])
def resume_downloader():
    # Check if tokens are available in session
    ashby_token = session.get('ashby_token')
    google_token = session.get('google_token')
    
    if not ashby_token or not google_token:
        return f"No tokens found \n Ashby: {ashby_token} \n Google: {google_token}"
        #return redirect(url_for('index'))
    
    if request.method == 'POST':
        selected_job_id = request.form.get('job_id')
        print(f"=== SELECTED JOB ID ===")
        print(f"Job ID: {selected_job_id}")
        print("======================")
        
        return render_template('resume_downloader.html', jobs=session.get('jobs', []), 
                             selected_job_id=selected_job_id, success_message="Job ID printed to console!")
    
    try:
        # Fetch jobs from Ashby
        jobs, raw_data = fetch_jobs_from_ashby(ashby_token)
        session['jobs'] = jobs  # Store jobs in session for later use
        
        print(f"=== FETCHED {len(jobs)} JOBS ===")
        for job in jobs:
            print(f"Job: {job['name']} (ID: {job['id']})")
        print("==============================")
        
        return render_template('resume_downloader.html', jobs=jobs)
        
    except Exception as e:
        error_message = f"Error fetching jobs: {str(e)}"
        print(f"=== ERROR ===")
        print(error_message)
        print("=============")
        return render_template('resume_downloader.html', error=error_message, jobs=[])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
