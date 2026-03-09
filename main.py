"""
URL Shortener Service
----------------------
Run:  uvicorn main:app --reload
Docs: http://localhost:8000/docs

Endpoints:
  POST /shorten       — submit a long URL, get a short code
  GET  /{code}        — visit short URL, get redirected to original
  GET  /stats/{code}  — see click count and URL info
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from database import init_db, save_url, get_url, increment_clicks
from shortener import generate_short_code

app = FastAPI(title="URL Shortener")

# Create the database table when the app starts
init_db()

BASE_URL = "http://localhost:8000"


# ── Request body model ─────────────────────────────────────────────────────────

class ShortenRequest(BaseModel):
    long_url: str   # the URL the user wants to shorten


# ── Routes ─────────────────────────────────────────────────────────────────────


@app.post("/shorten")
def shorten_url(request: ShortenRequest):
    """
    Takes a long URL and returns a shortened version.

    Example input:  { "long_url": "https://www.google.com" }
    Example output: { "short_url": "http://localhost:8000/aa747c", "code": "aa747c" }
    """
    # Step 1: Generate a 6-character code from the URL
    code = generate_short_code(request.long_url)

    # Step 2: Save it to the database
    save_url(code, request.long_url)

    # Step 3: Return the short URL
    return {
        "short_url": f"{BASE_URL}/{code}",
        "code":      code,
        "long_url":  request.long_url,
    }


@app.get("/stats/{code}")
def get_stats(code: str):
    """
    Returns info about a short URL — original link, click count, creation time.

    Example: GET /stats/aa747c
    """
    url = get_url(code)

    if url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return {
        "code":       url["code"],
        "short_url":  f"{BASE_URL}/{url['code']}",
        "long_url":   url["long_url"],
        "clicks":     url["clicks"],
        "created_at": url["created_at"],
    }


@app.get("/{code}")
def redirect_to_url(code: str):
    """
    Redirects the user to the original URL when they visit a short link.

    Example: GET /aa747c  →  302 redirect to https://www.google.com
    """
    url = get_url(code)

    if url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Record this visit
    increment_clicks(code)

    # Redirect the user to the original URL
    return RedirectResponse(url=url["long_url"])
