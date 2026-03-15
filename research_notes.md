# Research Basis For Nonverbal Cue Feedback

This note records the main sources used to expand the nonverbal-cue evaluator.

## Core sources

1. Teacher nonverbal expressiveness boosts students’ attitudes and achievements: controlled experiments and meta-analysis. International Journal of Educational Technology in Higher Education, 2025.
   Link: https://link.springer.com/article/10.1186/s41239-025-00566-6
   Use in pipeline: supports keeping expressiveness, enthusiasm, and visible energy as positive feedback dimensions rather than treating all movement as distraction.

2. Instructors’ expressive nonverbal behavior hinders learning when learners’ prior knowledge is low. Frontiers in Psychology, 2022.
   Link: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.810451/full
   Use in pipeline: supports explicit excessive-animation risk instead of assuming more gesture is always better.

3. Instructor presence in video lectures: Eye gaze matters, but not body orientation. Computers & Education, 2020.
   Link: https://www.sciencedirect.com/science/article/pii/S0360131519302660
   Use in pipeline: supports giving more weight to face/head orientation and room-scan behavior than to coarse body orientation alone.

4. Teachers’ Gaze over Space and Time in a Real-World Classroom. Journal of Eye Movement Research / indexed summary, classroom eye-tracking study.
   Link: https://www.mdpi.com/1995-8692/13/4/28
   Use in pipeline: supports eye-contact distribution as a spatial-allocation problem and motivates sector-balance and scan-rate metrics.

5. A Multimodal Framework for Automated Teaching Quality Assessment of One-to-many Online Instruction Videos. ICPR 2022.
   Links:
   - https://ieeexplore.ieee.org/document/9956185/
   - https://sites.duke.edu/dkusmiip/files/2023/03/A_Multimodal_Framework_for_Automated_Teaching_Quality_Assessment_of_One_to_many_Online_Instruction_Videos.pdf
   Use in pipeline: supports interpretable mid-level features such as head pose/gaze and facial-expression proxies rather than black-box scoring.

6. EduSense: Practical Classroom Sensing at Scale. IMWUT 2019.
   Links:
   - https://dblp.org/rec/journals/imwut/AhujaKXVXZTHOA19
   - https://ubicomp.org/ubicomp2019/program_papers.html
   Use in pipeline: supports practical use of modular, interpretable features including gaze, smiles, pose, and movement in real classrooms.

7. Graph convolutional network for automatic detection of teachers’ nonverbal behavior. Computers & Education: Artificial Intelligence, 2023.
   Link: https://www.sciencedirect.com/science/article/pii/S2666920X2300053X
   Use in pipeline: supports posture/action-centric teacher behavior analysis and reinforces pose-based behavior categories as a viable cue family.

## Design implications adopted

- Natural movement is scored as a moderate-band target, not a monotonic “more is better” scale.
- Positive affect is treated mainly through facial openness and smile-related proxies.
- Hostility and rigidity are treated as low-confidence tension-risk flags, not as definitive emotion labels.
- Eye contact is estimated from head/face orientation and sector transitions because pupil-level gaze is not available in this pipeline.
- Grooming/professional appearance remains manual review only; no validated and fair landmark-only proxy was found for this setup.
