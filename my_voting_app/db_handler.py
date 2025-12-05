import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# 設定：ここに自分のスプレッドシート名などを書く
# ---------------------------------------------------------
SPREADSHEET_NAME = "voting_app_db"  # さっき作ったスプレッドシートの名前
KEY_FILE = "key.json"               # さっき名前を変えた鍵ファイル

# ---------------------------------------------------------
# Googleスプレッドシートに接続する関数
# ---------------------------------------------------------
def connect_to_sheet():
    # 認証情報を設定
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, scope)
    client = gspread.authorize(creds)
    
    # スプレッドシートを開く
    sheet = client.open(SPREADSHEET_NAME)
    return sheet

# ---------------------------------------------------------
# データ操作用の関数
# ---------------------------------------------------------

# 1. 議題を保存する
def add_topic_to_sheet(title, author, options, deadline):
    sheet = connect_to_sheet()
    worksheet = sheet.worksheet("topics") # "topics"というシートを使う
    
    # 追加するデータ（リスト形式）
    # 日時はここで取得
    import datetime
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_row = [title, author, options, str(deadline), created_at]
    
    # 行を追加
    worksheet.append_row(new_row)

# 2. 議題を読み込む
def get_topics_from_sheet():
    try:
        sheet = connect_to_sheet()
        worksheet = sheet.worksheet("topics")
        
        # 全データを辞書形式で取得してDataFrameにする
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame() # エラーや空の場合は空のDataFrameを返す

# 3. 投票を保存する
def add_vote_to_sheet(topic_title, option):
    sheet = connect_to_sheet()
    worksheet = sheet.worksheet("votes") # "votes"というシートを使う
    
    import datetime
    voted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_row = [topic_title, option, voted_at]
    worksheet.append_row(new_row)

# 4. 投票数を集計する
def get_votes_from_sheet():
    try:
        sheet = connect_to_sheet()
        worksheet = sheet.worksheet("votes")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()