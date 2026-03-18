# Local Clips Gemini Flash Batch Summary

- Source dir: `/workspace/clips`
- Tracked batch dir: `/workspace/TeacherEvaluation/evaluation/runtime_batches/smoke_flash_current_2clips`
- Runs root: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local`
- Analysis FPS: `12.0`
- Window size: `15.0s`, step `15.0s`
- Semantic model: `gemini-2.5-flash`
- Coaching model: `gemini-2.5-flash`
- Selected clips: `2`

## Status Counts

| run_status | count |
| --- | --- |
| ok | 2 |

## Score Summary

| metric | count | mean | min | max |
| --- | --- | --- | --- | --- |
| overall_score | 2 | 42.43 | 38.29 | 46.57 |
| audience_score | 2 | 46.95 | 45.93 | 47.97 |
| alertness_score | 2 | 73.39 | 71.69 | 75.08 |

## Top 2

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| cs50_business_150_210 | 46.57 | template_fallback | 3 | cs50 business 150 210 |
| mit_ocw_aero_300_360 | 38.29 | template_fallback | 3 | mit ocw aero 300 360 |

## Bottom 2

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_aero_300_360 | 38.29 | template_fallback | 3 | mit ocw aero 300 360 |
| cs50_business_150_210 | 46.57 | template_fallback | 3 | cs50 business 150 210 |

## Completed Clip Tracker

| clip_id | semantic_status | coaching_mode | top_action_count | confidence_note | reliability |
| --- | --- | --- | --- | --- | --- |
| cs50_business_150_210 | failed | template_fallback | 3 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
| mit_ocw_aero_300_360 | failed | template_fallback | 3 | Face visibility is limited in parts of the clip, so eye-contact and facial-tone… |  |
