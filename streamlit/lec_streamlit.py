import streamlit as st
import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import pydeck as pdk
import time

from PIL import Image 

# df = pd.DataFrame({
#     '段位': ["四段", "四段", "四段", "四段", "二段", "初段", "二段"],
#     '名前': ["miya", "ななみん", "cocoro", "4593", "ゆっきーぢ", "ろっころ", "ははるく"]

# })

option_button = st.button('生成')

if option_button:
    st.write('生成されました')
else:
    st.write('生成をクリックして表示')


option_radio = st.radio(
    "好きな戦法を選択してください",
    ('四間飛車', '中飛車','居飛車')
)

st.write(f"あなたの好きな戦法は{option_radio}です")

option_check = st.checkbox('将棋を指したことがあります')

df = pd.DataFrame({
    '段位': ["四段", "四段", "四段", "四段", "二段", "初段", "二段"],
    '名前': ["miya", "ななみん", "cocoro", "4593", "ゆっきーぢ", "ろっころ", "ははるく"]
})

if option_check:
    st.write('以下は将棋プレイヤーのデータです')
    st.write(df)


option_multi = st.multiselect(
    '好きな戦法を選んでください',
    ['ノーマル四間飛車', '藤井システム', '四間飛車穴熊', 'ゴキゲン中飛車'],
    ['ノーマル四間飛車']
)
st.write(f"あなたの好きな戦法は{option_multi}です")


# time = st.slider('持ち時間を設定してください', min_value=1, max_value=60, step=1, value=10)
# st.write(f"持ち時間{time}分")


mtime = st.sidebar.slider('持ち時間を設定してください', min_value=1, max_value=60, step=1, value=10)
st.write(f"持ち時間{mtime}分")

stime = st.sidebar.slider('秒読み時間を設定してください', min_value=1, max_value=60, step=1, value=30)
st.write(f"秒読み時間{stime}秒")

progress_button = st.button('解析開始')
if progress_button:
    st.write('解析中...')
    bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        bar.progress(percent_complete + 1)
    st.write('解析完了！')
else:
    st.write('解析開始をクリック')
