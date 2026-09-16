import argparse
import os
import sys

from . import __version__


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="exvideo",
        description="강의 영상 → 전사 + 슬라이드 텍스트 + 슬라이드/그림 이미지 → 붙여넣기용 프롬프트 묶음",
    )
    p.add_argument("input", help="영상 파일 경로 또는 구글드라이브/URL 링크")
    p.add_argument("-o", "--out", default="output", help="결과 저장 폴더 (기본: output)")
    p.add_argument("--model", default="large-v3", help="Whisper 모델 크기 (tiny/base/small/medium/large-v3)")
    p.add_argument("--lang", default="ko", help="음성 언어 코드 (기본: ko)")
    p.add_argument("--sample-interval", type=float, default=1.0, help="슬라이드 검사 간격(초)")
    p.add_argument("--diff-threshold", type=float, default=8.0, help="슬라이드 전환 감지 민감도(클수록 둔감)")
    p.add_argument("--no-ocr", action="store_true", help="슬라이드 OCR 생략")
    p.add_argument("--no-figures", action="store_true", help="그림 크롭 생략")
    p.add_argument("--skip-transcribe", action="store_true", help="음성 전사 생략(슬라이드만)")
    p.add_argument("--cpu", action="store_true", help="GPU 대신 CPU 강제")
    p.add_argument("--version", action="version", version=f"ex-video {__version__}")
    args = p.parse_args(argv)

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    # 1) 입력 해석 (로컬/구글드라이브/URL)
    from .download import resolve_input
    video = resolve_input(args.input, out_dir)
    print(f"[입력] {video}")

    # 2) 음성 전사
    transcript = []
    if not args.skip_transcribe:
        from .transcribe import transcribe
        transcript = transcribe(video, model_size=args.model, language=args.lang,
                                 device="cpu" if args.cpu else "auto")
    else:
        print("[전사] 생략됨(--skip-transcribe)")

    # 3) 슬라이드 추출
    from .slides import extract_slides
    print("[슬라이드] 키프레임 추출/중복제거 중 ...")
    slides = extract_slides(video, out_dir, sample_interval=args.sample_interval,
                            diff_threshold=args.diff_threshold)
    print(f"[슬라이드] 고유 슬라이드 {len(slides)}개")

    # 4) 슬라이드별 OCR + 그림 크롭
    gpu = not args.cpu
    for sl in slides:
        boxes = []
        if not args.no_ocr:
            try:
                from .ocr import ocr_image
                sl["ocr_text"], boxes = ocr_image(sl["path"], gpu=gpu)
            except Exception as e:
                print(f"  [OCR 경고] {sl['path']}: {e}")
                sl["ocr_text"] = ""
        else:
            sl["ocr_text"] = ""
        if not args.no_figures:
            try:
                from .figures import extract_figures
                sl["figures"] = extract_figures(sl["path"], out_dir, text_boxes=boxes)
            except Exception as e:
                print(f"  [그림 경고] {sl['path']}: {e}")
                sl["figures"] = []
        else:
            sl["figures"] = []
        print(f"  슬라이드 {sl['index']} [{sl['ts']}] · 그림 {len(sl.get('figures', []))}개")

    # 5) 프롬프트 묶음 생성
    from .bundle import build_bundle
    bundle_path = build_bundle(out_dir, transcript, slides)
    print("\n완료!")
    print(f"  - 프롬프트 묶음: {bundle_path}")
    print(f"  - 슬라이드 이미지: {os.path.join(out_dir, 'slides')}")
    print(f"  - 그림 이미지:   {os.path.join(out_dir, 'figures')}")
    print("이 bundle.md 내용을 Gemini/Claude에 붙여넣고, 필요하면 슬라이드/그림 이미지를 함께 첨부하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
