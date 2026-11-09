# 🎵 Music Recommender Simulation: VibeFinder 1.0

## Project Summary
VibeFinder 1.0 is a small content-based music recommender. It loads a 20-song catalog from
data/songs.csv, compares every song to a user's taste profile (favorite genre, favorite mood,
target energy, and whether they like acoustic music), scores each song, and returns the top 5
with a plain-English reason for each pick.
It is a CLI-first simulation: run `python -m src.main` to see ranked recommendations
with scores and reasons for five user profiles.

## How The System Works
**Real-world recommenders:** Platforms like Spotify and YouTube combine two ideas.
*Collaborative filtering* uses behavior from many users (likes, skips, replays, playlist adds,
watch time) and recommends what similar listeners enjoyed. *Content-based filtering* uses the
item's own attributes (genre, mood, tempo, energy, acousticness) to find songs similar to what a
user already likes. At scale they mix both and train models on billions of interactions.
VibeFinder builds only the content-based half. It prioritizes **genre first, then energy, then
mood**, because those best capture a song's "vibe" in this dataset.

**Song features used:** genre, mood, energy (0–1), acousticness (0–1).
(tempo_bpm, valence, and danceability are loaded but not scored yet.)

**UserProfile features:** favorite_genre, favorite_mood, target_energy, likes_acoustic.
Example profile: {"genre": "pop", "mood": "happy", "energy": 0.85}

**Algorithm Recipe (Scoring Rule, applied to one song):**
- +2.0 if the genre matches
- +1.0 if the mood matches
- +0 to 2.0 for energy closeness = 2.0 × (1 − |song energy − target energy|).
  A song closer to the target scores higher. Being louder or quieter is not rewarded.
- +0.5 acoustic bonus if the user likes acoustic and acousticness ≥ 0.6

**Ranking Rule (applied to the list):** score every song, sort highest to lowest with sorted(),
and return the top k. We need both: scoring judges one song in isolation, and ranking compares all
the scores to decide which songs get shown.

**Data flow:**
Input (user prefs) → Process (loop: score every song in songs.csv) → Output (sort → top-k list with reasons)

**Expected bias:** genre is worth the most points, so the system might over-prioritize genre and
ignore great songs that match the user's mood and energy but carry a different genre label.

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .\.venv\Scripts\Activate.ps1          # Windows PowerShell
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output
Terminal output of `python -m src.main` for all five profiles:

