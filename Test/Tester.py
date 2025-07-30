import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
import api_calls

ashby_token = "NO_TEST"
google_token = "NO_TEST"
job_id = "NO_TEST"
candidate_id = "NO_TEST"
file_handle = "NO_TEST" 
file_url = "NO_TEST"

#file_url = 'https://images.pexels.com/photos/674010/pexels-photo-674010.jpeg?cs=srgb&dl=pexels-anjana-c-169994-674010.jpg&fm=jpg'

# Get jobs
get_jobs = False

# Prepare filters for fetch_applications
filters = {
    'jobId': job_id,
    'limit': 100,
    #'status': 'Hired',
    #'dateFilter': '2025-01-01',
    }

# Prepare test file data for upload testing
file_name = "Test_Resume.pdf"
sample_file_path = os.path.join(parent_dir, 'samples', 'sample_[pdf.hex].txt')
with open(sample_file_path, 'r') as file:
    file_data = file.read()
    test_file_data = {
        'content': file_data.encode() if isinstance(file_data, str) else file_data,
        'content_type': 'application/pdf',
        'file_size': len(file_data)
    }

if ashby_token != "NO_TEST" and get_jobs:    
    jobs, raw_data = api_calls.fetch_jobs(ashby_token)
    print(jobs)

if ashby_token != "NO_TEST" and job_id != "NO_TEST":
    candidates, raw_data = api_calls.fetch_applications(ashby_token, filters)
    print(candidates)

if ashby_token != "NO_TEST" and candidate_id != "NO_TEST":
    candidate_info, raw_data = api_calls.fetch_candidate_info(ashby_token, candidate_id)
    print(candidate_info)

if ashby_token != "NO_TEST" and file_handle != "NO_TEST":
    file_info, raw_data = api_calls.fetch_file_info(ashby_token, file_handle)
    print(file_info)

if file_url != "NO_TEST":
    file_data = api_calls.download_file(file_url)
    print(file_data)

if google_token != "NO_TEST":
    upload_info, upload_data = api_calls.upload_file(google_token, file_name, test_file_data)
    print(upload_info)












