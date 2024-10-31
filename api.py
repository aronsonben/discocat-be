import time
import json
import requests
import random
from flask import Flask
from flask import request
from datetime import datetime
from spot import spot

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<p>test world</p>"

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@app.route("/api/view")
def view_all():
    data = view()
    return {'artists': data}

# save_artist("https://open.spotify.com/artist/5pKCCKE2ajJHZ9KAiaK11H")
@app.route("/api/save", methods=['POST', 'GET'])
def save():
    error = None
    data = {}
    if request.method == 'POST':
        # do the thing
        print('post')
        incoming = request.get_json()
        print(incoming['uri'])
        save_artist(incoming['uri'])
        data = view()
        return {'artists': data}
    else: 
        error = 'Invalid save input'
        return {'artists': error}

@app.route("/api/delete", methods=['POST', 'GET'])
def delete():
    error = None
    data = {}
    if request.method == 'POST':
        # do the thing
        print('post')
        incoming = request.get_json()
        print(incoming['id'])
        dr = delete_artist(incoming['id'])
        if dr is True:
            data = view()
            return {'artists': data}
        else:
            return {'artists': None}
    else: 
        error = 'Invalid save input'
        return {'artists': error}


# =============================== #


# Return all data for viewing
def view():
    db = {}
    with open('artists.json') as f:
        db = json.load(f)
    return db


###
# Saves the specified artist to the database
# 'artist' param must be a Spotify URI
###
def save_artist(artist):
    error = None

    # 0. Get URI and find Artist data (name & follower count)
    uri = str(artist).split('/')[4]
    artist_data = spot(uri)
    
    # 1. Open JSON file
    db = {}
    with open('artists.json') as f:
        db = json.load(f)

    # 2. Read JSON file & get artist list
    artists = db['artists']
    
    # 3. Check if artist exists. Return if it does
    for a in artists:
        if a['name'] == artist_data['name']:
            print('Artist Already Exists')
            return False
      
    # 4. If not, proceed to create artist object (id, count, timestamp)
    count = get_count(uri)
    date_added = datetime.now().replace(microsecond=0).strftime("%m/%d/%Y, %H:%M:%S")
    new_artist = {
        'id': round(random.random()*1000000,7),
        'name': artist_data['name'],
        'count': count,
        'followers': artist_data['followers'],
        'date': date_added,
        'tags': []
    }
  
    # 5. Add artist obj to JSON
    artists.append(new_artist)
    db['artists'] = artists
    updated_db = json.dumps(db, indent=4)
    
    # 6. Write to JSON file
    with open('artists.json', 'w') as f:
        f.write(updated_db)
    return True


# Delete a single artist by id
def delete_artist(id):
    db = {}
    with open('artists.json') as f:
        db = json.load(f)

    found = find_artist_by_id(db, id)
    if not found:
        return False
    db['artists'][:] = [d for d in db['artists'] if d.get('id') != id]
    updated_db = json.dumps(db)
    return save_db(updated_db)


# ====== Auxilliary Functions ============ #

# Return artist object if found in Db, otherwise return False
def find_artist_by_id(db, id):
    for a in db['artists']:
        if a['id'] == id:
            return a
    return False

# Pass in JSON database and write to file
def save_db(updated_db):
    with open('artists.json', 'w') as f:
        f.write(updated_db)
    return True

### 
# Function to retrieve count from Spotify API
# Takes in a Spotify URI
def get_count(artist_uri):
    # artist_uri = '3TVXtAsR1Inumwj472S9r4'
    # print('getting uri: ', artist_uri)
    request_url = f'http://127.0.0.1:8000/grab/{artist_uri}'
    r = requests.get(request_url)
    if r.status_code == 200:
        return int(r.text)
    else:
        return False