from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

PROMETHEUS_SERVER = 'http://39.105.63.18:30908'
# test
@app.route('/open', methods=['GET'])
def open_door():
    return jsonify(u'芝麻开门！')

def get_time_series_data(query, start_time, end_time, step='15s'):
    response = requests.get(f'{PROMETHEUS_SERVER}/api/v1/query_range', params={
        'query': query,
        'start': start_time,
        'end': end_time,
        'step': step
    })
    return response.json()['data']['result']


def normalize_data(data):
    # Extract values from the data and perform normalization
    values = [float(sample[1]) for result in data for sample in result['values']]
    min_val = min(values)
    max_val = max(values)
    if max_val - min_val == 0:  # Avoid division by zero
        return data
    # Apply normalization
    for result in data:
        for sample in result['values']:
            sample[1] = (float(sample[1]) - min_val) / (max_val - min_val)
    return data

@app.route('/get_data', methods=['POST'])
def get_data():
    data = request.get_json()
    starttime = data.get('starttime')
    endtime = data.get('endtime')
    query = data.get('query')
    
    # response = get_time_series_data(query, starttime, endtime, step='15s')
    # # print(response)
    # return jsonify(response)

    response = requests.get(f'{PROMETHEUS_SERVER}/api/v1/query_range', params={
        'query': query,
        'start': starttime,
        'end': endtime,
        'step': '15s'
    }).json()['data']['result']

    # Normalize the data before returning
    normalized_data = normalize_data(response)
    return jsonify(normalized_data)



    
if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(port=5000)