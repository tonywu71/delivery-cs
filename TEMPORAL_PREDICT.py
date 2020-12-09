import os
import re
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from pylab import rcParams
from datetime import datetime
from tqdm import tqdm
from sklearn.metrics import mean_squared_error
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning) # Permet d'éviter l'affichage des Warnings


df = pd.read_pickle("data/df_train.pkl")


df_ACE = df[df['filename']=='champs-elysees.csv']
df_Sts = df[df['filename']=='convention.csv']
df_convention = df[df['filename']=='sts.csv']

dfs = [df_ACE, df_Sts, df_convention]

# def clean_date(date):
#     date = re.sub('T', ' ', date)
#     date=date[:-6]
#     return date

#for df in (df_ACE, df_Sts, df_convention):
#    df['Date et heure de comptage'] = df['Date et heure de comptage'].apply(lambda s : clean_date(s))


# Format d'une série temporelle
#for df in dfs:
#    df['Date et heure de comptage']= pd.to_datetime(df["Date et heure de comptage"], format='%Y-%m-%d %H:%M:%S')

# Lignes rangées par ordre chronologique
for df in dfs:
    df.sort_values("Date et heure de comptage",inplace = True)
    
# Nous indiquons que la série temporelle est indexée selon la date
df_ACE = df_ACE.set_index('Date et heure de comptage')
df_convention = df_convention.set_index('Date et heure de comptage')
df_Sts = df_Sts.set_index('Date et heure de comptage')

def create_df(original_df):
    data = pd.DataFrame()
    data['debit'] = original_df['Débit horaire']
    data['taux'] = original_df["Taux d'occupation"]
    data['date'] = original_df.index
    data.sort_values("date",inplace = True)
    data = data.set_index('date')
    return data

def fill_with_AR(df, column):
    '''Fills missing values in column with rolling mean. Creates column "filled_debit" or "filled_taux"'''
    y = df[column].rolling(10, center=True, min_periods=1).mean()
    if column == 'debit':
        name = column
    else:
        name = 'taux'
    df['filled_'+ name] = y
    df['filled_'+ name].update(df[column])
    
    # Si plus de 10 NaN d'affilée, on remplit ce qui reste:
    df['filled_'+ name].fillna(method='ffill', inplace=True)


def create_and_fill(original_df):
    data = create_df(original_df)
    fill_with_AR(data, 'debit')
    fill_with_AR(data, 'taux')
    data = data.asfreq('H', method= 'ffill')
    return data

data = create_and_fill(df_Sts)
decomposition = sm.tsa.seasonal_decompose(data.filled_debit, model='additive')
fig = decomposition.plot()
plt.show()

# def string_to_model(model):
#     p = int(model[1])
#     q = int(model[4])
#     d = int(model[7])
#     seasonal = (int(model[10]), int(model[13]), int(model[16]), int(model[19:21]))
#     return p,q,d,seasonal

# def train_test_split(data):
#     '''Split train and test timeseries, training on period 1/08/2020 to 22/11/2020, testing from 22/11/2020 to 27/11/2020'''
#     # data = data.asfreq('H', method= 'ffill')
    
#     debit_train = data.loc['2020-08-01':'2020-11-22'].filled_debit
#     debit_test = data.loc['2020-11-22 23:00:00':'2020-11-27'].filled_debit
#     taux_train = data.loc['2020-08-01':'2020-11-22'].filled_taux
#     taux_test = data.loc['2020-11-22 23:00:00':'2020-11-27'].filled_taux
    
#     # Testing period delimitations
#     start = datetime.strptime('2020-11-22 23:00:00', '%Y-%m-%d %H:%M:%S')
#     end = datetime.strptime('2020-11-27 23:00:00', '%Y-%m-%d %H:%M:%S')
    
#     return debit_train, debit_test, taux_train, taux_test, start, end


# data = create_and_fill(df_ACE)

# mods = ['(1, 1, 4)(4, 1, 3, 24)', '(4, 1, 5)(4, 1, 4, 24)', '(5, 1, 2)(4, 1, 3, 24)']

# def setup_data_from_street(street_df):
#     data = create_and_fill(street_df)

#     debit_train, debit_test, taux_train, taux_test, start, end = train_test_split(data)

#     return data, debit_train, debit_test, taux_train, taux_test, start, end

# def fit_and_predict(model_params,X, start_pred, end_pred):
#     p,d,q,seasonal = string_to_model(model_params)
#     mod = sm.tsa.statespace.SARIMAX(X,order=(p,d,q),seasonal_order=seasonal,enforce_stationarity=False,enforce_invertibility=False)
#     results = mod.fit()
#     prediction = results.predict(start=start_pred, end=end_pred)

#     return prediction

# data, debit_train, debit_test, taux_train, taux_test, start, end = setup_data_from_street(df_Sts)

# prediction = fit_and_predict('(1, 1, 4)(4, 1, 3, 24)',debit_train.loc['2020-11-10':'2020-11-22'], start, end)

# plt.plot(prediction)
# plt.show()