import api_calls_dummy

ashby_token = "1234567890"
job_id = "1234567890"
candidate_id = "1234567890"
file_handle = "1234567890"
file_url = "https://www.google.com"
file_name = "test.pdf"
file_data = "test.pdf"

jobs, data = api_calls_dummy.fetch_jobs_from_ashby(ashby_token)
print("-------job.list--------")
print(jobs)
print("-------End--------")
#print(data)

applications, data = api_calls_dummy.fetch_applications_from_ashby(ashby_token, job_id)
print("-------candidate.list--------")
print(applications)
print("-------End--------")
#print(data)

candidate_info, data = api_calls_dummy.fetch_candidate_info_from_ashby(ashby_token, candidate_id)
print("-------candidate.info--------")
print(candidate_info)
print("-------End--------")
#print(data)

file_info, data = api_calls_dummy.fetch_file_info_from_ashby(ashby_token, file_handle)
print("-------file.info--------")
print(file_info)
print("-------End--------")
#print(data)

file_url = 'https://images.pexels.com/photos/674010/pexels-photo-674010.jpeg?cs=srgb&dl=pexels-anjana-c-169994-674010.jpg&fm=jpg'
file_data = api_calls_dummy.download_file_from_url(file_url)
print("-------file.data--------")
print(file_data)
print("-------End--------")









