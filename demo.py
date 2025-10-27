import librosa
import numpy as np
import json
import re

filename = "trial.mp3"
y, sr = librosa.load(filename)
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0]
energy = np.mean(librosa.feature.rms(y=y))
centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
zcr = np.mean(librosa.feature.zero_crossing_rate(y))
chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
print(tempo,energy,centroid,zcr,chroma)
import google.generativeai as genai

genai.configure(api_key = "AIzaSyAr4rrUYUFOgv7iSlqqamy7Fob6CL4Kd4k")
prompt = f"""
Accept the user input of a song, using the features tempo, energy, centroid, zcr, chroma, group the songs based on mood into the following categories:- music to calm (soft,relaxing music), music to boost your mood(loud, peppy, upbeat melodies, happy & positive mood), music to focus (neutral mood, good for while studying or working, should be apt background music)

Audio Features:
-Tempo:{tempo:.2f}BPM
-Energy (RMS): {energy:.4f}
-Special Centroid: {centroid:.2f}
-Zero Crossing Rate: {zcr:.4f}
-Chroma Mean: {chroma:.4f}

Return *only* valid JSON in this exact shape, with no extra text or code fences:

{{
  "song_analysis": {{
    "category": "<Analyse the song, classify it into one of the three categories.>",
    "explanation": "<explain the reasons for the choice. Use an informal register, conversational, friendly tone to explain the features of the chosen song that make it suited to achieving one of the three purposes of calming, boosting mood, and enabling focus. Don't add any technical details or numbers, only reply in 2-3 sentence>"
  }}
}}

**IMPORTANT**: Respond with **only** the JSON object. **Do not** include any explanations, markdown, code fences, or extra text.
"""

model = genai.GenerativeModel('gemini-2.5-pro')
response = model.generate_content(prompt)
print(response.text)

match = re.search(r'(\{.*\})', response.text, re.DOTALL)
if not match:
    raise ValueError("No JSON object found in response")

json_str = match.group(1)
print(json_str)
data = json.loads(json_str)

print(data["song_analysis"]["category"])
print(data["song_analysis"]["explanation"])


# import json
# import firebase_admin
# from firebase_admin import credentials, firestore

