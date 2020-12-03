import os
import datetime

from functools import reduce

import numpy as np
import pandas as pd

# PAS FINI !!!!!

def pipeline(percentage_train = 0.8, percentage_dev = 0.1, percentage_test = 0.1):
    """Run this function to generate the train / dev / test datasets in
    the ./data folder.

    Args:
        percentage_train (float, optional). Defaults to 0.8.
        percentage_dev (float, optional). Defaults to 0.1.
        percentage_test (float, optional). Defaults to 0.1.
    """

    data_path = './data'
    list_filenames = ['champs-elysees.csv', 'convention.csv', 'Sts.csv']

    df = pd.concat(
        [pd.read_csv(os.path.join(data_path, filename), sep=';', index_col=0).assign(filename=filename) for filename in list_filenames],
                ignore_index=True
    )

    df = df.drop(columns=[
        'Identifiant noeud amont', 'Identifiant noeud aval', 'geo_point_2d',
        'geo_shape', 'Date debut dispo data', 'Date fin dispo data'
    ])

    # Contient pour chaque fichier CSV un 2-tuple de la forme (noeud_amont, noeud_aval)
    dic_noeuds = {
        'champs-elysees.csv': ('Av_Champs_Elysees-Washington', 'Av_Champs_Elysees-Berri'),
        'convention.csv': ('Lecourbe-Convention', 'Convention-Blomet'),
        'Sts.csv': ('Sts_Peres-Voltaire', 'Sts_Peres-Universite')
    }


    list_criteria = []
    for key, val in dic_noeuds.items():
        criterion = (df['filename']==key) & (df['Libelle noeud amont']==val[0]) & (df['Libelle noeud aval']==val[1])
        list_criteria.append(criterion)

    criterion_noeuds = reduce(lambda x, y: x | y, list_criteria)

    ## Filtrage :
    df = df[criterion_noeuds]

    df = df.drop(columns=['Libelle noeud amont', 'Libelle noeud aval'])

    ## Nettoyage des NaN :
    df = df.dropna()

    ## Gestion des TimeStamp / DateTime
    def remove_timezone(row):
        return row.tz_localize(None)

    df['Date et heure de comptage'] = pd.to_datetime(df['Date et heure de comptage'], utc=True)
    df['Date et heure de comptage'] = df['Date et heure de comptage'].apply(remove_timezone)

    df['Date et heure de comptage'] = df['Date et heure de comptage'] + pd.DateOffset(hours=1)

    ## Gestion des variables catégoriques :
    mapper = {'Inconnu': 0, 'Fluide': 1, 'Pré-saturé': 2, 'Saturé': 3, 'Bloqué': 4}
    df['Etat trafic'] = df['Etat trafic'].map(mapper)
    
    ## Périodes de vacances :
    #FIXME: Prendre toutes les vacances en compte

    ## Ajout du jour (sans l'heure) :
    df['Date'] = pd.to_datetime(df["Date et heure de comptage"]).dt.date

    ## Ajout du jour de la semaine :
    df['Jour de la semaine'] = pd.to_datetime(df["Date et heure de comptage"]).dt.dayofweek

    ## Confinement :
    confinement_1 = pd.date_range(start='3/17/2020', end='5/11/2020')
    confinement_2 = pd.date_range(start='10/30/2020', end='11/28/2020')
    confinement_2_assoupli = pd.date_range(start='11/28/2020', end='12/15/2020')
    
    # create a list of our conditions
    conditions = [
        (df["Date et heure de comptage"] < confinement_1[0]), # 0
        (confinement_1[0] <= df["Date et heure de comptage"]) & (df["Date et heure de comptage"] < confinement_1[-1]), # 3
        (confinement_1[-1] <= df["Date et heure de comptage"]) & (df["Date et heure de comptage"] < confinement_2[0]), # 1
        (confinement_2[0] <= df["Date et heure de comptage"]) & (df["Date et heure de comptage"] < confinement_2[-1]), # 3
        (confinement_2_assoupli[0] <= df["Date et heure de comptage"]) & (df["Date et heure de comptage"] < confinement_2_assoupli[-1]), # 2
        (confinement_2_assoupli[-1] <= df["Date et heure de comptage"]) # 1
        ]

    # create a list of the values we want to assign for each condition
    values = [0, 3, 1, 3, 2, 1]

    # create a new column and use np.select to assign values to it using our lists as arguments
    df['Etat du confinement'] = np.select(conditions, values)

    ## Couvre-feu :
    couvre_feu_start = pd.Timestamp('10/17/2020')
    df['Couvre-feu'] = (couvre_feu_start <= df['Date'])

    ## Jours fériés :
    df_feries = pd.read_csv('data/jours_feries_metropole.csv')

    # On ne garde que les lignes relatives à 2019 ou 2020
    df_feries = df_feries[df_feries['annee'].isin(['2019', '2020'])]

    def get_date(row):
        return row.date()

    df_feries['date'] = pd.to_datetime(df_feries['date']).apply(get_date)
    series_feries = df_feries['date']
    df['Jour férié'] = df['Date'].isin(series_feries)

    ## Vacances scolaires :
    df_vacances = pd.read_csv('data/fr-en-calendrier-scolaire.csv', sep=';')

    df_vacances = df_vacances[df_vacances['location'] == 'Paris']
    df_vacances = df_vacances[df_vacances['annee_scolaire'].isin(['2019-2020', '2020-2021'])]
    df_vacances = df_vacances[~ df_vacances['end_date'].isna()]
    df_vacances['start_date'] = pd.to_datetime(df_vacances['start_date'])
    df_vacances['end_date'] = pd.to_datetime(df_vacances['end_date'])

    def est_pendant_vacances(date):    
        for index, row_vacances in df_vacances.iterrows():
            start = row_vacances['start_date']
            end = row_vacances['end_date']
            
            if start < date < end:
                return True
            else:
                pass
        
        return False

    df['Vacances scolaires'] = df['Date'].apply(est_pendant_vacances)

    df_sunrise = pd.read_csv('data/sunrise.csv', skiprows=2)

    def get_datasets(df, percentage_train, percentage_dev, percentage_test, seed=None):
        assert(percentage_train + percentage_dev + percentage_test == 1.), 'Please correct the input values.'
        df_train, df_dev, df_test = np.split(
            df.sample(frac=1, random_state=seed),
            [int(percentage_train*len(df)), int((percentage_train+percentage_dev)*len(df))]
        )
        return df_train, df_dev, df_test

    

    df_train, df_dev, df_test = get_datasets(df, percentage_train, percentage_dev, percentage_test, seed=0)

    print(f'% train: {len(df_train) / len(df)}')
    print(f'% dev: {len(df_dev) / len(df)}')
    print(f'% test: {len(df_test) / len(df)}')

    for df_export, df_filename in zip([df_train, df_dev, df_test], ['df_train.csv', 'df_dev.csv', 'df_test.csv']):
        filepath = os.path.join('data', df_filename)
        df_export.to_csv(filepath)

    return