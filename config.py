"""
Configuration file for R-Day Simulation
Contains all constants, station definitions, and simulation parameters
"""
from pathlib import Path
from typing import Dict, List, Tuple
import os
import sys
import pathlib

# Simulation Constants
TOTAL_CUSTOMERS = 1250
ARRIVAL_RATE = 2000  # customer arrivals per hour
BUS_BATCH_SIZE = 40
OATH_BATCH_SIZE = 20
CUSTOMER_BATCH_SIZE = 250
FEMALE_COUNT_MAX = 53
USMAPS_COUNT_MAX = 200
USMAPS_PROBABILITY = 0.25
SIMULATION_START_TIME = 5.5  # 0530 AM

def dir_setup():
    try:
        SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        SCRIPT_PATH = os.getcwd()
    
    os.chdir(SCRIPT_PATH)
    print(f"Working directory set to: {os.getcwd()}")
    
    OUTPUT_DIR_STR = os.path.join(os.getcwd(), 'output')
    OUTPUT_DIR = pathlib.Path(OUTPUT_DIR_STR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Directory '{OUTPUT_DIR}' is ready.")
    
    return(OUTPUT_DIR_STR)

# All service times now show min, mode, max; all times are in minutes
STATION_DIC = {"RN - Smart Card Issue":{"server_ct" : 8, "service_time" : [1,2,3], "next_stn" : 1, "next_fem_stn" : 1, "USMAPS_frac" : 1, "next_USMAPS_stn" : 1, "next_USMAPS_fem_stn" : 1}, #0
               "Ike 1 Scan-In":{"server_ct" : 200, "service_time" : [40,45,50], "next_stn" : 2, "next_fem_stn" : 2, "USMAPS_frac" : 1, "next_USMAPS_stn" : 2, "next_USMAPS_fem_stn" : 2}, #1 #includes bus movement
               "Ike 2 Scan-Out":{"server_ct" : 12, "service_time" : [2,3,5], "next_stn" : 3, "next_fem_stn" : 3, "USMAPS_frac" : 1, "next_USMAPS_stn" : 3, "next_USMAPS_fem_stn" : 3}, #2
               "Bus Movement":{"server_ct" : 300, "service_time" : [20,20,20], "next_stn" : 4, "next_fem_stn" : 4, "USMAPS_frac" : 1, "next_USMAPS_stn" : 6, "next_USMAPS_fem_stn" : 6}, #3
               "TH 2 Finance":{"server_ct" : 18, "service_time" : [3,4,5], "next_stn" : 5, "next_fem_stn" : 5, "USMAPS_frac" : 1, "next_USMAPS_stn" : 5, "next_USMAPS_fem_stn" : 5}, #4
               "TH 3 LRC Issue Point 1":{"server_ct" : 12, "service_time" : [2,3,4], "next_stn" : 6, "next_fem_stn" : 14, "USMAPS_frac" : 1, "next_USMAPS_stn" : 10, "next_USMAPS_fem_stn" : 10}, #5
               "TH 5 Med Screening 1":{"server_ct" : 36, "service_time" : [5,7,20], "next_stn" : 7, "next_fem_stn" : 7, "USMAPS_frac" : 0.5, "next_USMAPS_stn" : 13, "next_USMAPS_fem_stn" : 14}, #6
               "TH 6 Oath":{"server_ct" : 75, "service_time" : [20,20,20], "next_stn" : 8, "next_fem_stn" : 8, "USMAPS_frac" : 1, "next_USMAPS_stn" : 8, "next_USMAPS_fem_stn" : 8}, #7
               "TH 7 Med Screening 2":{"server_ct" : 36, "service_time" : [5,5,5], "next_stn" : 9, "next_fem_stn" : 9, "USMAPS_frac" : 0.2, "next_USMAPS_stn" : 9, "next_USMAPS_fem_stn" : 9},#8
               "TH 8 S1 (DD93/SGLI Verify)":{"server_ct" : 18, "service_time" : [2,3,10], "next_stn" : 10, "next_fem_stn" : 10, "USMAPS_frac" : 0.2, "next_USMAPS_stn" : 4, "next_USMAPS_fem_stn" : 4}, #9
               "TH 9 Company Holding Area":{"server_ct" : 500, "service_time" : [20,22,24], "next_stn" : 13, "next_fem_stn" : 13, "USMAPS_frac" : 1, "next_USMAPS_stn" : 15, "next_USMAPS_fem_stn" : 13}, #10
               "CA 1 Issue Point 2 (WB4)":{"server_ct" : 10, "service_time" : [2,3,4], "next_stn" : 12, "next_fem_stn" : 12, "USMAPS_frac" : 1, "next_USMAPS_stn" : 12, "next_USMAPS_fem_stn" : 12}, #11
               "LRC Issue Point 6 687":{"server_ct" : 12, "service_time" : [2,3,5], "next_stn" : 15, "next_fem_stn" : 6, "USMAPS_frac" : 0.2, "next_USMAPS_stn" : 7, "next_USMAPS_fem_stn" : 7}, #12
               "CA 2 Barber Shop":{"server_ct" : 13, "service_time" : [2,3,4], "next_stn" : 11, "next_fem_stn" : 15, "USMAPS_frac" : 1, "next_USMAPS_stn" : 11, "next_USMAPS_fem_stn" : 15}, #13
               "BH4f Female Issue Point 0":{"server_ct" : 10, "service_time" : [5,5,5], "next_fem_stn" : 11, "USMAPS_frac" : 1, "next_USMAPS_fem_stn" : 11}, #14
               "CA 5 Red Sash proceed to company":{"server_ct" : 18, "service_time" : [3,5,7], "next_stn" : 16, "next_fem_stn" : 16, "USMAPS_frac" : 1, "next_USMAPS_stn" : 16, "next_USMAPS_fem_stn" : 16}, #15
               "R-Day complete":{"server_ct" : 1, "service_time" : [0.01,0.01,0.01], "next_stn" : -99, "next_fem_stn" : -99, "USMAPS_frac" : 1, "next_USMAPS_stn" : -99, "next_USMAPS_fem_stn" : -99} #16
               } #-99 is exit station