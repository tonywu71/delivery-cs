#!/usr/bin/env python
# coding: utf-8

# <center> <font size='6' font-weight='bold'> Nettoyage des données </font> </center>

# **Description :** Notebook servant au nettoyage des données.

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Import-des-données" data-toc-modified-id="Import-des-données-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Import des données</a></span><ul class="toc-item"><li><span><a href="#Informations-générales" data-toc-modified-id="Informations-générales-1.1"><span class="toc-item-num">1.1&nbsp;&nbsp;</span>Informations générales</a></span></li><li><span><a href="#Lecture-des-CSV" data-toc-modified-id="Lecture-des-CSV-1.2"><span class="toc-item-num">1.2&nbsp;&nbsp;</span>Lecture des CSV</a></span></li><li><span><a href="#Filtrage-par-noeud" data-toc-modified-id="Filtrage-par-noeud-1.3"><span class="toc-item-num">1.3&nbsp;&nbsp;</span>Filtrage par noeud</a></span></li></ul></li><li><span><a href="#Conversion-en-datetime" data-toc-modified-id="Conversion-en-datetime-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Conversion en datetime</a></span></li><li><span><a href="#Analyse-et-visualisation-(partie-1)" data-toc-modified-id="Analyse-et-visualisation-(partie-1)-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Analyse et visualisation (partie 1)</a></span></li><li><span><a href="#Feature-engineering" data-toc-modified-id="Feature-engineering-4"><span class="toc-item-num">4&nbsp;&nbsp;</span>Feature engineering</a></span><ul class="toc-item"><li><span><a href="#Categorical-variables" data-toc-modified-id="Categorical-variables-4.1"><span class="toc-item-num">4.1&nbsp;&nbsp;</span>Categorical variables</a></span></li><li><span><a href="#Features-liées-aux-timestamp" data-toc-modified-id="Features-liées-aux-timestamp-4.2"><span class="toc-item-num">4.2&nbsp;&nbsp;</span>Features liées aux timestamp</a></span></li><li><span><a href="#Périodes-de-vacances" data-toc-modified-id="Périodes-de-vacances-4.3"><span class="toc-item-num">4.3&nbsp;&nbsp;</span>Périodes de vacances</a></span></li><li><span><a href="#Confinement" data-toc-modified-id="Confinement-4.4"><span class="toc-item-num">4.4&nbsp;&nbsp;</span>Confinement</a></span></li><li><span><a href="#Couvre-feu" data-toc-modified-id="Couvre-feu-4.5"><span class="toc-item-num">4.5&nbsp;&nbsp;</span>Couvre-feu</a></span></li><li><span><a href="#Jours-fériés" data-toc-modified-id="Jours-fériés-4.6"><span class="toc-item-num">4.6&nbsp;&nbsp;</span>Jours fériés</a></span></li><li><span><a href="#Vacances-scolaires" data-toc-modified-id="Vacances-scolaires-4.7"><span class="toc-item-num">4.7&nbsp;&nbsp;</span>Vacances scolaires</a></span></li><li><span><a href="#Temps-avant-les-prochaines-grandes-vacances-scolaires" data-toc-modified-id="Temps-avant-les-prochaines-grandes-vacances-scolaires-4.8"><span class="toc-item-num">4.8&nbsp;&nbsp;</span>Temps avant les prochaines grandes vacances scolaires</a></span></li><li><span><a href="#Données-météorologiques" data-toc-modified-id="Données-météorologiques-4.9"><span class="toc-item-num">4.9&nbsp;&nbsp;</span>Données météorologiques</a></span></li><li><span><a href="#Moment-de-la-journée" data-toc-modified-id="Moment-de-la-journée-4.10"><span class="toc-item-num">4.10&nbsp;&nbsp;</span>Moment de la journée</a></span></li></ul></li><li><span><a href="#Analyse-et-visualisation-(partie-2)" data-toc-modified-id="Analyse-et-visualisation-(partie-2)-5"><span class="toc-item-num">5&nbsp;&nbsp;</span>Analyse et visualisation (partie 2)</a></span></li><li><span><a href="#Export-train-/-dev-/-test" data-toc-modified-id="Export-train-/-dev-/-test-6"><span class="toc-item-num">6&nbsp;&nbsp;</span>Export train / dev / test</a></span></li></ul></div>

# In[1]:


import os
import datetime

from functools import reduce

