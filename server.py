from flask import Flask, render_template, request, session, redirect, url_for
import requests
import json
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this to a random secret key

def fetch_jobs_from_ashby(ashby_token):
    """Fetch jobs from Ashby API"""
    try:
        url = "https://api.ashbyhq.com/job.list"
        encoded_token = base64.b64encode(f"{ashby_token}:".encode()).decode()
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {encoded_token}"
        }
        
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        jobs = []
        if 'results' in data:
            for job in data['results']:
                jobs.append({
                    'name': job.get('title', 'No Title'),
                    'id': job.get('id', 'No ID')
                })
        
        return jobs, data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response: {str(e)}")

def fetch_applications_from_ashby(ashby_token, job_id):
    """Fetch applications for a specific job from Ashby API"""
    try:
        url = "https://api.ashbyhq.com/application.list"
        encoded_token = base64.b64encode(f"{ashby_token}:".encode()).decode()
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {encoded_token}"
        }
        
        payload = {
            "jobId": job_id
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract candidates in CandidateName, CandidateId format
        candidates = []
        if 'results' in data:
            for application in data['results']:
                candidate_info = {
                    'name': 'Name not available',
                    'id': 'ID not available'
                }
                
                if application.get('candidate'):
                    candidate = application['candidate']
                    candidate_info['name'] = candidate.get('name', 'Name not available')
                    candidate_info['id'] = candidate.get('id', 'ID not available')
                
                candidates.append(candidate_info)
        
        return candidates, data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ashby_token = request.form.get('ashby_token')
        
        if not ashby_token:
            return render_template('AshbyToken.html', error="Please provide an Ashby token")
        
        try:
            jobs, raw_data = fetch_jobs_from_ashby(ashby_token)
            
            # Store jobs and token in session for later use
            session['jobs'] = jobs
            session['ashby_token'] = ashby_token
            session['raw_jobs_data'] = json.dumps(raw_data, indent=2)
            
            return redirect(url_for('job_selection'))
            
        except Exception as e:
            return render_template('AshbyToken.html', error=str(e))
    
    return render_template('AshbyToken.html')

@app.route('/jobs')
def job_selection():
    jobs = session.get('jobs', [])
    if not jobs:
        return redirect(url_for('index'))
    
    return render_template('job_selection.html', jobs=jobs)

@app.route('/applications', methods=['POST'])
def applications():
    selected_job_name = request.form.get('selected_job')
    jobs = session.get('jobs', [])
    ashby_token = session.get('ashby_token')
    
    if not selected_job_name or not jobs or not ashby_token:
        return redirect(url_for('index'))
    
    # Find the job ID based on selected job name
    selected_job_id = None
    for job in jobs:
        if job['name'] == selected_job_name:
            selected_job_id = job['id']
            break
    
    if not selected_job_id:
        return render_template('job_selection.html', jobs=jobs, error="Invalid job selection")
    
    try:
        candidates, applications_data = fetch_applications_from_ashby(ashby_token, selected_job_id)
        raw_json = json.dumps(applications_data, indent=2)
        
        return render_template('applications.html', 
                             job_name=selected_job_name,
                             job_id=selected_job_id,
                             candidates=candidates,
                             raw_json=raw_json)
        
    except Exception as e:
        return render_template('job_selection.html', jobs=jobs, error=str(e))

@app.route('/results')
def results():
    jobs = session.get('jobs', [])
    raw_json = session.get('raw_jobs_data', '{}')
    
    if not jobs:
        return redirect(url_for('index'))
    
    return render_template('results.html', jobs=jobs, raw_json=raw_json)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