```
Loaded songs: 20
============================================================
Profile: High-Energy Pop
Prefs:   {'genre': 'pop', 'mood': 'happy', 'energy': 0.85}
------------------------------------------------------------
1. Sunrise City by Neon Echo  [pop, happy]
   Score: 4.94
   Because: genre match (+2.0); mood match (+1.0); energy closeness (+1.94)
2. Gym Hero by Max Pulse  [pop, intense]
   Score: 3.84
   Because: genre match (+2.0); energy closeness (+1.84)
3. Neon Fiesta by Ritmo Sur  [latin, happy]
   Score: 3.00
   Because: mood match (+1.0); energy closeness (+2.00)
4. Rooftop Lights by Indigo Parade  [indie pop, happy]
   Score: 2.82
   Because: mood match (+1.0); energy closeness (+1.82)
5. Storm Runner by Voltline  [rock, intense]
   Score: 1.88
   Because: energy closeness (+1.88)

============================================================
Profile: Chill Lofi
Prefs:   {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}
------------------------------------------------------------
1. Library Rain by Paper Lanterns  [lofi, chill]
   Score: 5.50
   Because: genre match (+2.0); mood match (+1.0); energy closeness (+2.00); acoustic bonus (+0.5)
2. Midnight Coding by LoRoom  [lofi, chill]
   Score: 5.36
   Because: genre match (+2.0); mood match (+1.0); energy closeness (+1.86); acoustic bonus (+0.5)
3. Focus Flow by LoRoom  [lofi, focused]
   Score: 4.40
   Because: genre match (+2.0); energy closeness (+1.90); acoustic bonus (+0.5)
4. Spacewalk Thoughts by Orbit Bloom  [ambient, chill]
   Score: 3.36
   Because: mood match (+1.0); energy closeness (+1.86); acoustic bonus (+0.5)
5. Coffee Shop Stories by Slow Stereo  [jazz, relaxed]
   Score: 2.46
   Because: energy closeness (+1.96); acoustic bonus (+0.5)

============================================================
Profile: Deep Intense Rock
Prefs:   {'genre': 'rock', 'mood': 'intense', 'energy': 0.92}
------------------------------------------------------------
1. Storm Runner by Voltline  [rock, intense]
   Score: 4.98
   Because: genre match (+2.0); mood match (+1.0); energy closeness (+1.98)
2. Gym Hero by Max Pulse  [pop, intense]
   Score: 2.98
   Because: mood match (+1.0); energy closeness (+1.98)
3. Bassline Riot by DJ Kinetic  [edm, euphoric]
   Score: 1.94
   Because: energy closeness (+1.94)
4. Iron Lung Choir by Blackvein  [metal, angry]
   Score: 1.90
   Because: energy closeness (+1.90)
5. Neon Fiesta by Ritmo Sur  [latin, happy]
   Score: 1.86
   Because: energy closeness (+1.86)

============================================================
Profile: Conflicted (sad but high energy)
Prefs:   {'genre': 'blues', 'mood': 'sad', 'energy': 0.95}
------------------------------------------------------------
1. Blue Hour Smoke by Theo Grant Trio  [blues, sad]
   Score: 3.90
   Because: genre match (+2.0); mood match (+1.0); energy closeness (+0.90)
2. Bassline Riot by DJ Kinetic  [edm, euphoric]
   Score: 2.00
   Because: energy closeness (+2.00)
3. Gym Hero by Max Pulse  [pop, intense]
   Score: 1.96
   Because: energy closeness (+1.96)
4. Iron Lung Choir by Blackvein  [metal, angry]
   Score: 1.96
   Because: energy closeness (+1.96)
5. Storm Runner by Voltline  [rock, intense]
   Score: 1.92
   Because: energy closeness (+1.92)

============================================================
Profile: Unknown Genre (k-pop)
Prefs:   {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.6}
------------------------------------------------------------
1. Rooftop Lights by Indigo Parade  [indie pop, happy]
   Score: 2.68
   Because: mood match (+1.0); energy closeness (+1.68)
2. Sunrise City by Neon Echo  [pop, happy]
   Score: 2.56
   Because: mood match (+1.0); energy closeness (+1.56)
3. Neon Fiesta by Ritmo Sur  [latin, happy]
   Score: 2.50
   Because: mood match (+1.0); energy closeness (+1.50)
4. Velvet Static by Mara Lune  [r&b, romantic]
   Score: 1.90
   Because: energy closeness (+1.90)
5. Island Breeze by Coral Kings  [reggae, relaxed]
   Score: 1.84
   Because: energy closeness (+1.84)
```

## Experiments You Tried
**Weight shift:** genre 2.0 → 1.0, energy 2.0 → 4.0 (`python experiments.py`).

```
Loaded songs: 20

##### BASELINE  weights={'genre': 2.0, 'mood': 1.0, 'energy': 2.0, 'acoustic': 0.5}

High-Energy Pop
  1. Sunrise City (pop, happy) 4.94
  2. Gym Hero (pop, intense) 3.84
  3. Neon Fiesta (latin, happy) 3.00
  4. Rooftop Lights (indie pop, happy) 2.82
  5. Storm Runner (rock, intense) 1.88

Conflicted (sad but high energy)
  1. Blue Hour Smoke (blues, sad) 3.90
  2. Bassline Riot (edm, euphoric) 2.00
  3. Gym Hero (pop, intense) 1.96
  4. Iron Lung Choir (metal, angry) 1.96
  5. Storm Runner (rock, intense) 1.92

##### EXPERIMENT: genre halved, energy doubled  weights={'genre': 1.0, 'mood': 1.0, 'energy': 4.0, 'acoustic': 0.5}

High-Energy Pop
  1. Sunrise City (pop, happy) 5.88
  2. Neon Fiesta (latin, happy) 5.00
  3. Gym Hero (pop, intense) 4.68
  4. Rooftop Lights (indie pop, happy) 4.64
  5. Storm Runner (rock, intense) 3.76

Conflicted (sad but high energy)
  1. Bassline Riot (edm, euphoric) 4.00
  2. Gym Hero (pop, intense) 3.92
  3. Iron Lung Choir (metal, angry) 3.92
  4. Storm Runner (rock, intense) 3.84
  5. Blue Hour Smoke (blues, sad) 3.80
```

