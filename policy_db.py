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
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT,
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

st.set_page_config(page_title="正論・論拠リアルタイムポータル", page_icon="🌐", layout="wide")

st.markdown("### 🌐 正論・論拠リアルタイム検索ポータル")
st.caption("リアルタイムの最新情報を取得・閲覧しつつ、重要な記事はクリック一つでマイクリップ（保存）できます。")

# タブによる切り替え
tab1, tab2 = st.tabs(["🔍 リアルタイム検索", "📌 保存済みクリップ一覧"])

with tab1:
    # 検索条件の入力
    col1, col2 = st.columns([2, 1])
    with col1:
        search_keyword = st.text_input("キーワード・人物名検索（例：石原慎太郎、尖閣諸島、防衛論 など）", "石原慎太郎 尖閣")
    with col2:
        search_scope = st.selectbox("情報ソース", ["Google ニュース（Web全体）", "トレンド・論考"])

    st.markdown("---")

    if search_keyword:
        st.markdown(f"**「{search_keyword}」に関する最新情報をインターネットからリアルタイム取得中...**")
        
        try:
            encoded_query = urllib.parse.quote(search_keyword)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
            
            req = urllib.request.Request(
                rss_url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            
            if items:
                st.markdown(f"**取得結果:** リアルタイム最新記事 {len(items)} 件")
                st.markdown("---")
                
                for idx, item in enumerate(items[:15]):
                    title = item.find('title').text if item.find('title') is not None else "タイトルなし"
                    link = item.find('link').text if item.find('link') is not None else "#"
                    raw_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    
                    # 日付を標準ライブラリのみで日本時間（〇年〇月〇日 〇時〇分）に変換
                    formatted_date = raw_date
                    if raw_date:
                        try:
                            parsed_tuple = email.utils.parsedate_tz(raw_date)
                            if parsed_tuple:
                                timestamp = email.utils.mktime_tz(parsed_tuple)
                                # 日本時間 (UTC+9) のタイムゾーンを作成
                                jst = timezone(timedelta(hours=9))
                                dt_jst = datetime.fromtimestamp(timestamp, jst)
                                formatted_date = dt_jst.strftime('%Y年%m月%d日 %H:%M')
                        except Exception:
                            pass

                    source_node = item.find('source')
                    source_name = source_node.text if source_node is not None else "Webメディア"
                    
                    st.markdown(f"**[{source_name}] {title}**")
                    st.markdown(f"公開日時: {formatted_date} | 🔗 [詳細リンクを開く]({link})")
                    
                    # 各記事ごとのマイクリップ登録ボタン
                    if st.button("📌 この記事をマイクリップに登録", key=f"clip_{idx}_{link}"):
                        conn = sqlite3.connect("saved_clips.db")
                        c = conn.cursor()
                        c.execute("SELECT id FROM clips WHERE link = ?", (link,))
                        if not c.fetchone():
                            c.execute(
                                "INSERT INTO clips (source_name, title, link, pub_date, saved_at) VALUES (?, ?, ?, ?, ?)",
                                (source_name, title, link, formatted_date, str(datetime.now().strftime('%Y-%m-%d %H:%M')))
                            )
                            conn.commit()
                            st.success("✨ クリップに保存しました！")
                        else:
                            st.info("💡 この記事はすでに保存されています。")
                        conn.close()

                    st.markdown("---")
            else:
                st.info("💡 該当するリアルタイム情報が見つかりませんでした。別のキーワードでお試しください。")
                
        except Exception as e:
            st.error(f"⚠️ 情報の取得中にエラーが発生しました: {e}")
    else:
        st.info("💡 上部の検索ボックスに調べたい人物名やキーワードを入力してください。")

with tab2:
    st.markdown("### 📌 保存済みクリップ一覧")
    st.markdown("「リアルタイム検索」からワンクリックで保存した記事の一覧です。")
    
    conn = sqlite3.connect("saved_clips.db")
    c = conn.cursor()
    c.execute("SELECT id, source_name, title, link, pub_date, saved_at FROM clips ORDER BY id DESC")
    saved_items = c.fetchall()
    conn.close()

    if saved_items:
        st.markdown(f"**保存数:** {len(saved_items)} 件")
        st.markdown("---")
        for item in saved_items:
            clip_id, s_name, title, link, p_date, s_at = item
            st.markdown(f"**[{s_name}] {title}**")
            st.markdown(f"公開日時: {p_date} (保存日時: {s_at}) | 🔗 [詳細リンクを開く]({link})")
            
            if st.button("🗑️ 削除", key=f"del_{clip_id}"):
                conn = sqlite3.connect("saved_clips.db")
                c = conn.cursor()
                c.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
                conn.commit()
                conn.close()
                st.rerun()

            st.markdown("---")
    else:
        st.info("💡 保存されているクリップはありません。「リアルタイム検索」タブから気になる記事を保存してください。")
