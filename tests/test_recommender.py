from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""

from src.recommender import load_songs, score_song, recommend_songs


def test_load_songs_reads_all_rows_with_numeric_fields():
    songs = load_songs("data/songs.csv")
    assert len(songs) >= 18
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["id"], int)


def test_score_song_rewards_genre_and_mood_matches():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    score, reasons = score_song(prefs, song)
    assert score == 5.0  # 2.0 genre + 1.0 mood + 2.0 perfect energy
    assert any("genre" in r for r in reasons)


def test_recommend_songs_is_sorted_and_respects_k():
    songs = load_songs("data/songs.csv")
    results = recommend_songs({"genre": "lofi", "mood": "chill", "energy": 0.4}, songs, k=3)
    assert len(results) == 3
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)
    assert results[0][0]["genre"] == "lofi"

# ---- Stretch feature tests ----
import pytest


def test_advanced_features_are_loaded_and_scored():
    songs = load_songs("data/songs.csv")
    dust = next(s for s in songs if s["title"] == "Dust Road Home")
    assert dust["release_decade"] == 1990
    assert dust["mood_tags"] == ["nostalgic", "warm"]
    prefs = {"genre": "country", "mood": "nostalgic", "energy": 0.5,
             "decade": 1990, "mood_tags": ["nostalgic", "warm"]}
    score, reasons = score_song(prefs, dust)
    assert any("decade match" in r for r in reasons)
    assert any("mood tags" in r for r in reasons)


def test_mood_first_mode_ranks_happy_songs_above_gym_hero():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.85}
    titles = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=5, mode="mood-first")]
    assert titles.index("Neon Fiesta") < titles.index("Gym Hero")


def test_unknown_mode_raises():
    with pytest.raises(ValueError):
        recommend_songs({"genre": "pop"}, [], mode="nope")


def test_diversity_penalty_limits_repeated_artists():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
    results = recommend_songs(prefs, songs, k=3, diverse=True)
    artists = [s["artist"] for s, _, _ in results]
    assert len(artists) == len(set(artists))
