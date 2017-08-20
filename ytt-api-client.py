import requests
import json
import speech_recognition as sr
from pymongo import MongoClient

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

def main():
    print test_yt_api(str('https://www.youtube.com/watch?v=_3JZRxVPuew'))
    mongo = MongoClient()
    yt_col = mongo.yt_db.yt_collection.find_one({'_id':'_3JZRxVPuew'})

    audio_file = str(yt_col['filename'])
    print audio_file
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)

    print r.recognize_sphinx(audio)


if __name__ == '__main__':
    main()