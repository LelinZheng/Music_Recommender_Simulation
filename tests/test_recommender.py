import pytest
from src.recommender import Song, UserProfile, Recommender, load_songs, score_song, recommend_songs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_song_dict(**kwargs):
    """Return a song dict (for score_song tests) with sensible defaults."""
    defaults = dict(
        id=1, title="Test", artist="Artist", genre="pop", mood="happy",
        energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2,
    )
    defaults.update(kwargs)
    return defaults


def make_song(**kwargs):
    """Return a Song dataclass instance (for Recommender tests)."""
    return Song(**make_song_dict(**kwargs))


def make_prefs(**kwargs):
    """Return a user_prefs dict with sensible defaults, overridden by kwargs."""
    defaults = dict(genre="pop", mood="happy", energy=0.8, valence=0.85, tempo_bpm=120)
    defaults.update(kwargs)
    return defaults


LOFI_SONG = make_song_dict(id=2, genre="lofi", mood="chill", energy=0.4,
                           tempo_bpm=80, valence=0.6, danceability=0.5, acousticness=0.9)
ROCK_SONG = make_song_dict(id=3, genre="rock", mood="intense", energy=0.91,
                           tempo_bpm=152, valence=0.48, danceability=0.66, acousticness=0.1)


# ---------------------------------------------------------------------------
# UserProfile defaults
# ---------------------------------------------------------------------------

def test_userprofile_optional_fields_have_defaults():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    assert user.target_valence == 0.65
    assert user.target_tempo_bpm == 100


# ---------------------------------------------------------------------------
# load_songs
# ---------------------------------------------------------------------------

def test_load_songs_returns_correct_count():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 21


