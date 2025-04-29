# database.py
import sqlite3
import pandas as pd
from datetime import datetime
from config import DB_FILE
from metrics import calculate_metrics  # 評価指標を計算するため

# --- スキーマ定義 ---
TABLE_NAME = "chat_history"
SCHEMA = f'''
CREATE TABLE IF NOT EXISTS {TABLE_NAME}
(id INTEGER PRIMARY KEY AUTOINCREMENT,
 timestamp TEXT,
 question TEXT,
 answer TEXT,
 feedback TEXT,
 correct_answer TEXT,
 is_correct REAL,
 response_time REAL,
 bleu_score REAL,
 similarity_score REAL,
 word_count INTEGER,
 relevance_score REAL)
'''

# --- データベース初期化 ---
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()

# --- データ保存 ---
def save_to_db(question, answer, feedback, correct_answer, is_correct, response_time):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bleu_score, similarity_score, word_count, relevance_score = calculate_metrics(
            answer, correct_answer
        )

        c.execute(f'''
        INSERT INTO {TABLE_NAME} (timestamp, question, answer, feedback, correct_answer, is_correct,
                                 response_time, bleu_score, similarity_score, word_count, relevance_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, question, answer, feedback, correct_answer, is_correct,
             response_time, bleu_score, similarity_score, word_count, relevance_score))
        conn.commit()
    finally:
        if conn:
            conn.close()

# --- チャット履歴取得 ---
def get_chat_history():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} ORDER BY timestamp DESC", conn)
        if 'is_correct' in df.columns:
            df['is_correct'] = pd.to_numeric(df['is_correct'], errors='coerce')
        return df
    finally:
        if conn:
            conn.close()

# --- レコード数取得 ---
def get_db_count():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = c.fetchone()[0]
        return count
    finally:
        if conn:
            conn.close()

# --- 全レコード削除 ---
def clear_db():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"DELETE FROM {TABLE_NAME}")
        conn.commit()
    finally:
        if conn:
            conn.close()