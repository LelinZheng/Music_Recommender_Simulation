# 🎧 Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender that matches songs to a user's taste profile using
weighted similarity scoring.

---

## 2. Goal / Task

VibeFinder tries to answer one question: given what a user says they like, which songs
in the catalog are the closest match?

It takes a user's preferred genre, mood, energy level, emotional tone (valence), and
tempo as input. It scores every song in the catalog against those preferences and returns
the top 5 results, ranked from best to worst match.

This is for classroom exploration. It is not a production system and was not tested
with real users.

---

## 3. Algorithm Summary

Every song gets a score between 0.0 and 1.0. Here's how it's calculated:

- **Mood (30%)** — Does the song's mood match what the user wants? Exact match gets full
  points. A closely related mood (like "chill" and "relaxed") gets half points. No
  relationship gets zero.
- **Genre (30%)** — Same idea as mood. Exact match is full points, related genre is half,
  anything else is zero.
- **Energy (20%)** — How close is the song's energy level to what the user wants?
  A song at 0.40 energy scores nearly perfectly for a user who wants 0.40. A song at
  0.90 energy scores poorly for that same user.
- **Valence (15%)** — Same proximity logic applied to emotional positivity. High valence
  means happy/bright. Low valence means sad/dark.
- **Tempo (5%)** — How close is the song's BPM to what the user wants? Small weight
  because tempo already correlates with genre and energy.

Add those five scores together and you get the final score. Sort all 21 songs by that
score, return the top 5.

The output also includes a confidence label: HIGH (≥ 0.75), MEDIUM (0.50–0.74), or LOW
(< 0.50) based on how well the best result actually matched.

---

## 4. Data Used

The catalog has **21 songs** stored in a CSV file. Each song has these features:
genre, mood, energy (0–1), tempo in BPM, valence (0–1), danceability (0–1), and
acousticness (0–1).

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop,
folk, metal, edm, r&b, classical, reggae, country, chiptune, soul, darkwave

**Moods represented:** happy, chill, intense, relaxed, focused, moody, confident,
melancholic, euphoric, romantic, nostalgic

The original starter file had 10 songs. 11 more were added to increase genre and mood
diversity. The data was hand-crafted for this simulation — it does not come from a real
music database like Spotify or MusicBrainz.

**Limits of the data:**
- Most genres have only 1 song. Lofi is the exception with 3.
- The catalog skews toward higher energy songs (12 of 21 have energy ≥ 0.60).
- Danceability and acousticness are stored but not used in scoring.
- No lyrics, no audio files, no listening history — just metadata.

---

## 5. Strengths

The system works well when a user's preferences map cleanly onto the catalog.

- A **lofi + chill** user gets a tight, accurate top 3 (all three lofi songs, correctly
  ordered by energy and valence proximity).
- A **rock + intense** user gets Storm Runner and Voltage Drop at the top, with the
  rock/metal affinity correctly pulling Voltage Drop into view even though the user
  said "rock," not "metal."
- The **confidence label** correctly flags weak matches. The `all_extremes` profile
  (trap + angry, neither of which exist in the catalog) produced a LOW confidence
  warning with a top score of 0.33 — the system knew it was guessing.
- The **reason strings** make every recommendation explainable. You can see exactly
  which features contributed and how much each one added to the score.

---

## 6. Limitations and Bias

**Lofi filter bubble.** Lofi has 3 songs — more than any other genre. A lofi user always
gets the same 3 songs at the top with no variety. There's nothing wrong with those songs,
but the user will never discover anything outside that tiny cluster.

**Invisible moods and genres.** Four moods (confident, nostalgic, romantic, melancholic)
have no entries in the mood affinity map. Songs with those moods can never earn a mood
score for any user — they're capped at 0.40 maximum. A hip-hop fan will never see
"Concrete Jungle" surface through genre affinity because hip-hop isn't connected to
anything else in the map.

**Unused features.** Danceability and acousticness are loaded and stored but never used
in scoring. A user who loves acoustic music gets no benefit from that preference.

