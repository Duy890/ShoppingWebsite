import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/locations", tags=["locations"])

# Load location data on startup
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_json_file(filename: str) -> dict | list:
    """Load JSON file from data directory"""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        return {} if filename.endswith("dict") else []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Cache location data
PROVINCES = load_json_file("provinces.json")
DISTRICTS = load_json_file("districts.json")
WARDS = load_json_file("wards.json")


@router.get("/provinces")
async def get_provinces():
    """Get all provinces/cities of Vietnam"""
    return {"data": PROVINCES}


@router.get("/districts/{province_code}")
async def get_districts(province_code: str):
    """Get districts for a specific province"""
    districts = DISTRICTS.get(province_code, [])
    return {"data": districts}


@router.get("/wards/{district_code}")
async def get_wards(district_code: str):
    """Get wards for a specific district"""
    wards = WARDS.get(district_code, [])
    return {"data": wards}


@router.get("/search")
async def search_location(q: str, type: str = "all"):
    """
    Search for provinces, districts, or wards by name
    
    Args:
        q: Search query (case-insensitive)
        type: 'province', 'district', 'ward', or 'all'
    """
    q_lower = q.lower()
    results = {}
    
    if type in ["province", "all"]:
        results["provinces"] = [
            p for p in PROVINCES 
            if q_lower in p["name"].lower()
        ]
    
    if type in ["district", "all"]:
        all_districts = []
        for districts in DISTRICTS.values():
            all_districts.extend(districts)
        results["districts"] = [
            d for d in all_districts 
            if q_lower in d["name"].lower()
        ]
    
    if type in ["ward", "all"]:
        all_wards = []
        for wards in WARDS.values():
            all_wards.extend(wards)
        results["wards"] = [
            w for w in all_wards 
            if q_lower in w["name"].lower()
        ]
    
    return {"data": results}
