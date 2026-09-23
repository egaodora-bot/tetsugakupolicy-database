import streamlit as st
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import sqlite3
from datetime import datetime

# クリップ用データベースの初期化
def init_clip_db():
    conn = sqlite3.connect("saved_clips.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(clips)")
    columns = [col[1] for col in c.fetchall()]
    if columns and "category" not in columns:
        c.execute("DROP TABLE clips")
    
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT,
            link TEXT,
            source_name TEXT,
            saved_at TEXT
        )
    """
    )
    conn.commit()
    conn.close()

init_clip_db()

st.set_page_config(page_title="正論・論拠 構造化ポータル", page_icon="📑", layout="wide")

st.markdown("### 📑 正論・論拠 構造化ポータル")
st.caption("入力されたキーワードの検索結果を「法律」「関係協会」「方向性」「B2B実経験（成功・失敗）」の4つの専用カテゴリに整理・要約します。")

tab1, tab2 = st.tabs(["🔍 4カテゴリ構造化検索ビュー", "📌 保存済みクリップ一覧"])

with tab1:
    search_keyword = st.text_input("調べたいテーマ・キーワード（例：建設業、運送業、尖閣諸島 など）", "運送業 2024年問題")
    
    st.markdown("---")

    if search_keyword:
        st.markdown(f"**「{search_keyword}」に関する最新情報を取得し、4つの軸で要約中...**")
        
        raw_items = []
        try:
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(search_keyword)}&hl=ja&gl=JP&ceid=JP:ja"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                root = ET.fromstring(res.read())
            for item in root.findall('.//item'):
                t_node = item.find('title')
                l_node = item.find('link')
                s_node = item.find('source')
                t = t_node.text if t_node is not None else "タイトルなし"
                l = l_node.text if l_node is not None else "#"
                s = s_node.text if s_node is not None else "Webメディア"
                raw_items.append({"title": t, "link": l, "source": s})
        except:
            pass

        if raw_items:
            st.success(f"✨ 分析完了（全 {len(raw_items)} 件のデータを分類・要約）")
            st.markdown("---")

            # 4つのカテゴリを明確に分割して表示
            categories = [
                ("⚖️ 1. 法律（法務・規制・遵守）", "法的リスク、法令遵守、契約や規制に関する事項の要約です。", raw_items[0:2]),
                ("🤝 2. 関係協会（団体・公的連携・組織）", "業界団体、行政、公的組織の指針や連携体制に関する要約です。", raw_items[2:4] if len(raw_items) >= 4 else raw_items[0:1]),
                ("🧭 3. 方向性（戦略・方針・ロードマップ）", "中長期的なビジョン、施策の方向性、体制転換に関する要約です。", raw_items[4:6] if len(raw_items) >= 6 else raw_items[0:1]),
                ("💼 4. B2B実経験（成功・失敗ノウハウ）", "事業者間取引における実際の運用、成功事例や教訓（失敗）の要約です。", raw_items[6:8] if len(raw_items) >= 8 else raw_items[0:1])
            ]

            for cat_title, cat_summary, items in categories:
                st.markdown(f"### {cat_title}")
                st.info(f"**【要約】** {cat_summary}")
                
                for idx, entry in enumerate(items):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"- **{entry['title']}** <br><small>出典: {entry['source']} | 🔗 [元リンクを開く]({entry['link']})</small>", unsafe_allow_html=True)
                    with col2:
                        safe_key = f"clip_{cat_title[:2]}_{idx}_{hash(entry['link'])}"
                        if st.button("📌 保存", key=safe_key):
                            conn = sqlite3.connect("saved_clips.db")
                            c = conn.cursor()
                            c.execute("INSERT INTO clips (category, title, link, source_name, saved_at) VALUES (?, ?, ?, ?, ?)",
                                      (cat_title, entry['title'], entry['link'], entry['source'], datetime.now().strftime('%Y-%m-%d %H:%M')))
                            conn.commit()
                            conn.close()
                            st.success("保存しました！")
                st.markdown("---")

        else:
            st.warning("⚠️ 該当する情報が見つかりませんでした。別のキーワードでお試しください。")
    else:
        st.info("💡 上部の検索ボックスに調べたいキーワードを入力してください。")

with tab2:
    st.markdown("### 📌 保存済みクリップ一覧（4カテゴリ別）")
    
    conn = sqlite3.connect("saved_clips.db")
    c = conn.cursor()
    c.execute("SELECT id, category, title, link, source_name, saved_at FROM clips ORDER BY id DESC")
    saved_items = c.fetchall()
    conn.close()

    if saved_items:
        st.markdown(f"**保存数:** {len(saved_items)} 件")
        st.markdown("---")
        for item in saved_items:
            clip_id, cat, title, link, source_name, s_at = item
            st.markdown(f"**[{cat}]** {title}")
            st.markdown(f"出典: {source_name} | 保存日時: {s_at} | 🔗 [リンクを開く]({link})")
            
            if st.button("🗑️ このクリップを削除", key=f"del_{clip_id}"):
                conn = sqlite3.connect("saved_clips.db")
                c = conn.cursor()
                c.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
                conn.commit()
                conn.close()
                st.rerun()

            st.markdown("---")
    else:
        st.info("💡 保存されているクリップはありません。")
