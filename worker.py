import os
import redis
from rq import Worker, Queue, Connection
from urlparse import urlparse
from pymongo import MongoClient
listen = ['default']
import youtube_dl
import speech_recognition as sr


redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

tmp_folder = "./tmp/"


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
        id = find_between(d['filename'], './tmp/', '.')
        key = {
            '_id': id
        }
        data = d
        print d
        data['filename'] = data['filename'].replace('.webm', '.wav').replace('.m4a','.wav')
        result = mongo.yt_db['yt_collection'].update(
            key,
            data, upsert=True)
        print result

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

def audio_analyzer(filename):
    print "Analyzing audio.."
    audio_file = str(filename)
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        print "Analyzing more audio.."
        audio = r.record(source)
    return r.recognize_sphinx(audio)

def analyze_yt_video(url):
    print "HOLD UPPP"
    yt_id = urlparse(url).query.split('=')[1]
    key = {
        '_id': yt_id
    }
    mongo = MongoClient()
    try:
        yt_col = mongo.yt_db.yt_collection.find_one({'_id': str(yt_id)})
        if yt_col:
            if yt_col.get('speech_text'):
                print "Text found.. returning that instead"
                return yt_col.get('speech_text')
            else:
                print "There's no text, analyzing audio"
                if yt_col.get('filename'):
                    print "Find filename.."
                    yt_col['speech_text'] = audio_analyzer(yt_col.get('filename'))
                    mongo.yt_db.yt_collection.update(key, yt_col, upsert=True)

        else:
            print "Extracting Audio.."

            myt = youtube_dl.YoutubeDL(get_filename_options)
            myt.download([str(url)])
            yt_col = mongo.yt_db.yt_collection.find_one({'_id': str(yt_id)})
            print "No entry exists, analyzing audio"
            yt_col['speech_text'] = audio_analyzer(yt_col.get('filename'))
            print "Getting metadata.."
            yt_col['metadata'] = myt.extract_info(url,download=False)

            mongo.yt_db.yt_collection.update(key, yt_col, upsert=True)


        return yt_col.get('speech_text')

    except Exception as ex:
        print ex
        return {"error": "Failure"}


if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()