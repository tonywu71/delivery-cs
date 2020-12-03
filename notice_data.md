# Notice pour les features considérées

[TOC]

# Description des colonnes

- Libelle : Nom de la rue
- Date et heure de comptage : `Timestamp` avec jour et heure
- Débit horaire : Nombre de véhicules ayant passé le point de comptage pendant un intervalle de temps fixe (une heure pour les données fournies)
- Taux d'occupation : Temps de présence de véhicules sur la boucle en pourcentage d’un intervalle de temps fixe (une heure pour les données fournies). Ainsi, 25% de taux d’occupation sur une heure signifie que des véhicules ont été présents sur la boucle pendant 15 minutes. Le taux fournit une information sur la congestion routière. L’implantation des boucles est pensée de manière à pouvoir déduire, d’une mesure ponctuelle, l’état du trafic sur un arc.
- Etat trafic :  Entier entre 0 et 4, selon la correspondance suivante :
  - 0 → Inconnu
  - 1 → Fluide
  - 2 → Pré-saturé
  - 3 → Saturé
  - 4 → Bloqué
- Etat arc : ❓ 
- filename : Nom du fichier ayant servi à récupérer la ligne
- Date : `datetime.date` avec le jour uniquement
- Jour de la semaine : Entier entre 0 et 6 (0 pour lundi et 6 pour dimanche)
- Etat du confinement : 
  - 0 → période avant le 1er confinement
  - 1 → pas de confinement mais avec expérience du 1er confinement et mesures d'hygiènes renforcées
  - 2 → confinement assoupli (réouverture des commerces non-essentiels notamment)
  - 3 → confinement total
- Couvre-feu : Booléen avec True si pendant le couvre-feu.
- Jour férié : Booléen avec True s'il s'agit d'un jour férié.
- Vacances scolaires : Booléen avec True si pendant les vacances scolaires
- Date des prochaines vacances scolaires : `Timestamp` avec jour et heure du début des prochaines vacances scolaires
- Temps avant les prochaines vacances scolaires : `Timedelta` donnant le nombre de jours restants avant les prochaines vacances scolaires.



# Sources

- Comptages routiers :
  - https://opendata.paris.fr/explore/dataset/comptages-routiers-permanents/information/?disjunctive.libelle&disjunctive.etat_trafic&disjunctive.libelle_nd_amont&disjunctive.libelle_nd_aval&sort=t_1h

- Jours fériés :
  - https://www.data.gouv.fr/en/datasets/jours-feries-en-france/
- Vacances scolaires :
  - https://www.data.gouv.fr/en/datasets/le-calendrier-scolaire/
- Données météo :
  - https://www.worldweatheronline.com/developer/api/docs/historical-weather-api.aspx