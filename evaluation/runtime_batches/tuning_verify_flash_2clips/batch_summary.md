# Local Clips Gemini Flash Batch Summary

- Source dir: `/workspace/clips`
- Tracked batch dir: `/workspace/TeacherEvaluation/evaluation/runtime_batches/tuning_verify_flash_2clips`
- Runs root: `/workspace/TeacherEvaluation/evaluation/local_data/runs/gemini_flash_local`
- Analysis FPS: `12.0`
- Window size: `15.0s`, step `15.0s`
- Semantic model: `gemini-2.5-flash`
- Coaching model: `gemini-2.5-flash`
- Selected clips: `1`

## Status Counts

| run_status | count |
| --- | --- |
| ok | 1 |

## Score Summary

| metric | count | mean | min | max |
| --- | --- | --- | --- | --- |
| overall_score | 1 | 59.55 | 59.55 | 59.55 |
| audience_score | 1 | 80.67 | 80.67 | 80.67 |
| alertness_score | 1 | 90.99 | 90.99 | 90.99 |

## Top 1

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_brain_300_360 | 59.55 | llm_api | 2 | mit ocw brain 300 360 |

## Bottom 1

| clip_id | overall_score | coaching_mode | top_action_count | title |
| --- | --- | --- | --- | --- |
| mit_ocw_brain_300_360 | 59.55 | llm_api | 2 | mit ocw brain 300 360 |

## Completed Clip Tracker

| clip_id | semantic_status | coaching_mode | top_action_count | confidence_note | reliability |
| --- | --- | --- | --- | --- | --- |
| mit_ocw_brain_300_360 | completed | llm_api | 2 | Hand visibility drops in parts of the clip, so gesture labels are less certain. |  |
