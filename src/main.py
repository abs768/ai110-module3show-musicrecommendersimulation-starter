"""
Command line runner for the Music Recommender Simulation.
Run from the project root with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs

PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92},
    # Edge cases / adversarial profiles
    "Conflicted (sad but high energy)": {"genre": "blues", "mood": "sad", "energy": 0.95},
    "Unknown Genre (k-pop)": {"genre": "k-pop", "mood": "happy", "energy": 0.6},
}


def print_recommendations(name: str, prefs: dict, songs: list, k: int = 5) -> None:
    """Prints a clean, readable top-k list for one profile."""
    print("=" * 60)
    print(f"Profile: {name}")
    print(f"Prefs:   {prefs}")
    print("-" * 60)
    for rank, (song, score, explanation) in enumerate(recommend_songs(prefs, songs, k), start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']}, {song['mood']}]")
        print(f"   Score: {score:.2f}")
        print(f"   Because: {explanation}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs)


if __name__ == "__main__":
    main()
