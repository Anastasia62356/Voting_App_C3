#%%writefile app.py
import streamlit as st
import pandas as pd
import datetime
import time
import sys
import os
from background import set_background

# ---------------------------------------------------------
# db_handler.py を読み込めるようにパスを通す
# ---------------------------------------------------------
# pagesフォルダの一つ上(親フォルダ)を見る設定
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import db_handler

# ---------------------------------------------------------
# 1. 設定 & 定数
# ---------------------------------------------------------
PAGE_TITLE = "投票アプリ"
APP_HEADER = "🗳️ 議題一覧"
APP_DESCRIPTION = "みんなで意見を集めよう！気になる議題に投票できます。"

# ---------------------------------------------------------
# 2. ページ設定
# ---------------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🗳️",
    layout="centered"
)

set_background("background.png")  # 背景画像の設定

# ---------------------------------------------------------
# ▼▼▼ 門番コード（ログインチェック） ▼▼▼
# ---------------------------------------------------------
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    st.warning("⚠️ このページを見るにはログインが必要です。")
    st.page_link("Home.py", label="ログイン画面へ戻る", icon="🏠")
    st.stop() # プログラム強制停止

# ---------------------------------------------------------
# 4. ヘッダー & フィルタ UI
# ---------------------------------------------------------
st.title(APP_HEADER)
st.caption(APP_DESCRIPTION)
st.divider()

# ソート用セッションステート初期化
if "fg" not in st.session_state:
    st.session_state["fg"] = 0  # 0: 締切順, 1: 新着順

# 右寄せでボタンを横並びに配置
col1, col2, col3, col4 = st.columns([0.36, 0.36, 0.14, 0.14])
with col1:
    # デフォルトはNone（絞り込みなし）にして、全件見れるようにしています
    input_date = st.date_input("締め切りで絞り込み", value=None)

with col3:
    st.write("")
    st.write("")
    if st.button("⬆️ 昇順"):
        st.session_state.fg = 1
   
with col4:
    st.write("")
    st.write("")
    if st.button("⬇️ 降順"):
        st.session_state.fg = 0

# ---------------------------------------------------------
# 5. スプレッドシートから議題を取得
# ---------------------------------------------------------
@st.cache_data(ttl=30)  # 30秒間キャッシュ
def load_topics():
    return db_handler.get_topics_from_sheet()

topics_df = load_topics()

if topics_df.empty:
    st.info("まだ議題が登録されていません。")
    st.stop()

# ---------------------------------------------------------
# 6. 投票データも取得
# ---------------------------------------------------------
@st.cache_data(ttl=30)
def load_votes():
    return db_handler.get_votes_from_sheet()

votes_df = load_votes()

# ---------------------------------------------------------
# 7. データ加工とフィルタリング
# ---------------------------------------------------------
# 現在日時（日本時間）
now = datetime.datetime.now()

# deadlineを日付型に変換
topics_df["deadline"] = pd.to_datetime(topics_df["deadline"], errors="coerce", format="%Y-%m-%d %H:%M")

# 締切があるものだけ残す（自動終了フィルタ）
# ※ 期限切れのものは表示されなくなります
topics_df = topics_df[topics_df["deadline"].isna() | (topics_df["deadline"] >= now)]

# ソート処理
if st.session_state.fg == 0:  # 締切順（昇順）
    topics_df = topics_df.sort_values("deadline", ascending=True)
elif st.session_state.fg == 1:  # 新着順（降順）
    topics_df = topics_df.sort_values("deadline", ascending=False)
    
# 締切日での検索（input_date でフィルタ）
if input_date:
    filtered_df = topics_df[
        topics_df["deadline"].dt.date == input_date
    ]
    if filtered_df.empty:
        st.warning("⚠️ 指定した締切日の議題は見つかりませんでした。")
        st.stop()
    else:
        topics_df = filtered_df

# ---------------------------------------------------------
# 8. 議題ループ表示
# ---------------------------------------------------------
for index, topic in topics_df.iterrows():
    title = topic["title"]
    author = topic.get("author", "不明")
    options_raw = topic["options"]
    deadline = topic.get("deadline", pd.NaT)
    status = topic.get("status", "active")       # ステータス取得
    owner_email = topic.get("owner_email", "")   # 作成者のメアド取得

    # deadline文字列化
    if pd.notna(deadline):
        deadline_str = deadline.strftime("%Y-%m-%d %H:%M")
    else:
        deadline_str = "未設定"

    # ▼▼▼ 終了判定（手動 or 自動） ▼▼▼
    is_closed = False
    if status == 'closed':
        is_closed = True

    with st.container(border=True):
        # タイトル（終了していたらアイコン変更）
        if is_closed:
            st.subheader(f"🔒 {title} (終了)")
        else:
            st.subheader(title)
            
        st.caption(f"作成者：{author}｜締め切り：{deadline_str}")

        # ▼▼▼ 作成者用：終了ボタン ▼▼▼
        current_user = st.session_state.logged_in_user
        
        # 「自分が作成者」かつ「まだ終わっていない」ならボタンを表示
        # ※ owner_emailが空文字の場合はボタンを出さない安全設計
        if owner_email and current_user == owner_email and not is_closed:
             with st.popover("⚠️ 投票を締め切る"):
                st.write("本当に終了しますか？")
                if st.button("はい、終了します", key=f"close_{index}", type="primary"):
                    db_handler.close_topic_status(title)
                    load_topics.clear() # ★重要：キャッシュを消して即反映
                    st.success("終了しました！")
                    st.rerun()

        st.markdown("---")

        col1, col2 = st.columns([1, 1])

        # 左カラム：投票UI
        with col1:
            if is_closed:
                # 終了理由の表示
                if status == 'closed':
                    st.warning("⛔ この投票は受け付けを終了しました。")
                else:
                    st.warning("⏰ 締め切り時間を過ぎました。")
            else:
                # 自由記述か選択式か
                submit_value = None
                
                if options_raw == "FREE_INPUT":
                    st.markdown("**回答を入力してください**")
                    submit_value = st.text_area("あなたの意見", key=f"text_{index}")
                else:
                    st.markdown("**選択肢を選んでください**")
                    # 安全策：万が一 FREE_INPUT 以外の文字列がおかしくてもエラーにしない
                    try:
                        options_list = str(options_raw).split("/")
                        submit_value = st.radio("選択肢", options_list, key=f"radio_{index}", label_visibility="collapsed")
                    except:
                        st.error("選択肢データの読み込みエラー")

                # 投票ボタン
                if st.button("👍 投票する", key=f"vote_{index}", type="primary"):
                    if not submit_value:
                        st.error("回答を入力してください")
                    else:
                        db_handler.add_vote_to_sheet(title, submit_value)
                        load_votes.clear() # キャッシュクリア
                        st.success("投票しました！")
                        st.rerun()

        # 右カラム：投票数集計表示
        with col2:
            st.write("### 📊 現在の投票数")
            topic_votes = votes_df[votes_df["topic_title"] == title] if not votes_df.empty else pd.DataFrame()
            
            if topic_votes.empty:
                st.write("まだ投票はありません")
            else:
                counts = topic_votes["option"].value_counts()
                st.bar_chart(counts)
                with st.expander("詳細を見る"):
                    st.dataframe(counts)


































