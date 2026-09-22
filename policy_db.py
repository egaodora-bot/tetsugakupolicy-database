import streamlit as st
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import sqlite3
from datetime import datetime, timezone, timedelta
import email.utils

# クリップ用データベースの初期化
def init_clip_db():
    conn = sqlite3.connect("saved_clips.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(clips)")
    columns = [col[1] for col in c.fetchall()]
    if columns and "source_type" not in columns:
        c.execute("DROP TABLE clips")
    
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT,
            title TEXT,
            link TEXT,
            pub_date TEXT,
            saved_at TEXT
        )
    """
    )
    conn.commit()
    conn.close()

init_clip_db()

st.set_page_config(page_title="正論・論拠 構造化ポータル", page_icon="📑", layout="wide")

st.markdown("### 📑 正論・論拠 構造化ポータル（情報整理 ⇒ 要約 ⇒ 典拠リンク）")
st.caption("検索キーワードについて「多角的な方向性の整理」を行い、「要約」と「具体的な情報源へのリンク」を体系的に紐づけて表示します。")

tab1, tab2 = tab1, tab2 = st.tabs(["🔍 構造化検索・要約ビュー", "📌 保存済みクリップ一覧"])

with tab1:
    search_keyword = st.text_input("調べたいテーマ・人物・キーワード（例：尖閣諸島、石原慎太郎、インフラ老朽化 など）", "尖閣諸島 防衛")
    
    st.markdown("---")

    if search_keyword:
        st.markdown(f"**「{search_keyword}」に関する情報を多角的な方向性（省庁・国会図書館・最新動向）から収集中...**")
        
        items_mlit = []
        items_ndl = []
        items_news = []
        
        # 1. 国土交通省・各省庁 (go.jp) の視点
        try:
            q = f"{search_keyword} (site:mlit.go.jp OR site:go.jp)"
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=ja&gl=JP&ceid=JP:ja"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                root = ET.fromstring(res.read())
            for item in root.findall('.//item'):
                t = item.find('title').text if item.find('title'] is not None else "タイトルなし"
                l = item.find('link').text if item.find('link') is not None else "#"
                items_mlit.append({"title": t, "link": l, "source": "省庁・公的機関 (go.jp)"})
        except:
            pass

        # 2. 国立国会図書館 (NDL Search) の視点
        try:
            url = f"https://ndlsearch.ndl.go.jp/api/opensearch?any={urllib.parse.quote(search_keyword)}&cnt=5"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                root = ET.fromstring(res.read())
            for item in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                t = item.find('{http://www.w3.org/2005/Atom}title')
                l = item.find('{http://www.w3.org/2005/Atom}link')
                title_txt = t.text if t is not None else "タイトルなし"
                link_txt = l.attrib.get('href', '#') if l is not None else "#"
                items_ndl.append({"title": title_txt, "link": link_txt, "source": "国立国会図書館 (NDL)"})
        except:
            pass

        # 3. Webニュース全般（幅広い論点・方向性）
        try:
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(search_keyword)}&hl=ja&gl=JP&ceid=JP:ja"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                root = ET.fromstring(res.read())
            for item in root.findall('.//item'):
                t = item.find('title').text if item.find('title') is not None else "タイトルなし"
                l = item.find('link').text if item.find('link') is not None else "#"
                s = item.find('source')
                s_name = s.text if s is not None else "Webメディア"
                items_news.append({"title": t, "link": l, "source": s_name})
        except:
            pass

        if items_mlit or items_ndl or items_news:
            st.success("✨ 多角的な情報収集と構造化整理が完了しました。")
            
            st.markdown("### 📊 【情報整理 ⇒ 要約 ⇒ 典拠リンクの体系】")
            st.markdown("---")

            # --- 方向性1：省庁・公的機関の視点 ---
            st.markdown("#### 🏛️ 方向性①：省庁・公的政策の視点（制度・方針）")
            st.markdown(
                "> **【要約】**: 政府や各省庁による公式発表や施策、報告書に基づく方向性です。"
                "制度的な枠組み、法的な裏付け、および公的な方針を確認することができます。"
            )
            if items_mlit:
                for idx, entry in enumerate(items_mlit[:3]):
                    st.markdown(f"- **{entry['title']}**")
                    st.markdown(f"  🔗 [公式情報源・詳細を見る（{entry['source']}）]({entry['link']})")
            else:
                st.info("💡 該当する省庁・公的データが見つかりませんでした。")

            st.markdown("---")

            # --- 方向性2：歴史的・学術的背景（国会図書館） ---
            st.markdown("#### 📚 方向性②：歴史的・文献的背景（国立国会図書館アーカイブ）")
            st.markdown(
                "> **【要約】**: 国立国会図書館に収蔵されている専門書や公的刊行物の記録に基づく方向性です。"
                "長期的な変遷や、過去からの政策的・歴史的な文脈を辿る際に有効です。"
            )
            if items_ndl:
                for idx, entry in enumerate(items_ndl[:3]):
                    st.markdown(f"- **{entry['title']}**")
                    st.markdown(f"  🔗 [国会図書館の資料・詳細ページを開く]({entry['link']})")
            else:
                st.info("💡 該当する国会図書館の文献データが見つかりませんでした。")

            st.markdown("---")

            # --- 方向性3：最新の社会動向・論考（メディア・各界） ---
            st.markdown("#### 📰 方向性③：最新の社会動向・多元的論考（メディア・各界の視点）")
            st.markdown(
                "> **【要約】**: 各種メディア報道や各界の論客による多面的な議論に基づく方向性です。"
                "現在進行形の世論の動きや、様々な角度からの解釈・争点を整理できます。"
            )
            if items_news:
                for idx, entry in enumerate(items_news[:5]):
                    st.markdown(f"- **[{entry['source']}] {entry['title']}**")
                    st.markdown(f"  🔗 [記事・論考の元情報へアクセス]({entry['link']})")
            else:
                st.info("💡 該当するニュース記事が見つかりませんでした。")

        else:
            st.warning("⚠️ 情報が見つかりませんでした。別のキーワードでお試しください。")
    else:
        st.info("💡 上部の検索ボックスに調べたいキーワードを入力してください。")

with tab2:
    st.markdown("### 📌 保存済みクリップ一覧")
    st.markdown("構造化検索から保存した資料や記事の一覧です。")
    
    conn = sqlite3.connect("saved_clips.db")
    c = conn.cursor()
    c.execute("SELECT id, source_type, title, link, pub_date, saved_at FROM clips ORDER BY id DESC")
    saved_items = c.fetchall()
    conn.close()

    if saved_items:
        st.markdown(f"**保存数:** {len(saved_items)} 件")
        st.markdown("---")
        for item in saved_items:
            clip_id, s_type, title, link, p_date, s_at = item
            st.markdown(f"**[{s_type}] {title}**")
            st.markdown(f"公開日: {p_date} (保存日時: {s_at}) | 🔗 [リンクを開く]({link})")
            
            if st.button("🗑️ 削除", key=f"del_{clip_id}"):
                conn = sqlite3.connect("saved_clips.db")
                c = conn.cursor()
                c.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
                conn.commit()
                conn.close()
                st.rerun()

            st.markdown("---")
    else:
        st.info("💡 保存されているクリップはありません。")
