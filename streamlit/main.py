import pandas as pd
import streamlit as st

st.sidebar.header("将棋ウォーズ 分析フィルター")

# 1. ファイルアップローダーをサイドバーに配置
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

# --- ファイルがアップロードされた場合のみ実行 ---
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.sidebar.header("分析フィルター")

    # 2. フィルタの初期選択肢を作成（空だとエラーになるため）
    # 何も選ばれていない時は全選択状態にするための準備
    all_turns = df["先後"].unique()
    all_styles = df["対象の戦法"].unique()
    all_times = df["持ち時間"].unique()

    # 3. サイドバーでフィルタリング
    selected_turn = st.sidebar.multiselect(
        "手番を選択", 
        options=all_turns, default=all_turns
    )
    selected_style = st.sidebar.multiselect(
        "戦法を選択", 
        options=all_styles, default=all_styles
    )
    selected_time = st.sidebar.multiselect(
        "持ち時間を選択",
        options=all_times, default=all_times
    )
    # 4. データ抽出 (フィルタリング)
    filterd_df = df[
        (df["先後"].isin(selected_turn)) &
        (df["対象の戦法"].isin(selected_style)) &
        (df["持ち時間"].isin(selected_time))
    ]


    # --- 1. 基本統計の表示 ---
    st.subheader("対局サマリー")
    if not filterd_df.empty:
        win_count = len(filterd_df[filterd_df["勝敗"] == "勝ち"])
        lose_count = len(filterd_df[filterd_df["勝敗"] == "負け"])
        total = win_count + lose_count

        if total > 0:
            # totalが0より大きい（データがある）場合
            win_rate = (win_count / total) * 100
        else:
            # totalが0以下（データが0件）の場合
            win_rate = 0

        # カラムを3分割してメトリクス表示
        # col1: 左側の枠, col2: 中央の枠, col3: 右側の枠
        col1, col2, col3 = st.columns(3)
        col1.metric("対局数", f"{total} 局")
        col2.metric("勝率", f"{win_rate:.1f} %")
        col3.metric("勝ち/負け", f"{win_count}勝 / {lose_count}敗")

        st.divider() # 区切り線

        # --- 2. フィルタリングされたデータテーブル ---
        st.subheader("対局履歴")
        st.dataframe(filterd_df)

    # --- 3. 戦型別の勝率（集計テーブル） ---
    st.subheader("戦型別の詳細成績")
    if not filterd_df.empty:
        # 対象と勝敗でクロス集計
        # groupby(['対象の戦法', '勝敗'])で対象の戦法と紹介を2つノセットにして、データをグループ分けする
        # .size()で各グループが何行あるかを数える(四間飛車で勝ったのは3回、負けたのは1回といった算出)
        # .unstack()で縦に並んでいるデータを横に広げる処理
        summary = filterd_df.groupby(['対象の戦法', '勝敗']).size().unstack(fill_value=0)
        
        # 「勝ち」や「負け」の列が存在しない場合の補完
        if "勝ち" not in summary.columns: summary["勝ち"] = 0
        if "負け" not in summary.columns: summary["負け"] = 0
        
        # 勝率の計算
        summary['合計'] = summary['勝ち'] + summary['負け']
        summary['勝率'] = (summary['勝ち'] / summary['合計'] * 100).round(1).astype(str) + '%'
        
        st.table(summary[['勝ち', '負け', '合計', '勝率']])
    else:
        st.warning("選択された条件に該当するデータがありません。フィルターを調整してください。")
else:
    # ファイルがアップロードされていない時の表示
    st.info("← サイドバーからCSVファイルをアップロードしてください。")
    # st.image("via.placeholder.com") # イメージ画像など