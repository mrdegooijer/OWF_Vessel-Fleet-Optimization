# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 11:50:07 2023

@author: ivana
"""

from gurobipy import *

model = Model("VesselFleetComposition")

import numpy as np
import pandas as pd
import itertools
import time
start_time = time.time()

# ---------------------------- Sets ----------------------------

bases = ["B1", "B2"]                                        # list of all candidate bases
data_bases = {
    "Distance": [60, 80],                                   # distance between base and OWF
    "Technicians_available": [20, 16],                      # number of technicians available per period
    "Cost": [550000, 450000]                                # yearly cost of operating the base
    }
df_bases = pd.DataFrame(data_bases, index = bases)

vessels = ["V1", "V2", "V3"]                          # list of vessel types considered
data_vessels = {
    "Hslimit": [2.0, 2.5, 3.5],                       # maximum wave height
    "speed": [20, 30, 25],                            # speed of vessel in knots
    "dayrate": [5000, 10000, 16250],                  # daily cost to charter vessel
    "tech_cap": [10, 12, 12],                         # capacity for technicians on board
    "transfer_time": [15, 20, 30],                    # time for technicians to access or return a turbine, also includes traveltime between turbines
    "available": [5, 4, 2],                           # maximum number of vessels available for chartering
    "max_time_offshore": [12, 12, 24],                # maximum time a vessel may stay offshore
    "purchase_cost": [10000, 80000, 130000]           # cost of purchasing a vessel
    }
df_vessels = pd.DataFrame(data_vessels, index = vessels)

tasks = ["Task1", "Task2", "Task3"]                   # list of maintenance tasks
data_tasks = {
    "Active_time": [3, 8, 12],                        # time it takes to execute task
    "Technicians": [2, 4, 5],                         # number of technicians required to execute task
    "Failure_rate": [4, 0.5, 0],                      # yearly failure rate per turbine                                   
    "Repair_cost": [2500, 10000, 12500]               # cost for performing task
    }
df_tasks = pd.DataFrame(data_tasks, index = tasks )

periods = []
for i in range(1,91):
    periods.append(i)           # planning horizon, one period equals one day

vessel_task_incomp = {          # vessels that are not compatible to perform a task
    "V1": ["Task3"],
    "V2": [],
    "V3": []
    }
        
pre_tasks = [tasks[-1]]     # all preventive tasks
cor_tasks = tasks[:2]       # all corrective tasks
charter_periods = [periods[i:i+30] for i in range(0, len(periods), 30)]     # set of periods for chartering vessels

def charter_period(y):      # returns the charter period for a certain period
    for i, x in enumerate(charter_periods):
        if y in x:
            return (i)
      
bundle = []
for i in range(4):
    bundle.append(list(itertools.product(tasks, repeat = i+1)))
bundles = [j for sub in bundle for j in sub]                    # all possible task combinations that may form a bundle

# ---------------------------- Parameters ----------------------------

cost_tech = 50                              # hourly costs for technicians
# cost_downtime = 500                       # costs of hourly production loss due to downtime
cost_penalty_late = 20000                   # penalty costs if a preventive task is performed not within the time window
cost_penalty_not_performed = 1000000        # penalty costs if a task in not performed during the planning horizon
base_cap_vessels = {                        # the base capacity for vessels
    "V1": [4,3],
    "V2": [4,2],
    "V3": [1,1]
    }
base_cap_vessels = pd.DataFrame(base_cap_vessels, index = bases )

latest_period = 80          # latest period to perform the preventive tasks without penalty
turbines = 30               # number of turbines in OWF

tasks_in_bundle = {}            # number and types of tasks in a bundle
for m in tasks:
    for k in range(len(bundles)):
        tasks_in_bundle[m,k] = bundles[k].count(m)
         
        
# ---------------------------- Uncertainties ----------------------------

# Preventive maintenance tasks
scheduled_pre_tasks = {}
for m in pre_tasks:
    scheduled_pre_tasks[m] = turbines*1        # number of preventive tasks to be performed

# Corrective maintenance tasks
daily_failures = pd.DataFrame(index = cor_tasks, columns = periods)
failures = {}
for m in cor_tasks:
    for p in periods:
        failures[p] = np.random.uniform(size = turbines)            # uniform distribution of failures
        daily_failures.loc[m,p] = sum(x < df_tasks.loc[m, 'Failure_rate']/len(periods) for x in failures[p])

#Weather
#2004
weather = pd.read_excel('weatherconditions.xlsx', nrows = 8783, usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
#2005
#weather = pd.read_excel('weatherconditions.xlsx', nrows = 8760, skiprows = range(1,8784), usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
#2006
#weather = pd.read_excel('weatherconditions.xlsx', nrows = 8760, skiprows = range(1,17544), usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
#2007
#weather = pd.read_excel('weatherconditions.xlsx', nrows = 8760, skiprows = range(1,26304), usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
#2008
#weather = pd.read_excel('weatherconditions.xlsx', nrows = 8784, skiprows = range(1,35064), usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
#2009
#weather = pd.read_excel('weatherconditions.xlsx', nrows = 8760, skiprows = range(1,43848), usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
#2010
#weather = pd.read_excel('weatherconditions.xlsx', nrows = 8760, skiprows = range(1,52608), usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
#2011
#weather = pd.read_excel('weatherconditions.xlsx', nrows = 8760, skiprows = range(1,61368), usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])

#Wind speed and power
wind = pd.read_excel('windpower.xlsx', usecols=['Wind speed', 'Power'])

# weather conditions
hoursavailable = {}
for v in vessels:
    for p in periods:
        if p == 1:
            x = sum(weather.loc[i,'Wave Height'] < df_vessels.loc[v,'Hslimit'] for i in range(0, 23))
        else:
            x = sum(weather.loc[i,'Wave Height'] < df_vessels.loc[v, 'Hslimit'] for i in range((24*p-25), (24*p-1)))
        hoursavailable[v,p] = x

# Cost downtime power curve
cost_downtime = {}
for p in periods:
    if p == 1:
        cost_downtime[p] = (90/1000) * wind.loc[np.where(wind['Wind speed'] == round(sum(weather.loc[i, 'Wind Speed'] for i in range(0,23))/23)), 'Power'].values[0]
    else:
        cost_downtime[p] = (90/1000) * wind.loc[np.where(wind['Wind speed'] == round(sum(weather.loc[i, 'Wind Speed'] for i in range((24*p-25), (24*p-1)))/24)), 'Power'].values[0]

# ---------------------------- Decision variables ----------------------------

purchased_vessel = {}           # number of purchased vessels
for b in bases:
    for v in vessels:
        purchased_vessel[b,v] = model.addVar(lb=0, vtype=GRB.INTEGER)

chartered_vessel = {}           # number of chartered vessels
for b in bases:
    for v in vessels:
        for p in range(len(charter_periods)):
            chartered_vessel[b,v,p] = model.addVar(lb=0, vtype=GRB.INTEGER)

base_used = {}                  # binary value for whether base is used or not
for b in bases:
    base_used[b] = model.addVar(0,1,vtype=GRB.BINARY)
    
task_performed = {}             # number of tasks performed
for b in bases:
    for v in vessels:
        for p in periods:
            for m in tasks:
                task_performed[b,v,p,m] = model.addVar(lb=0, vtype=GRB.INTEGER)
for b in bases:
    for v in vessels:
        for m in tasks:
            task_performed[b,v,0,m] = 0                

                
bundle_performed = {}           # number of bundles performed
for b in bases:
    for v in vessels:
        for p in periods:
            for k in range(len(bundles)):
                bundle_performed[b,v,p,k] = model.addVar(lb=0, vtype=GRB.INTEGER)

task_late = {}                  # number of tasks not performed within time window
for m in pre_tasks:
    task_late[m] = model.addVar(lb=0, vtype=GRB.INTEGER)
    
task_not_performed = {}         # number of tasks not performed within planning horizon
for m in tasks:
    task_not_performed[m] = model.addVar(lb=0, vtype=GRB.INTEGER)
    
days_late = {}                  # number of days it takes until start on corrective maintenance tasks
for p in periods:
    for m in cor_tasks:
        days_late[p,m] = model.addVar(lb=0, vtype=GRB.INTEGER)
for m in cor_tasks:
    days_late[0,m] = 0
    
hours_worked = {}               # number of hours spent on a task
for b in bases:
    for v in vessels:
        for p in periods:
            for m in tasks:
                hours_worked[b,v,p,m] = model.addVar(lb=0, vtype=GRB.CONTINUOUS)
for b in bases:
    for v in vessels:
        for m in tasks:
            hours_worked[b,v,0,m] = 0

model.update()

# ---------------------------- Constraints ----------------------------               

#1 Base capacity for vessels
con1 = {}
for b in bases:
    for v in vessels:
        for p in range(len(charter_periods)):
            con1[b,v,p] = model.addConstr( purchased_vessel[b,v] + chartered_vessel[b,v,p] <= base_cap_vessels.loc[b,v] * base_used[b] )

#2 Maximum vessels available for chartering
con2 = {}
for v in vessels:
    for p in range(len(charter_periods)):
        con2[v,p] = model.addConstr( quicksum(chartered_vessel[b,v,p] for b in bases) <= df_vessels.loc[v, 'available'] )

#3 Time to perform maintenance is less than shift
con3 = {}
for b in bases:
    for v in vessels:
        for p in periods:
            con3[b,v,p] = model.addConstr( quicksum( hours_worked[b,v,p,m] for m in tasks) <= quicksum(bundle_performed[b,v,p,k]  * (len(bundles[k]) * ( df_vessels.loc[v, 'max_time_offshore'] - 2 * (df_vessels.loc[v, 'transfer_time']/60) * ( 1 + (len(bundles[k])-1)/2 ) ) - 2 * (df_bases.loc[b, 'Distance']/(1.852*df_vessels.loc[v, 'speed']))) for k in range(len(bundles))) )

#4 Technicians available at base
con4 = {}
for b in bases:
    for p in periods:
        con4[b,p] = model.addConstr( quicksum( tasks_in_bundle[m,k] * df_tasks.loc[m, 'Technicians'] * bundle_performed[b,v,p,k] for v in vessels for m in tasks for k in range(len(bundles))) <= df_bases.loc[b, 'Technicians_available'] )

#5 Vessel capacity for technicians
con5 = {}
for b in bases:
    for v in vessels:
        for p in periods:
            for k in range(len(bundles)):
                con5[b,v,p,k] = model.addConstr( quicksum( tasks_in_bundle[m,k] * df_tasks.loc[m, 'Technicians'] for m in tasks ) * bundle_performed[b,v,p,k] <= df_vessels.loc[v, 'tech_cap'] * bundle_performed[b,v,p,k] )

#6 Vessels available at base
con6 = {}
for b in bases:
    for v in vessels:
        for p in periods:
            con6[b,v,p] = model.addConstr( quicksum( bundle_performed[b,v,p,k] for k in range(len(bundles))) <= purchased_vessel[b,v] + chartered_vessel[b,v,charter_period(p)] )

#7 Penalty if task performed outside time window
con7 = {}
for m in pre_tasks:
    con7[m] = model.addConstr( quicksum( task_performed[b,v,p,m] for b in bases for v in vessels for p in range(latest_period, periods[-1]+1)) == task_late[m] )

#8 Weather restrictions
con8 = {} 
for b in bases:
    for v in vessels:
        for p in periods: 
            con8[b,v,p] = model.addConstr( quicksum( hours_worked[b,v,p,m] for m in tasks) <= quicksum( bundle_performed[b,v,p,k] * ( len(bundles[k]) * ( max(hoursavailable[v,p], 2 * (df_vessels.loc[v, 'transfer_time']/60) * ( 1 + (len(bundles[k])-1) / 2 ) ) - 2 * (df_vessels.loc[v, 'transfer_time']/60) * ( 1 + (len(bundles[k])-1) / 2 ) )- 2 * (df_bases.loc[b, 'Distance']/(1.852*df_vessels.loc[v, 'speed']))) for k in range(len(bundles))) )

#0 Vessel compatibility
con9 = {}
for v in vessels:
    for m in vessel_task_incomp[v]:
        con9[v,m] = model.addConstr( quicksum(hours_worked[b,v,p,m] for b in bases for p in periods) == 0 )
 

#9 Perform scheduled preventive tasks
con10 = {}
for m in pre_tasks:
    con10[m] = model.addConstr( quicksum( task_performed[b,v,p,m] for b in bases for v in vessels for p in periods ) + task_not_performed[m] == scheduled_pre_tasks[m]  )


#10 Perform corrective maintenance tasks
con11 = {}
for m in cor_tasks:
    con11[m] = model.addConstr( quicksum( task_performed[b,v,p,m] for b in bases for v in vessels for p in periods ) + task_not_performed[m] == quicksum( daily_failures.loc[m,p] for p in periods ) )

#11 Corrective task performed after failure
con12 = {}
for m in cor_tasks:
    for p in periods:
        con12[p,m] = model.addConstr( quicksum( task_performed[b,v,p,m] for b in bases for v in vessels ) <= quicksum( daily_failures.loc[m,q] for q in range(1,p+1)) - quicksum(task_performed[b,v,q,m] for b in bases for v in vessels for q in range(1,p)))

#12 Downtime for corrective maintenance tasks
con13 = {}
for m in cor_tasks:
    for p in periods:
        con13[p,m] = model.addConstr( days_late[p,m] == daily_failures.loc[m,p] - quicksum(task_performed[b,v,p,m] for b in bases for v in vessels) + days_late[p-1,m] )

#13 Tasks performed form bundles
con14 = {}
for b in bases:
    for v in vessels:
        for p in periods:
            for m in tasks:
                con14[b,v,p,m] = model.addConstr( quicksum( bundle_performed[b,v,p,k] * tasks_in_bundle[m,k] for k in range(len(bundles)) ) >= task_performed[b,v,p,m] )

#15 Number of tasks performed determined by the number of hours spent on a task
con15 = {}
for b in bases:
    for v in vessels:
        for p in periods:
            for m in tasks:
                con15[b,v,p,m] = model.addConstr( task_performed[b,v,p,m] == quicksum( (hours_worked[c,w,q,m] / df_tasks.loc[m,'Active_time']) - task_performed[c,w,q,m] for c in bases for w in vessels for q in range(0,p) ) + (hours_worked[b,v,p,m] / df_tasks.loc[m,'Active_time']) )


model.update()

# ---------------------------- Objective function ----------------------------

Cost_bases = quicksum(df_bases.loc[b,'Cost']*base_used[b] for b in bases)
Cost_purchasing_vessels = quicksum(df_vessels.loc[v, 'purchase_cost']*purchased_vessel[b,v] for b in bases for v in vessels)
Cost_chartering_vessels = quicksum(df_vessels.loc[v, 'dayrate']*len(charter_periods[p])*chartered_vessel[b,v,p] for b in bases for v in vessels for p in range(len(charter_periods)))
Cost_operations = quicksum(bundle_performed[b,v,p,k]*sum(df_tasks.loc[bundles[k][i], 'Repair_cost'] for i in range(len(bundles[k]))) for b in bases for v in vessels for k in range(len(bundles)) for p in periods)
Cost_technicians = quicksum(task_performed[b,v,p,m]*df_tasks.loc[m, 'Active_time']*df_tasks.loc[m, 'Technicians']*cost_tech for b in bases for v in vessels for m in tasks for p in periods)
Cost_downtime_pretasks = quicksum(cost_downtime[p]*df_tasks.loc[m, 'Active_time']*task_performed[b,v,p,m] for b in bases for v in vessels for m in pre_tasks for p in periods)
Cost_downtime_cortasks = quicksum(cost_downtime[p] * task_performed[b,v,p,m] * ((df_bases.loc[b, 'Distance']/(1.852*df_vessels.loc[v, 'speed'])) + (2*df_vessels.loc[v, 'transfer_time']/60) + df_tasks.loc[m, 'Active_time']) + days_late[p,m]*24 for b in bases for v in vessels for m in cor_tasks for p in periods)
Cost_penalties = quicksum(cost_penalty_late*task_late[m] for m in pre_tasks) + quicksum(cost_penalty_not_performed*task_not_performed[m] for m in tasks)

model.setParam( 'OutputFlag', True)
model.setParam( 'NonConvex', 2)
model.setParam ('MIPGap', 0);

model.setObjective( Cost_bases + Cost_purchasing_vessels + Cost_chartering_vessels + Cost_operations + Cost_technicians + Cost_downtime_pretasks + Cost_penalties + Cost_downtime_cortasks)

# ---------------------------- Greedy construction algorithm ----------------------------

# Set all bases and vessels to zero
for b in bases:
    base_used[b].ub = 0
    for v in vessels:
        purchased_vessel[b,v].ub = 0
        for p in range(len(charter_periods)):
            chartered_vessel[b,v,p].ub = 0

# Choose optimal bases
obj_value_b = {}
for b in bases:
    obj_value_b[b] = []
    base_used[b].lb = 1
    base_used[b].ub = 1
    model.optimize()
    if model.status == GRB.Status.OPTIMAL:
        obj_value_b[b] = model.objVal

for b in bases:
    base_used[b].lb = 0
    base_used[b].ub = 0
base_used[min(obj_value_b, key=obj_value_b.get)].lb = 1
base_used[min(obj_value_b, key=obj_value_b.get)].ub = 1

# Choose optimal fleet of purchased vessels
obj_value_pv = {}
for v in vessels:
    obj_value_pv[v] = {}
    for i in range(min(df_vessels.loc[v, 'available'],base_cap_vessels.loc[min(obj_value_b, key=obj_value_b.get),v])+1):
       obj_value_pv[v][i] = []
       purchased_vessel[min(obj_value_b, key=obj_value_b.get),v].ub = i
       purchased_vessel[min(obj_value_b, key=obj_value_b.get),v].lb = i    
       model.optimize()
       if model.status == GRB.Status.OPTIMAL:
           obj_value_pv[v][i] = model.objVal
    purchased_vessel[min(obj_value_b, key=obj_value_b.get),v].lb = min(obj_value_pv[v], key=obj_value_pv[v].get)
    purchased_vessel[min(obj_value_b, key=obj_value_b.get),v].ub = min(obj_value_pv[v], key=obj_value_pv[v].get)

# Choose optimal fleet of chartered vessels
obj_value_cv = {}
for v in vessels:
    obj_value_cv[v] = {}
    for p in range(len(charter_periods)):
        obj_value_cv[v][p] = {}
        for i in range(min(df_vessels.loc[v, 'available'],base_cap_vessels.loc[min(obj_value_b, key=obj_value_b.get),v])+1-min(obj_value_pv[v], key=obj_value_pv[v].get)):
            obj_value_cv[v][p][i] = []
            chartered_vessel[min(obj_value_b, key=obj_value_b.get),v,p].ub = i
            chartered_vessel[min(obj_value_b, key=obj_value_b.get),v,p].lb = i    
            model.optimize()
            obj_value_cv[v][p][i] = model.objVal
        chartered_vessel[min(obj_value_b, key=obj_value_b.get),v,p].ub = min(obj_value_cv[v][p], key=obj_value_cv[v][p].get)
        chartered_vessel[min(obj_value_b, key=obj_value_b.get),v,p].lb = min(obj_value_cv[v][p], key=obj_value_cv[v][p].get)
 
model.optimize()

# ---------------------------- Tabu search ----------------------------

iteration = 0               # initial solution
objective = {}              # list of the minimum objective values
solution = {}               # list of solution, consisting of number of purchased vessels, chartered vessels and bases used
it_objectives = {}          # objective values for each neighbor at each iteration
tabu = []                   # list of tabu moves
solution[iteration] = []    # solution for each neighbor at each iteration
for i in range(len(purchased_vessel)+len(chartered_vessel)+len(bases)):
    solution[iteration].append(model.getVarByName("C"+str(i)).x)    

objective[iteration] = model.objVal
best_objective_so_far = []
it_objectives[iteration] = [model.objVal]
iteration = 1               # start of the iterations
max_it = 15                 # maximum number of iterations
while iteration < max_it and time.time() - start_time < 3600:        # stopping criteria   
    neighbors = []                  # list of neighbors of the current solution
    sol = solution[iteration-1]     # current solution
    it_move = []                    # move that results in the neighbor
    
    # neighbors for purchased vessels
    for b in bases:
        for v in vessels:
            i = bases.index(b)*len(vessels) + vessels.index(v)       
            # add a purchased vessel
            nb = sol.copy()
            if nb[i] < base_cap_vessels.loc[b,v] and 'add '+str(b)+str(v) not in tabu:
                nb[i] += 1
                neighbors.append(nb.copy())
                it_move.append('remove '+str(b)+str(v))
        
            if sol[i] > 0.5:
                # remove a purchased vessel
                if 'remove '+str(b)+str(v) not in tabu:
                    nb = sol.copy()
                    nb[i] -= 1
                    neighbors.append(nb.copy())
                    it_move.append('add '+str(b)+str(v))
                
                nb = sol.copy()
                for j in range(len(vessels)):
                    if j != i and nb[j] < base_cap_vessels.loc[b,vessels[j]] and 'switch '+str(b)+vessels[j]+str(v) not in tabu:
                        # change type of a purchased vessel
                        nb[i] -= 1
                        nb[j] += 1
                        neighbors.append(nb.copy())
                        it_move.append('switch '+str(b)+str(v)+vessels[j])
                        
                nb = sol.copy()
                for k in range(len(bases)):
                    l = (k-bases.index(b))*len(purchased_vessel) + i
                    if k != bases.index(b) and nb[l] < base_cap_vessels.loc[b,vessels[l-(k*len(purchased_vessel))]] and 'switch '+bases[k]+str(b)+str(v) not in tabu:
                        # change base of a purchased vessel
                        nb[i] -= 1
                        nb[l] += 1
                        neighbors.append(nb.copy())
                        it_move.append('switch '+str(b)+bases[k]+str(v))
    
    # neighbors for chartered vessels
    for b in bases:
        for v in vessels:
            for p in range(len(charter_periods)):
                i = len(purchased_vessel) + bases.index(b)*(len(vessels)+len(charter_periods)) + vessels.index(v)*len(charter_periods) + p
                # add a chartered vessel
                nb = sol.copy()
                if nb[i] < base_cap_vessels.loc[b,v] and 'add '+str(b)+str(v)+str(p) not in tabu:
                    nb[i] += 1
                    neighbors.append(nb.copy())
                    it_move.append('remove '+str(b)+str(v)+str(p))
                
                if sol[i] > 0.5:
                    # remove a chartered vessel
                    if 'remove '+str(b)+str(v)+str(p) not in tabu:
                        nb = sol.copy()
                        nb[i] -= 1
                        neighbors.append(nb.copy())
                        it_move.append('add '+str(b)+str(v)+str(p))
                    
                    # change type of a chartered vessel in the same period
                    nb = sol.copy()
                    for j in range(len(vessels)):
                        k = (j-vessels.index(v))*len(charter_periods) + i
                        if j != vessels.index(v) and nb[k] < base_cap_vessels.loc[b,vessels[j]] and 'switch '+str(b)+vessels[j]+str(v)+str(p) not in tabu:
                            nb[i] -= 1
                            nb[j] += 1
                            neighbors.append(nb.copy())
                            it_move.append('switch '+str(b)+str(v)+vessels[j]+str(p))
                    
                    # change the period of a chartered vessel
                    nb = sol.copy()
                    for l in range(len(charter_periods)):
                        m = i + (l-p)
                        if l != p and nb[m] < base_cap_vessels.loc[b,v] and 'switch '+str(b)+str(v)+str(l)+str(p) not in tabu:
                            nb[i] -= 1
                            nb[m] += 1
                            neighbors.append(nb.copy())
                            it_move.append('switch '+str(b)+str(v)+str(p)+str(l))
                        
                    # change base of a chartered vessel
                    nb = sol.copy()
                    for m in range(len(bases)):
                        n = (m-bases.index(b))*len(vessels)*len(charter_periods) + i
                        if m != bases.index(b) and nb[n] < base_cap_vessels.loc[bases[m],v] and 'switch '+bases[m]+str(b)+str(v)+str(p) not in tabu:
                            nb[i] -= 1
                            nb[n] += 1
                            neighbors.append(nb.copy())
                            it_move.append('switch '+str(b)+bases[m]+str(v)+str(p))
    
    # neighbors for bases
    for b in bases:
        i = len(purchased_vessel) + len(chartered_vessel) + bases.index(b)
        j = bases.index(b)*len(vessels)
        k = len(bases)*len(vessels) + bases.index(b)*len(vessels)*len(charter_periods)
        
        # remove base + vessels
        nb = sol.copy()
        if nb[i] > 0.5:
            nb[i] = 0
            for l in range(j, j+len(vessels)):
                nb[l] = 0
            for m in range(k, k+len(vessels)*len(charter_periods)):
                nb[m] = 0
            neighbors.append(nb.copy())
            it_move.append('remove '+str(b))
    
        # replace base and vessels with another base
        nb = sol.copy()
        if nb[i] > 0.5:
            for l in range(len(bases)):
                if l != bases.index(b) and nb[len(purchased_vessel) + len(chartered_vessel) + l] < 0.5 and 'switch '+bases[l]+str(b) not in tabu:
                    for x in range(l*len(vessels),(l+1)*len(vessels)):
                        nb[x] = nb[x-(l-bases.index(b))*len(vessels)]
                        nb[x-(l-bases.index(b))*len(vessels)] = 0
                    m = len(bases)*len(vessels) + l*len(vessels)*len(charter_periods)
                    for y in range(m, m + len(vessels)*len(charter_periods)):
                        nb[y] = nb[y-(l-bases.index(b))*(len(vessels)*len(charter_periods))]
                        nb[y-(l-bases.index(b))*(len(vessels)*len(charter_periods))] = 0
                    nb[len(purchased_vessel) + len(chartered_vessel) + l] = 1
                    nb[i] = 0
                    neighbors.append(nb.copy())
                    it_move.append('switch '+str(b)+bases[l])
    
    # Delete neighbors that have already been considered
    existing = []
    for o in range(len(neighbors)):
        for i in solution:
            if neighbors[o] == solution[i]:
                existing.append(neighbors[o])
    for i in range(len(existing)):
        if existing[i] in neighbors:
            neighbors.remove(existing[i])
    
    # Calculate objective values for neighbors
    it_objectives[iteration] = []
    for x in neighbors:
        for b in bases:
            l = len(purchased_vessel)+len(chartered_vessel) + bases.index(b)
            base_used[b].lb = x[l]
            base_used[b].lb = x[l]
            for v in vessels:
                i = bases.index(b)*len(vessels) + vessels.index(v)
                purchased_vessel[b,v].lb = x[i]
                purchased_vessel[b,v].ub = x[i]
                for p in range(len(charter_periods)):
                    j = bases.index(b)*len(vessels)*len(charter_periods) + vessels.index(v)*len(charter_periods) + p + len(purchased_vessel)
                    chartered_vessel[b,v,p].lb = x[j]
                    chartered_vessel[b,v,p].ub = x[j]
        model.optimize()
        if model.status == GRB.Status.OPTIMAL:
            it_objectives[iteration].append(model.objVal)
        else:
            it_objectives[iteration].append(10000000000)
    
    solution[iteration] = neighbors[it_objectives[iteration].index(min(it_objectives[iteration]))]
    objective[iteration] = min(it_objectives[iteration])
    best_objective_so_far.append(min(objective[o] for o in range(iteration)))
    tabu.append(it_move[it_objectives[iteration].index(min(it_objectives[iteration]))])
    
    # stopping criteria if no improvements in objective value have been found
    if iteration > 3:
        if objective[iteration-1] > min(best_objective_so_far) and objective[iteration-2] > min(best_objective_so_far) and objective[iteration] > min(best_objective_so_far):
            iteration += max_it
    
    iteration += 1

final_objective = min(objective[i] for i in range(len(objective)))      # the resulting objective value
final_solution = solution[min(objective, key=objective.get)]            # the resulting solution corresponding to the objective value

# set each decision variable to the resulting solution
for b in bases:
    l = len(purchased_vessel)+len(chartered_vessel) + bases.index(b)
    base_used[b].lb = final_solution[l]
    base_used[b].lb = final_solution[l]
    for v in vessels:
        i = bases.index(b)*len(vessels) + vessels.index(v)
        purchased_vessel[b,v].lb = final_solution[i]
        purchased_vessel[b,v].ub = final_solution[i]  
        for p in range(len(charter_periods)):
            j = bases.index(b)*len(vessels)*len(charter_periods) + vessels.index(v)*len(charter_periods) + p + len(purchased_vessel)
            chartered_vessel[b,v,p].lb = final_solution[j]
            chartered_vessel[b,v,p].ub = final_solution[j]

model.optimize()

# ---------------------------- Printing results ----------------------------

C_bases = sum(df_bases.loc[b,'Cost']*base_used[b].x for b in bases)
C_purchasing_vessels = sum(df_vessels.loc[v, 'purchase_cost']*purchased_vessel[b,v].x for b in bases for v in vessels)
C_chartering_vessels = sum(df_vessels.loc[v, 'dayrate']*chartered_vessel[b,v,p].x for b in bases for v in vessels for p in range(len(charter_periods)))
C_operations = sum(bundle_performed[b,v,p,k].x*sum(df_tasks.loc[bundles[k][i], 'Repair_cost'] for i in range(len(bundles[k]))) for b in bases for v in vessels for k in range(len(bundles)) for p in periods)
C_technicians = sum(task_performed[b,v,p,m].x*df_tasks.loc[m, 'Active_time']*df_tasks.loc[m, 'Technicians']*cost_tech for b in bases for v in vessels for m in tasks for p in periods)
C_downtime_pretasks = sum(cost_downtime*df_tasks.loc[m, 'Active_time']*task_performed[b,v,p,m].x for b in bases for v in vessels for m in pre_tasks for p in periods)
C_downtime_cortasks = (sum(cost_downtime * task_performed[b,v,p,m].x * ((df_bases.loc[b, 'Distance']/(1.852*df_vessels.loc[v, 'speed'])) + (2*df_vessels.loc[v, 'transfer_time']/60) + df_tasks.loc[m, 'Active_time']) + days_late[p,m].x*24 for b in bases for v in vessels for m in cor_tasks for p in periods))
C_penalties = sum(cost_penalty_late*task_late[m].x for m in pre_tasks) + sum(cost_penalty_not_performed*task_not_performed[m].x for m in tasks)

for b in bases:
    print('At '+str(b))
    for v in vessels:
        print('The number of purchased vessels of type ' +str(v) +' is: %d' % purchased_vessel[b,v].x)
    for v in vessels:
        for p in range(len(charter_periods)):
            print('The number of chartered vessels of type ' +str(v) +' in period '+str(p)+' is: %d' % chartered_vessel[b,v,p].x)

print('The total costs are: %.2f' % model.objVal )
print('The costs for using bases are: %.2f' % C_bases)
print('The costs for purchasing vessels are: %.2f' % C_purchasing_vessels)
print('The costs for chartering vessels are: %.2f' % C_chartering_vessels)
print('The costs for executing maintenance tasks are: %.2f' % C_operations)
print('The costs for technicians are: %.2f' % C_technicians)
print('The costs due to downtime are: %.2f' % (C_downtime_cortasks+C_downtime_pretasks))
print('The costs for penalties are: %.2f' % C_penalties)
    
print("--- %s seconds ---" % (time.time() - start_time))        