from wordcloud import WordCloud
from pymongo import MongoClient

mongo = MongoClient()
my_yt = mongo.yt_db.yt_collection.find_one({'_id':"Zsct0T5V03M"})

text = my_yt['speech_text']

wordcloud = WordCloud().generate(text)

wordcloud.to_file('test.png')

            wordcloud = WordCloud(width=636, height=348, stopwords=stopwords, max_words=2000, background_color="white").generate(words[user])
            wordcloud.to_file('/tmp/wc-{}.png'.format(user))
            with open("/tmp/wc-{}.png".format(user), "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())