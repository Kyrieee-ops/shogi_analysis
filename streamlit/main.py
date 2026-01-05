import pandas as pd
import streamlit as st

# --- 共通ユーティリティ: 勝敗メトリクス計算と表示 ---
def compute_metrics(df, result_col='勝敗'):
    if df is None or df.empty:
        return 0, 0, 0, 0.0
    if result_col in df.columns:
        win = len(df[df[result_col] == "勝ち"])
        lose = len(df[df[result_col] == "負け"])
    else:
        win, lose = 0, 0
    total = win + lose
    if total > 0:
        win_rate = win / total * 100
    else:
        win_rate = 0.0
    return win, lose, total, win_rate

def show_metrics(win, lose, total, win_rate):
    c1, c2, c3 = st.columns(3)
    c1.metric("対局数", f"{total} 局")
    c2.metric("勝率", f"{win_rate:.1f} %")
    c3.metric("勝ち/負け", f"{win}勝 / {lose}敗")

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

    # --- 直近N局を選択するコントロール ---
    recent_options = [10, 20, 30, 40, 50]
    recent_n = st.sidebar.select_slider("直近何局を表示", options=recent_options, value=10)


    # 4. データ抽出 (フィルタリング)
    filterd_df = df[
        (df["先後"].isin(selected_turn)) &
        (df["対象の戦法"].isin(selected_style)) &
        (df["持ち時間"].isin(selected_time)) 
    ]


    # --- 1. 基本統計の表示 ---
    st.subheader("対局サマリー")
    
    if not filterd_df.empty:
        win_count, lose_count, total, win_rate = compute_metrics(filterd_df)
        show_metrics(win_count, lose_count, total, win_rate)

        st.divider() # 区切り線

        # --- 2. フィルタリングされたデータテーブル ---
        st.subheader("対局履歴")
        st.dataframe(filterd_df)

        # --- 直近N局の成績表示 ---
        st.subheader(f"直近{recent_n}局の成績")

        # recent_n局を抽出する。日付列があればそれでソートして最新順を取得。
        if not filterd_df.empty:
            date_col = None

            # 優先する単一の列名を使う（ユーザー指定）
            preferred_name = "対局日時"
            found = None
            if preferred_name and preferred_name in filterd_df.columns:
                found = preferred_name
                try:
                    parsed = pd.to_datetime(filterd_df[found], errors='coerce')
                    if not parsed.isna().all():
                        date_col = found
                        filterd_df = filterd_df.assign(_parsed_date=parsed)
                    else:
                        # パースできなければ found をリセットしてフォールバックへ
                        found = None
                except Exception:
                    found = None


            if date_col:
                recent_df = filterd_df.sort_values('_parsed_date', ascending=False).head(recent_n)
            else:
                # 日付列が見つからない場合は、データフレームの先頭を最新と仮定して取得
                recent_df = filterd_df.head(recent_n)

            # 直近N局の簡易統計（共通関数を利用）
            rec_win, rec_lose, rec_total, rec_win_rate = compute_metrics(recent_df)
            show_metrics(rec_win, rec_lose, rec_total, rec_win_rate)

            st.dataframe(recent_df)
        else:
            st.info("選択された条件に該当するデータがないため、直近の対局は表示できません。")

    # --- 3. 戦型別の勝率（集計テーブル） ---
    st.subheader("戦型別の詳細成績")
    if not filterd_df.empty:
        # 対象と勝敗でクロス集計
        # groupby(['対象の戦法', '勝敗'])で対象の戦法と勝敗を2つセットにして、データをグループ分けする
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
    """
    将棋ウォーズの対局データを分析するためのアプリケーションです。

    将棋ウォーズ棋譜検索サイトから対局履歴をエクスポート

    → https://www.shogi-extend.com/swars/search
    """
    # ファイルがアップロードされていない時の表示
    st.info("← サイドバーからCSVファイルをアップロードしてください。")
