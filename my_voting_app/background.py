import base64
import streamlit as st
import os

def set_background(image_name):
    # このファイル（background.py）があるディレクトリを基準にする
    base_path = os.path.dirname(__file__)
    
    # imagesフォルダの画像を参照
    image_path = os.path.join(base_path, "images", image_name)

    # 画像が存在しない時のデバッグ表示（超重要）
    if not os.path.exists(image_path):
        st.error(f"背景画像が見つかりません: {image_path}")
        return

    # base64化して背景適用
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
