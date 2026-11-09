"""
Core logic for the Music Recommender Simulation (VibeFinder 1.0).

Scoring recipe ("Algorithm Recipe"):
    +2.0  genre matches the user's favorite genre
    +1.0  mood matches the user's favorite mood
    +0.0..2.0  energy closeness: 2.0 * (1 - |song.energy - target_energy|)
    +0.0..0.5  acoustic bonus (only when the user prefers acoustic songs)
Songs are scored one at a time, then ranked highest to lowest.
"""

import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple

# Weights live in one place so experiments only need one edit.
WEIGHTS = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 2.0,
    "acoustic": 0.5,
}


@dataclass
class Song:
    """Represents a song and its attributes. Required by tests/test_recommender.py"""
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
    """Represents a user's taste preferences. Required by tests/test_recommender.py"""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile into the dict format used by score_song."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }


class Recommender:
    """OOP implementation of the recommendation logic. Required by tests/test_recommender.py"""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k Song objects for this user, highest score first."""
        prefs = _profile_to_prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda s: score_song(prefs, asdict(s))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable reason string for why a song was scored the way it was."""
        score, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dicts with numeric fields converted."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for field in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against user preferences. Returns (score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    fav_genre = str(user_prefs.get("genre", "")).lower()
    if fav_genre and song["genre"].lower() == fav_genre:
        score += WEIGHTS["genre"]
        reasons.append(f"genre match (+{WEIGHTS['genre']:.1f})")

    fav_mood = str(user_prefs.get("mood", "")).lower()
    if fav_mood and song["mood"].lower() == fav_mood:
        score += WEIGHTS["mood"]
        reasons.append(f"mood match (+{WEIGHTS['mood']:.1f})")

    if "energy" in user_prefs:
        gap = abs(float(song["energy"]) - float(user_prefs["energy"]))
        energy_points = WEIGHTS["energy"] * (1 - gap)
        score += energy_points
        reasons.append(f"energy closeness (+{energy_points:.2f})")

    if user_prefs.get("likes_acoustic") and float(song["acousticness"]) >= 0.6:
        score += WEIGHTS["acoustic"]
        reasons.append(f"acoustic bonus (+{WEIGHTS['acoustic']:.1f})")

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song, sorts highest to lowest, and returns the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    # sorted() returns a new list and leaves the catalog untouched (unlike list.sort()).
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
