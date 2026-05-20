import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import sqlalchemy as sa
from utils.db.db_access import build_engine

engine = build_engine()

# --- Articles ---

def get_articles(competition=None, club=None, theme=None, user_id=None, liked_only=False):
    params = {"user_id": user_id or 0}
    join = "INNER JOIN" if liked_only else "LEFT JOIN"
    query = f"""
        SELECT a.id, a.source_url, a.competition, a.club, a.theme,
               a.published_at, a.clubs_mentioned, a.players_mentioned, a.body_text,
               CASE WHEN al.user_id IS NOT NULL THEN 1 ELSE 0 END AS liked
        FROM articles a
        {join} article_likes al ON al.article_id = a.id AND al.user_id = :user_id
        WHERE 1=1
    """

    if competition:
        query += " AND a.competition = :competition"
        params["competition"] = competition

    if club:
        query += " AND a.club = :club"
        params["club"] = club

    if theme:
        query += " AND a.theme = :theme"
        params["theme"] = theme

    query += " ORDER BY a.published_at DESC"

    with engine.connect() as conn:
        return conn.execute(sa.text(query), params).fetchall()

# --- Likes ---

def toggle_like(user_id: int, article_id: int) -> None:
    with engine.connect() as conn:
        existing = conn.execute(
            sa.text("SELECT 1 FROM article_likes WHERE user_id = :uid AND article_id = :aid"),
            {"uid": user_id, "aid": article_id},
        ).fetchone()
        if existing:
            conn.execute(
                sa.text("DELETE FROM article_likes WHERE user_id = :uid AND article_id = :aid"),
                {"uid": user_id, "aid": article_id},
            )
        else:
            conn.execute(
                sa.text("INSERT INTO article_likes (user_id, article_id) VALUES (:uid, :aid)"),
                {"uid": user_id, "aid": article_id},
            )
        conn.commit()


def get_like_state(user_id: int, article_id: int) -> bool:
    with engine.connect() as conn:
        return conn.execute(
            sa.text("SELECT 1 FROM article_likes WHERE user_id = :uid AND article_id = :aid"),
            {"uid": user_id, "aid": article_id},
        ).fetchone() is not None

# --- Chat messages ---

def save_message(user_id: int, role: str, content: str) -> None:
    with engine.connect() as conn:
        conn.execute(sa.text(
            "INSERT INTO chat_messages (user_id, role, content) VALUES (:uid, :role, :content)"
        ), {"uid": user_id, "role": role, "content": content})
        conn.commit()


def get_chat_history(user_id: int) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(sa.text(
            "SELECT role, content FROM chat_messages WHERE user_id = :uid ORDER BY created_at"
        ), {"uid": user_id}).fetchall()
    return [{"role": r.role, "content": r.content} for r in rows]

# --- User preferences ---

def get_favourite_club(user_id: int) -> str | None:
    with engine.connect() as conn:
        row = conn.execute(sa.text(
            "SELECT favourite_club FROM users WHERE id = :uid"
        ), {"uid": user_id}).fetchone()
    return row.favourite_club if row else None

def save_favourite_club(user_id: int, club: str) -> None:
    with engine.connect() as conn:
        conn.execute(sa.text(
            "UPDATE users SET favourite_club = :club WHERE id = :uid"
        ), {"club": club, "uid": user_id})
        conn.commit()

def get_recent_articles_for_chat(n: int = 20) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(sa.text(
            "SELECT id, competition, club, theme, body_text "
            "FROM articles ORDER BY published_at DESC LIMIT :n"
        ), {"n": n}).fetchall()
        return [{"id": r.id, "competition": r.competition, "club": r.club,
                 "theme": r.theme, "body_text": r.body_text} for r in rows]
