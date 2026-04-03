# Reflection: Profile Comparisons

This file compares pairs of user profiles side by side to explain what changed in the
recommendations, why it changed, and what that tells us about how the scoring logic works.

---

## Pair 1: `high_energy_pop` vs `chill_lofi`

**high_energy_pop** top results: Gym Hero, Neon Blossom, Sunrise City
**chill_lofi** top results: Library Rain, Midnight Coding, Focus Flow

These two profiles are almost perfect opposites, and the recommendations reflect that
completely. High-energy pop wants loud, fast, intense songs — the kind you'd hear in a
gym or at a party. Chill lofi wants quiet, slow, background music — the kind you'd put
on while studying at 2am.

The interesting thing is *why* Gym Hero never appears in the lofi results, and Library
Rain never appears in the pop results, even though both have decent numeric scores across
the board. It comes down to the mood and genre labels. Gym Hero is tagged "intense" and
Library Rain is tagged "chill" — and those two moods have no relationship in the system's
affinity map. They're not just different, they're strangers to each other. So the genre
and mood scores both zero out, and a song loses 60% of its possible score before energy
or tempo even gets considered.

**What this tells us:** mood and genre act like a gatekeeper. If you don't get past them,
you're fighting for the leftover 40% of the score.

---

## Pair 2: `deep_rock` vs `high_energy_pop`

**deep_rock** top results: Storm Runner, Voltage Drop, Gym Hero
**high_energy_pop** top results: Gym Hero, Neon Blossom, Sunrise City

Both profiles want high energy and intense mood, so they share some overlap — Gym Hero
appears in both top 5s. But the key difference is genre: one wants rock, the other wants
pop. This single label change reshuffles the rankings significantly.

Storm Runner (rock, intense) scores 0.98 for deep_rock but only 0.64 for high_energy_pop
because it picks up a full genre match (+0.30) for rock but nothing for pop. Gym Hero
does the reverse — it dominates the pop profile because it's the only pop + intense song,
but drops to #3 in the rock profile because it can't earn the genre bonus.

This is the clearest demonstration of how genre acts as a multiplier, not just a filter.
Two songs with nearly identical energy (0.91 vs 0.93) and the same mood (intense) can
score 0.35 apart purely because of their genre tag.

**Plain language version:** Imagine you want "intense workout music." The system finds
Gym Hero and Storm Runner — both fast and loud. But if you specifically said "rock," the
system bumps Storm Runner up because it wears the right label, even though Gym Hero
sounds just as intense.

---

## Pair 3: `chill_lofi` vs `deep_rock`

**chill_lofi** top results: Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts
**deep_rock** top results: Storm Runner, Voltage Drop, Gym Hero, Night Drive Loop

These profiles not only return different songs — they return songs from completely
different corners of the catalog. There is zero overlap between their top 5 results.

The energy gap between them is large: chill lofi targets 0.38, deep rock targets 0.92.
That's a 0.54 difference, which triggers the "large mismatch" warning in the scoring
logic. A lofi song like Library Rain (energy 0.35) scores nearly perfectly for chill lofi
but would score only +0.09 on energy for the rock profile. Multiplied by the weight, that
wipes out most of the numeric contribution.

Interestingly, Spacewalk Thoughts (ambient) appears in the chill lofi results at #4 even
though it's not lofi. It earns partial credit because ambient is in the lofi affinity map
and the mood "chill" matches exactly. This is the affinity map working as intended — it
allows related styles to surface without forcing an exact genre match.

**What this tells us:** energy is the strongest numeric separator in the catalog. When
two profiles are far apart on energy, their recommendation lists diverge almost entirely.

---

## Pair 4: `energy_sad` vs `chill_lofi`

**energy_sad** top results: Midnight Coding, Focus Flow, Library Rain (all lofi, score ~0.58)
**chill_lofi** top results: Library Rain, Midnight Coding, Focus Flow (all lofi, score ~0.99)

These two profiles return almost the same songs — but for completely different reasons,
and with very different confidence levels (MEDIUM 0.58 vs HIGH 0.99).

The `energy_sad` profile wanted lofi genre but a "sad" mood, which doesn't exist in the
dataset. Because mood scored 0 for every single song, the genre match (+0.30) became the
dominant signal by default. The lofi songs floated to the top not because they felt right
for a sad listener, but simply because they were the best available genre match when the
mood signal went dark.

Meanwhile, the energy target (0.90) was completely ignored in practice — the lofi songs
that rose to the top have energy around 0.35–0.42, which is flagged as a "large mismatch"
in every single result. The system knew something was wrong but recommended those songs
anyway.

**Plain language version:** Imagine asking a music store clerk for "something sad and
high energy." The clerk doesn't have anything sad in stock, so they just give you the
lofi section because that's what you said you liked. The result technically satisfies
half your request, but it completely misses what you actually wanted.

---

## Pair 5: `classical_rave` vs `metal_relaxed`

**classical_rave** top results: Neon Blossom (EDM), Gym Hero, Sunrise City
**metal_relaxed** top results: Coffee Shop Stories (jazz), Smoke & Honey (reggae), Spacewalk Thoughts

Both profiles are built around contradictions — a genre and a mood that don't naturally
go together. What's interesting is that both profiles ended up getting recommendations
that completely ignored the user's preferred genre.

For `classical_rave`: classical music exists in the catalog (Glacial Drift), but it's
slow, melancholic, and quiet — the opposite of euphoric. The mood signal won the
tiebreaker, and the system returned EDM songs because euphoric + high energy + high
valence matched the numeric profile. The user's genre preference was silently ignored.

For `metal_relaxed`: the two metal songs in the catalog (Storm Runner, Voltage Drop) are
both tagged "intense" — the opposite of relaxed. Mood won here too, and the system
returned jazz and reggae because they matched "relaxed" closely. The user wanted metal
but got a coffee shop playlist.

**What this comparison reveals:** when genre and mood are in conflict, mood wins — not
because the system explicitly decided that, but because the catalog doesn't contain songs
that satisfy both at once. The system always finds *something* to recommend, even when
the request is impossible to fulfill. It doesn't know how to say "I don't have what
you're looking for."

---

## Why Does "Gym Hero" Keep Showing Up for Happy Pop Users?

This is worth addressing directly because it came up repeatedly across profiles.

"Gym Hero" is tagged as pop + intense, with energy 0.93 and valence 0.77. A "happy pop"
user wants pop + happy, with energy 0.80 and valence 0.85.

Here's the math: Gym Hero earns a full genre match (+0.30 for pop), misses on mood
(intense ≠ happy, and they're not in the affinity map, so +0.00), then scores well on
energy and valence because its numbers are close. Total: roughly 0.61.

But here's the problem — there are only 2 pop songs in the entire catalog. Sunrise City
(pop, happy) is the ideal match, but after that, Gym Hero is the next-best pop song
regardless of mood. So it keeps appearing not because it's truly right for a happy
listener, but because the catalog is too small and too genre-constrained to offer a
better alternative.

This is what "filter bubble" means in practice. The system's job is to return the top 5
results no matter what. When a genre has limited coverage, the best available option
fills the gap — even if it's a mismatch on the most emotionally relevant feature.
