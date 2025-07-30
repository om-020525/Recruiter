from flask import Flask, render_template, request, session, redirect, url_for
import json
from datetime import datetime
from Test.api_calls_dummy import fetch_jobs, fetch_applications, filter_candidates, add_resumes
#from api_calls import fetch_jobs, fetch_applications, filter_candidates, add_resumes
import web_logger

app = Flask(__name__)

def load_secrets():
    try:
        with open('secrets.json', 'r') as file:
            file_data = json.load(file)
            return file_data
    except Exception as e:
        raise Exception(f"ERR_001 : Error loading secrets.json : {str(e)}")

secrets = load_secrets()

app.secret_key = secrets.get('flask_secret_key', 'fallback_secret_key_CHANGE_ME')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            ashby_token = request.form.get('ashby_token')
            google_token = request.form.get('google_token')
            
            web_logger.INFO("=== RECEIVED TOKENS ===")
            web_logger.INFO(f"Ashby Token: {ashby_token}")
            web_logger.INFO(f"Google Token: {google_token}")
            
            session['ashby_token'] = ashby_token
            session['google_token'] = google_token
            
            return redirect(url_for('resume_downloader'))
        except Exception as e:
            raise Exception(f"ERR_002 : Error processing token input : {str(e)}")
    
    return render_template('token_input.html', 
                         google_client_id=secrets.get('google_client_id', ''),
                         google_scopes=secrets.get('google_scopes', ''))

@app.route('/resume_downloader', methods=['GET', 'POST'])
def resume_downloader():
    ashby_token = session.get('ashby_token')
    google_token = session.get('google_token')
    
    if not ashby_token or not google_token:
        return f"No tokens found \n Ashby: {ashby_token} \n Google: {google_token}"
        #return redirect(url_for('index'))
    
    if request.method == 'POST':
        selected_job_id = request.form.get('job_id')
        filter_by_date = request.form.get('filter_by_date')
        filter_date = request.form.get('filter_date')
        application_status = request.form.get('application_status')
        
        # Create filters dictionary for API call
        filters = {
            'jobId': selected_job_id,
            'limit': 100  # Default limit from API docs
        }
        
        # Add status filter if selected
        if application_status:
            filters['status'] = application_status
            
        # Add date filter if enabled and date provided
        if filter_by_date == 'on' and filter_date:
            try:
                date_obj = datetime.strptime(filter_date, '%Y-%m-%d')
                unix_timestamp_ms = int(date_obj.timestamp() * 1000)
                filters['createdAfter'] = unix_timestamp_ms
            except ValueError:
                raise Exception(f"ERR_003 : Invalid date format: {filter_date}")
        
       
        
        web_logger.INFO(f"=== FORM SUBMISSION ===")
        web_logger.INFO(f"Job ID: {selected_job_id}")
        web_logger.INFO(f"Date Filter Enabled: {filter_by_date}")
        web_logger.INFO(f"Selected Date: {filter_date if filter_by_date else 'Not selected'}")
        web_logger.INFO(f"Application Status: {application_status if application_status else 'All Statuses'}")
        web_logger.INFO(f"API Filters: {filters}")
        
        
        try:
            # Fetch & filter candidates
            candidates, raw_data = fetch_applications(ashby_token, filters)
            web_logger.INFO(f"=== FETCHED {len(candidates)} CANDIDATES ===")
        except Exception as e:
            raise Exception(f"ERR_004 : Error fetching candidates: {str(e)}")
        filtered_candidates = filter_candidates(ashby_token, candidates) 
        web_logger.INFO(f"=== APPLIED FILTERS ===")

        web_logger.INFO(f"Original count: {len(candidates)}")
        for candidate in candidates:
            web_logger.INFO(f"Candidate: {candidate['name']} (ID: {candidate['id']})")
        
        web_logger.INFO(f"Filtered count: {len(filtered_candidates)}")
        for candidate in filtered_candidates:
            web_logger.INFO(f"Candidate: {candidate['name']} (ID: {candidate['id']})")
        
        try:
            # Fetch URL, Download and Upload resumes
            web_logger.INFO(f"=== STARTING RESUME UPLOAD ===")
            download_results = add_resumes(ashby_token, google_token, filtered_candidates)
            
            successful_uploads = 0
            failed_uploads = 0
            
            for result in download_results:
                if result['error'] is None:
                    successful_uploads += 1

                    web_logger.INFO(f"✓ SUCCESS: {result['candidate_name']} (ID: {result['candidate_id']})")
                    web_logger.INFO(f"  - File ID: {result['upload_info']['file_id']}")
                    web_logger.INFO(f"  - File Size: {result['upload_info']['file_size']} bytes")
                else:
                    failed_uploads += 1
                    
                    web_logger.INFO(f"✗ FAILED: {result['candidate_name']} (ID: {result['candidate_id']})")
                    web_logger.INFO(f"  - Error: {result['error']}")
            
            web_logger.INFO(f"=== RESUME UPLOAD COMPLETE ===")
            web_logger.INFO(f"Successful uploads: {successful_uploads}")
            web_logger.INFO(f"Failed uploads: {failed_uploads}")
            web_logger.INFO("========================")
            
            success_message = f"Resume upload completed! {successful_uploads} successful, {failed_uploads} failed out of {len(filtered_candidates)} candidates."

            
            return render_template('resume_downloader.html', jobs=session.get('jobs', []), 
                                 selected_job_id=selected_job_id, candidates=filtered_candidates,
                                 success_message=success_message)
        except Exception as e:
            error_message = f"Error uploading resumes: {str(e)}"
            web_logger.INFO(f"=== RESUME UPLOAD ERROR ===")
            web_logger.INFO(error_message)
            return render_template('resume_downloader.html', jobs=session.get('jobs', []), 
                                 selected_job_id=selected_job_id, error=error_message)
    
    try:
        jobs, raw_data = fetch_jobs(ashby_token)
        session['jobs'] = jobs  
        
        web_logger.INFO(f"=== FETCHED {len(jobs)} JOBS ===")
        for job in jobs:
            web_logger.INFO(f"Job: {job['name']} (ID: {job['id']})")
        
        return render_template('resume_downloader.html', jobs=jobs)
        
    except Exception as e:
        error_message = f"Error fetching jobs: {str(e)}"
        web_logger.INFO(f"=== ERROR FETCHING JOBS ===")
        web_logger.INFO(error_message)
        return render_template('resume_downloader.html', jobs=[] , error=error_message)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
