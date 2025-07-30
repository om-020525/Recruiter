import requests
import json
import base64
from datetime import datetime

def fetch_jobs(ashby_token):
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

def fetch_applications(ashby_token, filters):
    try:
        url = "https://api.ashbyhq.com/application.list"
        encoded_token = base64.b64encode(f"{ashby_token}:".encode()).decode()
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {encoded_token}"
        }

        response = requests.post(url, headers=headers, json=filters)
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

def fetch_candidate_info(ashby_token, candidate_id):
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
        resume_file_handle = None
        
        try:
            resume_file = results['resumeFileHandle']
            resume_file_handle = resume_file['handle']
        except KeyError:
            try:
                file_handles = results['fileHandles']
                for file_handle in file_handles:
                    file_name = file_handle['name']
                    handle = file_handle['handle']
                    
                    if 'resume' in file_name.lower():
                        resume_file_handle = handle
                        break
            except KeyError:
                resume_file_handle = None #pass

        candidate_info = {
            'name': candidate_name,
            'id': candidate_id,
            'resume_file_handle': resume_file_handle
        }
        
        return candidate_info, data
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"API request failed: {str(e)}")

def fetch_file_info(ashby_token, file_handle):
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
        file_url = results['url']
        file_info = { 'url': file_url }
        
        return file_info, data
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"API request failed: {str(e)}")

def download_file(file_url):
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        
        content = response.content
        headers = response.headers
        content_type = headers['content-type']
        file_size = len(content)
        
        file_data = {
            'content': content,
            'content_type': content_type,
            'file_size': file_size
        }

        return file_data
        
    except (requests.exceptions.RequestException, KeyError) as e:
        raise Exception(f"File download failed: {str(e)}") 

def upload_file(google_token, file_name, file_data):
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
        
        upload_data = upload_response.json()
    
        # Return upload info
        upload_info = {
            'file_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'upload_success': True
        }

        data = { 'metadata_data': metadata_data, 'upload_data': upload_data }
        
        return upload_info, data
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"File upload failed: {str(e)}") 
   
def filter_candidates(ashby_token, candidates):
    filtered_candidates = []

    for candidate in candidates:
        candidate_info, data = fetch_candidate_info(ashby_token, candidate['id'])
        if candidate_info.get('resume_file_handle') is not None:
            filtered_candidates.append(candidate_info)
    
    return filtered_candidates

def add_resumes(ashby_token, google_token, filtered_candidates):
    results = []
    for candidate in filtered_candidates:
        candidate_name = candidate.get('name')
        candidate_id = candidate.get('id')
        file_handle = candidate.get('resume_file_handle')
        
        
        try:
            # Skip candidates without file handle
            if not file_handle:
                result = {'error': 'No resume file handle found'}
                results.append(result)
                continue
            
            # Step 1: Fetch file info from Ashby
            file_info, raw_file_data = fetch_file_info(ashby_token, file_handle)
            file_url = file_info['url']
            
            # Step 2: Download file from URL
            file_data = download_file(file_url)
            
            # Step 3: Create appropriate filename
            file_name = f"{candidate_name.replace(' ', '_')}_{candidate_id}_resume.pdf"
            
            # Step 4: Upload to Google Drive
            upload_info, upload_metadata = upload_file(google_token, file_name, file_data)

            result = {
                'candidate_name': candidate_name,
                'candidate_id': candidate_id,
                'file_info': file_info,
                'upload_info': upload_info,
                'error': None
            }
        except Exception as e:
            result = {'error': str(e)}
        
        results.append(result)
    
    return results 

