import streamlit as st
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
            speaker TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            url TEXT,
            tags TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def main():
    init_db()
    st.set_page_config(page_title="政策論・有識者データベース", layout="wide")
    
    st.title("🏛️ 政策論・有識者データベース")
    st.write("会田卓司氏をはじめとする有識者・参考人の正論や政策論、参考URLを一元管理します。")

    # サイドバーでメニュー切り替え
    menu = st.sidebar.selectbox("メニュー", ["データ一覧・検索", "新規データ登録"])

    # 1. データ一覧・検索画面
    if menu == "Data List & Search" or menu == "データ一覧・検索":
        st.subheader("🔍 データ検索・閲覧")
        
        keyword = st.text_input("キーワード検索 (発言者、タイトル、タグ、内容など)")
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        if keyword:
            query = """
                SELECT speaker, category, title, content, source, url, tags, created_at 
                FROM statements 
                WHERE speaker LIKE ? OR category LIKE ? OR title LIKE ? OR content LIKE ? OR tags LIKE ? OR url LIKE ?
            """
            pattern = f"%{keyword}%"
            cursor.execute(query, (pattern, pattern, pattern, pattern, pattern, pattern))
        else:
            cursor.execute("SELECT speaker, category, title, content, source, url, tags, created_at FROM statements ORDER BY id DESC")
            
        results = cursor.fetchall()
        conn.close()

        st.write(f"検索結果: **{len(results)}** 件")
        st.markdown("---")

       for r in results:
            st.markdown(f"### [{r[1]}] {r[2]}")
            st.markdown(f"**発言者・論客:** {r[0]} | **出典:** {r[4]} | **登録日:** {r[7]}")
            st.markdown(f"**【正論・論拠の要約】**\n{r[3]}")
            if r[5]:
                st.markdown(f"🔗 [参考URL/動画]({r[5]})")
            if r[6]:
                st.markdown(f"🏷️ **タグ:** {r[6]}")
            st.markdown("---")

    # 2. 新規データ登録画面
    elif menu == "New Data Entry" or menu == "新規データ登録":
        st.subheader("📝 新規データの登録")
        
        with st.form("entry_form"):
            speaker = st.text_input("発言者・論客名 (例: 会田 卓司)")
            category = st.selectbox("カテゴリ", ["財政規律", "成長投資", "エネルギー", "国家会計", "経済理論", "その他"])
            title = st.text_input("タイトル / テーマ")
            content = st.text_area("【正論・論拠の要約】(データや客観的事実に基づく主張)")
            source = st.text_input("出典 (国会公聴会・著書・媒体名など)")
            url = st.text_input("参考URL (YouTube動画、Facebookリール、記事のリンク等)")
            tags = st.text_input("タグ (カンマ区切り 例: 積極財政, 投資不足)")
            
            submitted = st.form_submit_button("登録する")
            
            if submitted:
                if speaker and title and content:
                    created_at = datetime.now().strftime("%Y-%m-%d")
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO statements (speaker, category, title, content, source, url, tags, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (speaker, category, title, content, source, url, tags, created_at))
                    conn.commit()
                    conn.close()
                    st.success(">> データを正常に登録しました！")
                else:
                    st.error("「発言者」「タイトル」「論拠の要約」は必須入力です。")

if __name__ == "__main__":
    main()
