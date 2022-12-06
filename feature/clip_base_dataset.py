import pandas as pd
import numpy as np
import datetime

def make_dataset(all_input_list, all_target_list):
    '''
    Train, Test데이터를 하나의 데이터 프레임으로 변경
    '''
    df_all = pd.DataFrame()
    df_all2 = pd.DataFrame()
    length = len(all_input_list)
    for idx in range(length):
        X = pd.read_csv(all_input_list[idx])
        y = pd.read_csv(all_target_list[idx])
        q5 = X.quantile(0.01)
        q95 = X.quantile(0.99)
        X1 = X.clip(q5, q95, axis=1)
        y['DAT'] = y['DAT']-1
        df_concat = pd.merge(X1, y, on='DAT', how='left')
        df_concat2 = pd.merge(X, y, on='DAT', how='left')
        df_concat['Case'] = idx+1
        df_all = pd.concat([df_all, df_concat])
        df_all2 = pd.concat([df_all2, df_concat2])
    return df_all, df_all2


def time_value(df):
    ''' 
    ex) 00:59:59 => 01:00:00으로 변환 후 시간단위만 추출
    '''
    df['obs_time'] = pd.to_datetime(df["obs_time"]) + datetime.timedelta(seconds=1)
    df['obs_time'] = df['obs_time'].dt.hour
    return df

def limit_range(df):
    '''
    환경 변수 별 제한 범위를 넘어서는 값을 결측치 처리
    '''
    df.loc[(df['내부온도관측치'] < 4) | (df['내부온도관측치'] > 40), '내부온도관측치'] = np.nan
    df.loc[(df['내부습도관측치'] < 0) | (df['내부습도관측치'] > 100), '내부습도관측치'] = np.nan
    df.loc[(df['co2관측치'] < 0) | (df['co2관측치'] > 1200), 'co2관측치'] = np.nan
    df.loc[(df['ec관측치'] < 0) | (df['ec관측치'] > 8), 'ec관측치'] = np.nan
    df.loc[(df['시간당분무량'] < 0) | (df['시간당분무량'] > 3000), '시간당분무량'] = np.nan
    df.loc[(df['일간누적분무량'] < 0) | (df['일간누적분무량'] > 72000), '일간누적분무량'] = np.nan
    df.loc[(df['시간당백색광량'] < 0) | (df['시간당백색광량'] > 120000), '시간당백색광량'] = np.nan
    df.loc[(df['일간누적백색광량'] < 0) | (df['일간누적백색광량'] > 2880000), '일간누적백색광량'] = np.nan
    df.loc[(df['시간당적색광량'] < 0) | (df['시간당적색광량'] > 120000), '시간당적색광량'] = np.nan
    df.loc[(df['일간누적적색광량'] < 0) | (df['일간누적적색광량'] > 2880000), '일간누적적색광량'] = np.nan
    df.loc[(df['시간당청색광량'] < 0) | (df['시간당청색광량'] > 120000), '시간당청색광량'] = np.nan
    df.loc[(df['일간누적청색광량'] < 0) | (df['일간누적청색광량'] > 2880000), '일간누적청색광량'] = np.nan
    df.loc[(df['시간당총광량'] < 0) | (df['시간당총광량'] > 120000), '시간당총광량'] = np.nan
    df.loc[(df['일간누적총광량'] < 0) | (df['일간누적총광량'] > 2880000), '일간누적총광량'] = np.nan
    return df

def col_cumsum(df, col, cum_col):
    '''
    시간값에 이상치가 있어서 누적값을 새로 생성(train)
    '''
    import itertools
    df[cum_col] = 0
    for i in range(784):
        result = itertools.accumulate(df[col][i*24:(i+1)*24])
        cumsum = [value for value in result]
        df[cum_col][i*24:(i+1)*24] = cumsum
        
    return df


def col_cumsum_test(df, col, cum_col):
    '''
    시간값에 이상치가 있어서 누적값을 새로 생성(test)
    '''
    import itertools
    df[cum_col] = 0
    for i in range(140):
        result = itertools.accumulate(df[col][i*24:(i+1)*24])
        cumsum = [value for value in result]
        df[cum_col][i*24:(i+1)*24] = cumsum
        
    return df


def time_split(df):
    '''
    6시간 단위로 시간분할(pivot_data function 사전작업)
    '''
    df.loc[(df['obs_time'] < 6), '6time'] = 1
    df.loc[(df['obs_time'] >=6) & (df['obs_time'] < 12), '6time'] = 2
    df.loc[(df['obs_time'] >= 12) & (df['obs_time'] < 19), '6time'] = 3
    df.loc[(df['obs_time'] >= 19) & (df['obs_time'] <= 24), '6time'] = 4
    
    return df


def pivot_data(df):
    '''
    6시간 단위의 pivot table 생성
    '''
    df = df.drop(['predicted_weight_g', 'obs_time', '내부온도관측치', '내부습도관측치', 'co2관측치', 'ec관측치',
                  '시간당분무량', '시간당백색광량', '시간당적색광량', '시간당청색광량', '시간당총광량',], axis=1)
    df = pd.pivot_table(df, index=['DAT', 'Case'], columns=['6time'], aggfunc='sum')
    df.columns = [''.join(str(col)) for col in df.columns]
    df = df.reset_index()
    df = df.drop(['DAT', 'Case'], axis=1)
    return df