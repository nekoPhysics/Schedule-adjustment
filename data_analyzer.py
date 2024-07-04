import pandas as pd
import numpy as np


n = 5
# import csv
df = pd.read_csv('gashuku_data.csv')


def calc_points(df):
    # df[適用対象] = df[検出対象列].apply(関数)(apply内を繰り返す)
    # lambda 検出対象値: 実行したい計算(もしくは結果) if...
    df['points'] = df['car'].apply(lambda x: 1.5 if x == 'はい' else 1)

    # Pref_dateを個別の日付に分割
    dates_points = df.apply(lambda row: pd.Series(row['Pref_date'].split(', ')), axis=1).stack().reset_index(level=1, drop=True).to_frame('Pref_date')
    dates_points['points'] = np.repeat(df['points'].values, dates_points.groupby(level=0).size().values)

    # df.groupby(集計カテゴリ)[スコア]
    return dates_points


def return_most_voted(points_date, n):
    max_points = 0
    best_start_date = None
    points_date['Pref_date'] = points_date['Pref_date'].str.replace(',', '').str.strip()
    points_date['Pref_date'] = pd.to_datetime(points_date['Pref_date'], format='%m/%d')

    points_date = points_date.sort_values('Pref_date').reset_index(drop=True)

    for i in range(len(points_date) - n + 1):
        current_dates = points_date.iloc[i:i + n]
        current_points = current_dates['points'].sum()

        if current_points > max_points:
            max_points = current_points
            best_start_date = current_dates.iloc[0]['Pref_date']

    best_dates = points_date[(points_date['Pref_date'] >= best_start_date) & (points_date['Pref_date'] <= best_start_date + pd.Timedelta(days=n-1))]
    return best_dates


def sum_votes_per_date(df):
    df['points'] = df['car'].apply(lambda x: 1.5 if x == 'はい' else 1)
    dates_points = df.apply(lambda row: pd.Series(row['Pref_date'].split(', ')), axis=1).stack().reset_index(level=1, drop=True).to_frame('Pref_date')
    dates_points['Pref_date'] = pd.to_datetime(dates_points['Pref_date'], format='%m/%d')
    dates_points['points'] = np.repeat(df['points'].values, dates_points.groupby(level=0).size().values)
    sum_votes = dates_points.groupby('Pref_date')['points'].sum().reset_index()
    sum_votes = sum_votes.sort_values(by='points', ascending=False).reset_index(drop=True)
    return sum_votes


def main(df, n):
    points_date = calc_points(df)
    best_dates = return_most_voted(points_date, n)
    sum_votes = sum_votes_per_date(df)

    print(f'投票が多かった連続した{n}日間の日程')
    grouped = best_dates.groupby('Pref_date')['points'].sum()
    for date, points in grouped.items():
        print(f"{date.strftime('%m/%d')}, 投票数: {points}")

    print("\n日付ごとの投票数の合計 (合計投票数が多い順):")
    for index, row in sum_votes.iterrows():
        print(f"日付: {row['Pref_date'].strftime('%m/%d')}, 合計投票数: {row['points']}")


main(df,n)