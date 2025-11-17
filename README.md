Movie Recommender with n8n, GPT-4, MySQL & TMDB
This project is an AI-powered movie recommender system built using n8n, GPT-4, MySQL, and data sourced from The Movie Database (TMDB). Users enter a natural-language prompt describing the type of movie they are looking for, and the system analyzes it, extracts features, queries a movie database, and returns the top recommendations.
⭐ Features
Natural-language movie recommendations powered by GPT-4
Automatic extraction of user intent across 8 categories
Weighted semantic search over MySQL
Fuzzy matching using SOUNDEX
Automated movie data ingestion using Python + TMDB API
Fully orchestrated using n8n
🚀 How It Works
1. User submits a movie request
Example:
“I want a sci-fi movie similar to Interstellar but shorter.”
2. GPT-4 classifies the prompt
The system asks GPT-4 to determine which of the following eight categories appear in the user prompt:
Actors
Directors
Language
Genre
Year
Duration
General description
Referenced movies (e.g., “similar to Interstellar”)
3. Extracting weighted keywords
For the first seven categories, GPT-4:
Receives the list of all possible values from the database (e.g., all actors, genres, languages)
Selects the relevant ones based on the prompt
Assigns a weight from 0 to 10 indicating relevance
4. Handling referenced movies
If the user mentions specific movies:
The system searches for these in the database
Retrieves their characteristics
Assigns weights to those characteristics
Adds the referenced movie IDs to a discard list (to avoid recommending them back)
5. Scoring movies in the database
The system generates a dynamic SQL query that:
Computes a score for every movie based on matching attributes
Multiplies matches by the weights assigned by GPT-4
Uses SOUNDEX to handle spelling errors and fuzzy matches
Excludes movies in the discard list
The query returns the top 5 movies with the highest score.
6. Returning the recommendations
The flow returns the recommendations directly to the same URL where the user submitted the form.
🏗️ Repository Structure
├── README.md
├── src/
│   └── data_ingest/
│       ├── fetch_tmdb.py
│       └── insert_to_mysql.py
├── n8n_flow/
│   └── movie_recommender.json
├── database/
│   └── schema.sql
├── .env.example
src/data_ingest/ — Python scripts for downloading and inserting TMDB data
n8n_flow/ — Exported n8n workflow (API keys removed)
database/ — MySQL schema definitions
.env.example — Environment variable template
📦 Data Ingestion
The Python ingestion script:
Fetches movie information from TMDB
Normalizes and cleans the data
Inserts all films and metadata into a MySQL database
Produces the lists of actors, genres, languages, etc., used later for GPT-4 keyword matching
🧠 Technologies Used
n8n – Orchestration and workflow automation
OpenAI GPT-4 – Prompt analysis and feature extraction
MySQL (Railway) – Movie database
TMDB API – Movie data source
Python + Cursor – Data ingestion scripting
🚀 Getting Started
1. Clone the repository
git clone https://github.com/yourusername/movie-recommender-n8n
cd movie-recommender-n8n
2. Configure environment variables
cp .env.example .env
Fill in:
OPENAI_API_KEY
TMDB_API_KEY
MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
3. Create the database schema
mysql -u USER -p DATABASE < database/schema.sql
4. Ingest movie data
python src/data_ingest/fetch_tmdb.py
5. Import the n8n workflow
Inside n8n → Import Workflow → upload movie_recommender.json.
🧪 Example Prompts
“A French thriller under 2 hours.”
“A comedy with Ryan Gosling from the 2010s.”
“Something like Interstellar but with more action.”
“A movie directed by Tarantino with a gangster vibe.”
🔐 Security
This repository does not include:
API keys
Database credentials
Private data
Full movie dataset
Use .env.example to configure your own environment.
📍 Future Improvements
Add embeddings-based semantic search
User history & personalization
A frontend UI
Caching for performance
Hybrid ML + rule-based scoring
🤝 Credits
Developed by [Your Name] and [Friend’s Name]
Movie data sourced from TMDB
Powered by OpenAI GPT-4
Database hosting via Railway
Workflow automation using n8n
