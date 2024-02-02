from flask import Flask, render_template, request, redirect, url_for
import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Initialize OpenAI and Spotify API clients
openai.api_key = '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'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='8998a20291f146e7afab85de2930444d',
                                               client_secret='ea8d036482ab4aebbe735cf19d0bfd1a',
                                               redirect_uri='http://localhost:5001/',
                                               scope='playlist-modify-public'))

def generate_playlist_with_openai(event_details):
    # Prepare prompt for OpenAI
    prompt = f"Create a playlist that lasts {event_details['duration']} minutes long with songs that are suitable for an {event_details['occasion']} at {event_details['location']} during {event_details['datetime']}? The songs should satisfy a {event_details['mood']} setting with a demographic of {event_details['demographics']} and have a variety of artists similar to {event_details['artists']}. In your response do not even say 'Sure', just begin your response immediately with the first song title. Your response should look exactly like this: Song Title by Song Artist"

    # Call OpenAI's API to generate playlist
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful chatbot"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )

    # Extract song titles and artists from OpenAI's response
    generated_playlist = response['choices'][0]['message']['content'].strip().split('\n')

    return generated_playlist

def create_spotify_playlist(occasion):
    # Create a new playlist on Spotify
    playlist = sp.user_playlist_create(user='g7r4rw3do0x3qgxarzpvmf007', name=f'{occasion} Playlist', public=True)
    return playlist['id']

def add_tracks_to_playlist(playlist_id, tracks):
    # Add tracks to the Spotify playlist
    track_uris = []
    added_tracks = set()  # Set to keep track of added tracks and avoid duplicates
    for track in tracks:
        # Check if the track has the expected format "Song Title by Song Artist"
        if ' by ' not in track:
            # Skip tracks that do not have the expected format
            continue
        # Split each song into title and artist
        title, artist = track.split(' by ')
        # Check if the track is already added to avoid duplicates
        if track in added_tracks:
            continue
        # Search for the track on Spotify
        search_result = sp.search(q=f"track:{title} artist:{artist}", type='track', limit=1)
        if search_result['tracks']['items']:
            track_uri = search_result['tracks']['items'][0]['uri']
            track_uris.append(track_uri)
            added_tracks.add(track)  # Add track to the set of added tracks
    sp.playlist_add_items(playlist_id, track_uris)






    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    
    # Fetch event details from the form
    event_details = {
        'occasion': request.form['occasion'],
        'location': request.form['location'],
        'datetime': request.form['datetime'],
        'mood': request.form['mood'],
        'demographics': request.form['demographics'],
        'artists': request.form['artists'],
        'duration': int(request.form['duration'])
    }

    # Generate playlist using OpenAI
    playlist = generate_playlist_with_openai(event_details)

    # Create a new playlist on Spotify
    playlist_id = create_spotify_playlist(event_details['occasion'])

    # Add tracks to the Spotify playlist
    add_tracks_to_playlist(playlist_id, playlist)

    # Generate the Spotify playlist URL
    playlist_url = f'https://open.spotify.com/playlist/{playlist_id}'

    # Redirect to the Spotify playlist URL
    return redirect(playlist_url)







@app.route('/generate_workshop_ideas', methods=['POST'])
def generate_workshop_ideas():
    purpose = request.form['purpose']
    interests = request.form['interests']
    
    # Prompt GPT-3.5-turbo with user inputs
    prompt = f"Please list out various workshop ideas for my event given that the purpose of the event is to {purpose} and the particular interests of the event attendees are {interests}. In your response do not even say 'Sure', just begin the workshop ideas immediately. "

    # Call OpenAI's API to generate workshop ideas
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful chatbot"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    
    workshop_ideas = response['choices'][0]['message']['content']
    return render_template('workshop_ideas.html', workshop_ideas=workshop_ideas)

@app.route('/generate_itinerary', methods=['POST'])
def generate_itinerary():
    start_date = request.form['start_date']
    start_time = request.form['start_time']
    end_date = request.form['end_date']
    end_time = request.form['end_time']
    event_name = request.form['event_name']
    speakers_workshops = request.form['speakers_workshops']

    # Prompt GPT-3.5-turbo with user inputs
    prompt = f"Please create a complete itinerary for my event given that the event starts on {start_date} at {start_time} and ends on {end_date} at {end_time}. The name of my event is {event_name}. The speakers and workshops that make up the itinerary are {speakers_workshops}. In your response do not even say 'Sure', just begin the itinerary immediately. "

    # Call OpenAI's API to generate itinerary
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful chatbot"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )

    itinerary = response['choices'][0]['message']['content']
    return render_template('itinerary.html', itinerary=itinerary)

@app.route('/connect_with_sponsors', methods=['POST'])
def connect_with_sponsors():
    event_name = request.form['event_name']
    event_purpose = request.form['event_purpose']
    current_sponsors = request.form['current_sponsors']
    event_location = request.form['event_location']


    prompt = f"Please provide other possible sponsors for my event and directly list out the contact information of each potential sponsor in your response. In your response do not even say 'Sure', just begin the sponsors immediately. The name of the event is {event_name}, the purpose of the event is {event_purpose}, and the location of the event is {event_location}. We may already have these sponsors: {current_sponsors}."

    # Call OpenAI's API to generate sponsor suggestions
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful chatbot"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )

    sponsor_suggestions = response['choices'][0]['message']['content']
    return render_template('sponsors.html', sponsor_suggestions=sponsor_suggestions)







if __name__ == '__main__':
    app.run(debug=True, port=5002) 

