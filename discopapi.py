import json
import random
import requests
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from algorithm import ArtistScraper
from spot import spot

#####################################################
## ## ## ## Initial Setup ## ## ## ## ## ## ## ## ###

discopapi = FastAPI()

origins = [
    "*",
]

discopapi.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ArtistURI(BaseModel):
    uri: str

class ArtistID(BaseModel):
    id: float


#####################################################
## ## ## ## API Endpoints ## ## ## ## ## ## ## ## ###

@discopapi.get("/")
def read_root():
    return {"Root Request": 200}

@discopapi.get("/test")
def test():
    return {"Test Request": 200, "Info": "testing"}

@discopapi.get("/grab/{uri}")
def grab_listeners(uri: Optional[str] = None):
    urilisteners = ArtistScraper("https://open.spotify.com/artist/" + uri)
    urilisteners.get_html()
    return urilisteners.get_monthlyListeners()

@discopapi.get("/discopapi/view")
def view_all():
    data = view()
    return {'artists': data}
    
@discopapi.post("/discopapi/save")
def save(artist: ArtistURI):
    print(artist.uri)
    save_artist(artist.uri)
    data = view()
    return {'artists': data}

@discopapi.post("/discopapi/delete")
def delete(artist_id: ArtistID):
    dr = delete_artist(artist_id.id)
    if dr is True:
        data = view()
        return {'artists': data}
    else:
        return {'artists': None}


#####################################################
## ## ## ## Key Functions ## ## ## ## ## ## ## ## ###

# Return all data for viewing
def view():
    db = {}
    with open('artists.json') as f:
        db = json.load(f)
    return {'artists': db}

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

#####################################################
## ## ## ## Auxilliary Functions ## ## ## ## ## ## ##

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