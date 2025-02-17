from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pymongo import MongoClient

# Initialize FastAPI app
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

@app.get("/vacances")
async def show_vacances(
    request: Request,
    max_price: str = Query(None, alias="prix"),  # Prix maximum optionnel
    only_available: bool = Query(False, alias="disponible")  # Filtrer la disponibilité
):
    query = {}

    # ✅ Appliquer le filtre uniquement si un prix est fourni
    if max_price and max_price.isnumeric() :
        if max_price is not None and int(max_price) > 0:
            query["prix"] = {"$lte": int(max_price)}

    # ✅ Appliquer le filtre de disponibilité uniquement si activé
    if only_available:
        query["disponibilite"] = "true"

    # ✅ Récupérer les offres filtrées
    offres = list(collectionVacances.find(query, {"_id": 0}))

    return templates.TemplateResponse("vacances.html", {"request": request, "offres": offres})