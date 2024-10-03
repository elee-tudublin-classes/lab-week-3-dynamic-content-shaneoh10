import httpx
import json
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager
from starlette.config import Config

# Load environment variables from .env
config = Config(".env")

# Get URL values from the .env file
ADVICE_URL = config("ADVICE_URL")
APOD_URL = f"{config("NASA_APOD_URL")}{config("NASA_API_KEY")}"


# Create an async context manager to handle the lifespan of the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.requests_client = httpx.AsyncClient()
    yield
    await app.requests_client.aclose()


# create app instance
app = FastAPI(lifespan=lifespan)


# set location for templates
templates = Jinja2Templates(directory="app/view_templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Return the index.html page."""
    server_time: datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse(
        "index.html", {"request": request, "server_time": server_time}
    )


@app.get("/advice", response_class=HTMLResponse)
async def advice(request: Request):
    """Return the advice.html page. Gets data from external advice API."""
    requests_client = request.app.requests_client

    response = await requests_client.get(ADVICE_URL)

    return templates.TemplateResponse(
        "advice.html", {"request": request, "data": response.json()}
    )


@app.get("/apod", response_class=HTMLResponse)
async def apod(request: Request):
    """Return the apod.html page. Get data from external APOD API."""
    requests_client = request.app.requests_client

    response = await requests_client.get(APOD_URL)

    return templates.TemplateResponse(
        "apod.html", {"request": request, "data": response.json()}
    )


@app.get("/params", response_class=HTMLResponse)
async def params(request: Request, name: str | None = ""):
    """Return the params.html page."""
    return templates.TemplateResponse("params.html", {"request": request, "name": name})


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)
