"""
Command line runner for the Music Recommender Simulation.
Run from the project root with:  python -m src.main

Optional flags (stretch features):
  --mode genre-first|mood-first|energy-focused   choose a scoring strategy
  --diverse                                      apply the artist/genre diversity penalty
  --table                                        show results as a summary table
  --advanced                                     add profiles that use the advanced song features
"""

import argparse

from tabulate import tabulate

from src.recommender import load_songs, recommend_songs, SCORING_MODES

PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92},
    # Edge cases / adversarial profiles
    "Conflicted (sad but high energy)": {"genre": "blues", "mood": "sad", "energy": 0.95},
    "Unknown Genre (k-pop)": {"genre": "k-pop", "mood": "happy", "energy": 0.6},
}

# Profiles that use the advanced features (popularity, decade, mood tags, instrumentalness, speechiness)
ADVANCED_PROFILES = {
    "Nostalgic Hidden-Gem Hunter": {
        "genre": "country", "mood": "nostalgic", "energy": 0.5,
        "likes_popular": False, "decade": 1990, "mood_tags": ["nostalgic", "warm"],
    },
    "Focused Instrumental Studier": {
        "genre": "lofi", "mood": "focused", "energy": 0.4,
        "likes_instrumental": True, "mood_tags": ["focused", "calm"], "decade": 2020,
    },
    "Mainstream Hip Hop Fan": {
        "genre": "hip hop", "mood": "confident", "energy": 0.8,
        "likes_popular": True, "likes_vocals": True, "mood_tags": ["driving"],
    },
}


def print_recommendations(name: str, prefs: dict, songs: list, k: int = 5,
                          mode: str = "genre-first", diverse: bool = False) -> None:
    """Prints a clean, readable top-k list for one profile."""
    print("=" * 60)
    print(f"Profile: {name}")
    print(f"Prefs:   {prefs}")
    if mode != "genre-first" or diverse:
        print(f"Mode:    {mode}{' + diversity penalty' if diverse else ''}")
    print("-" * 60)
    for rank, (song, score, explanation) in enumerate(recommend_songs(prefs, songs, k, mode, diverse), start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']}, {song['mood']}]")
        print(f"   Score: {score:.2f}")
        print(f"   Because: {explanation}")
    print()


def print_table(name: str, prefs: dict, songs: list, k: int = 5,
                mode: str = "genre-first", diverse: bool = False) -> None:
    """Prints the top-k as a summary table that includes the reasons for each score."""
    rows = [
        [rank, song["title"], song["artist"], song["genre"], f"{score:.2f}", explanation.replace("; ", "\n")]
        for rank, (song, score, explanation) in enumerate(recommend_songs(prefs, songs, k, mode, diverse), start=1)
    ]
    suffix = f" | mode: {mode}{' + diversity' if diverse else ''}"
    print(f"\n{name}{suffix}")
    print(tabulate(rows, headers=["#", "Title", "Artist", "Genre", "Score", "Reasons"],
                   tablefmt="grid", disable_numparse=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="VibeFinder music recommender")
    parser.add_argument("--mode", default="genre-first", choices=list(SCORING_MODES))
    parser.add_argument("--diverse", action="store_true", help="penalize repeated artists/genres")
    parser.add_argument("--table", action="store_true", help="show a summary table")
    parser.add_argument("--advanced", action="store_true", help="include advanced-feature profiles")
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    profiles = {**PROFILES, **ADVANCED_PROFILES} if args.advanced else PROFILES
    show = print_table if args.table else print_recommendations
    for name, prefs in profiles.items():
        show(name, prefs, songs, mode=args.mode, diverse=args.diverse)


if __name__ == "__main__":
    main()
