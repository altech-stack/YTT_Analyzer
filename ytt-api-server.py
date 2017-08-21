from __future__ import unicode_literals
import youtube_dl
from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
import json
import requests
from urlparse import urlparse
import sys
from rq import Queue
from rq.job import Job
from worker import conn,analyze_yt_video
import os





class API():
    @staticmethod
    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""


    tmp_folder = "./tmp/"
    app = Flask('ytt-api-server')

    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    q = Queue(connection=conn)

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
        job = API.q.enqueue_call(
            func=analyze_yt_video, args=[url],result_ttl=5000
        )
        results['job_id'] = job.get_id()
        return jsonify({'result': results})

    @staticmethod
    @app.route('/api/v1.0/yt/<job_key>', methods=['GET'])
    def get_results(job_key):
        results = {}

        job = Job.fetch(job_key,connection=conn)
        if job.is_finished:
            return str(job.result),200
        else:
            return 'Nay',202



    @staticmethod
    @app.errorhandler(404)
    @cross_origin()
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    def run(self,debug=False,port=5000):
        self.app.run(port=port, debug=debug,host='0.0.0.0', threaded=True)


ab = API()
ab.run(True)