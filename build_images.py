# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 12:33:03 2025

@author: paul.evangelista
"""

import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
import numpy as np
import argparse

from config import (
    dir_setup
)

OUTPUT_DIR_STR = dir_setup()
os.chdir(OUTPUT_DIR_STR)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='parse argument for R-Day simulated minutes per frame',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stitch_images.py --mins 6
        """
    )    
    parser.add_argument(
        '--mins',
        type=int,
        default=60,
        help='R-Day minutes between each frame in 30-second video'
    )
    return parser.parse_args()

args = parse_arguments()
R_Day_mins_per_frame = args.mins

# Color function based on fullness percentage
def get_color(in_q):
    if(in_q == None):
        in_q = 0
    if in_q > 50:
        return '#E53935'  # Red for over 100
    elif in_q > 25:
        return '#FFC107'  # Yellow for 50-100
    else:
        return '#4CAF50'  # Green for below 25

with open("recent_run.txt", "r") as file:
    path_descr = file.read()

df_time_stamp = pd.read_csv("df_time_stamp.csv")

queue_dic = {}
svc_dic = {}
cap_dic = {}
arc_ct = {}
svc_ct = {}

last_time = 0
for i in range(0,df_time_stamp.shape[0]):
    stn_idx = df_time_stamp['stn_idx'].iloc[i]
    next_stn = df_time_stamp['next_stn'].iloc[i]
    t = df_time_stamp['time'].iloc[i]
    queue_dic[stn_idx] = df_time_stamp['q_length'].iloc[i]
    svc_dic[stn_idx] = df_time_stamp['svc_count_after'].iloc[i]
    cap_dic[stn_idx] = df_time_stamp['svc_capacity'].iloc[i]
    arc_key = str(stn_idx) + "," + str(next_stn)
    if(arc_ct.get(arc_key) == None):
        arc_ct[arc_key] = 1
    else:
        arc_ct[arc_key] = arc_ct[arc_key] + 1
    if(svc_ct.get(stn_idx) == None):
        svc_ct[stn_idx] = 1
    else:
        svc_ct[stn_idx] = svc_ct[stn_idx] + 1
    time_value = df_time_stamp['time'].iloc[i]
    time_diff = time_value - last_time
    if(time_diff > R_Day_mins_per_frame/60 or i == (df_time_stamp.shape[0]-1)):
        #sys.exit()
        last_time = time_value

        # 1. Define data for multiple queues (Label, queue, in_svc)
        queue_data = [
            ('Smart Card Issue', queue_dic.get(0), svc_dic.get(0), cap_dic.get(0),0), #0
            ('Ike 1 - Scan In', queue_dic.get(1), svc_dic.get(1), cap_dic.get(1),1), #1
            ('Ike 2 - Scan Out', queue_dic.get(2), svc_dic.get(2), cap_dic.get(2),2), #2
            ('Bus Movement', queue_dic.get(3), svc_dic.get(3), cap_dic.get(3),3), #3
            ('TH 2 Finance', queue_dic.get(4), svc_dic.get(4), cap_dic.get(4),4), #4
            ('TH 3 LRC Issue Point 1', queue_dic.get(5), svc_dic.get(5), cap_dic.get(5),5), #5
            ('TH 5 Med Screening 1', queue_dic.get(6), svc_dic.get(6), cap_dic.get(6),6), #6
            ('TH 6 Oath', queue_dic.get(7), svc_dic.get(7), cap_dic.get(7),7), #7
            ('TH 7a Med Screening 2', queue_dic.get(8), svc_dic.get(8), cap_dic.get(8),8), #8
            ('TH 8 S1 (DD93/SGLI)', queue_dic.get(9), svc_dic.get(9), cap_dic.get(9),9), #9
            ('TH 9 Company Holding', queue_dic.get(10), svc_dic.get(10), cap_dic.get(10),10), #10
            ('BH4f Female Issue Point 0', queue_dic.get(14), svc_dic.get(14), cap_dic.get(14),14), #14
            ('CA 2 Barber Shop', queue_dic.get(13), svc_dic.get(13), cap_dic.get(13),13), #13
            ('CA 1 Issue Point 2 (WB4)', queue_dic.get(11), svc_dic.get(11), cap_dic.get(11),11), #11
            ('LRC Issue Pt 6 (687)', queue_dic.get(12), svc_dic.get(12), cap_dic.get(12),12), #12
            ('CA 3 Red Sash', queue_dic.get(15), svc_dic.get(15), cap_dic.get(15),15) #15
        ]
        
        #Queue	Normalized Position [left, bottom, width, height]
        
        custom_positions = [
        [0.01, 0.9, 0.15, 0.025],
        [0.01, 0.75, 0.15, 0.025],
        [0.01, 0.6, 0.15, 0.025],
        [0.01, 0.45, 0.15, 0.025],
        [0.3, 0.9, 0.15, 0.025],
        [0.3, 0.75, 0.15, 0.025],
        [0.3, 0.6, 0.15, 0.025],
        [0.3, 0.45, 0.15, 0.025],
        [0.3, 0.3, 0.15, 0.025],
        [0.3, 0.15, 0.15, 0.025],
        [0.3, 0, 0.15, 0.025],
        [0.6, 0.9, 0.15, 0.025],
        [0.9, 0.9, 0.15, 0.025],
        [0.9, 0.75, 0.15, 0.025],
        [0.9, 0.6, 0.15, 0.025],
        [0.9, 0.45, 0.15, 0.025]
            ]
        
        arrow_pos = [
        [0.09,0.89,0,-0.07,'green',[0.1, 0.85, arc_ct.get("0,1")]], #smart-card to Ike1
        [0.09,0.74,0,-0.07,'green',[0.1, 0.7, arc_ct.get("1,2")]], #Ike1 to Ike2
        [0.09,0.59,0,-0.07,'green',[0.1, 0.55, arc_ct.get("2,3")]], #Ike2 to bus
        [0.38,0.89,0,-0.07,'green',[0.39, 0.85, arc_ct.get("4,5")]], #fin to LRC1
        [0.38,0.74,0,-0.07,'green',[0.39, 0.7, arc_ct.get("5,6")]], #LRC1 to med
        [0.38,0.59,0,-0.07,'green',[0.39, 0.55, arc_ct.get("6,7")]], #med to oath
        [0.38,0.44,0,-0.07,'green',[0.39, 0.40, arc_ct.get("7,8")]], #oath to immun
        [0.38,0.29,0,-0.07,'green',[0.39, 0.25, arc_ct.get("8,9")]], #immun to s1
        [0.38,0.14,0,-0.07,'green',[0.39, 0.1, arc_ct.get("9,10")]], #s1 to company
        [0.98,0.89,0,-0.07,'maroon',[0.99, 0.85, arc_ct.get("13,11")]], #barber to wb4
        [0.98,0.74,0,-0.07,'green',[0.99, 0.7, arc_ct.get("11,12")]], #wb4 to 687
        [0.98,0.59,0,-0.07,'maroon',[0.99, 0.55, arc_ct.get("12,15")]], #687 to red sash
        [0.5,0.76,0.09,0.14,'blue',[0.50, 0.82, arc_ct.get("5,14")]], #LRC1 to preg
        [0.83,0.89,0.04,-0.13,'blue',[0.82, 0.9, arc_ct.get("14,11")]], #preg to wb4
        [0.86,0.61,-0.35,0,'blue',[0.66, 0.62, arc_ct.get("12,6")]], #687 to med
        [0.5,0.05,0.37,0.85,'green',[0.62, 0.45, arc_ct.get("10,13")]], #company to barber
        [0.88,0.89,0,-0.37,'blue',[0.89, 0.55, arc_ct.get("13,15")]], #barber to red sash
        [0.22,0.49,0.09,0.4,'green',[0.21, 0.65, arc_ct.get("3,4")]], #bus to finance
        [0.22,0.49,0.09,0.11,'red',[0.30, 0.56, arc_ct.get("3,6")]], #bus to med screening (USMAPS)
        [0.46,0.625,0.4,0.275,'red',[0.53,0.65, arc_ct.get("6,13")]], #med to barber (USMAPS)
        [0.86,0.61,-0.35,-0.15,'red',[0.63, 0.54, arc_ct.get("12,7")]], #687 to oath
        [0.46,0.625,0.17,0.27,'red',[0.52,0.7,arc_ct.get("6,14")]], #med to preg
        [0.27,0.15,0,0.77,'red',[0.23, 0.4, arc_ct.get("9,4")]], #s1 to finance
        [0.29,0.77,0,-0.75,'red',[0.3, 0.4, arc_ct.get("5,10")]], #LRC1 to company holding
        [0.5,0.05,0.37,0.45,'red',[0.6, 0.15, arc_ct.get("10,15")]] #company to red sash (USMAPS)
        ]
        
        awidth=0.0025           # Thickness of the arrow shaft
        ahead_width=0.01        # Width of the arrow head
        ahead_length=0.01        # Length of the arrow head
        acolor='blue'
        alength_includes_head=True
        
        fig = plt.figure(figsize=(10,8))
        
        # Set a main title for the figure
        fig_title = 'Simulating New Cadet In-processing on R-Day 2026 (' + path_descr + ')'  
        fig.suptitle(fig_title, fontsize=16, y=1.02)
        
        # 3. Loop through data and axes to create each chart
        # Loop through data and custom positions
        for (label, in_q, in_svc, cap, idx), rect in zip(queue_data, custom_positions):
            # 'rect' is a list like [0.1, 0.7, 0.4, 0.15]
            if(in_q == None):
                in_q = 0
            if(in_svc == None):
                in_svc = 0
            ax = fig.add_axes(rect) 
            # ... plotting code goes here
            color = get_color(in_q)
        
            # Plot the "full" part
            ax.barh(y=[0.5], width=[in_q], height=0.6, color=color, align='center')
        
            # Plot the "empty" part on top for visual clarity of the boundary
            empty_size = 100 - in_q
            ax.barh(y=[0.5], width=[empty_size], left=[in_q], height=0.6, color='#E0E0E0', align='center')
        
            # Set the x-axis limit from 0 to the total capacity
            ax.set_xlim(0, 100)
        
            # Clean up the chart (remove axis lines/ticks)
            ax.set_yticks([])
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xticks([])
        
            # Add the queue label (title)
            lab2 = label + "\n" + str(svc_ct.get(idx)) + " done"
            ax.set_title(lab2, fontsize=12, loc='left', pad=3)
        
            # Add a text label showing the percentage/value on the right
            #bar_text = "\nq: " + str(in_q) + "\n" + "s: " + str(in_svc) + "\n" + "c: " + str(cap)
            bar_text = "\nq: " + str(in_q) + "\n" + "s: " + str(in_svc) + "/" + str(cap)
            ax.text(100 * 1.05, 0.5, bar_text,
                    va='center', ha='left', fontsize=11, color='black')
        
        # Adjust layout to prevent overlap and accommodate external text
        ax = fig.add_axes([0,0,1,1]) 
        
        time_value = time_value + 5.5
        time_value_min = str(int(round((time_value - np.trunc(time_value))*60,0)))
        if(time_value_min == "60"):
            time_value_min = "00"
            time_value = time_value + 1
        time_value_hr = str(int(np.trunc(time_value)))
        if(len(time_value_min) == 1):
            time_value_min = "0" + time_value_min
        if(len(time_value_hr) == 1):
            time_value_hr = "0" + time_value_hr
        
        time_text = "Time: " + time_value_hr + ":" + time_value_min
        ax.text(0.7, 0.05, time_text, fontsize = 14)
        
        note_text = "Green "
        ax.text(0.7, 0.4, note_text, fontsize = 14, color = 'green', verticalalignment='top')
        note_text = "           text represents movement of all New        \nCadets." #11 spaces
        ax.text(0.7, 0.4, note_text, fontsize = 14, color = 'black', verticalalignment='top')
        
        note_text = "Blue "
        ax.text(0.7, 0.33, note_text, fontsize = 14, color = 'blue', verticalalignment='top')
        note_text = "        text represents movement of female only\nNew Cadets." #11 spaces
        ax.text(0.7, 0.33, note_text, fontsize = 14, color = 'black', verticalalignment='top')
        
        note_text = "Maroon "
        ax.text(0.7, 0.26, note_text, fontsize = 14, color = 'maroon', verticalalignment='top')
        note_text = "             text represents movement of male only\nNew Cadets." #11 spaces
        ax.text(0.7, 0.26, note_text, fontsize = 14, color = 'black', verticalalignment='top')
        
        if(arrow_pos[18][5][2] != None):
            note_text = "Red "
            ax.text(0.7, 0.19, note_text, fontsize = 14, color = 'red', verticalalignment='top')
            note_text = "       text represents movement of USMAPS\nNew Cadets." #11 spaces
            ax.text(0.7, 0.19, note_text, fontsize = 14, color = 'black', verticalalignment='top')
        
        note_text = "This is a simulated representation\nof a hypothetical R-Day for West Point\nin 2026. The process depicted in this\nsimulation does not represent official\npolicies or plans."
        note_text2 = " This simulation is\nintended solely for academic purposes."
        ax.text(0.001, 0.35, (note_text + note_text2), fontsize = 10, color = 'black', verticalalignment='top')
        
        note_text = \
        "Each bar reflects the length of the\
        \nqueue as a color, from a min of\
        \n0 to a max of 100. The color changes\
        \nto yellow at 25 and red at 50. The\
        \nqueue length is shown after \"q:\".\
        \nThe number of entities with the\
        \nserver and the capacity of the server\
        \nare shown after \"s:\", respectively."
        
        ax.text(0.001, 0.2, (note_text), fontsize = 10, color = 'black', verticalalignment='top')
        
        ax.set_axis_off()
        #plt.tight_layout(rect=[0, 0, 1, 0.98])
        #plt.arrow(0.2,0.8,0,0.1)
        # [0.46,0.625,0.4,0.275,'red',[0.53,0.65, arc_ct.get("6,13"), 'red']], #med to barber (USMAPS)
        for a in arrow_pos:
            if(a[5][2] != None):
                plt.arrow(a[0],a[1],a[2],a[3],width=awidth,
                          head_width = ahead_width,
                          head_length = ahead_length,
                          color = a[4],length_includes_head = alength_includes_head)
                ax.text(a[5][0], a[5][1], a[5][2], fontsize=12, color = a[4])
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        #plt.savefig('multiple_capacity_charts.png')
        fname = time_value_hr + time_value_min + "Rday.png"
        #plt.tight_layout()
        plt.savefig(fname, dpi=300, bbox_inches='tight')
        #fig.set_size_inches(16, 12)
        #plt.savefig(fname, dpi=300)
        #plt.show()
        
        
