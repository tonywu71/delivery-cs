




import ortools
from ortools.sat.python import cp_model
import numpy as np
import pandas as pd
import os
import re
from constraints import *
import xlwt
from xlwt import Workbook

def clean_date(date):
    date = re.sub('T', ' ', date)
    date = date[:-6]
    return date

def solve_shift_scheduling(livreurs, Creneaux, num_weeks, zones, max_shift_per_day, min_shift_per_day, contrainte_tp, daily_cover_demands,occ_rues, waiting_time,shift_hours):
    num_employees = len(livreurs.keys())
    num_shifts = len(Creneaux)
    num_days = num_weeks * 7

    model = cp_model.CpModel()
    work = {}

    for e in range (num_employees):
        for s in range (num_shifts):
            for d in range (num_days):
                for zone in zones:
                    work[e, s, d, zone] = model.NewBoolVar('work%i_%i_%i_%r' % (e, s, d, zone))
    work_wt = {}
    for e in range(num_employees):
        for d in range(num_days):
            for s in range(num_shifts):
                work_wt[e, s, d] = model.NewBoolVar('work_wt%i_%i_%i' % (e, s, d))
                model.Add(sum(work[e, s, d, zone] for zone in zones) == 1).OnlyEnforceIf(work_wt[e, s, d])
                model.Add(sum(work[e, s, d, zone] for zone in zones) == 0).OnlyEnforceIf(work_wt[e, s, d].Not())

    for d in range (num_days):
        for s in range (1,num_shifts):
            for zone in zones:
                model.Add(sum(work[e, s, d, zone] for e in range(num_employees)) <= 1)

    # nb min and max of shift per day.
    # for e in range(num_employees):
    #     for d in range(num_days):
    #         model.Add(sum(work_wt[e, s, d] for s in range(1,num_shifts)) <= max_shift_per_day)
    #         model.Add(sum(work_wt[e, s, d] for s in range(1,num_shifts)) >= min_shift_per_day)

    obj_bool_vars = []
    obj_bool_coeffs = []
    obj_int_vars = []
    obj_int_coeffs = []
    # total pourcentage work constraint
    if contrainte_tp != []:
        for e in range(num_employees):
            for w in range(num_weeks):
                works = [work[e, shift, d + w * 7, zone] for zone in contrainte_tp[0] for shift in contrainte_tp[1] for
                         d in range(7)]
                weights = [shift_hours[Creneaux[shift+1]] for zone in contrainte_tp[0] for shift in contrainte_tp[1] for
                           d in range(7)]
                variables, coeffs = add_soft_scalar_sum_constraint(
                    model, works, weights, int(contrainte_tp[3]),
                    int(contrainte_tp[2]), contrainte_tp[5],
                    int(contrainte_tp[2]),
                    int(contrainte_tp[4]), contrainte_tp[6],
                    'weekly_pourc_work_constraint(employee %i, week %i)' %
                    (e, w))
                obj_int_vars.extend(variables)
                obj_int_coeffs.extend(coeffs)

    # Cover constraints
    for zone in zones:
        for d in range(num_days):
            works = [work[e, s, d, zone]for s in range(1,num_shifts) for e in range(num_employees)]
            # Ignore Off shift.
            min_demand = daily_cover_demands[d,zone]
            model.Add(sum(works) == min_demand)

    for zone in zones:
        for e in range(num_employees):
            for d in range(num_days):
                for s in range(1,num_shifts):
                    obj_bool_vars.append(work[e, s, d, zone])
                    obj_bool_coeffs.append(occ_rues[s-1,d,zone])

    # Objective
    model.Minimize(
        sum(obj_bool_vars[i] * obj_bool_coeffs[i]
            for i in range(len(obj_bool_vars)))
        + sum(obj_int_vars[i] * obj_int_coeffs[i]
              for i in range(len(obj_int_vars)))
    )

    # Solve the model.
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    solver.parameters.max_time_in_seconds = waiting_time
    solution_printer = cp_model.ObjectiveSolutionPrinter()
    status_int = solver.SolveWithSolutionCallback(model, solution_printer)
    # print("status : {}".format(status_int))
    # print("INFEASIBLE:{}".format(cp_model.INFEASIBLE))

    return solver, work, status_int



