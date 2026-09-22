import sqlite3
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

init_db()

st.set_page_config(page_title="正論・論拠データベース", page_icon="🏛️", layout="wide")

st.title("🏛️ 正論・論拠データベース・検索システム")
st.markdown("必要な情報をマルチ条件（人物・カテゴリ・キーワード）で自在に即時抽出するためのデータベースビューです。")

# データベースから動的に「発言者」および「カテゴリ」の一覧を取得
conn = sqlite3.connect("policy_database.db")
c = conn.cursor()

c.execute("SELECT DISTINCT speaker FROM policies ORDER BY speaker")
speaker_list = ["すべて"] + [row[0] for row in c.fetchall() if row[0]]

c.execute("SELECT DISTINCT category FROM policies ORDER BY category")
category_list = ["すべて"] + [row[0] for row in c.fetchall() if row[0]]

# 検索フィルター（3カラムによる多角的絞り込み）
col1, col2, col3 = st.columns(3)
with col1:
    selected_speaker = st.selectbox("発言者・論客で絞り込み", speaker_list)
with col2:
    selected_category = st.selectbox("カテゴリで絞り込み", category_list)
with col3:
    search_keyword = st.text_input("キーワード検索（フリーワード）")

# 動的SQL構築
query = "SELECT speaker, category, title, summary, source, url, tags, date FROM policies WHERE 1=1"
params = []

if selected_speaker != "すべて":
    query += " AND speaker = ?"
    params.append(selected_speaker)

if selected_category != "すべて":
    query += " AND category = ?"
    params.append(selected_category)

if search_keyword:
    query += " AND (speaker LIKE ? || title LIKE ? || summary LIKE ? || tags LIKE ?)"
    # SQLiteの構文修正
    query = "SELECT speaker, category, title, summary, source, url, tags, date FROM policies WHERE 1=1"
    if selected_speaker != "すべて":
        query += " AND speaker = ?"
        params = [selected_speaker]
    else:
        params = []

    if selected_category != "すべて":
        query += " AND category = ?"
        params.append(selected_category)

    kw = f"%{search_keyword}%"
    query += " AND (speaker LIKE ? OR title LIKE ? OR summary LIKE ? OR tags LIKE ?)"
    params.extend([kw, kw, kw, kw])

query += " ORDER BY id DESC"

c.execute(query, params)
results = c.fetchall()
conn.close()

st.markdown(f"**抽出結果:** {len(results)} 件のデータが見つかりました。")
st.markdown("---")

if results:
    for r in results:
        st.markdown(f"### [{r[1]}] {r[2]}")
        st.markdown(f"**発言者・論客:** {r[0]} | **出典:** {r[4]} | **登録日:** {r[7]}")
        st.markdown(f"**【要約・内容】**\n{r[3]}")
        if r[5]:
            st.markdown(f"🔗 [参考リンク]({r[5]})")
        if r[6]:
            st.markdown(f"🏷️ **タグ:** {r[6]}")
        st.markdown("---")
else:
    st.info("💡 検索条件に一致するデータはありません。")
