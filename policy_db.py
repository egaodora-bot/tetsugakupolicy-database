import streamlit as st
import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET

st.set_page_config(page_title="正論・論拠リアルタイムポータル", page_icon="🌐", layout="wide")

st.title("🌐 正論・論拠リアルタイム検索ポータル")
st.markdown("データベースに蓄積する必要はありません。検索のたびにインターネット上の最新情報をリアルタイムで取得し、多角的に表示します。")

# 検索条件の入力（検索ワード、カテゴリ風の絞り込み）
col1, col2 = st.columns([2, 1])
with col1:
    search_keyword = st.text_input("キーワード・人物名検索（例：石原慎太郎、尖閣諸島、防衛論 など）", "石原慎太郎 尖閣")
with col2:
    search_scope = st.selectbox("情報ソース", ["Google ニュース（Web全体）", "トレンド・論考"])

st.markdown("---")

if search_keyword:
    st.markdown(f"**「{search_keyword}」に関する最新情報をインターネットからリアルタイム取得中...**")
    
    # 外部の無料RSS/API等（GoogleニュースのRSSなど）を利用してリアルタイムに情報を取得する処理
    try:
        encoded_query = urllib.parse.quote(search_keyword)
        # GoogleニュースのRSSフィードURL
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
        
        req = urllib.request.Request(
            rss_url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        # XMLを解析
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        if items:
            st.markdown(f"**取得結果:** リアルタイム最新記事 {len(items)} 件")
            st.markdown("---")
            
            for item in items[:15]: # 上位15件を表示
                title = item.find('title').text if item.find('title') is not None else "タイトルなし"
                link = item.find('link').text if item.find('link') is not None else "#"
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                source_node = item.find('source')
                source_name = source_node.text if source_node is not None else "Webメディア"
                
                st.markdown(f"### [{source_name}] {title}")
                st.markdown(f"**公開日時:** {pub_date}")
                st.markdown(f"🔗 [記事・詳細リンクを開く]({link})")
                st.markdown("---")
        else:
            st.info("💡 該当するリアルタイム情報が見つかりませんでした。別のキーワードでお試しください。")
            
    except Exception as e:
        st.error(f"⚠️ 情報の取得中にエラーが発生しました: {e}")
else:
    st.info("💡 上部の検索ボックスに調べたい人物名やキーワードを入力してください。")
