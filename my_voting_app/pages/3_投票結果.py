import streamlit as st
import pandas as pd
import sys
import os
import time

# ---------------------------------------------------------
# db_handler.py を読み込めるようにパスを通す
# ---------------------------------------------------------
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import db_handler

# ---------------------------------------------------------
# ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="投票結果", page_icon="📊")

st.title("📊 投票結果一覧")
st.caption("現在の投票状況を自動更新しています")

# ---------------------------------------------------------
# 自動更新（5秒）
# ---------------------------------------------------------
time.sleep(5)
st.rerun()

# ---------------------------------------------------------
# データ取得
# ---------------------------------------------------------
topics_df = db_handler.get_topics_from_sheet()
votes_df = db_handler.get_votes_from_sheet()

# ---------------------------------------------------------
# 議題リスト作成（空でもOKにする）
# ---------------------------------------------------------
if topics_df.empty:
    topic_titles = ["（議題がまだありません）"]
else:
    topic_titles = topics_df["title"].tolist()

# ---------------------------------------------------------
# 選択ボックスは常に表示
# ---------------------------------------------------------
selected_topic = st.selectbox("議題を選択してください", topic_titles)

# ---------------------------------------------------------
# 中身の表示
# ---------------------------------------------------------
if topics_df.empty or selected_topic == "（議題がまだありません）":
    st.info("議題が追加されると、ここに結果が表示されます。")

else:
    topic_row = topics_df[topics_df["title"] == selected_topic].iloc[0]
    options = topic_row["options"].split("/")

    topic_votes = votes_df[votes_df["topic_title"] == selected_topic] if not votes_df.empty else pd.DataFrame()

    st.subheader(f"📝 議題：{selected_topic}")

    result = []
    counts = topic_votes["option"].value_counts() if not topic_votes.empty else {}

    for opt in options:
        result.append({"選択肢": opt, "投票数": int(counts.get(opt, 0))})

    result_df = pd.DataFrame(result)

    st.table(result_df)
    st.bar_chart(result_df.set_index("選択肢"))
