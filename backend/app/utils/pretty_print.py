# File: app/utils/pretty_print.py

import json
import pprint
from typing import List, Dict, Any
from tabulate import tabulate

def print_json(data: Any, indent: int = 2):
    """
    Print data as formatted JSON.
    
    Args:
        data: Data to print (list, dict, etc.)
        indent: Number of spaces for indentation
    """
    print(json.dumps(data, indent=indent, default=str))

def print_tabular(data: List[Dict[str, Any]], headers: str = "keys"):
    """
    Print data in a tabular format.
    
    Args:
        data: List of dictionaries to display as a table
        headers: How to extract headers ('keys', 'firstrow', or list of column names)
    """
    if not data:
        print("No data to display")
        return
        
    # Convert OrderedDict to regular dict if needed
    cleaned_data = [dict(item) for item in data]
    
    print(tabulate(cleaned_data, headers=headers, tablefmt="grid"))

def print_summary(data: List[Dict[str, Any]], title: str = "Query Results"):
    """
    Print a summary of the query results.
    
    Args:
        data: List of dictionaries from query result
        title: Title for the summary section
    """
    if not data:
        print(f"{title}: No data returned")
        return
        
    print(f"\n=== {title} ===")
    print(f"Total records: {len(data)}")
    
    if data:
        print("\nSample record:")
        pprint.pprint(dict(data[0]))
        
        print("\nAvailable fields:")
        for field in data[0].keys():
            print(f"- {field}")
    
    print("=" * (len(title) + 8))

def format_regions(regions: List[Dict[str, Any]]):
    """
    Format and print regions in a readable format.
    
    Args:
        regions: List of region dictionaries
    """
    if not regions:
        print("No regions data available")
        return
    
    print("\n=== League of Legends Regions ===\n")
    
    # Create a formatted table
    headers = ["ID", "Name", "Abbreviation", "Region"]
    rows = []
    
    for region in regions:
        rows.append([
            region.get("League", ""),
            region.get("League", ""),
            region.get("League Short", ""),
            region.get("Region", "")
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"\nTotal regions: {len(regions)}")

def format_years(years: List[int]):
    """
    Format and print years in a readable format.
    
    Args:
        years: List of years
    """
    if not years:
        print("No years data available")
        return
    
    print("\n=== Available Tournament Years ===\n")
    years_str = ", ".join(str(year) for year in sorted(years, reverse=True))
    print(years_str)
    print(f"\nTotal years available: {len(years)}")

def format_tournaments(tournaments: List[Dict[str, Any]], region: str, year: int):
    """
    Format and print tournaments in a readable format.
    
    Args:
        tournaments: List of tournament dictionaries
        region: Region ID
        year: Year
    """
    if not tournaments:
        print(f"No tournaments found for {region} in {year}")
        return
    
    print(f"\n=== Tournaments for {region} in {year} ===\n")
    
    # Create a formatted table
    headers = ["Name", "Start Date", "End Date", "Split"]
    rows = []
    
    for tournament in tournaments:
        rows.append([
            tournament.get("Name", ""),
            tournament.get("DateStart", ""),
            tournament.get("Date", ""),
            tournament.get("Split", "")
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"\nTotal tournaments: {len(tournaments)}")