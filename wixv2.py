"""
Wix Collection Data Fetcher
Fetches all data from a Wix collection and saves it to CSV.
"""

import requests
import csv
import json
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()
# ============================================
# CONFIGURATION - Fill in your details here
# ============================================
COLLECTION_ID = "TvBroadcasts"  # e.g., "Products", "Members", or your custom collection name
# ============================================

ACCESS_TOKEN = os.getenv('WIX_ACCESS_TOKEN')
SITE_ID = os.getenv('WIX_SITE_ID')


def fetch_wix_collection_data(
    access_token: str,
    site_id: str,
    collection_id: str,
    limit: int = 50
) -> list[dict]:
    """
    Fetch all items from a Wix collection using the Wix Data API.
    Handles pagination automatically.
    """

    url = "https://www.wixapis.com/wix-data/v2/items/query"

    headers = {
        "Authorization": access_token,
        "wix-site-id": site_id,
        "Content-Type": "application/json"
    }

    all_items = []
    offset = 0

    while True:
        payload = {
            "dataCollectionId": collection_id,
            "query": {
                "paging": {
                    "limit": limit,
                    "offset": offset
                }
            },
            "returnTotalCount": True
        }

        print(f"Fetching items {offset} to {offset + limit}...")

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

        data = response.json()
        items = data.get("dataItems", [])

        if not items:
            break

        # Extract the actual data from each item
        for item in items:
            item_data = item.get("data", {})
            # Add the item ID to the data
            item_data["_id"] = item.get("id", "")
            item_data["_createdDate"] = item.get("createdDate", "")
            item_data["_updatedDate"] = item.get("updatedDate", "")
            all_items.append(item_data)

        print(f"  Retrieved {len(items)} items")

        # Check if we've fetched all items
        total_count = data.get("pagingMetadata", {}).get("total", 0)
        offset += limit

        if offset >= total_count or len(items) < limit:
            break

    print(f"\nTotal items fetched: {len(all_items)}")
    return all_items


def save_to_csv(data: list[dict], filename: str):
    """
    Save list of dictionaries to CSV file.
    Handles nested objects by converting them to JSON strings.
    """

    if not data:
        print("No data to save!")
        return

    # Get all unique keys from all items
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())

    # Sort keys for consistent column order, but put _id first
    sorted_keys = sorted(all_keys)
    if "_id" in sorted_keys:
        sorted_keys.remove("_id")
        sorted_keys.insert(0, "_id")

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted_keys)
        writer.writeheader()

        for item in data:
            # Convert any nested objects/lists to JSON strings
            row = {}
            for key in sorted_keys:
                value = item.get(key, "")
                if isinstance(value, (dict, list)):
                    row[key] = json.dumps(value)
                else:
                    row[key] = value
            writer.writerow(row)

    print(f"Data saved to: {filename}")


def insert_dataframe_to_wix(df, access_token: str = None, site_id: str = None, collection_id: str = None):
    """
    Insert all rows from a DataFrame into Wix collection.

    Expected DataFrame columns: ['video_id', 'title', 'url', 'release_date', 'view_count', 'duration']

    Returns list of inserted items.
    """
    inserted = []
    failed = []

    for idx, row in df.iterrows():
        try:
            result = insert_youtube_video_to_wix(
                video_id=row.get('video_id', ''),
                title=row.get('title', ''),
                url=row.get('url', ''),
                release_date=str(row.get('release_date', '')),
                view_count=row.get('view_count'),
                duration=row.get('duration'),
                access_token=access_token,
                site_id=site_id,
                collection_id=collection_id
            )
            inserted.append(result)
        except Exception as e:
            print(f"Failed to insert row {idx}: {e}")
            failed.append((idx, row, str(e)))

    print(f"\n{'='*50}")
    print(f"Inserted: {len(inserted)} | Failed: {len(failed)}")
    return inserted, failed


def save_wix_data(OUTPUT_FILE):
    # Validate configuration
    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("ERROR: Please set your ACCESS_TOKEN in the script!")
        return

    if SITE_ID == "YOUR_SITE_ID_HERE":
        print("ERROR: Please set your SITE_ID in the script!")
        return

    if COLLECTION_ID == "YOUR_COLLECTION_ID_HERE":
        print("ERROR: Please set your COLLECTION_ID in the script!")
        return

    print(f"Fetching data from collection: {COLLECTION_ID}")
    print("-" * 50)

    # Fetch all data
    data = fetch_wix_collection_data(
        access_token=ACCESS_TOKEN,
        site_id=SITE_ID,
        collection_id=COLLECTION_ID
    )

    # Save to CSV
    if data:
        save_to_csv(data, OUTPUT_FILE)
        print("-" * 50)
        print(f"Success! {len(data)} items saved to {OUTPUT_FILE}")
    else:
        print("No data found in the collection.")


def insert_youtube_video_to_wix(
        video_id: str,
        title: str,
        url: str,
        release_date: str,
        view_count: int = None,
        duration: str = None,
        access_token: str = None,
        site_id: str = None,
        collection_id: str = None
) -> dict:
    """
    Insert a YouTube video row into Wix collection.

    Maps DataFrame columns to Wix columns:
    - video_id → video_id
    - title → title
    - url → url
    - release_date → release_date2
    - view_count → view_count
    - duration → duration

    Returns the created item data or raises an exception on failure.
    """
    # Use defaults from config if not provided
    access_token = access_token or ACCESS_TOKEN
    site_id = site_id or SITE_ID
    collection_id = collection_id or COLLECTION_ID

    url_endpoint = "https://www.wixapis.com/wix-data/v2/items"

    headers = {
        "Authorization": access_token,
        "wix-site-id": site_id,
        "Content-Type": "application/json"
    }

    # Map YouTube data to Wix columns
    wix_data = {
        "video_id": video_id,
        "title": title,
        "url": url,
        "release_date2": release_date,  # Note: release_date maps to release_date2 in Wix
    }

    # Add optional fields if provided
    if view_count is not None:
        wix_data["view_count"] = view_count
    if duration is not None:
        wix_data["duration"] = duration

    payload = {
        "dataCollectionId": collection_id,
        "dataItem": {
            "data": wix_data
        }
    }

    response = requests.post(url_endpoint, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        print(f"Error inserting item: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"Failed to insert item: {response.status_code} - {response.text}")

    result = response.json()
    print(f"Successfully inserted video: {video_id}")
    return result

if __name__ == "__main__":
    save_wix_data()
