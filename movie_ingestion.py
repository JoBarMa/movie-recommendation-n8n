import os
import time
import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# -------------------------------------------------------------------
# Configuration (all sensitive data must be set as environment vars)
# -------------------------------------------------------------------

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# Ensure required variables are set
required_env = [
    "TMDB_API_KEY", "MYSQL_HOST", "MYSQL_PORT",
    "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"
]

missing = [var for var in required_env if os.getenv(var) is None]
if missing:
    raise EnvironmentError(
        f"❌ Missing required environment variables: {', '.join(missing)}"
    )

# -------------------------------------------------------------------
# TMDB API utilities
# -------------------------------------------------------------------

def get_discover_movies(year, max_pages=10):
    """Retrieve movie IDs from TMDB discover endpoint."""
    movie_ids = []

    for page in range(1, max_pages + 1):
        print(f"Fetching page {page} for year {year}...")

        params = {
            "api_key": API_KEY,
            "primary_release_year": year,
            "sort_by": "popularity.desc",
            "page": page
        }

        response = requests.get(f"{BASE_URL}/discover/movie", params=params)
        if response.status_code != 200:
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            break

        movie_ids.extend([movie["id"] for movie in results])

        if page >= data.get("total_pages", 1):
            break

        time.sleep(0.25)  # Rate limit safe pause

    return movie_ids


def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY}
    resp = requests.get(url, params=params)
    return resp.json() if resp.status_code == 200 else None


def get_movie_credits(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": API_KEY}
    resp = requests.get(url, params=params)
    return resp.json() if resp.status_code == 200 else None


def get_full_movie_info(movie_id):
    """Combine movie details and credits into a single dict."""
    details = get_movie_details(movie_id)
    credits = get_movie_credits(movie_id)

    if not details:
        return None

    movie_info = {
        "id": details.get("id"),
        "title": details.get("title"),
        "original_title": details.get("original_title"),
        "release_date": details.get("release_date"),
        "runtime": details.get("runtime"),
        "popularity": details.get("popularity"),
        "vote_average": details.get("vote_average"),
        "vote_count": details.get("vote_count"),
        "original_language": details.get("original_language"),
        "genres": [g["name"] for g in details.get("genres", [])],
        "overview": details.get("overview"),
    }

    if credits:
        movie_info["main_actors"] = [a["name"] for a in credits.get("cast", [])[:5]]
        movie_info["director"] = [
            m["name"] for m in credits.get("crew", []) if m["job"] == "Director"
        ]

    return movie_info

# -------------------------------------------------------------------
# MySQL Upload
# -------------------------------------------------------------------

def upload_to_mysql(df, table_name, year):
    """Upload DataFrame to MySQL, converting list columns into strings."""
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(
                lambda x: ", ".join(map(str, x)) if isinstance(x, list) else x
            )

    df["year"] = year  # Track data origin year

    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    df.to_sql(table_name, con=engine, if_exists="append", index=False)


def upload_to_mysql_with_retry(df, table_name, year, max_retries=5, base_delay=5):
    """Retry logic for unstable MySQL connections."""
    for attempt in range(1, max_retries + 1):
        try:
            upload_to_mysql(df, table_name, year)
            return
        except OperationalError as e:
            print(f"❌ MySQL connection failed (attempt {attempt}): {e}")
            if attempt == max_retries:
                raise
            delay = base_delay * attempt
            print(f"⏳ Retrying in {delay} seconds...")
            time.sleep(delay)

# -------------------------------------------------------------------
# Main Loop
# -------------------------------------------------------------------

if __name__ == "__main__":
    for year in range(2021, 2026):
        print(f"\n🔎 Processing year {year}...")
        movie_ids = get_discover_movies(year)

        movie_data = []
        for idx, movie_id in enumerate(movie_ids):
            info = get_full_movie_info(movie_id)
            if info:
                movie_data.append(info)

            if idx % 10 == 0:
                print(f"  → Fetched {idx + 1}/{len(movie_ids)} movies")

            time.sleep(0.25)

        if movie_data:
            df = pd.DataFrame(movie_data)
            print(f"📤 Uploading {len(df)} movies from {year} to MySQL...")
            upload_to_mysql_with_retry(df, "tmdb_movies", year)
        else:
            print(f"⚠️ No data found for {year}")
