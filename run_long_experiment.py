from __future__ import annotations

import argparse
from pathlib import Path

from nonverbal_eval.app_service import run_teacher_evaluation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run long-form nonverbal cue inference over an extended lecture segment.")
    parser.add_argument("--video", type=Path, required=True, help="Path to the source lecture video.")
    parser.add_argument("--output-root", type=Path, default=Path("/workspace/artifacts/nonverbal_eval_long"), help="Directory for long-run artifacts.")
    parser.add_argument("--start-sec", type=float, default=92.5, help="Start time of the analyzed context window in the source video.")
    parser.add_argument("--duration-sec", type=float, default=60.0, help="Duration of the analyzed context window. Use 0 to continue until the end.")
    parser.add_argument("--analysis-fps", type=float, default=12.0, help="FPS to use for the extracted analysis clip. Use 0 to keep the source FPS.")
    parser.add_argument("--window-sec", type=float, default=15.0, help="Window size for lecture-level summaries.")
    parser.add_argument("--window-step-sec", type=float, default=15.0, help="Window stride for lecture-level summaries.")
    parser.add_argument("--keyframe-offset-sec", type=float, default=-1.0, help="Keyframe offset inside the full analyzed segment. Negative means midpoint.")
    parser.add_argument("--enable-semantic", action="store_true", help="Run optional SAM2/Qwen semantic analysis as additive evidence.")
    parser.add_argument("--semantic-sample-interval-sec", type=float, default=6.0, help="Uniform sampling interval for semantic review frames.")
    parser.add_argument("--semantic-max-samples", type=int, default=8, help="Maximum number of sampled frames for semantic review.")
    parser.add_argument("--disable-qwen", action="store_true", help="Skip the Qwen semantic annotator.")
    parser.add_argument("--qwen-model", type=str, default="Qwen/Qwen2.5-VL-7B-Instruct", help="Transformers model id for Qwen vision-language inference.")
    parser.add_argument("--qwen-device", type=str, default="cuda:0", help="Device for the Qwen model, for example cuda:0, cpu, or auto.")
    parser.add_argument("--qwen-device-map", type=str, default="", help="Optional transformers device_map value such as auto for larger Qwen checkpoints.")
    parser.add_argument("--qwen-dtype", type=str, default="bfloat16", help="Torch dtype for Qwen model loading.")
    parser.add_argument("--qwen-max-new-tokens", type=int, default=180, help="Maximum generated tokens for each semantic frame prompt.")
    parser.add_argument("--qwen-temperature", type=float, default=0.1, help="Sampling temperature for the Qwen semantic prompt.")
    parser.add_argument("--disable-sam2", action="store_true", help="Skip SAM2 mask extraction.")
    parser.add_argument("--sam2-model-cfg", type=str, default="", help="SAM2 model config name or path.")
    parser.add_argument("--sam2-checkpoint", type=Path, default=None, help="Path to a local SAM2 checkpoint.")
    parser.add_argument("--sam2-device", type=str, default="cuda:1", help="Device for SAM2 inference, for example cuda:1 or cpu.")
    parser.add_argument("--enable-coaching", action="store_true", help="Generate a teacher-facing coaching brief as an additive artifact.")
    parser.add_argument("--coach-model", type=str, default="Qwen/Qwen2.5-3B-Instruct", help="Local text-only model used to synthesize the coaching brief.")
    parser.add_argument("--coach-device", type=str, default="cuda:1", help="Device for the coaching text model, for example cuda:1 or cpu.")
    parser.add_argument("--coach-max-windows", type=int, default=6, help="Maximum number of time windows to review in the coaching report.")
    parser.add_argument("--coach-top-actions", type=int, default=3, help="Number of top-priority actions to include in the coaching brief.")
    parser.add_argument("--coach-render-pdf", action=argparse.BooleanOptionalAction, default=True, help="Render the coaching brief to PDF in addition to markdown and JSON.")
    parser.add_argument("--coach-fallback-template-only", action="store_true", help="Skip the small text model and use the deterministic coaching template only.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_teacher_evaluation(
        video=args.video,
        output_root=args.output_root,
        start_sec=args.start_sec,
        duration_sec=args.duration_sec,
        analysis_fps=args.analysis_fps,
        window_sec=args.window_sec,
        window_step_sec=args.window_step_sec,
        keyframe_offset_sec=args.keyframe_offset_sec,
        enable_semantic=args.enable_semantic,
        semantic_sample_interval_sec=args.semantic_sample_interval_sec,
        semantic_max_samples=args.semantic_max_samples,
        disable_qwen=args.disable_qwen,
        qwen_model=args.qwen_model,
        qwen_device=args.qwen_device,
        qwen_device_map=args.qwen_device_map or None,
        qwen_dtype=args.qwen_dtype,
        qwen_max_new_tokens=args.qwen_max_new_tokens,
        qwen_temperature=args.qwen_temperature,
        disable_sam2=args.disable_sam2,
        sam2_model_cfg=args.sam2_model_cfg or None,
        sam2_checkpoint=args.sam2_checkpoint,
        sam2_device=args.sam2_device,
        enable_coaching=args.enable_coaching,
        coach_model=args.coach_model,
        coach_device=args.coach_device,
        coach_max_windows=args.coach_max_windows,
        coach_top_actions=args.coach_top_actions,
        coach_render_pdf=args.coach_render_pdf,
        coach_fallback_template_only=args.coach_fallback_template_only,
    )

    summary = result["summary"]
    metadata = result["metadata"]
    best = metadata["windowing"]["best_window"]
    worst = metadata["windowing"]["worst_window"]

    print(f"Run directory: {result['run_dir']}")
    print(
        f"Source window: start={summary['clip']['start_sec']:.2f}s "
        f"duration={summary['clip']['duration_sec_actual']:.2f}s"
    )
    print(f"Analysis FPS: {summary['clip']['fps']:.2f}")
    print(f"Full duration analyzed: {summary['clip']['duration_sec_actual']:.2f}s")
    print(f"Frames analyzed: {summary['quality_control']['frames_analyzed']}")
    print(f"Overall score: {summary['scores']['heuristic_nonverbal_score']:.2f}")
    print(f"Best window: {best['window_start_sec']:.0f}s-{best['window_end_sec']:.0f}s overall={best['heuristic_nonverbal_score']:.2f}")
    print(f"Worst window: {worst['window_start_sec']:.0f}s-{worst['window_end_sec']:.0f}s overall={worst['heuristic_nonverbal_score']:.2f}")
    for key, value in result["timings"].items():
        print(f"{key}: {value:.2f}s")
    if result["semantic_payload"] is not None:
        semantic_summary = result["semantic_payload"]["summary"]
        print(f"Semantic samples: {semantic_summary['sample_count']}")
        print(f"Qwen semantic status: {semantic_summary['qwen']['status']}")
        print(f"SAM2 semantic status: {semantic_summary['sam2']['status']}")
        print(f"Semantic summary: {result['semantic_payload']['artifacts']['summary_md']}")
    if result["coaching_payload"] is not None:
        print(f"Coaching report: {result['coaching_payload']['artifacts']['report_md']}")
        print(f"Coaching PDF: {result['coaching_payload']['artifacts']['report_pdf']}")


if __name__ == "__main__":
    main()
