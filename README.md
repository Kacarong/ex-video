# ex-video

강의 영상에서 **음성 전사 + 슬라이드 텍스트(OCR) + 슬라이드/그림 이미지**를 자동 추출해,
Gemini·Claude에 바로 붙여넣어 "원하는 구성/디자인으로 PDF 정리해줘"라고 시킬 수 있는
**붙여넣기용 프롬프트 묶음(bundle.md)** 을 만들어 주는 로컬 프로그램입니다.

- 추출 단계는 **외부 유료 API 없이 로컬에서 무료**로 동작합니다(전사=Whisper, OCR=easyOCR).
- 최종 정리·디자인은 사용자가 직접 Gemini/Claude에 붙여넣어 진행합니다.
- 구글드라이브 공유 링크 / 로컬 파일 / URL 모두 입력 가능합니다.

## 설치

Python 3.10+ 필요. (GPU가 있으면 자동으로 CUDA 가속을 사용합니다.)

```bash
git clone https://github.com/Kacarong/ex-video.git
cd ex-video
python -m venv .venv
# Windows: .venv\Scripts\activate   |  Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

시스템에 `ffmpeg`가 있으면 더 안정적입니다(없어도 대부분 동작).

## 사용법

```bash
# 로컬 파일
python -m exvideo "C:\lectures\lecture1.mp4" -o output

# 구글드라이브 공유 링크 ("링크가 있는 모든 사용자" 권한이어야 함)
python -m exvideo "https://drive.google.com/file/d/FILEID/view" -o output
```

끝나면 `output/` 에 다음이 생성됩니다.

- `bundle.md` — 전사 + 슬라이드 텍스트 + 그림 목록을 시간순으로 정리한 **붙여넣기용 프롬프트**
- `transcript.txt` — 순수 음성 전사본
- `slides/` — 고유 슬라이드 이미지(중복 제거됨)
- `figures/` — 슬라이드에서 잘라낸 **그림/도표 영역** 이미지

`bundle.md` 를 열어 맨 위 `[요청]` 칸에 원하는 정리 방식을 적고, 전체를 복사해
Gemini/Claude에 붙여넣으세요. 도표가 중요하면 `figures/` 이미지를 함께 첨부하면 됩니다.

## 주요 옵션

| 옵션 | 설명 |
|---|---|
| `--model` | Whisper 모델 크기 (tiny/base/small/medium/large-v3, 기본 large-v3) |
| `--lang` | 음성 언어 (기본 ko) |
| `--sample-interval` | 슬라이드 검사 간격(초, 기본 1.0) |
| `--diff-threshold` | 슬라이드 전환 감지 민감도(클수록 둔감, 기본 8.0) |
| `--no-ocr` | 슬라이드 OCR 생략 |
| `--no-figures` | 그림 크롭 생략 |
| `--skip-transcribe` | 음성 전사 생략(슬라이드만) |
| `--cpu` | GPU 대신 CPU 강제 |

## 참고

- 그림 크롭은 "배경과 다른 큰 영역에서 텍스트를 제외"하는 휴리스틱이라 슬라이드 디자인에 따라 정확도가 달라질 수 있습니다.
- 화면 캡처 방식이라 그림 화질은 원본 영상 해상도가 상한입니다. 원본 PPT/PDF가 있으면 그쪽이 더 깨끗합니다.
