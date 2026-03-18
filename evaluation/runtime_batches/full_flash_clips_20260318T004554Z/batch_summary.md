# Local Clips Gemini Flash Batch Summary

- Source dir: `/workspace/clips`
- Tracked batch dir: `/workspace/TeacherEvaluation/evaluation/runtime_batches/full_flash_clips_20260318T004554Z`
- Runs root: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local`
- Analysis FPS: `12.0`
- Window size: `15.0s`, step `15.0s`
- Semantic model: `gemini-2.5-flash`
- Coaching model: `gemini-2.5-flash`
- Selected clips: `9`

## Status Counts

| run_status | count |
| --- | --- |
| ok | 9 |

## Score Summary

| metric | count | mean | min | max |
| --- | --- | --- | --- | --- |
| overall_score | 9 | 48.54 | 29.31 | 63.44 |
| audience_score | 9 | 58.28 | 14.25 | 80.67 |
| alertness_score | 9 | 77.99 | 57.29 | 90.99 |

## Top 5

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_intro_120_180 | 63.44 | llm_api | 1 | mit ocw intro 120 180 |
| mit_ocw_brain_300_360 | 59.55 | llm_api | 2 | mit ocw brain 300 360 |
| mit_ocw_power_elec_240_300 | 51.93 | llm_api_hybrid | 3 | mit ocw power elec 240 300 |
| mit_ocw_pigeonhole_240_300 | 51.75 | llm_api_hybrid | 2 | mit ocw pigeonhole 240 300 |
| mit_ocw_how_to_speak_300_360 | 49.61 | llm_api_hybrid | 2 | mit ocw how to speak 300 360 |

## Bottom 5

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_linear_eq_180_240 | 29.31 | llm_api | 0 | mit ocw linear eq 180 240 |
| mit_ocw_aero_300_360 | 38.29 | llm_api_hybrid | 3 | mit ocw aero 300 360 |
| mit_ocw_microecon_180_240 | 46.40 | llm_api | 0 | mit ocw microecon 180 240 |
| cs50_business_150_210 | 46.57 | llm_api_hybrid | 3 | cs50 business 150 210 |
| mit_ocw_how_to_speak_300_360 | 49.61 | llm_api_hybrid | 2 | mit ocw how to speak 300 360 |

## Completed Clip Tracker

| clip_id | semantic_status | coaching_mode | top_action_count | confidence_note | reliability |
| --- | --- | --- | --- | --- | --- |
| cs50_business_150_210 | completed | llm_api_hybrid | 3 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_aero_300_360 | completed | llm_api_hybrid | 3 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_brain_300_360 | completed | llm_api | 2 | Hand visibility drops in parts of the clip, so gesture labels are less certain. |  |
| mit_ocw_how_to_speak_300_360 | completed | llm_api_hybrid | 2 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_intro_120_180 | completed | llm_api | 1 | Tracking quality is stable enough for formative review, but the outputs remain… |  |
| mit_ocw_linear_eq_180_240 | completed | llm_api | 0 | ["Face visibility is limited in parts of the clip, so eye-contact and facial-to… |  |
| mit_ocw_microecon_180_240 | completed | llm_api | 0 |  |  |
| mit_ocw_pigeonhole_240_300 | completed | llm_api_hybrid | 2 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_power_elec_240_300 | completed | llm_api_hybrid | 3 | Hand visibility drops in parts of the clip, so gesture labels are less certain. |  |