**Energy skew.** The catalog has many more high-energy songs than low-energy ones. A
user targeting very low energy (below 0.35) has only 2 close matches in the entire
catalog. A high-energy user has 6. This is a data bias that produces worse results for
one type of user.

**No diversity enforcement.** The top results can all be from the same genre or even the
same artist. LoRoom appears twice in the top 3 for any lofi profile. The system never
tries to spread the results around.

---

## 7. Evaluation Process

Seven profiles were tested: three normal use cases and four adversarial edge cases.

**Normal profiles:**
- `high_energy_pop` — pop + intense, high energy, fast tempo
- `chill_lofi` — lofi + chill, low energy, slow tempo
- `deep_rock` — rock + intense, very high energy, fast tempo

**Adversarial profiles:**
- `energy_sad` — lofi genre but "sad" mood (not in the dataset)
- `classical_rave` — classical genre + euphoric mood (opposite vibes)
- `metal_relaxed` — metal genre + relaxed mood (direct contradiction)
- `all_extremes` — trap genre + angry mood (both absent), extreme numeric values

Normal profiles returned HIGH confidence (scores 0.98–0.99) and matched intuition.
The adversarial tests exposed real weaknesses: unknown moods silently zero out, genre
gets ignored when catalog coverage is poor, and the system always returns 5 results
even when none of them are a real match.

The most instructive failure: `classical_rave` wanted classical + euphoric. The only
classical song (Glacial Drift) is slow and melancholic. The system returned EDM songs
instead because mood + numerics matched better. The user's genre preference was
completely overridden with no warning.

---

## 8. Intended Use and Non-Intended Use

**Intended use:**
- Learning how content-based recommender systems work
- Exploring how feature weights affect ranking decisions
- Classroom experimentation with scoring logic and bias

**Not intended for:**
- Real music discovery for actual users
- Any context where recommendations influence purchases, streams, or revenue
- Users who expect recommendations to reflect their full listening history or taste
- Replacing tools like Spotify, Apple Music, or YouTube Music

---

## 9. Ideas for Improvement

**1. Add acousticness and danceability to scoring.**
These features are already in the dataset — wiring them into `score_song` would make
the system more expressive and let acoustic or dance-focused users get better results.

**2. Expand the affinity maps.**
Many moods (nostalgic, romantic, melancholic, confident) and genres (hip-hop, country,
folk, darkwave) have no affinity connections. Adding those would stop 7+ songs from
being near-invisible to most users.

**3. Add a diversity rule to the top-k selection.**
After scoring, limit each artist or genre to appear at most once in the top 5. This
would break up the lofi bubble and prevent the same song from dominating every pop
profile.

---

## 10. Personal Reflection

The biggest learning moment for me was the `classical_rave` test. I built a profile that
asked for classical music with a euphoric mood — two things that don't really go together
— and the system just confidently returned EDM songs. It didn't hesitate. It didn't say
"I can't help you." It found the best available match and presented it like it was right.
That was the moment I understood why bias in AI systems is so hard to catch. The output
looks fine until you already know it's wrong.

Using AI tools throughout this project genuinely sped things up — especially for
designing the scoring weights and thinking through edge cases. But I had to double-check
the math manually a few times. The weighted scoring formula looked correct in explanation
but I had to trace it step by step through real songs to verify it actually produced the
rankings I expected. Trusting the explanation without verifying the output is exactly the
kind of mistake the `energy_sad` profile exposed.

What surprised me most is how quickly "just addition and multiplication" started to feel
like taste. When the lofi profile returned Library Rain at 0.99 and Gym Hero at 0.24, it
felt obviously right — even though all that happened was five numbers got multiplied and
added. The feeling of "this makes sense" came from the weights reflecting real human
judgment about what matters in music. The math didn't create taste, it just encoded it.

If I kept going, I'd add a diversity rule first. Right now the same artist can appear
three times in a row and the system doesn't care. That's the most noticeable flaw when
you just look at the output — it feels repetitive even when the scores are high.
