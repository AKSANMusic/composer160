"""AKSAN "Melankolik Asi" Canonical Preset.

Core artistic identity for the AKSAN project:
- Fusion of alternative rock, Anatolian melodies, and Persian poetic emotional depth.
- Sonic atmosphere: cinematic, dark, minimalist brutalism (#050508 + subtle 16mm film grain).
- Signature instrumentation: bağlama (saz), duduk, electric guitar, upright bass, soft drum brushes.
"""

from composer160.core.vector import ParameterVector


def aksan_preset() -> ParameterVector:
    """Return a fully configured ParameterVector expressing the canonical AKSAN identity."""
    vec = ParameterVector()

    # =========================================================================
    # Domain A: Tonal Foundation (T1: 1, 2; T2: 3, 4)
    # =========================================================================
    vec.set(1, "A")                           # Root Key: A
    vec.set(2, "Minor")                       # Tonality: Minor
    vec.set(3, "Aeolian")                     # Mode: Aeolian (natural minor with Anatolian modal inflection)
    vec.set(4, "Harmonic/melodic minor")      # Scale Type
    vec.set(5, 2)                             # Tonal Stability: anchored with slight modal mystery

    # =========================================================================
    # Domain B: Tempo & Meter (T1: 8, 11, 15)
    # =========================================================================
    vec.set(8, 86)                            # BPM: 86 (deliberate, slow-burn emotional pacing)
    vec.set(9, "Andante")                     # Tempo Feel
    vec.set(10, "Constant")                   # Tempo Variation
    vec.set(11, "4/4")                        # Time Signature
    vec.set(15, "Straight")                   # Groove Feel
    vec.set(16, 3)                            # Pulse Strength: restrained but grounded

    # =========================================================================
    # Domain C: Rhythm & Groove (T2: 17, 18, 20)
    # =========================================================================
    vec.set(17, 2)                            # Rhythmic Density: sparse (minimalist brutalism)
    vec.set(18, "Moderate")                   # Rhythmic Complexity
    vec.set(19, 2)                            # Syncopation Level: subtle breathing room
    vec.set(20, "Minimal")                    # Percussion Role: soft brush drums, restrained kick
    vec.set(24, 2)                            # Groove Intensity: relaxed, brooding

    # =========================================================================
    # Domain D: Melody (T1: 26; T2: 28, 34, 35)
    # =========================================================================
    vec.set(26, "Clear melody")               # Melodic Presence: distinctive lead vocal & duduk
    vec.set(28, "Wave")                       # Melodic Contour: undulating Persian/Anatolian wave
    vec.set(30, "Mixed")                      # Interval Preference
    vec.set(34, ["Repetition", "Sequence"])   # Motivic Development: poetic recurrent motifs
    vec.set(35, 4)                            # Hook Strength: poignant, lingering melodic hook
    vec.set(36, "Subtle")                     # Ornamentation: microtonal embellishments
    vec.set(38, "Late")                       # Climax Placement

    # =========================================================================
    # Domain E: Harmony (T1: 45; T2: 39, 40, 46, 47, 50, 53)
    # =========================================================================
    vec.set(39, "Slow")                       # Harmonic Rhythm: breathing chords
    vec.set(40, "7ths")                       # Chord Type: moody minor 7ths and suspended colors
    vec.set(45, "Modal")                      # Progression Type: Anatolian/modal circularity
    vec.set(46, "4")                          # Progression Length: 4-chord loop
    vec.set(47, 3)                            # Harmonic Complexity: moderate depth
    vec.set(50, 2)                            # Dissonance Level: mild bittersweet tension
    vec.set(53, "Half")                       # Cadence Type: open, unresolved longing

    # =========================================================================
    # Domain F: Bass (T2: 55)
    # =========================================================================
    vec.set(55, "Prominent")                  # Bass Presence: intimate acoustic upright bass
    vec.set(56, "Stepwise")                   # Bass Movement: expressive walking/stepwise lines
    vec.set(57, "Semi-melodic")               # Bass Melodic Independence
    vec.set(58, "Low")                        # Bass Register: warm acoustic wood resonance
    vec.set(59, "Sustained")                  # Bass Rhythmic Role

    # =========================================================================
    # Domain G: Texture & Counterpoint (T2: 60, 61)
    # =========================================================================
    vec.set(60, "Homophonic")                 # Texture Type: clear lead voice over layered acoustic beds
    vec.set(61, 2)                            # Texture Density: lean, spacious room
    vec.set(63, "Gradual")                    # Textural Evolution: slow organic layering

    # =========================================================================
    # Domain H: Orchestration & Timbre (T1: 68, 75; T2: 67, 72, 73, 76)
    # =========================================================================
    vec.set(67, "Small ensemble")             # Ensemble Size: intimate 5-piece feel
    vec.set(68, [                             # Primary Instrument Family
        "Strings", "Woodwinds", "Guitar", "Percussion", "Vocal"
    ])
    vec.set(72, 2)                            # Timbre Brightness: dark (#050508 aesthetic)
    vec.set(73, 4)                            # Timbre Warmth: lush analog tape saturation
    vec.set(75, "Hybrid")                     # Acoustic↔Electronic: mostly acoustic with subtle ambient textures
    vec.set(76, "Modern")                     # Vintage↔Modern: modern brutalism with 16mm vintage grain
    vec.set(77, "Legato")                     # Primary Articulation: flowing, bowed and plucked

    # =========================================================================
    # Domain I: Dynamics & Expression (T2: 79, 80, 81, 86)
    # =========================================================================
    vec.set(79, "mp")                         # Base Dynamic: mezzopiano (intimate, near-whisper start)
    vec.set(80, "Wide")                       # Dynamic Range: wide expressive swing
    vec.set(81, "Gradual swell")              # Dynamic Shape: building from quiet melancholy to explosive rebellion
    vec.set(86, 4)                            # Humanization: organic, live performance nuance

    # =========================================================================
    # Domain J: Form & Structure (T2: 87, 88, 91, 92, 94, 95, 99)
    # =========================================================================
    vec.set(87, "Verse-Chorus")               # Overall Form: classical alternative song structure
    vec.set(88, "Medium (3–5)")               # Duration: standard streaming length (3.5 minutes)
    vec.set(91, 3)                            # Section Contrast: noticeable dynamic lift in chorus
    vec.set(92, "Ambient")                    # Intro Style: atmospheric, solo duduk/bağlama texture
    vec.set(93, "Short")                      # Intro Length: 4 bars of mood-setting
    vec.set(94, "Gradual layers")             # Build-up Style: upright bass and brushes enter softly
    vec.set(95, 4)                            # Climax Intensity: intense, heart-wrenching emotional peak
    vec.set(99, "Fade-out")                   # Ending Style: lingering ritardando fading into ambient silence

    # =========================================================================
    # Domain K: Emotion & Narrative (T1: 100, 107; T2: 102, 103, 105)
    # =========================================================================
    vec.set(100, "Melancholy")                # Primary Emotion: Melankolik Asi (Melancholic Rebellious)
    vec.set(101, "Layered/ambiguous")         # Emotional Complexity: sorrow intertwined with defiant strength
    vec.set(102, "Arc")                       # Energy Curve: steady ascent to emotional release, then resolving
    vec.set(103, 4)                           # Tension Arc: profound build-and-release cycle
    vec.set(105, "Dramatic arc")              # Narrative Direction: cinematic journey
    vec.set(107, [                            # Genre / Cultural Reference
        "Alternative", "Anatolian Folk", "Cinematic", "Rock"
    ])

    # =========================================================================
    # Domain L: Production & Spatial (T2: 108, 109, 110, 116)
    # =========================================================================
    vec.set(108, "Room")                      # Spatial Depth: intimate wooden room, close-mic feel
    vec.set(109, "Wide")                      # Stereo Width: wide cinematic panorama
    vec.set(110, 3)                           # Reverb Amount: atmospheric natural room decay
    vec.set(111, "Plate")                     # Reverb Type: warm vintage plate
    vec.set(113, "Subtle warmth")             # Saturation / Distortion: 16mm film grain analogue warmth
    vec.set(116, 3)                           # Production Density: balanced, uncluttered mix

    # =========================================================================
    # Domain M: Vocal (T1: 117; T2: 118, 119)
    # =========================================================================
    vec.set(117, "Lead")                      # Vocal Presence: emotional focal point
    vec.set(118, "Tenor")                     # Vocal Type: expressive male tenor / baritone
    vec.set(119, "Raspy")                     # Vocal Style: breathy, emotionally raw, raspy delivery
    vec.set(120, "Light reverb")              # Vocal Processing: transparent, no artificial auto-tune

    # =========================================================================
    # Domain N: Lyrics & Prosody (T2: 121, 122, 126)
    # =========================================================================
    vec.set(121, ["TR80/EN20"])               # Language(s): Turkish-dominant bilingual blend
    vec.set(122, 8)                           # Lyric Density: 8 syllables/bar (spacious, poetic meter)
    vec.set(123, "ABCB")                      # Rhyme Scheme
    vec.set(124, "title-last")                # Hook Position: title resolved at the end of chorus
    vec.set(125, 2)                           # Hook Repetition: 2 times per chorus
    vec.set(126, 4)                           # Prosody Fit: speech-natural Turkish phrasing (prevents unsingable output)
    vec.set(127, "Poetic/literary")           # Diction Register: Persian/Turkish poetic resonance
    vec.set(128, 4)                           # Syllable–Melody Fit: sung-as-spoken
    vec.set(129, "1st")                       # Narrative Person: intimate first-person confession

    # =========================================================================
    # Domain O: Structure Timeline (T2: 130, 131, 134)
    # =========================================================================
    # 75 bars @ 86 BPM (4/4) = 75 * 4 * (60/86) = 209.3 seconds ≈ 3.5 min
    section_map = [
        ("Intro", 4),
        ("Verse 1", 12),
        ("Pre-Chorus", 4),
        ("Chorus 1", 12),
        ("Verse 2", 12),
        ("Pre-Chorus 2", 4),
        ("Chorus 2", 12),
        ("Bridge", 8),
        ("Outro", 7),
    ]
    vec.set(130, section_map)                 # Section Map (75 total bars)
    vec.set(131, [2, 3, 4, 5, 3, 4, 5, 3, 1]) # Per-Section Energy: arc peaking in choruses & resolving
    vec.set(134, 75)                          # Total Bars: 4+12+4+12+12+4+12+8+7 = 75

    # =========================================================================
    # Domain P: Exclusions (T2: 135)
    # =========================================================================
    vec.set(135, [                            # Avoid List
        "trap hats", "autotune", "guitar solos", "key change", "risers", "generic EDM", "synth brass"
    ])
    vec.set(136, ["keytar", "accordion", "vocoder"]) # Forbidden Instruments
    vec.set(137, 4)                           # Cliché Avoidance: non-obvious, tasteful arrangements
    vec.set(138, ["no sidechain pump", "no sub-drop", "no gated reverb"]) # Mix Exclusions

    # =========================================================================
    # Domain Q: Reference Anchors (T2: 139)
    # =========================================================================
    vec.set(139, [                            # Reference Anchors (weighted)
        "Anatolian bağlama texture ×0.5",
        "Dark alternative rock ×0.4",
        "Cinematic score ×0.3",
        "Persian poetic depth ×0.3",
    ])
    vec.set(140, "Modern hi-fi")              # Production Era
    vec.set(141, "Turkish")                   # Regional/Traditional Reference
    vec.set(143, 3)                           # Novelty↔Familiarity: balanced resonance

    # =========================================================================
    # Domain R: Mix & Arrangement (T2: 144)
    # =========================================================================
    vec.set(144, [                            # Stem Priority
        "lead vocal", "saz/bağlama", "duduk", "electric guitar", "upright bass", "soft drum brushes"
    ])
    vec.set(145, -14)                         # Loudness Target: -14 integrated LUFS (streaming)
    vec.set(147, "Keep upright bass intimate; let duduk float in reverb; keep drum brushes subtle.")
    vec.set(148, ["radio edit", "instrumental"])

    # =========================================================================
    # Domain S: AI Generator Directives (T2: 149)
    # =========================================================================
    vec.set(149, [                            # Negative Prompt (exclusions for generators)
        "trap hats", "autotune", "autotune ladder", "key change", "risers",
        "generic EDM", "synth brass", "guitar solos", "keytar", "accordion",
        "vocoder", "no sidechain pump", "no sub-drop", "no gated reverb",
        "generic pop synth", "over-compressed master", "electronic drop", "screaming"
    ])
    vec.set(153, "standard")                  # Prompt Verbosity

    # =========================================================================
    # Domain T: Project & Release Context (T2: 155)
    # =========================================================================
    vec.set(155, ["SoundCloud", "Spotify"])   # Release Platform
    vec.set(156, "AKSAN-Core")                # CRM Tag
    vec.set(157, "streaming")                 # Monetization Priority
    vec.set(158, 210)                         # Target Duration: 210 seconds (~3.5 minutes)
    vec.set(159, "release-day")               # Campaign Phase
    vec.set(160, "TR-primary")                # Language Market

    return vec
