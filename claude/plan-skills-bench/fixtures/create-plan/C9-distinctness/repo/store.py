"""Notes data access (Postgres)."""


def search_notes(db, user_id, query):
    """Current search: naive substring match on the title only.

    Matches the title with ILIKE and ignores the body. No ranking, and at 50k
    notes per user this is a sequential scan with no supporting index.
    """
    sql = (
        "SELECT id, title, body FROM notes "
        "WHERE user_id = %s AND title ILIKE %s "
        "ORDER BY updated_at DESC"
    )
    return db.query(sql, [user_id, f"%{query}%"])
