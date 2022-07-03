import sys
sys.path.append('/twitter-data-extractor')
sys.path.append('/database')

from flask import Flask, request
from flask import jsonify
from flask_cors import CORS

import sqlalchemy

app = Flask(__name__)
CORS(app)

@app.route('/')
def Main():
    return 'Welcome to the API!'

@app.route('/api/twits/partial', methods=['POST'])
def get_twits():
    if request.method == "POST":
        dataEx = DataExtraction('twitter_keys.json')
        language = request.form["lang"]
        count = request.form["count"]
        q = request.form["q"]

        params = {
        "q": q,
        "geocode": "",
        "count": int(count),
        "result_type": "mixed",
        "lang": language,
        "tweet_mode" : "extended"
        }
        
        try:
            response = dataEx.twitter_request('https://api.twitter.com/1.1/search/tweets.json', params)
            result = dataEx.extract_twit_data(response["statuses"])
            return jsonify(result)
        except Exception as e:
            return str(e)
    else:
        return "Error. Not a post request."

@app.route('/api/twits/all', methods=['POST'])
def get_all_twits():
    if request.method == "POST":
        try:
            dataEx = DataExtraction('twitter_keys.json')
            language = request.form["lang"]
            count = request.form["count"]
            q = request.form["q"]
            
            response = dataEx.get_all_hashtag_data(q, language, count)
            return jsonify(response)
        except Exception as e:
            return str(e)
        
    else:
        return "Error"

def create_connection():

    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            "mssql+pytds",
            username="sqlserver",
            password="",
            database="",
            host="127.0.0.1",
            port="1433",
        ),
        echo=True,
        pool_pre_ping=True
    )
    return pool

if __name__ == '__main__':
    app.run(debug=True)