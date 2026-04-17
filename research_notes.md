# Research Basis for TeacherEvaluation V2

This note records the research traceability used for the thesis-facing TeacherEvaluation update: Gemini Pro-first evaluation, richer landmark-only cues, and more readable teacher reports.

## Evidence tiers

1. Peer-reviewed educational / behavioral evidence
   Use this tier for claims about teacher nonverbal constructs: proxemics, gaze dynamics, pause structure, facial expressiveness, and teacher uptake of feedback.

2. Multimodal classroom-observation systems evidence
   Use this tier for claims that multimodal AI or vision-language systems are a legitimate substrate for teacher analytics and classroom observation.

3. Model-capability / operational evidence
   Use this tier for the Gemini choice. We should not claim that peer-reviewed education research proves Gemini Pro is better than Flash for teacher coaching. The defensible claim is narrower: Pro is the higher-capability multimodal reasoning tier, and local operational logs show Flash has been quota-constrained in this repo.

## Cue traceability matrix

| Construct | Implementation signal | Summary keys | Threshold provenance | Teacher-facing claim boundary | Sources |
| --- | --- | --- | --- | --- | --- |
| Proxemics / stage movement | `floor_x`, `floor_y`, left-center-right dwell, zone transitions, coverage grid occupancy | `movement_presence.zones.*.dwell_pct`, `movement_presence.zone_transition_count`, `movement_presence.static_zone_time_pct`, `movement_presence.coverage_area_pct` | `zone_edges` is an initial heuristic for calibration; static dwell and coverage bands are heuristic bands derived from immediacy literature | Report as room coverage, anchoring, and movement variety. Do not claim classroom effectiveness from any one movement pattern alone. | Andersen (1979); Witt et al. (2004); Liu et al. (2021); Ballester et al. (2025) |
| Pause / stillness events | low `gesture_motion` plus low hip drift over time, merged into contiguous pause events | `movement_presence.pause_count`, `movement_presence.dramatic_pause_count`, `movement_presence.static_stretch_count`, `movement_presence.pause_duration.*` | `static_min_sec=3.0` is literature-anchored by wait-time research; shorter dramatic-pause thresholds are heuristic bands derived from literature | Report as visible pause structure and stillness, not as definitive pedagogical wait-time quality without audio or classroom turn-taking context. | Rowe (1986); Tobin (1987); Stahl (1994) |
| Gaze sweep dynamics | run lengths and transitions over `gaze_sector` time series | `gaze_dynamics.sector_dwell_mean`, `gaze_dynamics.sector_dwell_max`, `gaze_dynamics.sector_distribution_entropy`, `gaze_dynamics.sweep_rate_per_min`, `gaze_dynamics.longest_fixation_sec` | Entropy and sweep-rate bands are heuristic bands derived from literature | Report as room-facing distribution and sweep behavior, not true pupil-level eye contact. | Pi et al. (2020); Smidekova et al. (2020); McIntyre et al. (2017); Goldberg et al. (2021) |
| Facial expressiveness variance | rolling standard deviation of smile, brow-eye, and mouth-open proxies | `facial_expressiveness.smile_rolling_std_mean`, `facial_expressiveness.brow_rolling_std_mean`, `facial_expressiveness.mouth_rolling_std_mean`, `facial_expressiveness.facial_flatness_flag` | Flatness thresholds are initial heuristics for calibration; the construct itself is literature-backed | Report as expressive range or facial flatness watch-items. Do not imply that more expressiveness is always better. | Tikochinski et al. (2025); Wang et al. (2022); Ekman and Friesen (1978) |
| Readable teacher report | scorecard, merged sections, moment-linked evidence, plain-language interpretation | `scorecard`, `priority_actions`, `top_strengths`, `evidence_moments`, `confidence_notes` | Design pattern, not a numeric threshold | Claim that concrete, brief, timestamped feedback is more actionable than raw metric dumps. | Demszky et al. (2024); Nadaf et al. (2025 preprint) |
| Gemini Pro-first runtime | `gemini-2.5-pro` default with dynamic thinking budget and existing retry logic | runtime default model, request metadata logs, coaching and semantic model selection | Operational choice; not a pedagogical threshold | Claim this is a system-engineering choice grounded in multimodal capability evidence plus local quota failures on Flash. | Zheng et al. (2024); Comanici et al. (2025); Google Developers Blog (2025); repo logs |

