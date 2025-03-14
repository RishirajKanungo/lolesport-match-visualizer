import sys
import os
import logging
from pathlib import Path
from mwrogue.esports_client import EsportsClient

# Add the backend directory to the Python path
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent.parent  # Go up three levels: playground -> app -> backend
sys.path.append(str(backend_dir))

# Now we can import from app modules
from app.utils.pretty_print import format_regions, format_years, format_tournaments

site = EsportsClient("lol")

logger = logging.getLogger(__name__)


def get_regions():
    """Get all major League of Legends competitive regions."""
    try:
        response = site.cargo_client.query(
            tables="Leagues",
            fields="League, League_Short, Region",
            where="League_Short IN ('LCS', 'LTA', 'LEC', 'LCK', 'LPL')",
            order_by="League"
        )
        
        logger.info(f"Retrieved {len(response)} regions")
        
        # Pretty print the results
        format_regions(response)
        
        return response
    except Exception as e:
        logger.error(f"Error fetching regions: {str(e)}", exc_info=True)
        return []

def get_available_years():
    """Get all years with professional League of Legends tournaments."""
    try:
        # First, let's examine the structure of a few tournament entries to understand the schema
        sample_response = site.cargo_client.query(
            tables="Tournaments",
            fields="Name, League, Region, DateStart",
            limit=10,
            order_by="DateStart DESC"
        )
        
        # print("\n=== Sample Tournament Data ===")
        # for item in sample_response:
        #     print(f"Tournament: {item.get('Name', '')}")
        #     print(f"  League: {item.get('League', '')}")
        #     print(f"  Region: {item.get('Region', '')}")
        #     print(f"  Date: {item.get('DateStart', '')}")
        #     print("")
            
        # Now try to get all years based on region instead of league
        
        response = site.cargo_client.query(
            tables="Tournaments",
            fields="DateStart",
            where=f"DateStart IS NOT NULL AND Region IN ('North America', 'Korea', 'Europe', 'China')"
        )
        
        # Extract years manually from the DateStart field
        years = set()
        for item in response:
            try:
                date_str = item.get('DateStart', '')
                if date_str and len(date_str) >= 4:
                    # Extract year from date string (usually in format YYYY-MM-DD)
                    year = int(date_str[:4])
                    if year > 0:
                        years.add(year)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing date {date_str}: {str(e)}")
                continue
                
        years_list = sorted(list(years), reverse=True)
        logger.info(f"Retrieved {len(years_list)} years with tournament data")
        
        # Pretty print the results
        format_years(years_list)
        
        return years_list
    except Exception as e:
        logger.error(f"Error fetching years: {str(e)}", exc_info=True)
        return []

def get_tournaments_by_region_year(region: str, year: int):
    """Get tournaments for a specific region and year."""
    try:
        response = site.cargo_client.query(
            tables="Tournaments",
            fields="Name, DateStart, Date, Split, League",
            where=f"League = '{region}' AND YEAR(DateStart) = {year}",
            order_by="DateStart"
        )
        
        logger.info(f"Retrieved {len(response)} tournaments for {region} in {year}")
        
        # Pretty print the results
        format_tournaments(response, region, year)
        
        return response
    except Exception as e:
        logger.error(f"Error fetching tournaments for {region} in {year}: {str(e)}", exc_info=True)
        return []

def get_all_tournaments():
    """Get a list of all tournaments with minimal filtering."""
    try:
        # Most basic query possible
        response = site.cargo_client.query(
            tables="Tournaments",
            fields="Name",
            limit=10
        )
        
        print(f"Retrieved {len(response)} tournaments")
        print("\n=== Sample Tournaments ===")
        for tournament in response:
            print(f"- {tournament.get('Name', '')}")
        
        return response
    except Exception as e:
        print(f"Error fetching tournaments: {str(e)}")
        return []
    
def get_tournament_results(year=None, region_code=None):
    """
    Get tournament results filtered by year and/or region code.
    
    Args:
        year: Year to filter by (optional)
        region_code: Region code to filter by (optional)
    
    Returns:
        List of tournament result dictionaries
    """
    try:
        where_conditions = []
        
        if year:
            where_conditions.append(f"Date_Year = {year}")
        
        if region_code:
            where_conditions.append(f"OverviewPage LIKE '%{region_code}%'")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else ""
        
        response = site.cargo_client.query(
            tables="TournamentResults",
            fields="Event, Date, OverviewPage",
            where=where_clause,
            limit=30,
            order_by="Date DESC"
        )
        
        print(f"\n=== Tournament Results for {region_code or 'All Regions'} {year or 'All Years'} ===")
        print(f"Retrieved {len(response)} results")
        
        for result in response:
            print(f"- {result.get('Event', '')} ({result.get('Date', '')})")
            print(f"  Overview: {result.get('OverviewPage', '')}")
            print("")
        
        return response
    except Exception as e:
        print(f"Error fetching tournament results: {str(e)}")
        return []