import numpy as np
import pandas as pd

# from matplotlib import pyplot as plt
# import seaborn as sns


def export_datasets(sep_date_str):
    """Exports train and test sets in ./data folder as a pickle file.
    Use pd.read_pickle to retrieve the data.

    Args:
        sep_date_str (string): String with default format for pd.Timestamp function
    """
    # Les données sont enregistrées dans 3 fichiers CSV différents. Elles portent le nom suivant :

    # In[2]:


    data_path = './data'


    # In[3]:


    # os.listdir(path=data_path)


    # In[4]:


    list_filenames = ['champs-elysees.csv', 'convention.csv', 'sts.csv']


    # # Import des données

    # ## Informations générales

    # **Les données  ont été téléchargées depuis :**  
    # - https://opendata.paris.fr/explore/dataset/comptages-routiers-permanents/information/?disjunctive.libelle&disjunctive.etat_trafic&disjunctive.libelle_nd_amont&disjunctive.libelle_nd_aval&sort=t_1h  
    #   
    # **Lien de la notice d'obtention des features :**  
    # - https://opendata.paris.fr/api/datasets/1.0/comptages-routiers-permanents/attachments/notice_donnes_trafic_capteurs_permanents_version_20190607_pdf/  
    #   
    # **Quelques infos issues du site sur le dataset:**  
    # >**Données de trafic routier issues des capteurs permanents sur 13 mois glissants en J-1**  
    # Sur le réseau parisien, la mesure du trafic s’effectue majoritairement par le biais de boucles électromagnétiques implantés dans la chaussée.  
    # La donnée est produite par la Direction de la Voirie et des déplacements - Service des Déplacements - Poste Central d'Exploitation Lutèce.  
    # La donnée et les visualisations associées (Tableau, Carte et Dataviz) sont brutes sans aucune interprétation ou analyse. Elles donnent à voir la donnée telle qu'elle est publiée quotidiennement. 
    # Elles donnent un aperçu du taux d'occupation et du débit sur plus de 3000 tronçons de voies. A elles seules, elles ne permettent pas de caractériser la complexité de la circulation à Paris.  
    # >  
    # **Deux types de données sont ainsi élaborés :**
    # le taux d’occupation, qui correspond au temps de présence de véhicules sur la boucle en pourcentage d’un intervalle de temps fixe (une heure pour les données fournies). Ainsi, 25% de taux d’occupation sur une heure signifie que des véhicules ont été présents sur la boucle pendant 15 minutes. Le taux fournit une information sur la congestion routière. L’implantation des boucles est pensée de manière à pouvoir déduire, d’une mesure ponctuelle, l’état du trafic sur un arc.
    # le débit est le nombre de véhicules ayant passé le point de comptage pendant un intervalle de temps fixe (une heure pour les données fournies).  
    # L'horodate horaire est effectué en fin de période d'élaboration. 
    # Par exemple, l’horodate « 2019-01-01 01:00:00 » désigne la période du 1er janvier 2019 à 00h00 au 1er janvier 2019 à 01h00.  
    # Ainsi, l’observation couplée en un point du taux d’occupation et du débit permet de caractériser le trafic. Cela constitue l’un des fondements de l’ingénierie du trafic, et l’on nomme d’ailleurs cela le « diagramme fondamental ».
    # Un débit peut correspondre à deux situations de trafic : fluide ou saturée, d’où la nécessité du taux d’occupation. A titre d’exemple : sur une heure, un débit de 100 véhicules par heure sur un axe habituellement très chargé peut se rencontrer de nuit (trafic fluide) ou bien en heure de pointe (trafic saturé).  
    # >  
    # **L’équipement du réseau parisien :**  
    # Les principaux axes de la Ville de Paris sont équipés de stations de comptage des véhicules et de mesure du taux d’occupation, à des fins à la fois de régulation du trafic et des transports en commun, d’information aux usagers (diffusion sur le site Sytadin), et d’étude.
    # Il existe deux types de stations sur le réseau : les stations de mesure du taux d’occupation seul, et des stations à la fois de mesure du taux et de comptage des véhicules.
    # Les stations de mesure du taux sont implantées très régulièrement : elles permettent une connaissance fine des conditions de circulation.
    # Les stations de débit sont moins nombreuses, et généralement implantées entre les principales intersections. En effet, le débit se conserve généralement sur une section entre deux grands carrefours.

    # ## Lecture des CSV

    # On regroupera toutes les lignes des 3 CSV dans un même DataFrame. Une colonne filename y a été ajoutée pour facilement avoir l'origine de la ligne à portée de main.  
    #   
    # Avant tout, nous allons imputer les NaN avec la méthode du *rolling mean*.

    # In[5]:


    window = 14 # modifier si besoin la taille de la fenêtre

    l_df = [pd.read_csv(
        os.path.join(data_path, filename), 
        sep=';', 
        index_col=0).assign(filename=filename) for filename in list_filenames]

    for idx, df in enumerate(l_df):
        df = df.sort_values("Date et heure de comptage")
        df['Débit horaire'] = df['Débit horaire'].interpolate()
        df["Taux d'occupation"] = df["Taux d'occupation"].interpolate()
        
        l_df[idx] = df


    # In[6]:


    df = pd.concat(l_df, ignore_index=True)

    # df.sample(5)


    # Vérification de la non-présence de NaN :

    # In[7]:


    # df.isna().sum()


    # ## Filtrage par noeud

    # On peut déjà drop les identifiants des noeuds et les données liées à la géométrie car ils ne nous serviront pas pour la suite.  
    # On supprimera aussi 

    # In[8]:


    df = df.drop(columns=[
        'Identifiant noeud amont', 'Identifiant noeud aval', 'geo_point_2d',
        'geo_shape', 'Date debut dispo data', 'Date fin dispo data'
    ])


    # In[9]:


    # Contient pour chaque fichier CSV un 2-tuple de la forme (noeud_amont, noeud_aval)
    dic_noeuds = {
        'champs-elysees.csv': ('Av_Champs_Elysees-Washington', 'Av_Champs_Elysees-Berri'),
        'convention.csv': ('Lecourbe-Convention', 'Convention-Blomet'),
        'Sts.csv': ('Sts_Peres-Voltaire', 'Sts_Peres-Universite')
    }


    # In[10]:


    list_criteria = []
    for key, val in dic_noeuds.items():
        criterion = (df['filename']==key) & (df['Libelle noeud amont']==val[0]) & (df['Libelle noeud aval']==val[1])
        list_criteria.append(criterion)

    criterion_noeuds = reduce(lambda x, y: x | y, list_criteria)

    # print(f'Taille du df avant filtrage: {len(df)}')
    df = df[criterion_noeuds]
    # print(f'Taille du df après filtrage: {len(df)}')


    # On peut désormais drop les libellés.

    # In[11]:


    df = df.drop(columns=['Libelle noeud amont', 'Libelle noeud aval'])
    df.head()


    # #  Conversion en datetime

    # In[12]:


    df.dtypes


    # In[13]:


    df['Date et heure de comptage']


    # ‼️ Il semble y avoir un soucis de timezone pour les capteurs... ‼️  
    #   
    # **Hypothèse:** On ca supposer que l'heure UTC est la bonne pour la suite.

    # In[14]:


    def remove_timezone(row):
        return row.tz_localize(None)


    # In[15]:


    df['Date et heure de comptage'] = pd.to_datetime(df['Date et heure de comptage'], utc=True)
    df['Date et heure de comptage'] = df['Date et heure de comptage'].apply(remove_timezone)
    # df['Date et heure de comptage']


    # On a pour l'instant l'heure UTC. Nous allons nous replacer à l'heure de Paris pour la suite, pour des questions pratiques.

    # In[16]:


    # df.dtypes


    # On rajoute 1 heure pour revenir à l'heure de Paris.

    # In[17]:


    df['Date et heure de comptage'] = df['Date et heure de comptage'] + pd.DateOffset(hours=1)
    # df['Date et heure de comptage']


    # In[18]:


    # date_begin = df['Date et heure de comptage'].min().strftime('%d/%m/%Y')
    # date_end = df['Date et heure de comptage'].max().strftime('%d/%m/%Y')
    # print(f'Première mesure de comptage prise : {date_begin}')
    # print(f'Dernière mesure de comptage prise : {date_end}')


    # # Analyse et visualisation (partie 1)

    # In[19]:


    # df[['Débit horaire', "Taux d'occupation"]].describe()


    # In[20]:


    # df[['Débit horaire', "Taux d'occupation"]].plot()


    # In[21]:


    # sns.violinplot(y='Débit horaire', data=df)


    # In[22]:


    # sns.violinplot(y="Taux d'occupation", data=df)


    # In[23]:


    # sns.displot(df, x="Taux d'occupation")


    # # Feature engineering

    # ## Categorical variables

    # Ajoutons un *one-hot encoding* pour les variables catégoriques. On n'oubliera cependant pas de passer à un *dummy encoding* avant d'entraîner le modèle pour éviter un problème de dimension. ‼️

    # In[24]:


    df.dtypes


    # **Ordinal encoding :**

    # Il semble en réalité plus pertinent d'utiliser un *ordinal encoding* pour donner une relation d'ordre à la feature. On se servira pour cela des informations contenues dans la notice.
    # <img src="ressources/ordinal_encoding.png" />

    # In[25]:


    df['Etat trafic']


    # In[26]:


    mapper = {'Inconnu': 0, 'Fluide': 1, 'Pré-saturé': 2, 'Saturé': 3, 'Bloqué': 4}
    df['Etat trafic'] = df['Etat trafic'].map(mapper)
    df.sample(5)


    # ## Features liées aux timestamp

    # Ajout du jour (sans l'heure) :

    # In[27]:


    df['Date'] = pd.to_datetime(df["Date et heure de comptage"]).dt.date
    # df.sample(5)


    # Ajout du jour de la semaine:

    # In[28]:


    df['Jour de la semaine'] = pd.to_datetime(df["Date et heure de comptage"]).dt.dayofweek
    # df.sample(5)


    # Reste maintenant à one-hot encoder cette variable.  
    # ‼️ On pensera à drop un des 7 jours pour éviter des problèmes d'overfitting ‼️

    # In[29]:


    df = pd.concat([
        df,
        pd.get_dummies(df['Jour de la semaine'],
                    prefix='Jour de la semaine',
                    drop_first=False)
    ], axis=1).drop(columns=['Jour de la semaine'])

    # df.head()


    # ## Périodes de vacances

    # ## Confinement

    # D'après Wikipedia:
    # >L'interdiction de déplacement en France, vulgarisée dans les médias par l'expression « confinement de la population » ou « confinement national », est une mesure sanitaire mise en place pour la première fois du 17 mars à 12 h au 11 mai 2020 (55 jours, soit 1 mois et 25 jours), et une deuxième fois à partir du 30 octobre 2020 au 15 décembre 2020 (soit 1 mois et 18 jours), s'insère dans un ensemble de politiques de restrictions de contacts humains et de déplacements en réponse à la pandémie de Covid-19 en France.

    # L'objectif est de donner une valeur qui traduit l'intensité du confinement.  
    #   
    # Nous allons donc créer une feature `Etat du confinement` qui traduira l'intensité de ce dernier. Elle prendra les valeurs suivantes :
    # - 0 -> période avant le 1er confinement
    # - 1 -> pas de confinement mais avec expérience du 1er confinement et mesures d'hygiènes renforcées
    # - 2 -> confinement assoupli (réouverture des commerces non-essentiels notamment)
    # - 3 -> confinement total.

    # In[30]:


    confinement_1 = pd.date_range(start='3/17/2020', end='5/11/2020')
    confinement_2 = pd.date_range(start='10/30/2020', end='11/28/2020')
    confinement_2_assoupli = pd.date_range(start='11/28/2020', end='12/15/2020')


    # In[31]:


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
    df.sample(5)


    # In[32]:


    df['Etat du confinement'].value_counts()


    # ## Couvre-feu

    # In[33]:


    couvre_feu_start = pd.Timestamp('10/17/2020')
    couvre_feu_start


    # In[34]:


    df['Couvre-feu'] = (couvre_feu_start <= df['Date'])
    df.sample(5)


    # ## Jours fériés

    # Le CSV a été obtenu via le lien suivant :  
    # - https://www.data.gouv.fr/en/datasets/jours-feries-en-france/

    # In[35]:


    df_feries = pd.read_csv('data/jours_feries_metropole.csv')
    # df_feries.head()


    # In[36]:


    # On ne garde que les lignes relatives à 2019 ou 2020
    df_feries = df_feries[df_feries['annee'].isin(['2019', '2020'])]
    # df_feries.sample(5)


    # In[37]:


    def get_date(row):
        return row.date()

    df_feries['date'] = pd.to_datetime(df_feries['date']).apply(get_date)
    series_feries = df_feries['date']


    # In[38]:


    df['Jour férié'] = df['Date'].isin(series_feries)
    # df['Jour férié'].value_counts()


    # In[39]:


    # df.head()


    # ## Vacances scolaires

    # Le CSV a été obtenu via le lien suivant :  
    # - https://www.data.gouv.fr/en/datasets/le-calendrier-scolaire/

    # In[40]:


    df_vacances = pd.read_csv('data/fr-en-calendrier-scolaire.csv', sep=';')
    df_vacances.head()


    # In[41]:


    df_vacances = df_vacances[df_vacances['location'] == 'Paris']
    # df_vacances.head()


    # In[42]:


    df_vacances = df_vacances[df_vacances['annee_scolaire'].isin(['2019-2020', '2020-2021'])]
    # df_vacances.head()


    # On observe un NaN... Affichons toute le DataFrame comme il n'y a que peu de lignes.

    # In[43]:


    # df_vacances


    # Le seul NaN ne correpond pas à une date comprise dans notre étude. On peut donc la drop sereinement.

    # In[44]:


    df_vacances = df_vacances[~ df_vacances['end_date'].isna()]
    # df_vacances


    # In[45]:


    # df_vacances.dtypes


    # In[46]:


    df_vacances['start_date'] = pd.to_datetime(df_vacances['start_date'])
    df_vacances['end_date'] = pd.to_datetime(df_vacances['end_date'])

    # df_vacances.dtypes


    # On peut maintenant ajouter notre colonne `Vacances scolaires` à notre DataFrame de départ.

    # In[47]:


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
    # df.sample(5)


    # ## Temps avant les prochaines grandes vacances scolaires

    # Déjà, créons un DataFrame avec uniquement les grandes vacances.

    # In[48]:


    df_grandes_vacances = df_vacances[df_vacances['description'].str.contains('Vacances')]
    df_grandes_vacances.head()


    # On trie maintenant ce DataFrame par ordre chronologique.

    # In[49]:


    df_grandes_vacances = df_grandes_vacances.sort_values(by=['start_date'])
    # df_grandes_vacances.head()


    # In[50]:


    # create a list of our conditions
    conditions = []

    # create a list of the values we want to assign for each condition
    values = []

    for idx, row in df_grandes_vacances.iterrows():
        conditions.append(df["Date et heure de comptage"] < row['start_date'])
        values.append(row['start_date'])

    df['Date des prochaines vacances scolaires'] = np.select(conditions, values)
    df['Date des prochaines vacances scolaires'] = df['Date des prochaines vacances scolaires']
    df.sample(5)


    # In[51]:


    df['Temps avant les prochaines vacances scolaires'] = df['Date des prochaines vacances scolaires'] - df['Date et heure de comptage']
    df.sample(5)


    # ## Données météorologiques

    # In[52]:


    df_weather = pd.read_pickle('data/combined_weather_data_from_2009_to_present.pkl')
    df_weather.head()


    # In[53]:


    df = df.merge(df_weather, left_on='Date et heure de comptage', right_on='datetime', how='left').drop(columns=['datetime'])
    # df.head()


    # Liste des colonnes à disposition :

    # In[54]:


    df.columns


    # ## Moment de la journée

    # In[55]:


    # create a list of our conditions
    criterion = (df['sunrise'] <= df["Date et heure de comptage"]) & (df["Date et heure de comptage"] < df['sunset'])

    # create a new column and use np.select to assign values to it using our lists as arguments
    df['Journée'] = criterion
    # df.sample(5)


    # # Analyse et visualisation (partie 2)

    # In[56]:


    # df.columns


    # In[57]:


    # corr = df.corr()
    # mask = np.zeros_like(corr)
    # mask[np.triu_indices_from(mask)] = True
    # with sns.axes_style("white"):
    #     plt.figure(figsize=(12,12))
    #     ax = sns.heatmap(corr, mask=mask, vmax=.3, square=True)


    # # Export train / dev / test

    # In[58]:


    sep_date = pd.Timestamp(sep_date_str)
    # sep_date


    # In[59]:


    df_train = df[df['Date et heure de comptage'] < sep_date]
    df_test = df[df['Date et heure de comptage'] >= sep_date]


    # In[60]:


    print(f'% train: {len(df_train) / len(df)}')
    print(f'% test: {len(df_test) / len(df)}')

    # In[61]:
    df_train.to_pickle('data/df_train.pkl')
    df_test.to_pickle('data/df_test.pkl')

    return