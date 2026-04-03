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
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Swap the key below to try a different profile
    active_profile = PROFILES["night_study"]

    user_prefs = {
        "genre":     active_profile.favorite_genre,
        "mood":      active_profile.favorite_mood,
        "energy":    active_profile.target_energy,
        "valence":   active_profile.target_valence,
        "tempo_bpm": active_profile.target_tempo_bpm,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