def get_tournaments_from_games():
    """Get tournament information from ScoreboardGames table."""
    try:
        response = site.cargo_client.query(
            tables="ScoreboardGames",
            fields="DISTINCT Tournament",
            limit=50,
            order_by="Tournament"
        )
        
        print(f"\n=== Tournaments from ScoreboardGames ===")
        print(f"Retrieved {len(response)} distinct tournaments")
        
        for tournament in response:
            print(f"- {tournament.get('Tournament', '')}")
        
        return response
    except Exception as e:
        print(f"Error fetching tournaments from games: {str(e)}")
        return []

def get_tournaments_by_filter(year=None, region_code=None):
    """
    Get tournaments filtered by year and/or region code.
    
    Args:
        year: Year to filter by (optional)
        region_code: Region code to filter by (optional, e.g., 'LCS', 'LEC')
    
    Returns:
        List of tournament dictionaries
    """
    try:
        # Start with the most basic query
        tables = "Tournaments"
        fields = "Name, League, Region, DateStart, Date"
        
        # Build where clause based on parameters
        where_clauses = []
        
        if year:
            where_clauses.append(f"DateStart LIKE '{year}%'")
        
        # Instead of filtering by League field, filter by Region which seems to match the major region names
        if region_code:
            # Map the league code to the region name
            region_map = {
                "LCS": "North America",
                "LCK": "Korea",
                "LEC": "EMEA",  # In 2023+ it's EMEA instead of Europe
                "LPL": "China",
                "PCS": "PCS"
            }
            
            # Use the mapped region name if available, otherwise use the code directly
            region_name = region_map.get(region_code, region_code)
            where_clauses.append(f"Region = '{region_name}'")
        
        # Combine where clauses if any exist
        where_clause = " AND ".join(where_clauses) if where_clauses else ""
        
        # Execute the query
        response = site.cargo_client.query(
            tables=tables,
            fields=fields,
            where=where_clause,
            limit=50,
            order_by="DateStart DESC"  # Order by date descending to get newest first
        )
        
        logger.info(f"Retrieved {len(response)} tournaments matching filters: year={year}, region_code={region_code}")
        
        # Use our pretty print utility
        format_filtered_tournaments(response, year, region_code)
        
        return response
    except Exception as e:
        logger.error(f"Error fetching tournaments with filters: {str(e)}", exc_info=True)
        return []

# Helper function to format tournaments
def format_filtered_tournaments(tournaments, year=None, region_code=None):
    """
    Format and print tournaments filtered by year and/or region.
    
    Args:
        tournaments: List of tournament dictionaries
        year: Year filter used (for display)
        region_code: Region code filter used (for display)
    """
    filter_desc = []
    if year:
        filter_desc.append(f"Year: {year}")
    if region_code:
        filter_desc.append(f"Region: {region_code}")
    
    filter_text = ", ".join(filter_desc) if filter_desc else "No filters"
    
    print(f"\n=== Tournaments ({filter_text}) ===\n")
    
    if not tournaments:
        print("No tournaments found matching these filters.")
        return
    
    # Create a simple table format
    print(f"{'Name':<50} {'League':<15} {'Region':<15} {'Start Date':<12} {'End Date':<12}")
    print("-" * 105)
    
    for tournament in tournaments:
        # Handle None values safely
        name = tournament.get('Name', 'N/A') or 'N/A'
        league = tournament.get('League', 'N/A') or 'N/A'
        region = tournament.get('Region', 'N/A') or 'N/A'
        start_date = tournament.get('DateStart', 'N/A') or 'N/A'
        end_date = tournament.get('Date', 'N/A') or 'N/A'
        
        # Truncate long values as needed
        name_display = name[:50] if isinstance(name, str) else str(name)[:50]
        league_display = league[:15] if isinstance(league, str) else str(league)[:15]
        region_display = region[:15] if isinstance(region, str) else str(region)[:15]
        start_date_display = start_date[:12] if isinstance(start_date, str) else str(start_date)[:12]
        end_date_display = end_date[:12] if isinstance(end_date, str) else str(end_date)[:12]
        
        print(f"{name_display:<50} {league_display:<15} {region_display:<15} {start_date_display:<12} {end_date_display:<12}")
    
    print(f"\nTotal tournaments: {len(tournaments)}")

# Test cases to run
if __name__ == "__main__":
    print("Testing tournament queries...")
    
    # Test 1: Get tournaments without filters
    print("\nTEST 1: All tournaments (limited to 50)")
    get_tournaments_by_filter()
    
    # Test 2: Filter by year only
    print("\nTEST 2: Tournaments in 2023")
    get_tournaments_by_filter(year="2023")
    
    # Test 3: Filter by region only
    print("\nTEST 3: LCS tournaments (North America region)")
    get_tournaments_by_filter(region_code="LCS")
    
    # Test 4: Filter by both year and region
    print("\nTEST 4: LCK tournaments in 2024 (Korea region)")
    get_tournaments_by_filter(year="2024", region_code="LCK")
    
    # Additional test for European tournaments
    print("\nTEST 5: LEC tournaments (EMEA region)")
    get_tournaments_by_filter(region_code="LEC")
    
    # Additional test for Chinese tournaments
    print("\nTEST 6: LPL tournaments (China region)")
    get_tournaments_by_filter(region_code="LPL")