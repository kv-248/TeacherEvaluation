# Local Clips Gemini Flash Batch Summary

- Source dir: `/workspace/clips`
- Tracked batch dir: `/workspace/TeacherEvaluation/evaluation/runtime_batches/local_flash_full_live`
- Runs root: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local`
- Analysis FPS: `12.0`
- Window size: `15.0s`, step `15.0s`
- Semantic model: `gemini-2.5-flash`
- Coaching model: `gemini-2.5-flash`
- Selected clips: `3`

## Status Counts

| run_status | count |
| --- | --- |
| ok | 3 |

## Score Summary

| metric | count | mean | min | max |
| --- | --- | --- | --- | --- |
| overall_score | 3 | 48.13 | 38.29 | 59.55 |
| audience_score | 3 | 58.19 | 45.93 | 80.67 |
| alertness_score | 3 | 79.25 | 71.69 | 90.99 |

## Top 3

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_brain_300_360 | 59.55 | llm_api | 2 | mit ocw brain 300 360 |
| cs50_business_150_210 | 46.57 | llm_api_hybrid | 3 | cs50 business 150 210 |
| mit_ocw_aero_300_360 | 38.29 | llm_api_hybrid | 3 | mit ocw aero 300 360 |

## Bottom 3

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_aero_300_360 | 38.29 | llm_api_hybrid | 3 | mit ocw aero 300 360 |
| cs50_business_150_210 | 46.57 | llm_api_hybrid | 3 | cs50 business 150 210 |
| mit_ocw_brain_300_360 | 59.55 | llm_api | 2 | mit ocw brain 300 360 |

## Completed Clip Tracker

| clip_id | semantic_status | coaching_mode | top_action_count | confidence_note | reliability |
| --- | --- | --- | --- | --- | --- |
| cs50_business_150_210 | completed | llm_api_hybrid | 3 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_aero_300_360 | completed | llm_api_hybrid | 3 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_brain_300_360 | completed | llm_api | 2 | Hand visibility drops in parts of the clip, so gesture labels are less certain. |  |
