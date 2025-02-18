from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pymongo import MongoClient

from fastapi import FastAPI
from .vacances import router as vacances_router  # ✅ Import the router

app = FastAPI()



# ✅ Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client["mydatabase"]
collectionVacances = db["vacances"]


# finding vacances list
vac_list = collectionVacances.find()

# Set up Jinja2 templates
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Define a route to render the template
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello, FastAPI with Jinja2!"})

app.include_router(vacances_router, prefix="/vacances", tags=["vacances"])