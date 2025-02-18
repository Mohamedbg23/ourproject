from fastapi import APIRouter, Request, Query, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from pathlib import Path
from bson import ObjectId  

# ✅ Set up router
router = APIRouter()

# ✅ Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client["mydatabase"]
collectionVacances = db["vacances"]

# ✅ Set up Jinja2 templates
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ✅ Route to display vacations with filters
@router.get("/", response_class=HTMLResponse)
async def show_vacances(
    request: Request,
    max_price: str = Query(None, alias="prix"),  # Prix maximum optionnel
    only_available: bool = Query(False, alias="disponible")  # Filtrer la disponibilité
):
    query = {}

    # ✅ Apply price filter if provided
    if max_price and max_price.isnumeric():
        if int(max_price) > 0:
            query["prix"] = {"$lte": int(max_price)}

    # ✅ Apply availability filter if activated
    if only_available:
        query["disponibilite"] = "true"

    # ✅ Retrieve filtered offers
    offres = list(collectionVacances.find(query, {"_id": 0}))

    return templates.TemplateResponse(
        "vacances.html", 
        {"request": request, "offres": offres, "empty": not offres}
    )

# ✅ Route to display the vacation creation form
@router.get("/new", response_class=HTMLResponse)
async def create_vacances_form(request: Request):
    return templates.TemplateResponse("create_vacances.html", {"request": request})

@router.get("/delete", response_class=HTMLResponse)
async def delete_vacances_form(request: Request):
    # ✅ Fetch vacations and include `_id`, converting it to a string
    offres = list(collectionVacances.find({}, {"_id": 1, "nom": 1}))  
    for offre in offres:
        offre["id"] = str(offre["_id"])  # Convert ObjectId to string

    return templates.TemplateResponse("delete_vacances.html", {"request": request, "offres": offres})

# ✅ DELETE route to process the form submission
@router.post("/delete", response_class=RedirectResponse)
async def delete_vacances(vacance_id: str = Form(...)):
    # ✅ Convert the string ID back to ObjectId
    object_id = ObjectId(vacance_id)

    # ✅ Remove the vacation from MongoDB
    result = collectionVacances.delete_one({"_id": object_id})

    # ✅ Check if the vacation was deleted
    if result.deleted_count == 0:
        return RedirectResponse(url="/vacances?error=not_found", status_code=303)

    return RedirectResponse(url="/vacances", status_code=303)


# ✅ Route to handle form submission and insert new vacation
@router.post("/new", response_class=RedirectResponse)
async def create_vacances(
    nom: str = Form(...),
    description: str = Form(...),
    ville: str = Form(...),
    pays: str = Form(...),
    prix: int = Form(...),
    disponibilite: bool = Form(...)
):
    new_vacance = {
        "nom": nom,
        "description": description,
        "localisation": {
            "ville": ville,
            "pays": pays
        },
        "prix": prix,
        "disponibilite": "true" if disponibilite else "false"
    }

    # ✅ Prevent duplicates
    if not collectionVacances.find_one({"nom": nom}):
        collectionVacances.insert_one(new_vacance)

    return RedirectResponse(url="/vacances", status_code=303)
