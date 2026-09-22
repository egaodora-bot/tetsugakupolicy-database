import sqlite3
from datetime import datetime

DB_NAME = "policy_database.db"

def init_db():
    """データベースとテーブルの初期化"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            speaker TEXT NOT NULL,          -- 発言者（例: 会田卓司）
            category TEXT NOT NULL,         -- カテゴリ（例: 財政規律, エネルギー, 会計改革）
            title TEXT NOT NULL,            -- 資料・発言のタイトルやテーマ
            content TEXT NOT NULL,          -- 主張・要約内容
            source TEXT,                    -- 出典（例: 著書『〇〇』, 国会予算委員会, IEEI寄稿）
            tags TEXT,                      -- タグ（カンマ区切り: 積極財政, 60年ルール, GX）
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_statement():
    """データの追加"""
    print("\n--- 新規データの登録 ---")
    speaker = input("発言者・論客名: ")
    category = input("カテゴリ (例: 財政規律, 成長投資, エネルギー, 国家会計): ")
    title = input("タイトル/テーマ: ")
    content = input("主張・内容の要約: ")
    source = input("出典 (著書名・媒体・国会名など): ")
    tags = input("タグ (カンマ区切り 例: 積極財政,投資不足): ")
    created_at = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO statements (speaker, category, title, content, source, tags, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (speaker, category, title, content, source, tags, created_at))
    conn.commit()
    conn.close()
    print(">> データを登録しました！")

def search_statements():
    """キーワードによる検索"""
    print("\n--- データ検索 ---")
    keyword = input("検索キーワード (発言者、タグ、内容の一部など): ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = """
        SELECT speaker, category, title, content, source, tags 
        FROM statements 
        WHERE speaker LIKE ? OR category LIKE ? OR title LIKE ? OR content LIKE ? OR tags LIKE ?
    """
    pattern = f"%{keyword}%"
    cursor.execute(query, (pattern, pattern, pattern, pattern, pattern))
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("該当するデータは見つかりませんでした。")
        return

    print(f"\n検索結果: {len(results)}件が見つかりました。\n" + "="*40)
    for i, r in enumerate(results, 1):
        print(f"[{i}] 発言者: {r[0]} | カテゴリ: {r[1]}")
        print(f"    タイトル: {r[2]}")
        print(f"    要約: {r[3]}")
        print(f"    出典: {r[4]}")
        print(f"    タグ: {r[5]}")
        print("-" * 40)

def list_all():
    """全データのリスト表示"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, speaker, category, title, source FROM statements")
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("\n登録されているデータはありません。")
        return

    print("\n--- 登録データ一覧 ---")
    for r in results:
        print(f"ID: {r[0]} | [{r[1]}] ({r[2]}) {r[3]} [出典: {r[4]})]")

def main():
    init_db()
    while True:
        print("\n=== 有識者・参考人 財政・経済データベース ===")
        print("1. データを登録する")
        print("2. データを検索する")
        print("3. 一覧を表示する")
        print("4. 終了")
        choice = input("メニュー番号を選んでください (1-4): ")

        if choice == "1":
            add_statement()
        elif choice == "2":
            search_statements()
        elif choice == "3":
            list_all()
        elif choice == "4":
            print("プログラムを終了します。")
            break
        else:
            print("無効な選択です。1〜4の数字を入力してください。")

if __name__ == "__main__":
    main()