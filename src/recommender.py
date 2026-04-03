import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.65
    target_tempo_bpm: int = 100


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"


def load_songs(csv_path: str) -> List[Dict]:
    """Parse a CSV file of songs and return a list of dicts with typed numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    int(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


MOOD_AFFINITY = {
    frozenset({"chill", "relaxed"}),
    frozenset({"chill", "focused"}),
    frozenset({"focused", "relaxed"}),
    frozenset({"happy", "relaxed"}),
    frozenset({"intense", "moody"}),
    frozenset({"moody", "chill"}),
    frozenset({"intense", "euphoric"}),
    frozenset({"euphoric", "happy"}),
}

GENRE_AFFINITY = {
    frozenset({"lofi", "ambient"}),
    frozenset({"lofi", "jazz"}),
    frozenset({"pop", "indie pop"}),
    frozenset({"pop", "edm"}),
    frozenset({"rock", "metal"}),
    frozenset({"synthwave", "edm"}),
    frozenset({"r&b", "soul"}),
}


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return a weighted similarity score and human-readable reasons for a single song."""
    reasons = []
    score = 0.0

    # --- Mood (weight 0.35) ---
    pair = frozenset({user_prefs["mood"], song["mood"]})
    if user_prefs["mood"] == song["mood"]:
        mood_score = 0.35
        reasons.append(f"mood match: {song['mood']} (+0.35)")
    elif pair in MOOD_AFFINITY:
        mood_score = 0.175
        reasons.append(f"related mood: {song['mood']} (+0.18)")
    else:
        mood_score = 0.0
    score += mood_score

    # --- Genre (weight 0.25) ---
    pair = frozenset({user_prefs["genre"], song["genre"]})
    if user_prefs["genre"] == song["genre"]:
        genre_score = 0.25
        reasons.append(f"genre match: {song['genre']} (+0.25)")
    elif pair in GENRE_AFFINITY:
        genre_score = 0.125
        reasons.append(f"related genre: {song['genre']} (+0.13)")
    else:
        genre_score = 0.0
    score += genre_score

    # --- Energy (weight 0.20) ---
    energy_score = (1 - abs(song["energy"] - user_prefs["energy"])) * 0.20
    score += energy_score
    reasons.append(f"energy {song['energy']:.2f} (+{energy_score:.2f})")

    # --- Valence (weight 0.15) ---
    valence_score = (1 - abs(song["valence"] - user_prefs["valence"])) * 0.15
    score += valence_score
    reasons.append(f"valence {song['valence']:.2f} (+{valence_score:.2f})")

    # --- Tempo (weight 0.05) ---
    tempo_score = (
        max(0.0, 1 - abs(song["tempo_bpm"] - user_prefs["tempo_bpm"]) / 100)
    ) * 0.05
    score += tempo_score
    reasons.append(f"tempo {song['tempo_bpm']}bpm (+{tempo_score:.2f})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Score every song against user preferences and return the top-k ranked results."""
    scored = [
        (song, score, ", ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:k]
