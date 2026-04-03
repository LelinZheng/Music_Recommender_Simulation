"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs, UserProfile

# ---------------------------------------------------------------------------
# Taste profiles — pick one (or add your own) and pass it to recommend_songs
# ---------------------------------------------------------------------------

PROFILES = {
    # Late-night lo-fi study session
    "night_study": UserProfile(
        favorite_genre="lofi",
        favorite_mood="focused",
        target_energy=0.40,
        target_valence=0.58,
        target_tempo_bpm=80,
        likes_acoustic=True,
    ),

    # Morning run / workout
    "workout": UserProfile(
        favorite_genre="pop",
        favorite_mood="intense",
        target_energy=0.90,
        target_valence=0.80,
        target_tempo_bpm=130,
        likes_acoustic=False,
    ),

    # Sunday afternoon wind-down
    "sunday_chill": UserProfile(
        favorite_genre="r&b",
        favorite_mood="relaxed",
        target_energy=0.50,
        target_valence=0.72,
        target_tempo_bpm=85,
        likes_acoustic=True,
    ),

    # Late-night moody drive
    "night_drive": UserProfile(
        favorite_genre="synthwave",
        favorite_mood="moody",
        target_energy=0.72,
        target_valence=0.50,
        target_tempo_bpm=110,
        likes_acoustic=False,
    ),

    # Upbeat daytime pop
    "pop/happy": UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.80,
        target_valence=0.85,
        target_tempo_bpm=120,
        likes_acoustic=False,
    ),

    # High-energy pop bangers
    "high_energy_pop": UserProfile(
        favorite_genre="pop",
        favorite_mood="intense",
        target_energy=0.95,
        target_valence=0.80,
        target_tempo_bpm=135,
        likes_acoustic=False,
    ),

    # --- Adversarial / Edge-Case Profiles ---

    # "sad" mood doesn't exist in the dataset → mood score = 0 for every song.
    # High energy (0.9) ends up being the only real differentiator.
    "energy_sad": UserProfile(
        favorite_genre="lofi",
        favorite_mood="sad",       # not in any song or MOOD_AFFINITY
        target_energy=0.90,
        target_valence=0.50,
        target_tempo_bpm=100,
        likes_acoustic=False,
    ),

    # Classical genre (only 1 song: Glacial Drift, melancholic, energy 0.18)
    # paired with euphoric mood (only in EDM songs). Attributes directly oppose
    # each other — tests whether genre or mood+numeric wins.
    "classical_rave": UserProfile(
        favorite_genre="classical",
        favorite_mood="euphoric",
        target_energy=0.95,
        target_valence=0.95,
        target_tempo_bpm=140,
        likes_acoustic=False,
    ),

    # Metal genre (intense) paired with relaxed mood — no affinity between
    # "intense" and "relaxed" in MOOD_AFFINITY; genre match for metal is only
    # rock (via GENRE_AFFINITY). Tests contradiction between genre and mood.
    "metal_relaxed": UserProfile(
        favorite_genre="metal",
        favorite_mood="relaxed",
        target_energy=0.30,
        target_valence=0.70,
        target_tempo_bpm=85,
        likes_acoustic=True,
    ),

    # Both genre ("trap") and mood ("angry") are absent from the dataset and
    # affinity maps → genre=0, mood=0 for every song. Numeric features alone
    # decide the ranking: energy pinned to 1.0, valence to 0.0, tempo to 220
    # (above every song's tempo) → tests hard boundary behavior.
    "all_extremes": UserProfile(
        favorite_genre="trap",     # not in dataset
        favorite_mood="angry",     # not in dataset
        target_energy=1.0,
        target_valence=0.0,
        target_tempo_bpm=220,
        likes_acoustic=False,
    ),

    # Chill lofi background
    "chill_lofi": UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.38,
        target_valence=0.58,
        target_tempo_bpm=75,
        likes_acoustic=True,
    ),

    # Deep intense rock
    "deep_rock": UserProfile(
        favorite_genre="rock",
        favorite_mood="intense",
        target_energy=0.92,
        target_valence=0.40,
        target_tempo_bpm=155,
        likes_acoustic=False,
    ),
}


def print_recommendations(profile_name: str, active_profile: UserProfile, songs: list) -> None:
    """Run recommender for one profile and print a formatted results block."""
    user_prefs = {
        "genre":     active_profile.favorite_genre,
        "mood":      active_profile.favorite_mood,
        "energy":    active_profile.target_energy,
        "valence":   active_profile.target_valence,
        "tempo_bpm": active_profile.target_tempo_bpm,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)
    label = f"{active_profile.favorite_mood.title()} {active_profile.favorite_genre.title()}"
    top_score = recommendations[0][1] if recommendations else 0.0

    if top_score >= 0.75:
        confidence = "HIGH"
    elif top_score >= 0.50:
        confidence = "MEDIUM"
    else:
        confidence = "LOW — best match is weak, results may be unreliable"

    print(f"\n{'='*52}")
    print(f"  Profile    : {profile_name}  ({label})")
    print(f"  Confidence : {confidence}  (best score: {top_score:.2f})")
    print(f"{'='*52}\n")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        bar = "█" * int(score * 20)
        print(f"  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.2f}  {bar}")
        print(f"       Genre : {song['genre']}  |  Mood: {song['mood']}")
        print(f"       Why   : {explanation}")
        print()

    print(f"{'='*52}\n")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Stress-test with three distinct profiles
    stress_test_profiles = ["high_energy_pop", "chill_lofi", "deep_rock"]
    for name in stress_test_profiles:
        print_recommendations(name, PROFILES[name], songs)

    # Adversarial / edge-case profiles
    print("\n" + "#" * 52)
    print("#  ADVERSARIAL / EDGE-CASE PROFILES")
    print("#" * 52)
    adversarial_profiles = ["energy_sad", "classical_rave", "metal_relaxed", "all_extremes"]
    for name in adversarial_profiles:
        print_recommendations(name, PROFILES[name], songs)


if __name__ == "__main__":
    main()