## Threshold provenance labels used in code and thesis text

- `literature-anchored`
  Use when the literature supports the approximate cutoff directly enough to justify the band. In this update, the clearest example is the longer pause / static-stretch threshold family grounded by wait-time studies.

- `heuristic band derived from literature`
  Use when the literature strongly supports the construct, but not the exact cutoff used in the code. Most proxemics and gaze-dynamics bands fall here.

- `initial heuristic for calibration`
  Use when the construct is supported, but the threshold still needs tuning against the curated clip set. The expressiveness flatness cutoffs belong here.

## Thesis wording guardrails

- Say that Gemini Pro is the default because it is the higher-capability multimodal reasoning tier and because Flash has shown repeated quota pressure in this repo.
- Do not say that peer-reviewed education research proves Gemini Pro is educationally superior to Flash.
- Say that the new cue families are literature-backed constructs implemented with landmark-only proxies.
- Do not say that the landmark proxies recover ground-truth eye contact, pedagogical wait time, or emotional state.
- Say that the report redesign is intended to improve coachability and evidence uptake by moving the actionable summary to the top and preserving moment-linked evidence underneath.

## Key sources

1. Tikochinski, R., Babad, E., and Hammer, R. (2025). Teacher's nonverbal expressiveness boosts students' attitudes and achievements: controlled experiments and meta-analysis. International Journal of Educational Technology in Higher Education.
2. Wang, Y., Pi, Z., and Hu, W. (2022). Instructors' expressive nonverbal behavior hinders learning when learners' prior knowledge is low. Frontiers in Psychology.
3. Pi, Z., Xu, K., Liu, C., and Yang, J. (2020). Instructor presence in video lectures: Eye gaze matters, but not body orientation. Computers and Education.
4. Smidekova, H., Janik, T., and Najvar, P. (2020). Teachers' Gaze over Space and Time in a Real-World Classroom. Journal of Eye Movement Research.
5. Andersen, J. F. (1979). Teacher immediacy as a predictor of teaching effectiveness. Communication Yearbook 3.
6. Witt, P. L., Wheeless, L. R., and Allen, M. (2004). A meta-analytical review of the relationship between teacher immediacy and student learning. Communication Education.
7. Liu, S., Zhang, J., Jensen, J., and Gao, Y. (2021). Does Teacher Immediacy Affect Students? A Systematic Review. Frontiers in Psychology.
8. Ballester, L. et al. (2025). Teacher nonverbal immediacy: a validation study of the TeNOI observation scale. Scandinavian Journal of Educational Research.
9. Rowe, M. B. (1986). Wait Time: Slowing Down May Be a Way of Speeding Up. Journal of Teacher Education.
10. Tobin, K. (1987). The Role of Wait Time in Higher Cognitive Level Learning. Review of Educational Research.
11. Stahl, R. J. (1994). Using Think-Time and Wait-Time Skillfully in the Classroom. ERIC ED370885.
12. Ekman, P., and Friesen, W. V. (1978). Facial Action Coding System.
13. Demszky, D., Liu, J., Hill, H. C., Jurafsky, D., and Piech, C. (2024). Can Automated Feedback Improve Teachers' Uptake of Student Ideas?
14. Zheng, J. et al. (2024). I see you: teacher analytics with GPT-4 vision-powered observational assessment. Smart Learning Environments.
15. Comanici, A. et al. (2025). Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, Long Context, and Next-Generation Agentic Capabilities.
16. Google Developers Blog. (2025-05-09). Advancing the frontier of video understanding with Gemini 2.5.
17. Nadaf, et al. (2025). ClassMind: Scaling Classroom Observation and Instructional Feedback with Multimodal AI. Preprint.
18. Liu, Z. et al. (2025). A Multi-Modal Dataset for Teacher Behavior Analysis in Offline Classrooms. Scientific Data.
