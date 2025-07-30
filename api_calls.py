import requests
import json
import base64
from datetime import datetime
import web_logger

def fetch_jobs(ashby_token):
    try:
        url = "https://api.ashbyhq.com/job.list"
        encoded_token = base64.b64encode(f"{ashby_token}:".encode()).decode()

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {encoded_token}"
        }
        
        all_jobs = []
        all_raw_data = []
        cursor = None
        
        while True:
            # Prepare payload with cursor if available
            payload = {}
            if cursor:
                payload['cursor'] = cursor
            
            response = requests.post(url, headers=headers, json=payload if payload else None)
            response.raise_for_status()
            
            data = response.json()
            all_raw_data.append(data)
            results = data['results']
            
            # Process jobs from this page
            for job in results:
                title = job['title']
                job_id = job['id']
                job_info = {
                    'name': title,
                    'id': job_id
                }
                all_jobs.append(job_info)
            
            # Check if more data is available
            if not data.get('moreDataAvailable', False):
                break
                
            cursor = data.get('nextCursor')
            if not cursor:
                break
                
            web_logger.INFO(f"Fetched {len(results)} jobs, more available. Next cursor: {cursor}")
        
        web_logger.INFO(f"Total jobs fetched: {len(all_jobs)}")
        return all_jobs, all_raw_data
        
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

        all_candidates = []
        all_raw_data = []
        cursor = None
        
        while True:
            # Prepare payload with filters and cursor
            payload = filters.copy()
            if cursor:
                payload['cursor'] = cursor

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            all_raw_data.append(data)
            results = data['results']
            
            # Process applications from this page
            for application in results:
                candidate = application['candidate']
                candidate_name = candidate['name']
                candidate_id = candidate['id']           
                candidate_info = {
                    'name': candidate_name,
                    'id': candidate_id
                }
                
                all_candidates.append(candidate_info)
            
            # Check if more data is available
            if not data.get('moreDataAvailable', False):
                break
                
            cursor = data.get('nextCursor')
            if not cursor:
                break
                
            web_logger.INFO(f"Fetched {len(results)} applications, more available. Next cursor: {cursor}")
        
        web_logger.INFO(f"Total applications fetched: {len(all_candidates)}")
        return all_candidates, all_raw_data
        
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
        web_logger.INFO(f"Candidate info: {data}")
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

def upload_file(google_token, file_name, file_data, folder_id=None):
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
        
        # Add parent folder if specified
        if folder_id:
            metadata_payload["parents"] = [folder_id]
        
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

def create_or_find_folder(google_token, folder_name):
    try:
        # First, search for existing folder
        search_url = "https://www.googleapis.com/drive/v3/files"
        search_headers = {
            "Authorization": f"Bearer {google_token}"
        }
        search_params = {
            "q": f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            "fields": "files(id, name)"
        }
        
        search_response = requests.get(search_url, headers=search_headers, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        # If folder exists, return its ID
        if search_data['files']:
            folder_id = search_data['files'][0]['id']
            return folder_id
        
        # If folder doesn't exist, create it
        create_url = "https://www.googleapis.com/drive/v3/files"
        create_headers = {
            "Authorization": f"Bearer {google_token}",
            "Content-Type": "application/json"
        }
        create_payload = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        
        create_response = requests.post(create_url, headers=create_headers, json=create_payload)
        create_response.raise_for_status()
        create_data = create_response.json()
        folder_id = create_data['id']
        
        return folder_id
        
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"Folder creation/search failed: {str(e)}")
   
def filter_candidates(ashby_token, candidates):
    filtered_candidates = []


    for candidate in candidates:
        candidate_info, data = fetch_candidate_info(ashby_token, candidate['id'])
        if candidate_info.get('resume_file_handle') is not None:
            filtered_candidates.append(candidate_info)
    
    return filtered_candidates

def add_resumes(ashby_token, google_token, filtered_candidates, folder_name):
    results = []
    
    try:
        folder_id = create_or_find_folder(google_token, folder_name)
    except Exception as e:
        folder_id = None
    
    for candidate in filtered_candidates:
        candidate_name = candidate.get('name')
        candidate_id = candidate.get('id')
        file_handle = candidate.get('resume_file_handle')
        result = {
            'candidate_name': candidate_name,
            'candidate_id': candidate_id,
            'file_info': None,
            'upload_info': None,
            'error': None
        }
        
        
        try:
            # Skip candidates without file handle
            if not file_handle:
                result['error'] = 'No resume file handle found'
                results.append(result)
                continue
            
            # Step 1: Fetch file info from Ashby
            file_info, raw_file_data = fetch_file_info(ashby_token, file_handle)
            file_url = file_info['url']
            
            # Step 2: Download file from URL
            file_data = download_file(file_url)
            
            # Step 3: Create appropriate filename
            file_name = f"{candidate_name.replace(' ', '_')}_{candidate_id}_resume.pdf"
            
            # Step 4: Upload to Google Drive (in the specified folder)
            upload_info, upload_metadata = upload_file(google_token, file_name, file_data, folder_id)

            result = {
                'candidate_name': candidate_name,
                'candidate_id': candidate_id,
                'file_info': file_info,
                'upload_info': upload_info,
                'error': None
            }
        except Exception as e:
            result['error'] = str(e)
        
        results.append(result)
    
    return results 

