# Partner's microservice

import requests
from bs4 import BeautifulSoup
import json
from flask import Flask, request, json

#setup flask
app = Flask(__name__)

@app.route('/wiki', methods=['GET'])
def display_info():

    """in the browser type /wiki?arg1= DESIRED CRYPTO
    should return a json object
    """
    crypto = request.args['arg1']

    #get URL
    page = requests.get("https://en.wikipedia.org/w/index.php?search=" + crypto)

    #scrape webpage
    soup = BeautifulSoup(page.content, 'html.parser')

    #display status code
    print(page.status_code)

    #load first three paragraphs and then return such
    dump0 = (soup.find_all('p')[0].get_text())
    dump1 = (soup.find_all('p')[1].get_text())
    dump2 = (soup.find_all('p')[2].get_text())


    return {"0": dump0, "1": dump1, "2": dump2}

if __name__ == "__main__":
    app.run(port=9000)
