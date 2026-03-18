# Local Clips Gemini Flash Batch Summary

- Source dir: `/workspace/clips`
- Tracked batch dir: `/workspace/TeacherEvaluation/evaluation/runtime_batches/full_flash_tuned_20260318T010135Z`
- Runs root: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local`
- Analysis FPS: `12.0`
- Window size: `15.0s`, step `15.0s`
- Semantic model: `gemini-2.5-flash`
- Coaching model: `gemini-2.5-flash`
- Selected clips: `23`

## Status Counts

| run_status | count |
| --- | --- |
| ok | 23 |

## Score Summary

| metric | count | mean | min | max |
| --- | --- | --- | --- | --- |
| overall_score | 23 | 50.45 | 29.31 | 63.44 |
| audience_score | 23 | 63.51 | 14.25 | 88.48 |
| alertness_score | 23 | 76.75 | 43.13 | 90.99 |

## Top 5

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_intro_120_180 | 63.44 | llm_api_hybrid | 1 | mit ocw intro 120 180 |
| mit_ocw_psychology_240_300 | 61.46 | llm_api | 0 | mit ocw psychology 240 300 |
| stanford_give_lecture_180_240 | 60.92 | llm_api | 1 | stanford give lecture 180 240 |
| mit_ocw_brain_300_360 | 59.55 | llm_api | 1 | mit ocw brain 300 360 |
| yale_deconstruction_180_240 | 57.33 | llm_api | 1 | yale deconstruction 180 240 |

## Bottom 5

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_linear_eq_180_240 | 29.31 | llm_api | 0 | mit ocw linear eq 180 240 |
| stanford_hbb_300_360 | 37.97 | llm_api | 3 | stanford hbb 300 360 |
| mit_ocw_aero_300_360 | 38.29 | llm_api_hybrid | 3 | mit ocw aero 300 360 |
| yale_quantum_240_300 | 41.63 | llm_api_hybrid | 2 | yale quantum 240 300 |
| mit_ocw_microecon_180_240 | 46.40 | llm_api | 0 | mit ocw microecon 180 240 |

## Completed Clip Tracker

| clip_id | semantic_status | coaching_mode | top_action_count | confidence_note | reliability |
| --- | --- | --- | --- | --- | --- |
| cs50_business_150_210 | completed | llm_api_hybrid | 3 | Face visibility was limited in parts of the clip, so eye-contact and facial-ton… |  |
| mit_ocw_aero_300_360 | completed | llm_api_hybrid | 3 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_brain_300_360 | completed | llm_api | 1 | Hand visibility drops in parts of the clip, so gesture labels are less certain. |  |
| mit_ocw_how_to_speak_300_360 | completed | llm_api | 1 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_intro_120_180 | completed | llm_api_hybrid | 1 | Tracking quality is stable enough for formative review, but the outputs remain… |  |
| mit_ocw_linear_eq_180_240 | completed | llm_api | 0 | ["Face visibility is limited in parts of the clip, so eye-contact and facial-to… |  |
| mit_ocw_microecon_180_240 | completed | llm_api | 0 |  |  |
| mit_ocw_pigeonhole_240_300 | completed | llm_api_hybrid | 2 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_power_elec_240_300 | completed | llm_api_hybrid | 2 | Hand visibility drops in parts of the clip, so gesture labels are less certain. |  |
| mit_ocw_psychology_240_300 | completed | llm_api | 0 | ["Face visibility is limited in parts of the clip, so eye-contact and facial-to… |  |
| stanford_cs230_240_300 | completed | llm_api_hybrid | 2 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| stanford_give_lecture_180_240 | completed | llm_api | 1 | Hand visibility drops in parts of the clip, so gesture labels are less certain. |  |
| stanford_hbb_300_360 | completed | llm_api | 3 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| stanford_last_lecture_180_240 | completed | llm_api | 0 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| stanford_prog_method_240_300 | completed | llm_api_hybrid | 1 | Face coverage dropped below 95%; audience orientation and facial scores are les… |  |
| yale_deconstruction_180_240 | completed | llm_api | 1 | Tracking quality is stable enough for formative review, but the outputs remain… |  |
| yale_evolution_180_240 | completed | llm_api | 0 |  |  |
| yale_finance_240_300 | completed | llm_api_hybrid | 2 | Hand visibility drops in parts of the clip, so gesture labels are less certain. |  |
| yale_linguistics_180_240 | completed | llm_api_hybrid | 1 | Face coverage dropped below 95%; audience orientation and facial scores are les… |  |
| yale_newtonian_240_300 | completed | llm_api | 2 | Face coverage dropped below 95%; audience orientation and facial scores are les… |  |
| yale_power_politics_180_240 | completed | llm_api | 0 |  |  |
| yale_quantum_240_300 | completed | llm_api_hybrid | 2 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| yale_rome_180_240 | completed | llm_api_hybrid | 2 | ["Hand visibility drops in parts of the clip, so gesture labels are less certai… |  |
