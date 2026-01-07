import simpy
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import pathlib
import argparse

 
from config import (
    dir_setup, STATION_DIC
)

OUTPUT_DIR_STR = dir_setup()

mod_path = 'mod'
usmaps_path = 'rand'
# print(sys.argv)

def parse_arguments():
    """
    Parse command line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='R-Day Simulation - SimPy-based cadet processing simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simulation.py --usmaps rand --mod std
  python simulation.py --usmaps front --mod mod --no-show
  python simulation.py --usmaps back --mod std --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--usmaps',
        type=str,
        choices=['rand', 'front', 'back'],
        default='rand',
        help='USMAPS cadet distribution strategy (default: rand)'
    )
    
    parser.add_argument(
        '--mod',
        type=str,
        choices=['mod', 'std'],
        default='std',
        help='Modification path: modified or standard (default: std)'
    )
    
    parser.add_argument(
        '--no-show',
        action='store_true',
        help='Do not display plots (only save them)'
    )
      
    return parser.parse_args()

args = parse_arguments()
usmaps_path = args.usmaps
mod_path = args.mod

    
print("The usmaps path is: " + usmaps_path)
print("The mod path is: " + str(mod_path))

TOTAL_CUSTOMERS = 1250
ARRIVAL_RATE = 2000 #customer arrivals per unit of time

time_stamp = []
arc_dic = {}

def generic_stn(env, i, stn):
    stn_idx = station_idx_dic[stn]
    svc_time_mode = STATION_DIC[stn]["service_time"]
    s_loc = svc_time_mode[0]/60
    s_scale = svc_time_mode[2]/60 - s_loc
    if(s_scale == 0):
        s_c = 0
    else:
        s_c = (svc_time_mode[1]/60 - s_loc)/s_scale
    svc_time_rand = stats.triang.rvs(c = s_c,
                                     loc = s_loc,
                                     scale = s_scale,
                                     size = 1)
    #enter_time = env.now
    if(usmaps_dic[i] == 1):
        svc_time_rand = svc_time_rand * STATION_DIC[stn]["USMAPS_frac"]
    if(sex_dic[i] == 0 and stn == "CA 2 Barber Shop" ): # female NC barber time = 0
        svc_time_rand = svc_time_rand * 0
    with resource_list[stn_idx].request() as req:
        yield req
        fin_time = env.now[0] + svc_time_rand[0]
        time_stamp_a = [i,stn_idx,len(resource_list[stn_idx].queue),
                           resource_list[stn_idx].count,resource_list[stn_idx].capacity,
                           stn,fin_time]
        q_list[stn_idx].append(len(resource_list[stn_idx].queue))
        q_list_time[stn_idx].append(env.now[0] + 6)
        yield env.timeout(svc_time_rand)
    if(sex_dic[i] == 1):
        next_stn = STATION_DIC[stn]["next_stn"]
        if(usmaps_dic[i] == 1 and mod_path == 'mod'):
            next_stn = STATION_DIC[stn]["next_USMAPS_stn"]
    if(sex_dic[i] == 0):
        next_stn = STATION_DIC[stn]["next_fem_stn"]
        if(usmaps_dic[i] == 1 and mod_path == 'mod'):
            next_stn = STATION_DIC[stn]["next_USMAPS_fem_stn"]
    time_stamp_a.append(next_stn)
    arc_dic_key = str(stn_idx) + "," + str(next_stn)
    if(arc_dic.get(arc_dic_key) == None):
        arc_dic[arc_dic_key] = 1
    else:
        arc_dic[arc_dic_key] = arc_dic[arc_dic_key] + 1
    time_stamp_a.append(arc_dic[arc_dic_key])
    time_stamp_a.append(resource_list[stn_idx].count)
    time_stamp.append(time_stamp_a)
    if next_stn > 0:
        if station_idx_dic["Bus Movement"] == next_stn:
            batch_bus(env, i)
        elif station_idx_dic["TH 6 Oath"] == next_stn:
            batch_oath(env, i)
        else:
            env.process(generic_stn(env, i, station_list[next_stn]))
            #print("next station is ", station_list[next_stn])

batch_bus_q = []
def batch_bus(env, i):
    global batch_bus_q
    batch_bus_q.append(i)
    if (len(batch_bus_q) > 40 or (arc_dic.get("2,3") == TOTAL_CUSTOMERS - 1)):
        for cdt in batch_bus_q:
            next_stn = station_idx_dic["Bus Movement"]
            env.process(generic_stn(env, cdt, station_list[next_stn]))
        batch_bus_q = []

batch_oath_q = []
def batch_oath(env, i):
    global batch_oath_q
    batch_oath_q.append(i)
    try:
        arc_12_7 = arc_dic.get("12,7")
        if(arc_dic.get("12,7") is None):
            arc_12_7 = 0
        arc_sum = arc_dic.get("6,7") + arc_12_7
    except:
        arc_sum = 0
    if (len(batch_oath_q) > 20 or (arc_sum == TOTAL_CUSTOMERS - 1)):
        for cdt in batch_oath_q:
            next_stn = station_idx_dic["TH 6 Oath"]
            env.process(generic_stn(env, cdt, station_list[next_stn]))
        batch_oath_q = []

def generate_cust(env):#, tailor):
    #generate the customers - this is essentially an arrival generator
    ct = 0
    start_time = 0
    fem_ct = 0
    usmaps_ct = 0
    for i in range(1,TOTAL_CUSTOMERS):
        usmaps_dic[i] = 0
        usmaps_rand = stats.uniform.rvs()
        usmaps_go = 0
        if(usmaps_path == 'rand'):
            if(usmaps_rand < 0.25 and usmaps_ct < 200):
                usmaps_go = 1
        if(usmaps_path == 'front'):
            if(i < 200):
                usmaps_go = 1
        if(usmaps_path == 'back'):
            if(i >= (TOTAL_CUSTOMERS - 200)):
                usmaps_go = 1    
        if(usmaps_go == 1):
            usmaps_dic[i] = 1 #USMAPS cadet
            usmaps_ct = usmaps_ct + 1
        sex_dic[i] = 1
        if(i % 2 == 0 and fem_ct < 53):
            sex_dic[i] = 0 #female cadet
            fem_ct = fem_ct + 1
        #print('generating customer %s' % i)
        inter_arr_time = stats.expon.rvs(loc=0,scale=(1/ARRIVAL_RATE),size=1) #location is offset, scale is mean
        yield env.timeout(inter_arr_time)
        #inter_arr_time = np.array([1/ARRIVAL_RATE]) #static for testing
        env.process(generic_stn(env, i, station_list[0]))
        ct = ct + 1
        if(ct == 250):
            discount_time = env.now[0] - start_time
            if((1 - discount_time) > 0):
                yield env.timeout(1 - discount_time)
            ct = 0
            start_time = env.now[0]
            fem_ct = 0



station_list = list(STATION_DIC.keys())

station_idx_dic = dict(zip(station_list,range(0,len(station_list))))

resource_list = []
q_list = []
q_list_time = []
sex_dic = {}
usmaps_dic = {}

env = simpy.Environment() #create a simpy environment
for stn_nm in station_list:
    resource_list.append(simpy.Resource(env, STATION_DIC[stn_nm]["server_ct"]))
    q_list.append([])
    q_list_time.append([])


#barber = simpy.Resource(env, 14) #barber resource with capacity of 1
#tailor = simpy.Resource(env, 6) #tailors
#WB4 = simpy.Resource(env, 12) # WB4 tailors; esimate 12 based on 230 cdts per hour, 3 min service time
env.process(generate_cust(env))#, tailor)) #set the initial simulation process
env.run() #run the simulation

# time_stamp_a = [i,stn_idx,len(resource_list[stn_idx].queue),
#                           resource_list[stn_idx].count,resource_list[stn_idx].capacity,
#                           stn,fin_time]

df_time_stamp = pd.DataFrame()
df_time_stamp['o_time_stamp'] = time_stamp
df_time_stamp['pn_id'] = [item[0] for item in time_stamp]
df_time_stamp['stn_no'] = [item[1] for item in time_stamp]
df_time_stamp['station'] = [item[5] for item in time_stamp]
df_time_stamp['time_stamp'] = [item[6] for item in time_stamp]
df_time_stamp['hr'] = df_time_stamp['time_stamp'].astype(int) + 6

#df_time_stamp_sum = pd.DataFrame(df_time_stamp[["stn_no","station","hr"]].groupby(["stn_no","station"]).value_counts()).reset_index()
df_time_stamp_sum = (
    df_time_stamp[["stn_no", "station", "hr"]]
    .groupby(["stn_no", "station"])
    .value_counts()
    .reset_index(name="count")  # <--- This ensures the column is named 'count'
)

df_time_stamp_wide = df_time_stamp_sum.pivot(index = ["stn_no","station"], columns = "hr", values = "count" ).reset_index()

def plot_queue(idx):
    #q_x = np.linspace(1,len(q_list[idx]),len(q_list[idx]))
    #plt.scatter(q_x,q_list[idx])
    plt.scatter(q_list_time[idx],q_list[idx])
    plt_title = "queue plot: " + station_list[idx] + " (stn " + str(idx) + ")"
    plt.title(plt_title)
    plt.xlim(5,20)
    plt.show()
    
#for i in range(0,len(station_list)):
#    plot_queue(i)
    
df_time_stamp = pd.DataFrame(time_stamp, columns = ["entity","stn_idx","q_length",
                                                    "svc_count","svc_capacity","stn_nm",
                                                    "time","next_stn","arc_ct","svc_count_after"])

df_fname = os.path.join(OUTPUT_DIR_STR, "df_time_stamp.csv")
df_time_stamp.to_csv(df_fname, index=False)

df_time_stamp_max = df_time_stamp.loc[df_time_stamp.groupby('stn_nm')['time'].idxmax()]
df_fname = os.path.join(OUTPUT_DIR_STR, "df_time_stamp_max.csv")
df_time_stamp_max.to_csv(df_fname, index=False)    
#print(df_time_stamp_max['time'].loc[df_time_stamp_max['stn_nm'] == 'R-Day complete'].iloc[0])

# 1. Find the index of the row with the maximum 'time' for each 'stn_nm'
idx_max_time = df_time_stamp.groupby('stn_nm')['time'].idxmax()

# 2. Select those specific rows from the original DataFrame
df_max_time_per_stn = df_time_stamp.loc[idx_max_time].sort_values(by='stn_idx', ascending=True).reset_index(drop=True)

# 2. Extract the 'time' column
time_values = df_max_time_per_stn['time']

# 3. Convert the time values to strings and join them with a comma and space
# Use map(str) to ensure all elements are strings before joining
time_string = ", ".join(time_values.map(str))

# 4. Print the resulting string
#print(time_string)

fin_time = round(df_time_stamp['time'].iloc[df_time_stamp.shape[0]-1],2)

fig, ax = plt.subplots(nrows=4, ncols=4, figsize=(15, 12))
fig.suptitle(mod_path + " " + usmaps_path + " | " + str(fin_time), fontsize = 24)
for i in range(0,len(station_list)-1):
    row = i // 4
    col = i % 4
    ax[row,col].scatter(q_list_time[i],q_list[i])
    ax[row,col].set_title(station_list[i])

plt.tight_layout() # Adjust subplots to fit in figure area

# Join the directory and the filename safely
filename = f"{mod_path}_{usmaps_path}.png"
plt_fname = os.path.join(OUTPUT_DIR_STR, filename)
plt.savefig(plt_fname)
plt.show()

recent_run_fname = os.path.join(OUTPUT_DIR_STR,"recent_run.txt")
with open(recent_run_fname, "w") as file:
    file.write(mod_path + " " + usmaps_path)
    

