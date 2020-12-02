# Notes de réunion Datathlon

- [ ] Présentation rapide des membres
- [ ] Relire le document avec le groupe
- [ ] Regarder ensemble les 3 lieux sur Google Maps
- [ ] Bien insister sur le calendrier
  - [ ] Bien se fixer une répartition d'équipe / temporelle pour ne pas oublier le 2ème livrable !
- [ ] Evoquer direct l'aspect technique avec Git, conda / venv et les notebook + langue + tasks
- [ ] Brainstorm



- Evoquer la date particulière (11 au 16 décembre)
- Quelles autres données utiliser ?
- Chercher les accidents ?
- Feature engineering
  - Ajouter le deltaTime par rapport à la prochaine date des vacances qui arrive
  - 



Présentation rapide des compétences du groupe :

- Tony :
  - Data Analyst
  - Pandas ++
  - Data Visualisation (Seaborn +)
  - Un peu de tout ce qui est ML / DataScience en général
- Soukaina :
  - Apprentissage non-supervisé
  - Réduction de dimension
  - Apprentissage supervisé
  - Régression linéaire
  -  Compétence sur les vidéos
- Timothé :
  - Data à PSA
    - LSTM (la pratique)
    - Apprentissage par renforcement
    - Prédiction de séries temporelles avec réseau convolutif
  - API de Google Maps
  - Slides de présentation
- Carlos :
  - Apprentissage par renforcement
  - EI → Statistiques en finance
    - ARIMA ++
  - Projet de Computer Vision cette année
  - Test d'hypothèses statistique
- Matthias :
  - Scikit-learn
  - Quelques compétitions Kaggle
  - Hopia avec Julien
    - ML surtout
    - Aspect organisationnel
  - EI BigData & Santé
  - Slides de présentation
- Julien :
  - Hopia
  - Reconnaissance d'image
  - TimeSeries
  - Kaggle (NLP)
    - Traffic de page web sur Wikipédia



Récupération des données :

- Il semble que ça ne sert à rien de filtrer les noeuds dans le code.
- On va le faire quand même au cas où.
  - Est-ce que c'est bien de le faire le jour J ? (déso pas sûr d'avoir compris 😅 )
- [ ] Il faut clean les données et les mettre sur le drive.



Combien de modèles pour les 3 rues ?

- Peut-être que c'est une bonne idée de regarder les caractéristiques des rues ?

  - Nombre de voies, parkings...

- Idée de Soukaina :

  - One-hot encoding
  - C'est même recommandé (par Hopia) de tout concaténer.
  - Peut-être pas besoin de chercher les caractéristiques comme le modèle va apprendre par lui-même la caractéristique de celle-ci !
  - Google Maps → simuler le temps de trajet
    - C'est pas mal pour le livrable 2 !
    - Timothé pensait même l'utiliser comme feature.
    - Julien demande en quoi c'est informatif ?
    - Soukaina pense que c'est en effet pas très apprécié.
      - Evoquer si c'est possible ou pas pour le client.
    - Tim dit que les données seront toujours disponibles et que ça vaut la peine.

  

Question des sources externes

- On a le droit de se servir des données externes.
- Cf le mail (ou Slack) pour avoir une idée



Question des données :

- Delta avec le 1er jour des vacances → intéressant
- [Insérer les boxplots de Julien]
- Tim propose d'utiliser toutes les données précédentes
  - On pourrait ajouter une colonne (mon idée) 'Pré-confinement', 'Confinement', 'Post-confinement'
  - Pas trop compris l'idée du NLP
  - Aussi on peut mettre genre le niveau de mesures sanitaires
  - Voire aussi le degré de gravité de la situation ?



Calendrier :

- On peut commencer le livrable 2 vers le weekend.
- Case Team Meeting → when2meet à faire



Demander une confirmation pour la vidéo.



Répartition des tâches :

- Pour les sets:
  - Préparer train, dev et test set communs
  - Mettre sur le OneDrive testset, trainset
- Mettre les utilitaires :
  - dans un utils.py
- Penser à donner le nombre d'epochs, tracer des learning curves
- Commenter bien le code et les notebooks



- Timothé :
  - Réseaux de convolution
- Julien :
  - LSTM
  - Arima
- Soukaina :
  - Ensemble learning
    - Random forest
  - Régression linéaire
- Carlos :
  - ARIMA

