import streamlit as st

# 1. ページ設定（ブラウザのタブ名やアイコンなど）
# ※必ずコードの一番最初に書く必要があります
st.set_page_config(
    page_title="チーム制作アプリ Home",
    page_icon="🏠",
    layout="wide",  # 画面を広く使う設定
    initial_sidebar_state="expanded"
)

# 2. タイトルとメインビジュアル
st.title("🚀 チーム制作プロジェクトへようこそ")
st.markdown("### Python x Streamlitで作成したデモアプリです")

# 画像を入れる場合は以下のコメントアウトを外す
# st.image("top_image.png", use_column_width=True) 

st.divider()  # 区切り線

# 3. アプリの機能紹介（2列レイアウトで見やすくする）
col1, col2 = st.columns(2)

with col1:
    st.header("📊 投票機能")
    st.info("リアルタイムで投票を行い、集計します。")
    st.write("クラスの意見を一つにまとめるための機能です。")
    if st.button("投票ページへ移動（デモ）"):
        st.switch_page("pages/01_voting.py") # ※実際にファイルがないとエラーになります

with col2:
    st.header("📈 結果確認")
    st.success("投票結果をグラフで可視化します。")
    st.write("データに基づいた意思決定をサポートします。")
    # こちらにも遷移ボタンを設置可能

st.divider()

# 4. お知らせや更新情報（Expanderで折りたたみ）
with st.expander("ℹ️ 更新情報・お知らせ"):
    st.write("- 2025/12/01: アプリのプロトタイプを公開しました。")
    st.write("- 2025/12/05: デザインを修正予定です。")

# 5. サイドバー（共通メニュー）
st.sidebar.info("製作者: チーム〇〇")
