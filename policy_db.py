import sqlite3
from datetime import datetime
import streamlit as st

# データベースの初期化
def init_db():
    conn = sqlite3.connect("policy_database.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            speaker TEXT,
            category TEXT,
            title TEXT,
            summary TEXT,
            source TEXT,
            url TEXT,
            tags TEXT,
            date TEXT
        )
    """
    )
    conn.commit()
    conn.close()

# 初期化実行
init_db()

st.set_page_config(page_title="正論・論拠データベース", page_icon="🏛️", layout="wide")

st.title("🏛️ 正論・論拠データベース")
st.markdown("心に響く正論、的確な論拠、優れた意見を蓄積・検索するためのデータベースです。")

# サイドバーメニュー
menu = st.sidebar.selectbox("メニュー", ["検索・閲覧", "新規登録"])

if menu == "新規登録":
    st.header("📝 新しい正論・論拠の登録")

    with st.form("policy_form"):
        speaker = st.text_input("発言者・論客（例：〇〇 〇〇、有識者A など）")
        category = st.selectbox(
            "カテゴリ",
            ["政治・経済", "社会・倫理", "テクノロジー", "科学・教育", "ビジネス・労働", "その他"]
        )
        title = st.text_input("主張・タイトルの要約（例：〇〇に関する一刀両断の意見）")
        summary = st.text_area("正論・論拠の要約・詳細内容", height=150)
        source = st.text_input("出典（例：〇〇書籍、〇〇のインタビュー、YouTube番組名 など）")
        url = st.text_input("参考URL/動画リンク（任意）")
        tags = st.text_input("タグ（カンマ区切り 例：AI, 労働, 規制緩和）")
        date = st.date_input("登録日", datetime.today())

        submitted = st.form_submit_button("登録する")

        if submitted:
            if speaker and title and summary:
                conn = sqlite3.connect("policy_database.db")
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO policies (speaker, category, title, summary, source, url, tags, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (speaker, category, title, summary, source, url, tags, str(date)),
                )
                conn.commit()
                conn.close()
                st.success("🎉 正常に登録されました！")
            else:
                st.error("⚠️ 「発言者・論客」「主張・タイトル」「要約」は必須項目です。")

elif menu == "検索・閲覧":
    st.header("🔍 登録データの検索・閲覧")

    # 検索フィルター
    col1, col2 = st.columns(2)
    with col1:
        search_keyword = st.text_input("キーワード検索（発言者、タイトル、内容など）")
    with col2:
        selected_category = st.selectbox(
            "カテゴリ絞り込み",
            ["すべて", "政治・経済", "社会・倫理", "テクノロジー", "科学・教育", "ビジネス・労働", "その他"]
        )

    conn = sqlite3.connect("policy_database.db")
    c = conn.cursor()

    query = "SELECT speaker, category, title, summary, source, url, tags, date FROM policies WHERE 1=1"
    params = []

    if search_keyword:
        query += " AND (speaker LIKE ? OR title LIKE ? OR summary LIKE ? OR tags LIKE ?)"
        keyword_param = f"%{search_keyword}%"
        params.extend([keyword_param, keyword_param, keyword_param, keyword_param])

    if selected_category != "すべて":
        query += " AND category = ?"
        params.append(selected_category)

    query += " ORDER BY id DESC"

    c.execute(query, params)
    results = c.fetchall()
    conn.close()

    st.markdown(f"**検索結果:** {len(results)} 件のデータが見つかりました。")
    st.markdown("---")

    if results:
        for r in results:
            st.markdown(f"### [{r[1]}] {r[2]}")
            st.markdown(f"**発言者・論客:** {r[0]} | **出典:** {r[4]} | **登録日:** {r[7]}")
            st.markdown(f"**【正論・論拠の要約】**\n{r[3]}")
            if r[5]:
                st.markdown(f"🔗 [参考URL/動画]({r[5]})")
            if r[6]:
                st.markdown(f"🏷️ **タグ:** {r[6]}")
            st.markdown("---")
    else:
        st.info("💡 該当するデータが見つかりませんでした。「新規登録」からデータを追加してみてください。")
