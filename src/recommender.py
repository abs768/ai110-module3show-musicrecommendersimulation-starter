"""
Core logic for the Music Recommender Simulation (VibeFinder 1.0).

Base scoring recipe ("Algorithm Recipe", Genre-First mode):
    +2.0  genre matches the user's favorite genre
    +1.0  mood matches the user's favorite mood
    +0.0..2.0  energy closeness: 2.0 * (1 - |song.energy - target_energy|)
    +0.0..0.5  acoustic bonus (only when the user prefers acoustic songs)

Advanced features (only scored when the user profile asks for them):
    popularity (0-100), release_decade, mood_tags, instrumentalness, speechiness

Scoring modes use a lightweight Strategy pattern: each ScoringStrategy is a named
set of weights, and score_song() uses whichever strategy it is given.
"""

import csv
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Tuple, Optional

# Default weights (Genre-First). Kept as a module-level dict so experiments.py still works.
WEIGHTS = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 2.0,
    "acoustic": 0.5,
    "popularity": 1.0,
    "decade": 1.0,
    "mood_tags": 0.5,
    "instrumental": 0.5,
    "speechy": 0.5,
}

# Diversity penalties applied while building the top-k list.
ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5


@dataclass
class ScoringStrategy:
    """A named ranking strategy: the weights that score_song should use."""
    name: str
    weights: Dict[str, float]


def _mode(name: str, **overrides: float) -> ScoringStrategy:
    """Builds a strategy from the default weights plus overrides."""
    return ScoringStrategy(name, {**WEIGHTS, **overrides})


SCORING_MODES: Dict[str, ScoringStrategy] = {
    "genre-first": _mode("genre-first"),
    "mood-first": _mode("mood-first", genre=1.0, mood=2.5),
    "energy-focused": _mode("energy-focused", genre=1.0, mood=0.5, energy=4.0),
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
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    speechiness: float = 0.0


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
            for name in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
                row[name] = float(row[name])
            # Advanced features (optional columns)
            if row.get("popularity"):
                row["popularity"] = int(row["popularity"])
            if row.get("release_decade"):
                row["release_decade"] = int(row["release_decade"])
            row["mood_tags"] = [t.strip() for t in row.get("mood_tags", "").split(";") if t.strip()]
            for name in ("instrumentalness", "speechiness"):
                if row.get(name):
                    row[name] = float(row[name])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None) -> Tuple[float, List[str]]:
    """Scores one song against user preferences using the given weights. Returns (score, reasons)."""
    w = weights or WEIGHTS
    score = 0.0
    reasons: List[str] = []

    # --- Base recipe ---
    fav_genre = str(user_prefs.get("genre", "")).lower()
    if fav_genre and song["genre"].lower() == fav_genre:
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']:.1f})")

    fav_mood = str(user_prefs.get("mood", "")).lower()
    if fav_mood and song["mood"].lower() == fav_mood:
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']:.1f})")

    if "energy" in user_prefs:
        gap = abs(float(song["energy"]) - float(user_prefs["energy"]))
        energy_points = w["energy"] * (1 - gap)
        score += energy_points
        reasons.append(f"energy closeness (+{energy_points:.2f})")

    if user_prefs.get("likes_acoustic") and float(song["acousticness"]) >= 0.6:
        score += w["acoustic"]
        reasons.append(f"acoustic bonus (+{w['acoustic']:.1f})")

    # --- Advanced features: only scored when the profile asks for them ---
    if "likes_popular" in user_prefs and "popularity" in song:
        pop = int(song["popularity"]) / 100
        share = pop if user_prefs["likes_popular"] else 1 - pop
        points = w["popularity"] * share
        score += points
        label = "popularity" if user_prefs["likes_popular"] else "hidden-gem"
        reasons.append(f"{label} (+{points:.2f})")

    if "decade" in user_prefs and "release_decade" in song:
        diff = abs(int(song["release_decade"]) - int(user_prefs["decade"]))
        if diff == 0:
            score += w["decade"]
            reasons.append(f"decade match (+{w['decade']:.1f})")
        elif diff == 10:
            score += w["decade"] / 2
            reasons.append(f"near decade (+{w['decade'] / 2:.1f})")

    wanted_tags = {t.lower() for t in user_prefs.get("mood_tags", [])}
    if wanted_tags:
        overlap = wanted_tags & {t.lower() for t in song.get("mood_tags", [])}
        if overlap:
            points = min(len(overlap) * w["mood_tags"], 2 * w["mood_tags"])
            score += points
            reasons.append(f"mood tags {sorted(overlap)} (+{points:.1f})")

    if user_prefs.get("likes_instrumental") and float(song.get("instrumentalness", 0)) >= 0.6:
        score += w["instrumental"]
        reasons.append(f"instrumental bonus (+{w['instrumental']:.1f})")

    if user_prefs.get("likes_vocals") and float(song.get("speechiness", 0)) >= 0.3:
        score += w["speechy"]
        reasons.append(f"vocal/rap bonus (+{w['speechy']:.1f})")

    return round(score, 2), reasons


def _diversify(scored: List[Tuple[Dict, float, str]], k: int) -> List[Tuple[Dict, float, str]]:
    """Greedily builds the top-k, penalizing songs whose artist or genre is already picked."""
    remaining = list(scored)
    picked: List[Tuple[Dict, float, str]] = []
    while remaining and len(picked) < k:
        best = None
        for song, score, explanation in remaining:
            penalty, notes = 0.0, []
            if any(p[0]["artist"] == song["artist"] for p in picked):
                penalty += ARTIST_PENALTY
                notes.append(f"diversity penalty: artist repeat (-{ARTIST_PENALTY:.1f})")
            if any(p[0]["genre"] == song["genre"] for p in picked):
                penalty += GENRE_PENALTY
                notes.append(f"diversity penalty: genre repeat (-{GENRE_PENALTY:.1f})")
            adjusted = round(score - penalty, 2)
            if best is None or adjusted > best[1]:
                best = (song, adjusted, "; ".join([explanation] + notes) if notes else explanation)
        picked.append(best)
        remaining = [item for item in remaining if item[0] is not best[0]]
    return picked


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "genre-first",
    diverse: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Scores every song with the chosen mode, ranks highest to lowest, and returns the top k."""
    strategy = SCORING_MODES.get(mode)
    if strategy is None:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(SCORING_MODES)}")
    # genre-first reads the live WEIGHTS dict so experiments.py can still change it at runtime.
    weights = WEIGHTS if mode == "genre-first" else strategy.weights
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        scored.append((song, score, "; ".join(reasons)))
    # sorted() returns a new list and leaves the catalog untouched (unlike list.sort()).
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return _diversify(ranked, k) if diverse else ranked[:k]