def test_load_songs_keys_present():
    songs = load_songs("data/songs.csv")
    expected = {"id", "title", "artist", "genre", "mood",
                "energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    assert set(songs[0].keys()) == expected


def test_load_songs_numeric_types():
    songs = load_songs("data/songs.csv")
    s = songs[0]
    assert isinstance(s["id"], int)
    assert isinstance(s["energy"], float)
    assert isinstance(s["valence"], float)
    assert isinstance(s["danceability"], float)
    assert isinstance(s["acousticness"], float)
    assert isinstance(s["tempo_bpm"], int)


def test_load_songs_energy_in_range():
    songs = load_songs("data/songs.csv")
    for s in songs:
        assert 0.0 <= s["energy"] <= 1.0


# ---------------------------------------------------------------------------
# score_song — categorical scoring
# ---------------------------------------------------------------------------

def test_score_exact_mood_and_genre_match():
    prefs = make_prefs(genre="pop", mood="happy", energy=0.8, valence=0.85, tempo_bpm=120)
    song = make_song_dict(genre="pop", mood="happy", energy=0.8, tempo_bpm=120, valence=0.85)
    score, reasons = score_song(prefs, song)
    assert score >= 0.95
    assert any("mood match" in r for r in reasons)
    assert any("genre match" in r for r in reasons)


def test_score_related_mood_gives_partial_credit():
    prefs = make_prefs(mood="chill")
    song_exact = make_song_dict(mood="chill")
    song_related = make_song_dict(mood="relaxed")   # chill ↔ relaxed is in MOOD_AFFINITY
    song_unrelated = make_song_dict(mood="intense")

    score_exact, _ = score_song(prefs, song_exact)
    score_related, _ = score_song(prefs, song_related)
    score_unrelated, _ = score_song(prefs, song_unrelated)

    assert score_exact > score_related > score_unrelated


def test_score_related_genre_gives_partial_credit():
    prefs = make_prefs(genre="lofi")
    song_exact = make_song_dict(genre="lofi")
    song_related = make_song_dict(genre="ambient")   # lofi ↔ ambient is in GENRE_AFFINITY
    song_unrelated = make_song_dict(genre="metal")

    score_exact, _ = score_song(prefs, song_exact)
    score_related, _ = score_song(prefs, song_related)
    score_unrelated, _ = score_song(prefs, song_unrelated)

    assert score_exact > score_related > score_unrelated


def test_score_no_mood_or_genre_match_capped():
    """Without any categorical match, max possible score is 0.40 (energy+valence+tempo)."""
    prefs = make_prefs(genre="trap", mood="angry", energy=1.0, valence=1.0, tempo_bpm=100)
    song = make_song_dict(genre="classical", mood="melancholic", energy=1.0,
                          tempo_bpm=100, valence=1.0)
    score, _ = score_song(prefs, song)
    assert score <= 0.40 + 1e-6


# ---------------------------------------------------------------------------
# score_song — numeric proximity
# ---------------------------------------------------------------------------

def test_score_closer_energy_scores_higher():
    prefs = make_prefs(energy=0.5)
    song_close = make_song_dict(energy=0.52)
    song_far = make_song_dict(energy=0.9)
    score_close, _ = score_song(prefs, song_close)
    score_far, _ = score_song(prefs, song_far)
    assert score_close > score_far


def test_score_closer_valence_scores_higher():
    prefs = make_prefs(valence=0.5)
    song_close = make_song_dict(valence=0.52)
    song_far = make_song_dict(valence=0.95)
    score_close, _ = score_song(prefs, song_close)
    score_far, _ = score_song(prefs, song_far)
    assert score_close > score_far


def test_score_tempo_never_goes_negative():
    prefs = make_prefs(tempo_bpm=60)
    song = make_song_dict(tempo_bpm=300)   # extreme difference
    score, _ = score_song(prefs, song)
    assert score >= 0.0


def test_score_returns_value_between_0_and_1():
    prefs = make_prefs()
    for song in [make_song_dict(), LOFI_SONG, ROCK_SONG]:
        score, _ = score_song(prefs, song)
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# score_song — warnings in reasons
# ---------------------------------------------------------------------------

def test_score_unknown_mood_adds_warning():
    prefs = make_prefs(mood="sad")   # not in dataset or affinity map
    song = make_song_dict(mood="happy")
    _, reasons = score_song(prefs, song)
    assert any("unrecognized" in r for r in reasons)


def test_score_unknown_genre_adds_warning():
    prefs = make_prefs(genre="trap")   # not in dataset or affinity map
    song = make_song_dict(genre="pop")
    _, reasons = score_song(prefs, song)
    assert any("unrecognized" in r for r in reasons)


def test_score_large_energy_mismatch_flagged():
    prefs = make_prefs(energy=0.9)
    song = make_song_dict(energy=0.2)   # diff = 0.7, above 0.4 threshold
    _, reasons = score_song(prefs, song)
    assert any("large mismatch" in r for r in reasons)


def test_score_small_energy_mismatch_not_flagged():
    prefs = make_prefs(energy=0.8)
    song = make_song_dict(energy=0.82)
    _, reasons = score_song(prefs, song)
    assert not any("large mismatch" in r for r in reasons)


# ---------------------------------------------------------------------------
# recommend_songs
# ---------------------------------------------------------------------------

def make_catalog():
    return [
        {"id": 1, "title": "Pop Track", "artist": "A", "genre": "pop", "mood": "happy",
         "energy": 0.8, "tempo_bpm": 120, "valence": 0.9, "danceability": 0.8, "acousticness": 0.2},
        {"id": 2, "title": "Lofi Track", "artist": "B", "genre": "lofi", "mood": "chill",
         "energy": 0.4, "tempo_bpm": 80, "valence": 0.6, "danceability": 0.5, "acousticness": 0.9},
        {"id": 3, "title": "Rock Track", "artist": "C", "genre": "rock", "mood": "intense",
         "energy": 0.91, "tempo_bpm": 152, "valence": 0.48, "danceability": 0.66, "acousticness": 0.1},
    ]


def test_recommend_returns_top_k():
    prefs = make_prefs()
    results = recommend_songs(prefs, make_catalog(), k=2)
    assert len(results) == 2


def test_recommend_sorted_descending():
    prefs = make_prefs()
    results = recommend_songs(prefs, make_catalog(), k=3)
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)


def test_recommend_best_match_is_first():
    prefs = make_prefs(genre="pop", mood="happy", energy=0.8, valence=0.9, tempo_bpm=120)
    results = recommend_songs(prefs, make_catalog(), k=3)
    assert results[0][0]["genre"] == "pop"
    assert results[0][0]["mood"] == "happy"


def test_recommend_returns_tuple_format():
    prefs = make_prefs()
    results = recommend_songs(prefs, make_catalog(), k=1)
    song, score, explanation = results[0]
    assert isinstance(song, dict)
    assert isinstance(score, float)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_recommend_k_larger_than_catalog():
    prefs = make_prefs()
    results = recommend_songs(prefs, make_catalog(), k=100)
    assert len(results) == len(make_catalog())


def test_recommend_empty_catalog():
    prefs = make_prefs()
    results = recommend_songs(prefs, [], k=5)
    assert results == []


# ---------------------------------------------------------------------------
# Recommender class (OOP interface)
# ---------------------------------------------------------------------------

def make_small_recommender() -> Recommender:
    songs = [
        Song(id=1, title="Test Pop Track", artist="Test Artist", genre="pop",
             mood="happy", energy=0.8, tempo_bpm=120, valence=0.9,
             danceability=0.8, acousticness=0.2),
        Song(id=2, title="Chill Lofi Loop", artist="Test Artist", genre="lofi",
             mood="chill", energy=0.4, tempo_bpm=80, valence=0.6,
             danceability=0.5, acousticness=0.9),
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
