import requests
import json
import speech_recognition as sr
from pymongo import MongoClient
import time
headers = {'Content-Type': 'application/json'}
api_endpoint='http://localhost:5000/api/v1.0'

def api_post(endpoint,payload=None):
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post('{}{}'.format(api_endpoint, endpoint), data=json.dumps(payload),headers=headers)
    return response

def api_get(endpoint, params=None):
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get('{}{}'.format(api_endpoint, endpoint), params=params,headers=headers)
    return response


def test_yt_api(url):
    data_obj = {
        'url':url
    }
    response = api_post('/yt',data_obj)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        return None

def test_getter(j_id):
    response = api_get('/yt/'+str(j_id))
    return response.content

def main():
    job_id = test_yt_api(str('https://www.youtube.com/watch?v=L5uNIbtAKxc'))
    print job_id['result']['job_id']
    j_id = job_id['result']['job_id']
    wait_time = 10
    while (wait_time > 0):
        if test_getter(j_id) == 'Nay':
            print "Waiting for response to come back.." + str(wait_time) + ' tries left..'
            print test_getter(j_id)
            wait_time = wait_time - 1
            time.sleep(2)
        else:
            print "found response!"
            print test_getter(j_id)
            wait_time = 0



if __name__ == '__main__':
    main()