import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "api_base_url": API_BASE_URL}
    )