- High-Energy Pop: Neon Fiesta (latin, happy) passed Gym Hero (pop, intense) for #2. Arguably more
  accurate, since a happy song suits a happy listener better.
- Conflicted: the only sad blues song fell from #1 to #5. Energy took over and the user's mood and
  genre were ignored. The results changed, but they didn't get more accurate.

## Limitations and Risks
- Tiny catalog (20 songs), and most genres have only one song.
- Exact text matching: "indie pop" ≠ "pop", "chill" ≠ "relaxed".
- Genre (2 pts) outweighs mood (1 pt), so Gym Hero (intense) shows up for happy-pop users.
- Energy closeness gives every song some points, so the same high-energy songs fill many lists
  (a filter bubble).
- No lyrics, language, artist diversity, or listening history.

## Reflection
Full details are in the [Model Card](model_card.md).

I learned that a recommendation is just arithmetic on features plus a sort. Which features you
pick and how you weight them *is* the model. Changing two weights reshuffled the results more than I
expected, and the "Because:" explanations made it obvious why: energy quietly takes over whenever
genre and mood don't match.

Bias comes less from bad intentions and more from what the data and weights leave out. A blues or
k-pop fan gets one good match (or none) followed by filler, while pop and lofi fans get several real
matches, and nothing in the output warns the user that this is happening.

The clearest example for me was the blues profile: Blue Hour Smoke dropped from #1 to #5 when I
raised the energy weight, even though its genre and mood still matched.

---

## Stretch Features

All four optional challenges are implemented as **opt-in flags**, so the default
`python -m src.main` output above is unchanged.

| Challenge | How to run | What it does |
|---|---|---|
| 1. Advanced song features | `python -m src.main --advanced` | 5 new attributes (popularity, release_decade, mood_tags, instrumentalness, speechiness) and 3 profiles that use them |
| 2. Multiple scoring modes | `python -m src.main --mode mood-first` (or `energy-focused`) | Strategy pattern: swappable weight sets |
| 3. Diversity penalty | `python -m src.main --diverse` | −1.0 for a repeated artist, −0.5 for a repeated genre in the top k |
| 4. Summary table | `python -m src.main --table` | tabulate grid with a reasons column |

Flags can be combined, e.g. `python -m src.main --advanced --mode mood-first --diverse --table`.
Process notes are in [ai_interactions.md](ai_interactions.md).

**Mood-first mode fixes the "Gym Hero" problem.** Gym Hero drops from #2 to #4 and the happy songs move up:

```
Profile: High-Energy Pop
Prefs:   {'genre': 'pop', 'mood': 'happy', 'energy': 0.85}
Mode:    mood-first
------------------------------------------------------------
1. Sunrise City by Neon Echo  [pop, happy]
   Score: 5.44
   Because: genre match (+1.0); mood match (+2.5); energy closeness (+1.94)
2. Neon Fiesta by Ritmo Sur  [latin, happy]
   Score: 4.50
   Because: mood match (+2.5); energy closeness (+2.00)
3. Rooftop Lights by Indigo Parade  [indie pop, happy]
   Score: 4.32
   Because: mood match (+2.5); energy closeness (+1.82)
4. Gym Hero by Max Pulse  [pop, intense]
   Score: 2.84
   Because: genre match (+1.0); energy closeness (+1.84)
5. Storm Runner by Voltline  [rock, intense]
   Score: 1.88
   Because: energy closeness (+1.88)
```

**Diversity penalty.** Focus Flow (a second LoRoom song and a third lofi song) is pushed down, and an ambient song gets in:

