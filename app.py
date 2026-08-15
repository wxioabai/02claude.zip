"""1024 游戏排行榜后端

Flask + SQLite，提供分数提交与排行榜查询接口，并在根路径托管前端页面。

运行:
    pip install -r requirements.txt
    python app.py

接口:
    GET  /api/scores      -> 返回 Top N 排行榜
    POST /api/scores      -> 提交一条分数 { name, score }
    GET  /               -> 前端游戏页面
"""

from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "scores.db"
LEADERBOARD_LIMIT = 10

app = Flask(__name__)


# ==================== 数据库 ====================
def get_db():
    """建立 SQLite 连接，行以字典形式返回。"""
    import sqlite3

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            score      INTEGER NOT NULL,
            created_at TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# ==================== CORS（便于直接用 file:// 打开前端也能访问） ====================
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


# ==================== 前端页面 ====================
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "1024-game.html")


# ==================== 排行榜接口 ====================
@app.route("/api/scores", methods=["GET"])
def get_scores():
    conn = get_db()
    rows = conn.execute(
        "SELECT name, score, created_at FROM scores "
        "ORDER BY score DESC, created_at ASC LIMIT ?",
        (LEADERBOARD_LIMIT,),
    ).fetchall()
    conn.close()

    scores = []
    for i, row in enumerate(rows, start=1):
        scores.append(
            {
                "rank": i,
                "name": row["name"],
                "score": row["score"],
                "created_at": row["created_at"],
            }
        )
    return jsonify(scores)


@app.route("/api/scores", methods=["POST"])
def add_score():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    if not name:
        name = "玩家"
    name = name[:20]  # 限制昵称长度

    try:
        score = int(data.get("score", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "score 必须是整数"}), 400
    if score < 0:
        return jsonify({"error": "score 不能为负数"}), 400

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    conn.execute(
        "INSERT INTO scores (name, score, created_at) VALUES (?, ?, ?)",
        (name, score, created_at),
    )
    conn.commit()

    # 当前分数在排行榜中的名次（分数比它高的条数 + 1）
    rank = conn.execute(
        "SELECT COUNT(*) AS c FROM scores WHERE score > ?", (score,)
    ).fetchone()["c"]
    conn.close()

    return jsonify(
        {"ok": True, "rank": rank + 1, "name": name, "score": score, "created_at": created_at}
    ), 201


# ==================== 预检请求（跨域 POST 时浏览器会先发 OPTIONS） ====================
@app.route("/api/scores", methods=["OPTIONS"])
def scores_options():
    return ("", 204)


if __name__ == "__main__":
    init_db()
    # 0.0.0.0 让手机/局域网设备也能访问；debug=True 便于开发时热重载
    app.run(host="0.0.0.0", port=5000, debug=True)
