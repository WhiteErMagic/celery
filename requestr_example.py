import requests

response = requests.post('http://localhost:5000/upscale', files={'image_1': open('lama_300px.png', 'rb')})
print(response.status_code)

new_file = response.json()['output_path']
response = requests.get(f'http://localhost:5000/processed/{new_file}')
print(response.status_code)