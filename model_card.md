# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name
**VibeFinder 1.0**

## 2. Goal / Task
VibeFinder suggests the 5 songs from a small catalog that best fit a user's taste.
It predicts how well each song matches the user's favorite genre, mood, and energy level,
and ranks songs by that match.

## 3. Data Used
- 20 songs: 10 from the starter plus 10 I added.
- Features per song: genre, mood, energy, tempo, valence, danceability, acousticness.
  The model uses genre, mood, energy, and acousticness.
- 17 genres and 14 moods. Lofi has 3 songs and pop has 2; every other genre has just 1.
- Limits: the data is invented and small, uses mostly Western genre labels, and has no lyrics,
  language, release year, popularity, or real listening history.

## 4. Algorithm Summary
Every song earns points:
- A matching genre earns 2 points.
- A matching mood earns 1 point.
- Energy earns up to 2 points. The closer the song's energy is to what the user wants, the more
  points it gets.
- If the user likes acoustic music, very acoustic songs get a small 0.5 bonus.
Then all songs are sorted by points, and the top 5 are shown with the reasons they earned points.

Example: Sunrise City ranked #1 for the High-Energy Pop user because it's the only song that
matches both genre (pop) and mood (happy) for 3 points, and its energy (0.82) is almost exactly
the target (0.85) for 1.94 more points, making 4.94 in total.

## 5. Observed Behavior / Biases (Limitations and Bias)
The biggest weakness is that energy acts as a catch-all that creates a filter bubble. Every song
earns some energy points, so when a user's genre and mood barely exist in the catalog, the empty
slots fill with whatever matches energy, usually the same few EDM, metal, and rock tracks. Most
genres have only one song, so a blues fan gets one real match and four unrelated loud songs, while
pop and lofi fans get several good matches. Matching is exact text, so "indie pop" earns nothing for
a pop fan and "relaxed" earns nothing for a "chill" fan. Genre outweighs mood, which is why Gym Hero
(pop but intense) beats happy songs from other genres for a happy-pop listener.

## 6. Evaluation Process
I tested five profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, plus two edge cases:
"Conflicted" (blues, sad, energy 0.95) and "Unknown Genre" (k-pop, which isn't in the catalog).
I checked whether each #1 made sense and whether the reasons matched my intuition. I also ran a
weight-shift experiment (genre 2.0 → 1.0, energy 2.0 → 4.0) and wrote 5 pytest tests. One test
checks that a perfect match scores exactly 5.0.

**What surprised me:** in the experiment, the only sad blues song fell from #1 to #5 for the
Conflicted user. Doubling energy didn't make the results smarter. It made energy the only thing
the system cared about.

**Profile comparisons:**
- **High-Energy Pop vs Chill Lofi:** no songs in common. Pop pulls bright, fast songs (Sunrise City,
  Gym Hero) and lofi pulls quiet, acoustic ones (Library Rain, Midnight Coding). That makes sense,
  because they differ on genre, mood, and energy, so every part of the score pushes them apart.
- **High-Energy Pop vs Deep Intense Rock:** Gym Hero is #2 for both, for different reasons. For pop
  it's the genre match. For rock it's the "intense" mood and an energy (0.93) almost exactly on target.
- **Deep Intense Rock vs Conflicted:** after #1, both lists are nearly the same songs (Bassline Riot,
  Gym Hero, Iron Lung Choir, Storm Runner). When only one song matches genre and mood, energy decides
  the rest, so very different listeners get the same loud songs.
- **Chill Lofi vs Unknown Genre (k-pop):** lofi gets three genre matches; k-pop gets zero. The k-pop
  list is built only from mood and energy, so an underrepresented user gets a weaker experience
  with no warning.
- **Chill Lofi vs Deep Intense Rock:** opposite ends of the energy scale. Lofi's list stays under 0.4
  energy, and the acoustic bonus lifts ambient and jazz songs. Rock's list is all above 0.85.

**Why does Gym Hero keep showing up for people who just want "Happy Pop"?** In plain words: the
system cares most about the genre label. Gym Hero is labeled "pop", which is worth 2 points, more
than a mood match (1 point). So even though it's an intense workout song, the label lifts it above
happy songs from other genres. The system can't tell that "intense" and "happy" feel different.

## 7. Intended Use and Non-Intended Use
**Intended use:** classroom exploration of how content-based recommenders turn data into ranked
suggestions. It assumes a user can describe their taste with one genre, one mood, and one energy level.

**Not intended for:** real music apps or real users, people whose taste spans many genres, or
judging what music is "good". It shouldn't be used for any decision where a bad suggestion matters.

## 8. Ideas for Improvement
1. Partial credit for related genres and moods (indie pop ≈ pop, chill ≈ relaxed).
2. A diversity rule so the top 5 isn't filled by the same high-energy songs or artists.
3. Use tempo, valence, and danceability, and let users list several favorite genres.

## 9. Personal Reflection
**Biggest learning moment:** seeing one weight change reshuffle everything. Doubling energy pushed
the only song that truly fit the sad-blues user down to #5.

**How AI helped and when I double-checked:** AI helped me draft the scoring logic, generate new
songs, and brainstorm edge-case profiles quickly. I had to verify its work: the starter's import in
main.py was broken, and the starter tests passed only by luck, because they just returned the first
two songs. I checked the scores against hand math (Sunrise City = 2 + 1 + 1.94 = 4.94).

**What surprised me:** a few lines of addition plus a sort, with a "Because:" line, already *feel*
like a real recommender.

**What I'd try next:** a bigger and more diverse catalog, partial genre matching, and learning weights
from likes and skips instead of choosing them by hand.