# Audio examples

WAV files of the sounds the notebooks play, so they can be heard without running any code. They are mono unless the name says stereo, at 22,050 samples per second. All sounds are synthesized or simulated from the models in the notebooks, with the assumed values those notebooks state. Nothing is recorded in the real building.

To regenerate them, from the `integratron` directory (takes about a minute):

```bash
.venv/bin/python make_audio_examples.py
```

Files that share a volume setting can be compared for loudness. The others are each scaled to the same peak level.

## 01 Dome reflections and focusing

The simulated pulse holds little sound above 1 kHz, so these play as soft thumps. Same volume setting.

| File | What it is |
|---|---|
| `01_pulse_at_mirror_point.wav` | A pulse 1 m from the centre, heard at the mirror point: a faint direct tap, then the focused echo at 49 ms |
| `01_pulse_1m_past_mirror_point.wav` | The same pulse heard 1 m further on, where nothing focuses |

## 02 Ringing and room modes

Played through the echo rule at the dome's centre, with wall absorption α = 0.1.

| File | What it is |
|---|---|
| `02_click_at_centre.wav` | One click and its echo train, an echo every 49 ms |
| `02_noise_dry.wav`, `02_noise_at_centre.wav` | 3 s of hiss, dry and at the centre |
| `02_sweep_410_450hz_dry.wav`, `02_sweep_410_450hz_at_centre.wav` | A tone gliding from 410 to 450 Hz. At the centre it swells at the resonances at 419.4 and 439.9 Hz, then beats against the dome's ringing |

## 04 Whispering gallery

The simulated pulse holds little sound above 1 kHz. The 90° and 180° files share a volume setting.

| File | What it is |
|---|---|
| `04_whisper_next_to_source.wav` | A whisper 0.3 m from the wall, heard where it started: it returns after each 154 ms lap |
| `04_whisper_90_degrees.wav` | Heard a quarter of the way round the wall |
| `04_whisper_opposite_wall.wav` | Heard at the opposite wall, where the two gallery waves meet at 77 ms |

## 05 The singing bowl

| File | What it is |
|---|---|
| `05_bowl_warble_1hz_split.wav` | One bowl partial split into two frequencies 1 Hz apart: the bowl's slow pulse |
| `05_bowl_struck.wav` | A struck metal bowl with five partials, assumed fundamental 220 Hz |

## 06 Listening to the dome

The dry sounds, then the same sounds in the ray-traced dome with wall absorption α = 0.05. Wet files of the same sound share a volume setting.

| File | What it is |
|---|---|
| `06_dry_clap.wav`, `06_dry_whisper.wav`, `06_dry_voice.wav`, `06_dry_bowl.wav` | The four dry sounds |
| `06_whisper_at_mirror_point.wav` | A whisper 1 m from the centre, heard at the mirror point |
| `06_whisper_off_focus.wav` | The same whisper heard 2.5 m to the side, about 22 dB quieter |
| `06_voice_at_centre.wav` | A sung note heard by the singer at the centre: an echo every 49 ms |
| `06_bowl_at_centre.wav` | The struck bowl at the centre |
| `06_clap_mirror_point_smooth_dome.wav` | A clap at the mirror point in a perfectly smooth dome |
| `06_clap_mirror_point_rough_dome.wav` | The same clap with a wall that scatters 10% of the sound at each hit |

## 07 Two crystal bowls

Rubbed crystal bowls: an 8 s tone that swells over 2 s and then rings down.

| File | What it is |
|---|---|
| `07_one_crystal_bowl.wav` | One bowl at 261.6 Hz |
| `07_two_bowls_1p4hz_apart.wav` | Two bowls 1.4 Hz apart: a throb 1.4 times a second |
| `07_two_bowls_6hz_apart.wav` | 6 Hz apart: a fast tremolo |
| `07_two_bowls_25hz_apart.wav` | 25 Hz apart: a rough, buzzing tone |
| `07_two_bowls_in_room_stereo.wav` | Stereo, for headphones: bowls 2 m to each side, both ears hear both bowls, so both ears beat |
| `07_two_bowls_binaural_stereo.wav` | Stereo, for headphones: each ear hears one bowl only, so no sound wave beats. Any pulse is a binaural beat |
| `07_two_bowls_dome_centre_both_in_dip.wav` | Both bowls at the dome's centre, between two resonances: the throb stays deep |
| `07_two_bowls_dome_centre_one_on_peak.wav` | Bowls at 255.8 and 257.2 Hz, the first on a resonance peak: the throb almost disappears |
