import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="snake",
    user="postgres",
    password="1234"
)

def get_or_create_player(username):
    cur = conn.cursor()
    cur.execute("SELECT id FROM players WHERE username=%s", (username,))
    result = cur.fetchone()

    if result:
        return result[0]

    cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
    conn.commit()
    return cur.fetchone()[0]


def save_game(player_id, score, level):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s,%s,%s)",
        (player_id, score, level)
    )
    conn.commit()


def get_top10():
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, g.score, g.level_reached, g.played_at
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        ORDER BY g.score DESC
        LIMIT 10
    """)
    return cur.fetchall()


def get_best_score(player_id):
    cur = conn.cursor()
    cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id=%s", (player_id,))
    result = cur.fetchone()[0]
    return result if result else 0