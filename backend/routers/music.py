import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from config import MUSIC_API_BASE

router = APIRouter(prefix="/api/music", tags=["music"])

MUSIC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class CookieInput(BaseModel):
    cookie: str


async def _proxy_get(path: str, params: dict = None):
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(f"{MUSIC_API_BASE}{path}", params=params)
            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Music API service not available. Please start the NeteaseCloudMusicApi service."
            )


@router.get("/search")
async def search_music(keywords: str = Query(...), limit: int = Query(30, ge=1, le=100)):
    data = await _proxy_get("/search", {"keywords": keywords, "limit": limit})
    return data


@router.get("/url")
async def get_music_url(id: int = Query(...)):
    data = await _proxy_get("/song/url", {"id": id})
    return data


@router.get("/detail")
async def get_music_detail(ids: str = Query(...)):
    data = await _proxy_get("/song/detail", {"ids": ids})
    return data


@router.get("/lyric")
async def get_lyric(id: int = Query(...)):
    data = await _proxy_get("/lyric", {"id": id})
    return data


@router.get("/recommend")
async def get_recommend():
    data = await _proxy_get("/personalized/newsong")
    return data


@router.get("/playlist")
async def get_playlist(id: int = Query(...)):
    data = await _proxy_get("/playlist/detail", {"id": id})
    return data


@router.get("/hot")
async def get_hot():
    data = await _proxy_get("/search/hot")
    return data


@router.get("/stream")
async def stream_audio(url: str = Query(...)):
    client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    try:
        req = client.build_request("GET", url, headers={
            "User-Agent": MUSIC_UA,
            "Referer": "https://music.163.com/",
            "Range": "bytes=0-",
        })
        resp = await client.send(req, stream=True)

        if resp.status_code not in (200, 206):
            await resp.aclose()
            raise HTTPException(status_code=502, detail="Upstream returned error")

        content_type = resp.headers.get("content-type", "audio/mpeg")
        content_length = resp.headers.get("content-length")

        async def stream_chunks():
            try:
                async for chunk in resp.aiter_bytes(chunk_size=8192):
                    yield chunk
            finally:
                await resp.aclose()
                await client.aclose()

        headers = {
            "Accept-Ranges": "bytes",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
        }
        if content_length:
            headers["Content-Length"] = content_length

        return StreamingResponse(
            stream_chunks(),
            media_type=content_type,
            headers=headers,
        )
    except httpx.ConnectError:
        await client.aclose()
        raise HTTPException(status_code=502, detail="Cannot connect to music CDN")


@router.get("/cookie")
async def get_cookie_status():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{MUSIC_API_BASE}/cookie")
            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Music API service not available")


@router.post("/cookie")
async def set_cookie(data: CookieInput):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(
                f"{MUSIC_API_BASE}/cookie",
                json={"cookie": data.cookie},
            )
            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Music API service not available")