def print_solution_blockwise_del(zones,all_shift, livreurs, solver, work, shift_tagg):

    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1', cell_overwrite_ok=True)


    for i, s in enumerate(zones):
        sheet1.write(3, 2+i, str(s))
        # for j in range(len(tasks[task])):
        #     tasks[task].append(tasks[task][j] + 21)
        #     tasks[task].append(tasks[task][j] + 42)
    l = len(zones)
    days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

    c = 4
    # print(xlwt.Style.colour_map)
    for i in range(all_shift):
        k = 2
        if i % len(shift_tagg) == len(shift_tagg) - 1:
            sheet1.write(4+i, 0, days[(i // len(shift_tagg)) % 7])
        sheet1.write(4 + i, 1, shift_tagg[(i) % len(shift_tagg)])


        for zone in zones:

            for e in livreurs.keys():
                if solver.BooleanValue(work[e, i % len(shift_tagg) + 1, i // len(shift_tagg), zone]):

                    sheet1.write(c, k, livreurs[e])


            k += 1


        c += 1

    return wb

def main():
    num_weeks = 1
    tagg_heure = ["0:00-1:00", "1:00-2:00", "2:00-3:00", "3:00-4:00","4:00-5:00","5:00-6:00","6:00-7:00","7:00-8:00","8:00-9:00","9:00-10:00","10:00-11:00","11:00-12:00","12:00-13:00","13:00-14:00","14:00-15:00","15:00-16:00","16:00-17:00","17:00-18:00","18:00-19:00","19:00-20:00","20:00-21:00","21:00-22:00","22:00-23:00","23:00-00:00"]
    zones = ["Avenue des Champs Elysées", "Sts-Pères", "Convention"]
    zones_heures={}
    for index, zone in enumerate(zones):
        zones_heures[zone] = [i for i in range(len(tagg_heure)*num_weeks*7)]

    livreurs ={0:"Julien",1:"Timothé",2:"Soukaina",3:"Tony",4:"Carlos",5:"Matthias",6:"livreur_1",7:"livreur_2",8:"livreur_3"}
    Creneaux=["R"]+tagg_heure
    max_shift_per_day = 8
    min_shift_per_day= 4
    nb_colis_ACE = {0: 3, 1: 1, 2: 2, 3: 1, 4: 1, 5: 4, 6: 2}
    nb_colis_Sts = {0: 2, 1: 2, 2: 2, 3: 4, 4: 1, 5: 1, 6: 2}
    nb_colis_convention = {0: 1, 1: 3, 2: 2, 3: 1, 4: 4, 5: 1, 6: 2}
    daily_cover_demands={}
    for d in range (num_weeks*7):
        for zone in zones:
            if zone == "Avenue des Champs Elysées":
                daily_cover_demands[d,zone]=nb_colis_ACE[d]
            if zone == "Sts-Pères":
                daily_cover_demands[d,zone]=nb_colis_Sts[d]
            if zone == "Convention":
                daily_cover_demands[d,zone]=nb_colis_convention[d]
    # paramètres temps de travails
    # contrainte_tp = [ [task1, task2,....], [shift1, shift2,...], total_nb_of_hours, nb_of_hours_min, nb_of_hours_max, min_penalty, max_penalty]
    contrainte_tp = [
    ]
    contrainte_tp.append([zone for zone in zones])
    contrainte_tp.append([shifts for shifts in range(len(tagg_heure))])
    # base_pourc_work
    contrainte_tp.append(35)
    contrainte_tp.append(0)
    contrainte_tp.append(60)
    contrainte_tp.append(15)
    contrainte_tp.append(15)

    shift_hours = {"0:00-1:00" : 1, "1:00-2:00":1, "2:00-3:00":1, "3:00-4:00":1,"4:00-5:00":1,"5:00-6:00":1,"6:00-7:00":1,"7:00-8:00":1,"8:00-9:00":1,"9:00-10:00":1,"10:00-11:00":1,"11:00-12:00":1,"12:00-13:00":1,"13:00-14:00":1,"14:00-15:00":1,"15:00-16:00":1,"16:00-17:00":1,"17:00-18:00":1,"18:00-19:00":1,"19:00-20:00":1,"20:00-21:00":1,"21:00-22:00":1,"22:00-23:00":1,"23:00-00:00":1}

    df_ACE = pd.read_csv(os.path.join(r"comptages-routiers-permanents_ACE.csv"), sep=";")
    df_Sts = pd.read_csv(os.path.join(r"comptages-routiers-permanents_Sts.csv"), sep=";")
    df_convention = pd.read_csv(os.path.join(r"comptages-routiers-permanents_convention.csv"), sep=";")
    debut = pd.Timestamp('2020-11-23')
    fin = pd.Timestamp('2020-11-30')

    for df in (df_ACE, df_Sts, df_convention):
        df['Date et heure de comptage'] = df['Date et heure de comptage'].apply(lambda s: clean_date(s))
    for df in (df_ACE, df_Sts, df_convention):
        df['Date et heure de comptage'] = pd.to_datetime(df["Date et heure de comptage"], format='%Y-%m-%d %H:%M:%S')
    for df in (df_ACE, df_Sts, df_convention):
        df.sort_values("Date et heure de comptage", inplace=True)


    df_ACE = df_ACE[(df_ACE['Date et heure de comptage'] >= debut)]
    df_ACE = df_ACE[(df_ACE['Date et heure de comptage'] <= fin)]
    tx_occup_ACE = np.array(df_ACE["Taux d'occupation"])
    debit_ACE = np.array(df_ACE['Débit horaire'])

    # print(df_ACE['Date et heure de comptage'])
    df_Sts = df_Sts[(df_Sts['Date et heure de comptage'] >= debut)]
    df_Sts = df_Sts[(df_Sts['Date et heure de comptage'] <= fin)]
    tx_occup_Sts = np.array(df_Sts["Taux d'occupation"])
    debit_Sts = np.array(df_Sts['Débit horaire'])

    df_convention = df_convention[(df_convention['Date et heure de comptage'] >= debut)]
    df_convention = df_convention[(df_convention['Date et heure de comptage'] <= fin)]
    tx_occup_convention = np.array(df_convention["Taux d'occupation"])
    debit_convention = np.array(df_convention['Débit horaire'])
    # print(len(tx_occup_convention))

    ## print(tx_occup_convention)
    occ_rues = {}
    for zone in zones:
        for d in range (num_weeks*7):
            for s in range(len(tagg_heure)):
                if zone == "Avenue des Champs Elysées":
                    occ_rues[s, d, zone] = int((tx_occup_ACE[d*len(tagg_heure)+s]/debit_ACE[d*len(tagg_heure)+s])*1000)
                if zone == "Sts-Pères":
                    occ_rues[s, d, zone] = int((tx_occup_Sts[d*len(tagg_heure)+s]/debit_Sts[d*len(tagg_heure)+s])*1000)
                if zone == "Convention":
                    occ_rues[s, d, zone] = int((tx_occup_convention[d * len(tagg_heure) + s] / debit_convention[d * len(tagg_heure) + s])*1000)

    waiting_time = 60

    solver, work, status = solve_shift_scheduling(livreurs, Creneaux, num_weeks, zones, max_shift_per_day, min_shift_per_day, contrainte_tp, daily_cover_demands,occ_rues, waiting_time,shift_hours)


    all_shifts=num_weeks * len(tagg_heure) * 7
    wb = print_solution_blockwise_del(zones, all_shifts, livreurs, solver, work, tagg_heure)
    wb.save('planning_test.xls')