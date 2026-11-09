# AI Interactions Log

> **Stretch features only.** This log covers the optional challenges I attempted: Advanced Song Features (Challenge 1), Multiple Scoring Modes (Challenge 2), Diversity Penalty (Challenge 3), and a Visual Summary Table (Challenge 4).

---

## Agentic Workflow (SF8): Challenge 1, Advanced Song Features

**What task did you give the agent?**

Add 5 new attributes to every song in `data/songs.csv` and make `src/recommender.py` score them, without changing the results for my existing five profiles.

**Prompts used:**

- "Add 5 new columns to data/songs.csv for all 20 songs: popularity (0-100), release_decade (e.g. 1990), mood_tags (semicolon-separated detailed tags like nostalgic;warm), instrumentalness (0-1), and speechiness (0-1). Keep the values realistic for each song's genre and mood."
- "Update load_songs to convert the new numeric columns and split mood_tags into a list. Update score_song so the new features are scored ONLY when the user profile asks for them (likes_popular, decade, mood_tags, likes_instrumental, likes_vocals), and add a reason string for each one. The output of `python -m src.main` for my existing profiles must stay identical."
- "Give Song default values for the new fields so the existing tests that build Song(...) objects still work."

**What did the agent generate or change?**

- `data/songs.csv`: 5 new columns: popularity, release_decade, mood_tags, instrumentalness, speechiness.
- `src/recommender.py`: new scoring rules:
  - popularity: up to +1.0, or a "hidden-gem" bonus if `likes_popular` is False
  - decade: exact match +1.0, one decade off +0.5
  - mood tags: +0.5 per shared tag, max +1.0
  - instrumental bonus: +0.5
  - vocal/rap bonus: +0.5
- New default fields on `Song` and parsing in `load_songs`.
- `src/main.py`: 3 new profiles behind an `--advanced` flag (Nostalgic Hidden-Gem Hunter, Focused Instrumental Studier, Mainstream Hip Hop Fan).

**What did you verify or fix manually?**

- Diffed the default `python -m src.main` output before and after the change: it is **identical**, so my README and model card results are still accurate.
- Checked one score by hand: Dust Road Home = 2.0 genre + 1.0 mood + 1.96 energy + 0.55 hidden-gem (popularity 45 → 1 − 0.45) + 1.0 decade + 1.0 tags = **7.51**, which matches the output.
- Added tests: the new features load as the right types, and the decade and mood-tag reasons appear.

---

## Design Pattern (SF10): Challenge 2, Multiple Scoring Modes

**Which design pattern did you use?**

A lightweight **Strategy pattern**. Each ranking strategy is a `ScoringStrategy(name, weights)` object stored in a `SCORING_MODES` registry: `genre-first`, `mood-first`, and `energy-focused`.

**How did AI help you brainstorm or implement it?**

I attached recommender.py and asked: *"Suggest a design pattern that lets a user switch between Genre-First, Mood-First, and Energy-Focused ranking in main.py without copying score_song three times."* The AI suggested three options:

1. if/else branches inside score_song
2. a separate scoring function per mode
3. a Strategy object that only holds the weights

I chose option 3. The modes only differ in *how much* each feature counts, not *what* is checked, so one `score_song(prefs, song, weights)` function plus swappable weight sets keeps the code small. Adding a new mode is a single line.

**How does the pattern appear in your final code?**

- `ScoringStrategy` dataclass and the `SCORING_MODES` dict in `src/recommender.py`
- `score_song(user_prefs, song, weights=None)` uses whichever strategy's weights it receives
- `recommend_songs(..., mode="genre-first")` looks up the strategy, and an unknown mode raises a `ValueError`
- `python -m src.main --mode mood-first` switches modes from the command line

---

## Diversity Penalty: Challenge 3

**Prompt used:** *"After scoring, build the top-k one song at a time. If a candidate's artist is already in the picked list, subtract 1.0 from its score; if its genre is already there, subtract 0.5. Add the penalty to the reasons so the user can see it. Make it optional with diverse=False by default."*

**Verified:** with `--diverse`, the Chill Lofi list no longer has two LoRoom songs in a row. Focus Flow drops from #3 to #4 (−1.0 for the artist, −0.5 for the genre) and Spacewalk Thoughts (ambient) moves up to #3. A test checks that the top 3 has no repeated artist.

## Visual Summary Table: Challenge 4

**Prompt used:** *"Use tabulate to show the top recommendations as a grid table with columns #, Title, Artist, Genre, Score, Reasons. The table must include the reasons for each score, one reason per line."*

**Fixed manually:** tabulate turned the score "3.00" into "3", so I added `disable_numparse=True`.
