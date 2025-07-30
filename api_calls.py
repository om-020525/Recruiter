import requests
import json
import base64

def fetch_jobs_from_ashby(ashby_token):
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
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"API request failed: {str(e)}")

def fetch_applications_from_ashby(ashby_token, job_id):
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
        results = data['results']
        candidates = []
        for application in results:
            candidate = application['candidate']
            candidate_name = candidate['name']
            candidate_id = candidate['id']
            
            candidate_info = {
                'name': candidate_name,
                'id': candidate_id
            }
            candidates.append(candidate_info)
        
        return candidates, data
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"API request failed: {str(e)}")

def fetch_candidate_info_from_ashby(ashby_token, candidate_id):
    try:
        url = "https://api.ashbyhq.com/candidate.info"
        encoded_token = base64.b64encode(f"{ashby_token}:".encode()).decode()
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {encoded_token}"
        }
        
        payload = {
            "candidateId": candidate_id
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
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
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"API request failed: {str(e)}")

def fetch_file_info_from_ashby(ashby_token, file_handle):
    try:
        url = "https://api.ashbyhq.com/file.info"
        encoded_token = base64.b64encode(f"{ashby_token}:".encode()).decode()
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {encoded_token}"
        }
        
        payload = {
            "fileHandle": file_handle
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        results = data['results']
        success = data['success']       
        file_url = results['url']
        file_info = {
            'file_handle': file_handle,
            'file_url': file_url,
            'success': success
        }
        
        return file_info, data
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"API request failed: {str(e)}")

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

