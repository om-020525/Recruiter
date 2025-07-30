import requests
import json
import base64
import os

def fetch_jobs_from_ashby(ashby_token):
    try:
        # Read sample data instead of making API call
        sample_file_path = os.path.join('samples', 'sample_[job.list].json')
        with open(sample_file_path, 'r') as f:
            data = json.load(f)
        
        results = data['results']
        jobs = []
        for job in results:
            title = job['title']
            job_id = job['id']
            job_info = {
                'name': title,
                'id': job_id
            }
            jobs.append(job_info)
        return jobs, data
        
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"Sample data loading failed: {str(e)}")

def fetch_applications_from_ashby(ashby_token, job_id):
    try:
        # Read sample data instead of making API call
        sample_file_path = os.path.join('samples', 'sample_[candidate.list].json')
        with open(sample_file_path, 'r') as f:
            data = json.load(f)
        
        results = data['results']
        candidates = []
        for candidate in results:
            candidate_name = candidate['name']
            candidate_id = candidate['id']
            
            candidate_info = {
                'name': candidate_name,
                'id': candidate_id
            }
            candidates.append(candidate_info)
        
        return candidates, data
        
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"Sample data loading failed: {str(e)}")

def fetch_candidate_info_from_ashby(ashby_token, candidate_id):
    try:
        # Read sample data instead of making API call
        sample_file_path = os.path.join('samples', 'sample_[candidate.info].json')
        with open(sample_file_path, 'r') as f:
            data = json.load(f)
        
        results = data['results']
        candidate_name = results['name']
        candidate_id = results['id']
        
        candidate_info = {
            'name': candidate_name,
            'id': candidate_id,
            'resume_file_handler': None
        }
        
        try:
            resume_file = results['resumeFileHandle']
            resume_handle = resume_file['handle']
            candidate_info['resume_file_handler'] = resume_handle
        except KeyError:
            try:
                file_handles = results['fileHandles']
                for file_handle in file_handles:
                    file_name = file_handle['name']
                    handle = file_handle['handle']
                    
                    if 'resume' in file_name.lower():
                        candidate_info['resume_file_handler'] = handle
                        break
            except KeyError:
                candidate_info['resume_file_handler'] = None
        
        return candidate_info, data
        
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"Sample data loading failed: {str(e)}")

def fetch_file_info_from_ashby(ashby_token, file_handle):
    try:
        # Read sample data instead of making API call
        sample_file_path = os.path.join('samples', 'sample_[file.info].json')
        with open(sample_file_path, 'r') as f:
            data = json.load(f)
        
        results = data['results']
        success = data['success']       
        file_url = results['url']
        file_info = {
            'file_handle': file_handle,
            'file_url': file_url,
            'success': success
        }
        
        return file_info, data
        
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"Sample data loading failed: {str(e)}")

def download_file_from_url(file_url):
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        
        content = response.content
        headers = response.headers
        content_type = headers['content-type']
        file_size = len(content)
        
        return {
            'content': content,
            'content_type': content_type,
            'file_size': file_size
        }
        
    except (requests.exceptions.RequestException, KeyError) as e:
        raise Exception(f"File download failed: {str(e)}") 

def upload_file_to_google_drive(google_token, file_data, file_name):
    try:
        file_content = file_data['content']
        content_type = file_data['content_type']
        file_size = file_data['file_size']
        
        # Step 1: Create file with metadata
        metadata_url = "https://www.googleapis.com/drive/v3/files"
        
        metadata_headers = {
            "Authorization": f"Bearer {google_token}",
            "Content-Type": "application/json"
        }
        
        metadata_payload = {
            "name": file_name,
            "mimeType": content_type
        }
        
        metadata_response = requests.post(metadata_url, headers=metadata_headers, json=metadata_payload)
        metadata_response.raise_for_status()
        
        metadata_data = metadata_response.json()
        file_id = metadata_data['id']
        
        # Step 2: Upload the actual file content
        upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
        
        upload_headers = {
            "Authorization": f"Bearer {google_token}",
            "Content-Type": content_type
        }
        
        upload_response = requests.patch(upload_url, headers=upload_headers, data=file_content)
        upload_response.raise_for_status()
        
        # Return upload info
        upload_info = {
            'file_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'upload_success': True
        }
        
        return upload_info, metadata_data
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"File upload failed: {str(e)}") 