```
Profile: Chill Lofi
Prefs:   {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}
Mode:    genre-first + diversity penalty
------------------------------------------------------------
1. Library Rain by Paper Lanterns  [lofi, chill]
   Score: 5.50
   Because: genre match (+2.0); mood match (+1.0); energy closeness (+2.00); acoustic bonus (+0.5)
2. Midnight Coding by LoRoom  [lofi, chill]
   Score: 4.86
   Because: genre match (+2.0); mood match (+1.0); energy closeness (+1.86); acoustic bonus (+0.5); diversity penalty: genre repeat (-0.5)
3. Spacewalk Thoughts by Orbit Bloom  [ambient, chill]
   Score: 3.36
   Because: mood match (+1.0); energy closeness (+1.86); acoustic bonus (+0.5)
4. Focus Flow by LoRoom  [lofi, focused]
   Score: 2.90
   Because: genre match (+2.0); energy closeness (+1.90); acoustic bonus (+0.5); diversity penalty: artist repeat (-1.0); diversity penalty: genre repeat (-0.5)
5. Coffee Shop Stories by Slow Stereo  [jazz, relaxed]
   Score: 2.46
   Because: energy closeness (+1.96); acoustic bonus (+0.5)
```

**Advanced features.** The hidden-gem, decade, and mood-tag bonuses at work:

```
Profile: Nostalgic Hidden-Gem Hunter
Prefs:   {'genre': 'country', 'mood': 'nostalgic', 'energy': 0.5, 'likes_popular': False, 'decade': 1990, 'mood_tags': ['nostalgic', 'warm']}
------------------------------------------------------------
1. Dust Road Home by Willow Creek  [country, nostalgic]
   Score: 7.51
   Because: genre match (+2.0); mood match (+1.0); energy closeness (+1.96); hidden-gem (+0.55); decade match (+1.0); mood tags ['nostalgic', 'warm'] (+1.0)
2. Coffee Shop Stories by Slow Stereo  [jazz, relaxed]
   Score: 3.82
   Because: energy closeness (+1.74); hidden-gem (+0.58); decade match (+1.0); mood tags ['warm'] (+0.5)
3. Velvet Static by Mara Lune  [r&b, romantic]
   Score: 3.27
   Because: energy closeness (+1.90); hidden-gem (+0.37); near decade (+0.5); mood tags ['warm'] (+0.5)
4. Paper Boats by Autumn Thread  [folk, melancholic]
   Score: 3.22
   Because: energy closeness (+1.60); hidden-gem (+0.62); near decade (+0.5); mood tags ['nostalgic'] (+0.5)
5. Island Breeze by Coral Kings  [reggae, relaxed]
   Score: 2.96
   Because: energy closeness (+1.96); hidden-gem (+0.50); mood tags ['warm'] (+0.5)
```

**Summary table:**

```
High-Energy Pop | mode: genre-first
+-----+----------------+---------------+-----------+---------+--------------------------+
| #   | Title          | Artist        | Genre     | Score   | Reasons                  |
+=====+================+===============+===========+=========+==========================+
| 1   | Sunrise City   | Neon Echo     | pop       | 4.94    | genre match (+2.0)       |
|     |                |               |           |         | mood match (+1.0)        |
|     |                |               |           |         | energy closeness (+1.94) |
+-----+----------------+---------------+-----------+---------+--------------------------+
| 2   | Gym Hero       | Max Pulse     | pop       | 3.84    | genre match (+2.0)       |
|     |                |               |           |         | energy closeness (+1.84) |
+-----+----------------+---------------+-----------+---------+--------------------------+
| 3   | Neon Fiesta    | Ritmo Sur     | latin     | 3.00    | mood match (+1.0)        |
|     |                |               |           |         | energy closeness (+2.00) |
+-----+----------------+---------------+-----------+---------+--------------------------+
| 4   | Rooftop Lights | Indigo Parade | indie pop | 2.82    | mood match (+1.0)        |
|     |                |               |           |         | energy closeness (+1.82) |
+-----+----------------+---------------+-----------+---------+--------------------------+
| 5   | Storm Runner   | Voltline      | rock      | 1.88    | energy closeness (+1.88) |
+-----+----------------+---------------+-----------+---------+--------------------------+
```
