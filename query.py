#!/usr/bin/env python

import os
import sqlite3
import sys
import json
from dotenv import load_dotenv

def fuzzy_search(search_terms, data):
    results = []
    search_terms = search_terms.lower().split()
    for row in data:
        name = row[0].lower()
        if all(term in name for term in search_terms):
            results.append({'name': row[0], 'location_items': row[1]})
    return results

def find_parent_locations(location_id, cursor):
    cursor.execute("SELECT name, location_children FROM locations WHERE id = ?", (location_id,))
    location_info = cursor.fetchone()
    if not location_info:
        return []
    location_name, location_children = location_info
    parent_locations = [{'name': location_name, 'id': location_id}]
    if location_children:
        child_locations = location_children.split(',')
        for child_location_id in child_locations:
            parent_locations.extend(find_parent_locations(child_location_id, cursor))
    return parent_locations

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <search_terms>")
        sys.exit(1)

    try:
        search_terms = sys.argv[1]
        load_dotenv()
        database_path = os.getenv("DATABASE_PATH")

        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name, location_items FROM items")
            data = cursor.fetchall()

            results = fuzzy_search(search_terms, data)

            for result in results:
                location_id = result['location_items']
                parent_locations = find_parent_locations(location_id, cursor)
                result['parent_locations'] = parent_locations

            print(json.dumps(results, indent=4))

    except Exception as e:
        print(f"An error occurred: {e}")