# # 1. Initialize the Firebase Admin SDK
# cred = credentials.Certificate('eeg-music-minimalism-firebase-adminsdk-fbsvc-80885f8561.json')
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# songs= [
#   {
#     "name": "258Hz Meditation",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2F258Hz_meditation.jpg?alt=media&token=d5431b81-4dae-489e-abcf-2380e68207e9",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2F258Hz_meditation.jpg?alt=media&token=d5431b81-4dae-489e-abcf-2380e68207e9",
#     "genre": "calm"
#   },
#   {
#     "name": "360",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/360.mp3?alt=media&token=fbb0e704-c018-4b34-91a3-17a9f984ef09",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2F360.jpg?alt=media&token=389ae798-7655-4a60-b2d0-94fa1579223e",
#     "genre": "boost"
#   },
#   {
#     "name": "Born to de",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/Born%20To%20Die.mp3?alt=media&token=918d726a-ca9d-4a24-9535-c9ee365905cf",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fborn_to_die.jpg?alt=media&token=4531915f-3e2a-405d-b3fa-ee113e062a7c",
#     "genre": "boost"
#   },
#   {
#     "name": "B2B",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/Charli%20XCX%20-%20B2b%20(Official%20Audio).mp3?alt=media&token=23ee7921-94ea-430b-81a2-ebec6a1096e5",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fb2b.jpg?alt=media&token=952b3dd5-96e7-4cae-92c0-143ebf462c01",
#     "genre": "focus"
#   },
#   {
#     "name": "Everybody Talks",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/Everybody%20Talks.mp3?alt=media&token=f47dae23-7b5c-41e9-9e1b-7b44f093eb04",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Feverybody_talks.jpg?alt=media&token=0fad8014-5458-47d8-b1c1-822596ea9291",
#     "genre": "calm"
#   },
#   {
#     "name": "I Love It",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/Icona%20Pop%20-%20I%20Love%20It%20(Feat.%20Charli%20XCX)%20%20%5BAudio%5D.mp3?alt=media&token=8dcfe9ca-8d00-49a4-adfa-3f59f04ad9e5",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fi_love_it.jpg?alt=media&token=8a540ea1-5041-43e7-bac3-761371fa8dca",
#     "genre": "focus"
#   },
#   {
#     "name": "Illegal",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/PinkPantheress%20-%20Illegal%20(Official%20Audio).mp3?alt=media&token=a19118f4-464e-4ca0-823c-dd2bb281e0c9",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fillegal.jpg?alt=media&token=bd01ee9c-2354-494a-87c1-d3744c4dd0cd",
#     "genre": "boost"
#   },
#   {
#     "name": "Calming Sounds",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/calming-94427%20(1).mp3?alt=media&token=829f494d-e61d-4eaa-b019-f285d7d96f93",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fcalming_sounds.png?alt=media&token=2821d4cf-5687-450c-a753-8fcd7bfa0209",
#     "genre": "calm"
#   },
#   {
#     "name": "Deep Focus",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/deep-focus-113552%20(2).mp3?alt=media&token=fdba669b-c72a-400a-979d-bff4daffd467",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fdeep_focus.jpg?alt=media&token=3ff02694-687a-416e-9d25-083d8a5b9f09",
#     "genre": "focus"
#   },
#   {
#     "name": "Focus Zone Mellow Lofi",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/focus-zone-relax-mellow-lofi-music-259701%20(1).mp3?alt=media&token=0f5eef6d-6376-4f3d-8f25-6d32fc507ba4",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Ffocus_zone_mellow_lofi.jpg?alt=media&token=8d4b8379-f3b0-4422-b1e8-ac8bce92dee0",
#     "genre": "focus"
#   },
#   {
#     "name": "Good Night Cozy Lofi",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/good-night-lofi-cozy-chill-music-160166.mp3?alt=media&token=4fe0e76f-5d78-4f40-997f-fa851893f12b",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fgood_night_cozy_lofi.jpg?alt=media&token=a22a7de5-d185-4331-8585-4a84091151bd",
#     "genre": "calm"
#   },
#   {
#     "name": "Instrumental ambient calming",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/instrumental-ambient-calming-269887%20(1).mp3?alt=media&token=5c0548ea-3d0f-4b12-b4ac-e3aa0a12f05b",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2FChatGPT%20Image%20Jul%2015%2C%202025%2C%2003_08_00%20PM.png?alt=media&token=dda7e8c2-66b6-48a1-af1a-fdbe893be0bf",
#     "genre": "calm"
#   },
#   {
#     "name": "Lofi Ambiental Music",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/lofi-ambiental-music-for-study-141222%20(1).mp3?alt=media&token=8d6658f3-1357-46a8-8d4f-aa3b00c3470d",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Flofi_ambiental%20_music.jpg?alt=media&token=fa41b74f-8f73-440e-8d7b-6773369d3793",
#     "genre": "boost"
#   },
#   {
#     "name": "Lofi Hiphop Chill",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/lofi-hiphop-chill-background-music-298551%20(1).mp3?alt=media&token=5628a663-295a-4a11-a810-667545677d5b",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Flofi_hiphop_chill.jpg?alt=media&token=c68a1da5-f088-4cb4-a07b-d0e17e39336e",
#     "genre": "boost"
#   },
#   {
#     "name": "Peaceful Guitar Serenade",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/peaceful-serenade-guitar-instrumental-by-jesse-quinn-163655%20(1).mp3?alt=media&token=70d1bf87-4beb-4338-b5be-907f641adb62",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fpeaceful_guitar_serenade.jpg?alt=media&token=069ba51f-093e-48f5-83b3-7d60b2cc4658",
#     "genre": "boost"
#   },
#   {
#     "name": "Instrumental Piano",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/piano-instrumental-306208%20(1).mp3?alt=media&token=3cf1b976-8860-4733-93f0-fd0b7b5375cf",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Finstrumental_piano.jpg?alt=media&token=4a961146-8074-4f06-b533-bc0a1990703e",
#     "genre": "calm"
#   },
#   {
#     "name": "Piano Waltz",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/piano-waltz-elegant-and-graceful-instrumental-music-285601%20(1).mp3?alt=media&token=6c447ab4-1491-4a25-ac36-58b8e58c5343",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fpiano_waltz.jpg?alt=media&token=10c8b2cf-d311-4828-84d1-e65640318a99",
#     "genre": "boost"
#   },
#   {
#     "name": "Pure Theta 47Hz Soundscape",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/pure-theta-4-7hz-with-deep-focus-soundscapes-351362%20(1).mp3?alt=media&token=60c6c502-a51f-4979-b66d-3202cf8711a2",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fpure_theta_47Hz_soundscape.jpg?alt=media&token=ffafeb5b-284e-42b9-8540-e34eb3bf497e",
#     "genre": "focus"
#   },
#   {
#     "name": "Satisfying Lofi for Focus",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/satisfying-lofi-for-focus-study-amp-working-242103%20(1).mp3?alt=media&token=3eccabbf-3db6-4f1c-9f6f-ae20d789df1e",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fsatisfying_lofi_for_focus.jpg?alt=media&token=1b3f3edd-99b6-4688-813c-853c2b94d0ef",
#     "genre": "calm"
#   },
#   {
#     "name": "Study",
#     "song_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/study-110111%20(1).mp3?alt=media&token=7d9beb33-17b0-4e2e-89f5-5d68348fb196",
#     "image_url": "https://firebasestorage.googleapis.com/v0/b/eeg-music-minimalism.firebasestorage.app/o/album%20covers%2Fstudy.jpg?alt=media&token=b049c658-a18f-4d8d-9d07-95c70a8675e1",
#     "genre": "focus"
#   }
# ]


# # 3. Upload each song as a document
# for song in songs:
#     # Option A: Auto-generate document ID
#     db.collection('songs').add(song)
#     # Option B: Use song name as the document ID (slugify if needed)
#     # doc_id = song['name'].lower().replace(' ', '_')
#     # db.collection('songs').document(doc_id).set(song)

# print("All songs have been uploaded to Firestore!")
