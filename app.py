from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
               f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
app = FastAPI(title="ClipOracle API")

@app.get("/api/videos")
async def get_videos(
    category_id: int = None,
    min_views: int = None,
    max_views: int = None,
    min_likes: int = None,
    max_likes: int = None,
    min_comments: int = None,
    max_comments: int = None,
    min_shares: int = None,
    max_shares: int = None
):
    try:
        with engine.connect() as conn:
            query = """
                SELECT 
                    v.id, v.video_text, v.views, v.likes, v.comments, v.shares, v.tags,
                    g.name as genre_name,
                    v.file_path
                FROM videos v
                LEFT JOIN genres g ON v.genre_id = g.id
                WHERE 1=1
            """
            params = {}

            if category_id is not None:
                query += " AND v.genre_id = :category_id"
                params["category_id"] = category_id

            if min_views is not None:
                query += " AND v.views >= :min_views"
                params["min_views"] = min_views

            if max_views is not None:
                query += " AND v.views <= :max_views"
                params["max_views"] = max_views

            if min_likes is not None:
                query += " AND v.likes >= :min_likes"
                params["min_likes"] = min_likes

            if max_likes is not None:
                query += " AND v.likes <= :max_likes"
                params["max_likes"] = max_likes

            if min_comments is not None:
                query += " AND v.comments >= :min_comments"
                params["min_comments"] = min_comments

            if max_comments is not None:
                query += " AND v.comments <= :max_comments"
                params["max_comments"] = max_comments

            if min_shares is not None:
                query += " AND v.shares >= :min_shares"
                params["min_shares"] = min_shares

            if max_shares is not None:
                query += " AND v.shares <= :max_shares"
                params["max_shares"] = max_shares

            query += " ORDER BY RANDOM() LIMIT 1"

            result = conn.execute(text(query), params)
            video = result.fetchone()

            if video:
                return [dict(video._mapping)]
            else:
                return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, name 
                FROM genres 
                ORDER BY id
            """))
            categories = [dict(row._mapping) for row in result]
            return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Отдаём статику
app.mount("/", StaticFiles(directory="static", html=True), name="static")