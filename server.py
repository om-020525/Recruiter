from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ashby_token = request.form.get('ashby_token')
        
        if not ashby_token:
            return render_template('index.html', error="Please provide an Ashby token")
        
        try:
            # Call Ashby API
            url = "https://api.ashbyhq.com/job.list"
            
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {ashby_token}"
            }
            
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            data = response.json()
            
            # Extract jobs in Name, ID format
            jobs = []
            if 'results' in data:
                for job in data['results']:
                    jobs.append({
                        'name': job.get('title', 'No Title'),
                        'id': job.get('id', 'No ID')
                    })
            
            # Format raw JSON for display
            raw_json = json.dumps(data, indent=2)
            
            return render_template('index.html', jobs=jobs, raw_json=raw_json)
            
        except requests.exceptions.RequestException as e:
            return render_template('index.html', error=f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            return render_template('index.html', error=f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            return render_template('index.html', error=f"An error occurred: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
