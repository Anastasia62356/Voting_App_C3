#%%writefile app.py
import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. 設定 & 定数
# ---------------------------------------------------------
PAGE_TITLE = "投票アプリ"
APP_HEADER = "🗳️ 議題一覧"
APP_DESCRIPTION = "議題が表示されます"

# ---------------------------------------------------------
# 2. ページ設定
# ---------------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🗳️",
    layout="centered"
)

# ---------------------------------------------------------
# 3. カスタムCSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stat-text {
        font-size: 0.9rem;
        color: #666;
        text-align: center;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. サイドバー（画面遷移メニュー）
# ---------------------------------------------------------
st.sidebar.title("📌 メニュー")
with st.sidebar:
    
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)

    with col_nav1:
        if st.button("🏠 HOME"):
            st.switch_page("home.py")

    with col_nav2:
        if st.button("📋 議題一覧"):
            st.switch_page("app.py")   # ← 自分自身でもOK

    with col_nav3:
        if st.button("➕ 議題作成"):
            st.switch_page("pages/create_topic.py")

    with col_nav4:
        if st.button("📊 投票結果"):
            st.switch_page("pages/results.py")

# ---------------------------------------------------------
# 5. 議題リスト（仮データ）
# ---------------------------------------------------------
topics = [
    {"id": 1, "title": "好きなプログラミング言語は？", "votes": 0},
    {"id": 2, "title": "次回のイベント開催場所は？", "votes": 0},
    {"id": 3, "title": "欲しい部活動設備は？", "votes": 0},
]

# ---------------------------------------------------------
# 6. 議題表示と投票ボタン
# ---------------------------------------------------------
st.header("📋 議題一覧")

for topic in topics:
    st.subheader(topic["title"])
    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button(f"投票 [{topic['id']}]", key=f"vote_{topic['id']}"):
            topic["votes"] += 1
            st.success("投票しました！")

    with col2:
        st.write(f"現在の投票数: {topic['votes']}")
