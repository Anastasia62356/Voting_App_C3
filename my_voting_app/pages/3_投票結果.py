import streamlit as st
import pandas as pd

import sys
import os
from background import set_background  #  # 背景画像の設定ファイルをインポート
from google import genai # gemini api

# 環境変数から API キーを取得
API_KEY = os.getenv('GEMINI_API_KEY')

# Gemini クライアント初期化
client = genai.Client(api_key=API_KEY)


# db_handler.py を読み込めるようにパスを通す
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import db_handler

# ページ設定
st.set_page_config(page_title="投票結果", page_icon="📊")

st.title("📊 投票結果一覧")
st.caption("締切済みの議題のみ表示します")

set_background("background.png")  # 背景画像の設定

# データ取得
topics_df = db_handler.get_topics_from_sheet()
votes_df = db_handler.get_votes_from_sheet()


# 日付変換
if not topics_df.empty and "deadline" in topics_df.columns:
    topics_df["deadline_parsed"] = pd.to_datetime(
        topics_df["deadline"], errors="coerce"
    )
    topics_df["deadline_date"] = topics_df["deadline_parsed"].dt.date


# 今日の日付
today = pd.to_datetime("now").date()


# 締切済み議題のみ抽出
if not topics_df.empty and "deadline_date" in topics_df.columns:
    finished_topics = topics_df[
        topics_df["deadline_date"].notna() &
        (topics_df["deadline_date"] < today)
    ].copy()
else:
    finished_topics = pd.DataFrame()


# 議題ドロップダウン
if finished_topics.empty:
    topic_titles = ["（締切済みの議題がありません）"]
else:
    topic_titles = finished_topics["title"].tolist()

selected_topic = st.selectbox("議題を選択してください", topic_titles)


# 表示処理
if finished_topics.empty or selected_topic == "（締切済みの議題がありません）":
    st.info("締切済みの議題はまだありません。")

else:
    topic_row = finished_topics[finished_topics["title"] == selected_topic].iloc[0]
    options = topic_row["options"].split("/")

    topic_votes = (
        votes_df[votes_df["topic_title"] == selected_topic]
        if not votes_df.empty else pd.DataFrame()
    )

    st.subheader(f"📝 議題：{selected_topic}")

    # 集計
    result = []
    counts = (
        topic_votes["option"].value_counts()
        if not topic_votes.empty else {}
    )

    for opt in options:
        result.append({
            "選択肢": opt,
            "投票数": int(counts.get(opt, 0))
        })

    result_df = pd.DataFrame(result)

    # 表表示
    st.dataframe(result_df, hide_index=True)

    # ===== Geminiによる分析機能 =====
    st.subheader("🔍 Gemini による投票結果分析")
    
    if st.button("AIに分析してもらう"):
        with st.spinner("Gemini が分析中です..."):
    
            # 分析用の文章生成
           analysis_prompt = f"""
            あなたはデータ分析を専門とする **厳格で経験豊富なアナリスト** です。
            
            このメッセージの最後に **解析対象の CSV データ** が添付されています。
            それを元に投票結果を分析してください。
            
            重要な指示：
            - 以下の「出力フォーマット」は必ず厳守すること
            - 「解析対象の CSV データブロック」は **回答に絶対に含めないこと**
            - CSV の内容は解析のみに使用し、出力に表示してはならない
            
            ========================
            【出力フォーマット（厳守）】
            ========================
            ---
            ## 概要
            （最重要ポイントを2〜4行で簡潔に）
            
            ---
            ## 投票傾向
            - （傾向1）
            - （傾向2）
            - （傾向3）
            
            ---
            ## 支持理由の分析
            - （理由1）
            - （理由2）
            - （理由3）
            
            ---
            ## 全体の特徴
            - （特徴1）
            - （特徴2）
            - （特徴3）
            
            （※ この下には何も追加しないこと）
            ========================
            
            以下は **解析対象の CSV データ（回答に含めるな）**
            ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
            
            {result_df.to_csv(index=False)}
            
            ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
            （解析用のデータ。回答に表示してはならない）
            """


    
           response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=analysis_prompt
            )
    
           st.write("### 🧠 分析結果")
           st.write(response.text)



# 更新ボタン
st.divider()
if st.button("🔄 更新"):
    st.rerun()














