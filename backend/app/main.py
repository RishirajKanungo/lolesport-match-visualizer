from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from mwrogue.esports_client import EsportsClient

app = FastAPI()

# Add CORS middleware to allow frontend to call these APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Leaguepedia client
site = EsportsClient("lol")

@app.get("/")
async def root():
    return {"message": "LoL Match Visualizer API"}

@app.get("/api/regions")
async def get_regions():
    """Get all major League of Legends competitive regions."""
    try:
        # Use hard-coded region data based on the actual Leagues table
        regions = [
            {"code": "LCS", "name": "League of Legends Championship Series", "region": "North America"},
            {"code": "LTA", "name": "League of Legends Championship of The Americas", "region": "Americas"},
            {"code": "LEC", "name": "LoL EMEA Championship", "region": "Europe"},
            {"code": "LCK", "name": "LoL Champions Korea", "region": "Korea"},
            {"code": "LPL", "name": "Tencent LoL Pro League", "region": "China"},
            {"code": "LCP", "name": "League of Legends Championship Pacific", "region": "Asia Pacific"}
        ]
        return regions
    except Exception as e:
        print(f"Error in get_regions: {str(e)}")
        return {"error": str(e)}

@app.get("/api/years")
async def get_years(start_year: int = 2022, end_year: int = 2025):
    """Get years for the dropdown (static range for now)."""
    return list(range(end_year, start_year - 1, -1))  # Returns years in descending order

@app.get("/api/tournaments")
async def get_tournaments(region_code: str = Query(...), year: str = Query(...)):
    """Get tournaments for a specific region and year."""
    try:
        # Map the league code to the region name
        region_map = {
            "LCS": "North America",
            "LTA": "Americas",
            "LCK": "Korea",
            "LEC": "Europe",  # For older data it's Europe, for newer it's EMEA
            "LPL": "China",
            "LCP": "Asia Pacific"
        }
        
        # Build query
        where_clauses = []
        
        if year:
            where_clauses.append(f"DateStart LIKE '{year}%'")
        
        if region_code:
            # Use the mapped region name if available, otherwise use the code directly
            region_name = region_map.get(region_code, region_code)
            # For LEC, handle both Europe and EMEA
            if region_code == "LEC":
                where_clauses.append(f"(Region = 'Europe' OR Region = 'EMEA')")
            else:
                where_clauses.append(f"Region = '{region_name}'")
        
        # Combine where clauses
        where_clause = " AND ".join(where_clauses) if where_clauses else ""
        
        # Execute the query
        response = site.cargo_client.query(
            tables="Tournaments",
            fields="Name, League, Region, DateStart, Date",
            where=where_clause,
            limit=50,
            order_by="DateStart DESC"
        )
        
        # Format the response for frontend use
        tournaments = []
        for t in response:
            tournaments.append({
                "id": t.get("Name", ""),
                "name": t.get("Name", ""),
                "startDate": t.get("DateStart", ""),
                "endDate": t.get("Date", "")
            })
            
        return tournaments
    except Exception as e:
        print(f"Error in get_tournaments: {str(e)}")
        return {"error": str(e)}