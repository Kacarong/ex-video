"""ex-video 웹앱 백엔드 (FastAPI).

드라이브 링크/URL/로컬경로를 받아 백그라운드에서 처리하고,
진행률을 폴링으로 제공하며, 완료 시 결과(zip)를 내려받게 한다.
서버(.9)의 GPU에서 처리가 돌아간다.
"""
import io
import os
import sys
import threading
import uuid
import zipfile

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 프로젝트 루트를 import 경로에 추가 (exvideo 패키지 사용)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from exvideo.pipeline import run_pipeline  # noqa: E402

APP_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_DIR = os.path.join(APP_DIR, "jobs")
os.makedirs(JOBS_DIR, exist_ok=True)

app = FastAPI(title="ex-video web")
JOBS = {}
_lock = threading.Lock()


class JobRequest(BaseModel):
    source: str
    transcribe: bool = True
    ocr: bool = True
    figures: bool = True
    model: str = "large-v3"
    cpu: bool = False


def _worker(job_id: str, req: JobRequest):
    out_dir = os.path.join(JOBS_DIR, job_id)

    def progress(msg, pct=None):
        with _lock:
            j = JOBS[job_id]
            j["messages"].append(msg)
            if pct is not None:
                j["progress"] = pct
            j["status"] = "running"

    try:
        res = run_pipeline(
            req.source, out_dir,
            model=req.model, do_transcribe=req.transcribe,
            do_ocr=req.ocr, do_figures=req.figures, cpu=req.cpu,
            progress=progress,
        )
        with _lock:
            JOBS[job_id].update(status="done", progress=100, result=res)
    except Exception as e:  # noqa: BLE001
        with _lock:
            JOBS[job_id].update(status="error", error=str(e))


@app.post("/api/jobs")
def create_job(req: JobRequest):
    job_id = uuid.uuid4().hex[:12]
    with _lock:
        JOBS[job_id] = {"status": "queued", "progress": 0, "messages": [],
                        "result": None, "error": None}
    threading.Thread(target=_worker, args=(job_id, req), daemon=True).start()
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    with _lock:
        j = JOBS.get(job_id)
        if not j:
            raise HTTPException(404, "job not found")
        out = dict(j)
    return out


@app.get("/api/jobs/{job_id}/bundle")
def get_bundle(job_id: str):
    with _lock:
        j = JOBS.get(job_id)
    if not j or j.get("status") != "done":
        raise HTTPException(404, "not ready")
    return FileResponse(j["result"]["bundle"], media_type="text/markdown", filename="bundle.md")


@app.get("/api/jobs/{job_id}/download")
def download_zip(job_id: str):
    with _lock:
        j = JOBS.get(job_id)
    if not j or j.get("status") != "done":
        raise HTTPException(404, "not ready")
    out_dir = os.path.join(JOBS_DIR, job_id)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _dirs, files in os.walk(out_dir):
            for f in files:
                if f == "source_video.mp4":
                    continue  # 원본 영상은 제외
                fp = os.path.join(root, f)
                z.write(fp, os.path.relpath(fp, out_dir))
    buf.seek(0)
    return StreamingResponse(
        buf, media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="exvideo_{job_id}.zip"'},
    )


# 정적 프론트엔드
app.mount("/", StaticFiles(directory=os.path.join(APP_DIR, "static"), html=True), name="static")
