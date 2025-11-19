**Movie Recommender with n8n, GPT-4, MySQL & TMDB**

This project is an AI-powered movie recommender system built using n8n, GPT-4, MySQL, and data sourced from The Movie Database (TMDB). 

Users enter a natural-language prompt describing the type of movie they are looking for, and the system analyzes it, extracts features, queries a movie database, and returns the top recommendations.

**Features**

Natural-language movie recommendations powered by GPT-4

Automatic extraction of user intent across 8 categories

Weighted semantic search over MySQL

Fuzzy matching using SOUNDEX

Automated movie data ingestion using Python + TMDB API

Fully orchestrated using n8n

**How It Works**
1. User submits a movie request (*e.g., “I want a sci-fi movie similar to Interstellar but shorter.”*)
2. GPT-4 classifies the prompt. The system asks GPT-4 to determine which of the following eight categories appear in the user prompt:
- Actors
- Directors
- Language
- Genre
- Year
- Duration
- General description
- Referenced movies (*e.g., “similar to Interstellar”*)
3. Extracting weighted keywords. For the first seven categories, GPT-4:
- Receives the list of all possible values from the database (e.g., all actors, genres, languages)
- Selects the relevant ones based on the prompt
- Assigns a weight from 0 to 10 indicating relevance
4. Handling referenced movies. If the user mentions specific movies:
- The system searches for these in the database
- Retrieves their characteristics
- Assigns weights to those characteristics
- Adds the referenced movie IDs to a discard list (to avoid recommending them back)
5. Scoring movies in the database. The system generates a dynamic SQL query that:
- Computes a score for every movie based on matching attributes
- Multiplies matches by the weights assigned by GPT-4
- Uses SOUNDEX to handle spelling errors and fuzzy matches
- Excludes movies in the discard list
6. Returning the recommendations. The query returns the top 5 movies with the highest score.
  
The flow returns the recommendations directly to the same URL where the user submitted the form.

**Repository Content:**

1. Python ingestion script (movie_ingestion.py):
- Fetches movie data from TMDB across multiple years and pages based on popularity
- Retrieves detailed metadata for each film, including credits, directors, and top-billed actors
- Normalizes, cleans, and structures the data (genres, languages, lists, text fields, etc.)
- Handles rate limits and implements retry logic for resilient API and database operations
- Inserts all processed movie records into a MySQL database for downstream analytics
- Produces reusable structures (actors, directors, genres, languages) that can support LLM keyword matching or recommendation pipelines.

2. SQL transformation queries (sql_transformations.sql):
- Query for creating a table with unique actors from the main table
- Query for adding SOUNDEX columns to be used in fuzzy matching

3. JSON file with n8n flow (n8n_flow.json):
- JSON file with n8n code without credentials or webhookID (must be modified in order to work)
- The flow structure can be viewed in the n8n_flow_view.png file

**Technologies Used**
1. n8n – Orchestration and workflow automation
2. OpenAI GPT-4 – Prompt analysis and feature extraction
3. MySQL (Railway) – Movie database
4. TMDB API – Movie data source
5. Python + Cursor – Data ingestion scripting

**Credits**
- Developed by Oriol Farràs Figuera and Josep Baradat Marí
- Movie data sourced from TMDB
- Powered by OpenAI GPT-4
- Database hosting via Railway
- Workflow automation using n8n
