from __future__ import unicode_literals
import youtube_dl
from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
import json
import requests


class API():
    @staticmethod
    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""


    def text_extractor(d):
        mongo = MongoClient()
        if d['status'] == 'finished':
            id = API.find_between(d['filename'],'./tmp/','.webm')
            key = {
                '_id':id
            }
            data = d
            data['filename'] = data['filename'].replace('.webm','.wav')
            result = mongo.yt_db['yt_collection'].update(
                key,
                data, upsert=True)
            print result

    tmp_folder = "./tmp/"
    get_filename_options = {
        'format':'bestaudio/best',
        'extractaudio': True,
        'audioformat' : 'wav',
        'noplaylist': True,
        'quiet': True,
        'outtmpl':tmp_folder+'%(id)s.%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            } 
        ],
        'no-warnings':True,
        'progress_hooks':[text_extractor]
    }
    app = Flask('ytt-api-server')
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    mongo_config = {
        'host': 'localhost',
        'port': 27017
    }

    mongo = MongoClient(mongo_config['host'],int(mongo_config['port']))

    def __init__(self):
        pass

    @staticmethod
    @app.route('/api/v1.0/yt', methods=['POST'])
    def yt_analyzer():
        results = {}
        url = request.json['url']
        try:
            myt = youtube_dl.YoutubeDL(API.get_filename_options)
            print myt.download([str(url)])
            results['output'] = "Success!"
        except Exception as ex:
            print ex
            results['output'] = "Failure"

        return jsonify({'result': results})


    @staticmethod
    @app.errorhandler(404)
    @cross_origin()
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    def run(self,debug=False,port=5000):
        self.app.run(port=port, debug=debug,host='0.0.0.0', threaded=True)


ab = API()
ab.run(True)