from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import librosa
import numpy as np
import json
import re

import google.generativeai as genai

import os, tempfile
from werkzeug.utils import secure_filename


# -------------------- Config --------------------
genai.configure(api_key="AIzaSyAr4rrUYUFOgv7iSlqqamy7Fob6CL4Kd4k")
model = genai.GenerativeModel('gemini-2.5-pro')

# pyrebase (Auth)
config = {
  "apiKey": "AIzaSyDCeWPxsqFUHeGVHy2Qelt-VP_GB3X0vAo",
  "authDomain": "eeg-music-minimalism.firebaseapp.com",
  "projectId": "eeg-music-minimalism",
  "databaseURL": "",
  "storageBucket": "eeg-music-minimalism.firebasestorage.app",
  "serviceAccount": "eeg-music-minimalism-firebase-adminsdk-fbsvc-80885f8561.json"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# Firestore (Admin)
cred = credentials.Certificate("eeg-music-minimalism-firebase-adminsdk-fbsvc-80885f8561.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = "replace-this-with-a-strong-secret" 

def current_uid():
    """Return UID from session if logged in, else None."""
    return session.get("uid")

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def _wrap(*args, **kwargs):
        if not current_uid():
            return redirect(url_for("login_page", next=request.path))
        return fn(*args, **kwargs)
    return _wrap

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/analyze")
def analyze_():
    return render_template("test_your_music.html")

@app.route("/listen_now")
def stream_now():
   
    docs = db.collection('songs').stream()
    songs = [doc.to_dict() for doc in docs]

    songs_by_genre = {"calm": [], "boost": [], "focus": []}
    for s in songs:
        genre = s.get("genre", "calm")
        if genre in songs_by_genre:
            songs_by_genre[genre].append({
                "name": s.get("name", "Untitled"),
                "artist": s.get("artist", ""),
                "song_url": s.get("song_url", ""),
                "image_url": s.get("image_url", ""),
                "genre": genre
            })

    uid = session.get("uid")
    user = None
    if uid:
        try:
            snap = db.collection('users').document(uid).get()
            if snap.exists:
                user = snap.to_dict() or {}
            else:
                db.collection('users').document(uid).set(
                    {"created_at": firestore.SERVER_TIMESTAMP}, merge=True
                )
                user = {}

            user.setdefault("first_name", user.get("name", ""))
            user.setdefault("avatar_url", "/static/images/default_avatar.png")
            user["uid"] = uid
        except Exception as e:
            app.logger.exception("Failed to fetch user profile for %s", uid)
            user = {"uid": uid, "first_name": "", "avatar_url": "/static/images/default_avatar.png"}

    return render_template(
        "listen_now.html",
        songs_by_genre=songs_by_genre,
        user=user,
        is_logged_in=bool(uid)
    )

@app.route("/login_page")
def login_page():
    return render_template("login.html")

@app.route("/register_page")
def register_page():
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():
  
    data = request.form.to_dict() or (request.get_json(silent=True) or {})
    print(data)
    email = data.get("email")
    password = data.get("password")
    print(data)
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print(user)
        session["uid"] = user["localId"]
        print("done")
        if request.is_json:
            return jsonify({"uid": user["localId"], "next": url_for("home")})
        return redirect(url_for("listen_now"))
    except Exception:
        print("error")
        if request.is_json:
            return jsonify({"error": "Login failed"}), 400
        return redirect(url_for("login_page"))

@app.route("/register", methods=["POST"])
def register():
    data = request.form.to_dict() or (request.get_json(silent=True) or {})
    email = data.get("email")
    password = data.get("password")
    try:
        user = auth.create_user_with_email_and_password(email, password)
        uid = user["localId"]
        session["uid"] = uid
        db.collection("users").document(uid).set(
            {"email": email, "created_at": firestore.SERVER_TIMESTAMP},
            merge=True
        )
        print("registered")
        return redirect(url_for("choose_avatar"))
    except Exception:
        if request.is_json:
            print("error")
            return jsonify({"error": "Registration failed"}), 400
        return redirect(url_for("register_page"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/choose_avatar", methods=["GET"])
@login_required
def choose_avatar():
    print("in")
    return render_template("selectAvatar.html")

@app.route("/choose_avatar", methods=["POST"])
@login_required
def save_avatar():
    payload = request.get_json(silent=True) or request.form.to_dict()
    avatar = (payload or {}).get("avatar")
    allowed = {
        "pop_princess",
        "goth_rock_emo",
        "dance_party_edm",
        "mid_west_country_girl"
    }
    if avatar not in allowed:
        return jsonify({"error": "Invalid avatar"}), 400

    uid = current_uid()
    db.collection("users").document(uid).set({"avatar": avatar}, merge=True)

    if request.is_json:
        return jsonify({"status": "ok", "next": url_for("stream_now")})
    return redirect(url_for("stream_now"))

@app.route("/test_music", methods=["GET","POST"])
def test_music():
    data = None
    if request.method == "POST":
        file = request.files.get('track')
        if file and file.filename:
            safe_name = secure_filename(file.filename)
            _, ext = os.path.splitext(safe_name)
            if not ext:
                ext = ".wav"  
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=tempfile.gettempdir()) as tmp:
                    file.save(tmp.name)
                    tmp_path = tmp.name

                y, sr = librosa.load(tmp_path, sr=None, mono=True)
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                tempo = float(librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0])
                energy = float(np.mean(librosa.feature.rms(y=y)))
                centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
                zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
                chroma = float(np.mean(librosa.feature.chroma_stft(y=y, sr=sr)))

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

                response = model.generate_content(prompt)
                match = re.search(r'(\{.*\})', response.text or "", re.DOTALL)
                if not match:
                    raise ValueError("No JSON object found in response")
                data = json.loads(match.group(1))

            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

    return render_template("result.html", result=data or {})

@app.route('/api/update_last_played', methods=['POST'])
def update_last_played():
    uid = current_uid()
    if not uid:
        return jsonify({"error": "unauthorized"}), 401
    track = request.get_json()
    db.collection('users').document(uid).set({'last_played': track}, merge=True)
    return ('', 204)

@app.route('/api/get_last_played')
def get_last_played():
    uid = current_uid()
    if not uid:
        return jsonify({"error": "unauthorized"}), 401
    doc = db.collection('users').document(uid).get()
    if doc.exists and 'last_played' in doc.to_dict():
        return jsonify(doc.to_dict()['last_played'])
    return ('', 404)

@app.route('/api/add_to_playlist', methods=['POST'])
def add_to_playlist():
    uid = current_uid()
    if not uid:
        return jsonify({"error": "unauthorized"}), 401
    track = request.get_json()
    db.collection('users').document(uid).collection('playlist').add(track)
    return ('', 204)

@app.route('/playlist')
@login_required
def playlist_page():
    uid = current_uid()
    docs = db.collection('users').document(uid).collection('playlist').stream()
    saved = [d.to_dict() for d in docs]
    return render_template('playlist.html', saved=saved)


@app.route("/about")
def about():
    return render_template("about_us.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
