# Reviewed Validation Notes

The reviewed set keeps the strongest teacher-facing clips from the original validation manifest and replaces the weakest adjacent clips with local lecture clips from `/workspace/clips`.

## Why clips were dropped

The dropped clips were mostly in four buckets:

- setup-heavy teaching videos where the clip is about lighting, recording, or tools more than teaching
- teacher interview or demo-class coaching where the content is meta-advice rather than classroom delivery
- generic public-speaking or presentation advice with limited teacher specificity
- a few classroom-adjacent clips that were still weaker than the available local lecture footage

Representative drops include `clip_009`, `clip_013`, `clip_019`, `clip_025`, `clip_026`, `clip_033`, `clip_041`, `clip_046`, `clip_048`, `clip_049`, and `clip_050`.

## What was added

The replacements shift the set toward clearer lecture footage with stronger teacher visibility and better nonverbal signal. The added clips emphasize:

- visible lecturer posture and audience orientation
- board, screen, or front-of-room coordination
- sustained lecture pacing instead of setup narration
- more direct classroom or faculty-style delivery

Replacement families added from `/workspace/clips` include:

- MIT OCW lecture clips such as `mit_ocw_intro_120_180`, `mit_ocw_brain_300_360`, `mit_ocw_how_to_speak_300_360`, `mit_ocw_linear_eq_180_240`, `mit_ocw_microecon_180_240`, `mit_ocw_pigeonhole_240_300`, `mit_ocw_power_elec_240_300`, and `mit_ocw_psychology_240_300`
- Stanford lecture clips such as `stanford_cs230_240_300`, `stanford_give_lecture_180_240`, `stanford_hbb_300_360`, `stanford_last_lecture_180_240`, and `stanford_prog_method_240_300`
- Yale lecture clips such as `yale_deconstruction_180_240`, `yale_evolution_180_240`, `yale_finance_240_300`, `yale_linguistics_180_240`, `yale_newtonian_240_300`, `yale_power_politics_180_240`, `yale_quantum_240_300`, and `yale_rome_180_240`
- `cs50_business_150_210` as a more classroom-like lecture benchmark

## Coverage note

The final reviewed set is `50` clips. One local clip, `mit_ocw_aero_300_360`, was left unused so the reviewed set could stay at the cap while prioritizing the clearest lecture-style options.
