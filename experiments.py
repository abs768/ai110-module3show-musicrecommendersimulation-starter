import src.recommender as r

songs = r.load_songs("data/songs.csv")
profiles = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85},
    "Conflicted (sad but high energy)": {"genre": "blues", "mood": "sad", "energy": 0.95},
}

def run(label):
    print(f"\n##### {label}  weights={r.WEIGHTS}")
    for name, prefs in profiles.items():
        print(f"\n{name}")
        for i, (song, score, _) in enumerate(r.recommend_songs(prefs, songs, 5), 1):
            print(f"  {i}. {song['title']} ({song['genre']}, {song['mood']}) {score:.2f}")

run("BASELINE")
r.WEIGHTS.update(genre=1.0, energy=4.0)
run("EXPERIMENT: genre halved, energy doubled")
