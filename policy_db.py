import sqlite3
from datetime import datetime
import streamlit as st

# データベースの初期化（動的カテゴリに対応したスキーマ）
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

st.title("🏛️ 正論・論拠データベース（自動・動的更新型）")
st.markdown("最新トレンドや情報をスマートに自動収集・蓄積し、多角的に検索できる次世代データベースです。")

# サイドバーによるモード切り替え
menu = st.sidebar.selectbox("メニュー", ["検索・閲覧", "AI自動インポート・収集"])

if menu == "AI自動インポート・収集":
    st.header("🤖 AI自動インポート・情報収集")
    st.markdown("テキスト、ニュースの抜粋、または長文を貼り付けるだけで、AIが自動で項目を解析・構造化してデータベースに蓄積します。")

    with st.form("auto_import_form"):
        raw_text = st.text_area("収集・登録したい文章やニュース内容をここに貼り付け", height=200, placeholder="例：石原慎太郎氏の尖閣諸島に関する発言や、関連する論考のテキストをそのままペースト...")
        
        # 補助的な自動タグ・カテゴリのヒント指定
        col_a, col_b = st.columns(2)
        with col_a:
            suggested_speaker = st.text_input("発言者・論客（任意・未入力の場合はAI自動推論）", placeholder="例：石原慎太郎")
        with col_b:
            suggested_category = st.text_input("カテゴリ・テーマ（任意・未入力の場合は自動生成）", placeholder="例：外交・安全保障")

        submitted = st.form_submit_button("AI解析・自動データベース登録実行")

        if submitted:
            if raw_text:
                # 自動解析のシミュレーション（実運用時はAI API等で構造化）
                inferred_speaker = suggested_speaker if suggested_speaker else "未指定（自動抽出）"
                inferred_category = suggested_category if suggested_category else "トレンド・その他"
                
                # テキストの先頭をタイトルにする等の自動処理
                lines = raw_text.strip().split("\n")
                inferred_title = lines[0][:50] if lines else "自動インポート記事"
                summary = raw_text

                conn = sqlite3.connect("policy_database.db")
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO policies (speaker, category, title, summary, source, url, tags, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        inferred_speaker,
                        inferred_category,
                        inferred_title,
                        summary,
                        "AI自動収集・Webスクレイピング",
                        "",
                        "自動生成, トレンド",
                        str(datetime.today().date()),
                    ),
                )
                conn.commit()
                conn.close()
                st.success("🎉 情報を自動解析し、データベースへ正常に組み込みました！")
            else:
                st.error("⚠️ 解析するテキストを入力してください。")

elif menu == "検索・閲覧":
    st.header("🔍 動的スマート検索・閲覧")

    # データベースから動的に「発言者」および「カテゴリ」の一覧を取得
    conn = sqlite3.connect("policy_database.db")
    c = conn.cursor()
    
    c.execute("SELECT DISTINCT speaker FROM policies ORDER BY speaker")
    speaker_list = ["すべて"] + [row[0] for row in c.fetchall() if row[0]]

    c.execute("SELECT DISTINCT category FROM policies ORDER BY category")
    category_list = ["すべて"] + [row[0] for row in c.fetchall() if row[0]]

    # 検索フィルター（3カラムによる動的絞り込み）
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
        query += " AND (speaker LIKE ? OR title LIKE ? OR summary LIKE ? OR tags LIKE ?)"
        kw = f"%{search_keyword}%"
        params.extend([kw, kw, kw, kw])

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
            st.markdown(f"**【要約・内容】**\n{r[3]}")
            if r[5]:
                st.markdown(f"🔗 [参考リンク]({r[5]})")
            if r[6]:
                st.markdown(f"🏷️ **タグ:** {r[6]}")
            st.markdown("---")
    else:
        st.info("💡 該当するデータがありません。「AI自動インポート・収集」から新しい情報を流し込んでデータベースを動的に更新してください。")
