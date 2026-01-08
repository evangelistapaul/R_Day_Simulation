"""
Refactored R-Day Simulation with class-based structure
This eliminates global variables and improves code organization
"""

import simpy
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse
from typing import Dict, List, Tuple

from config import (
    dir_setup, STATION_DIC, TOTAL_CUSTOMERS, ARRIVAL_RATE,
    SIMULATION_START_TIME, BUS_BATCH_SIZE, OATH_BATCH_SIZE,
    USMAPS_COUNT_MAX, USMAPS_PROBABILITY, FEMALE_COUNT_MAX,
    CUSTOMER_BATCH_SIZE
)


class RDaySimulation:
    """
    Discrete event simulation for West Point R-Day cadet processing.
    
    Attributes:
        env: SimPy environment for discrete event simulation
        mod_path: Modification path ('mod' or 'std')
        usmaps_path: USMAPS distribution strategy ('rand', 'front', or 'back')
        output_dir: Directory for output files
    """
    
    def __init__(self, mod_path: str = 'std', usmaps_path: str = 'rand', 
                 output_dir: str = None):
        """
        Initialize the R-Day simulation.
        
        Args:
            mod_path: Modification path ('mod' or 'std')
            usmaps_path: USMAPS distribution strategy ('rand', 'front', 'back')
            output_dir: Output directory path
        """
        self.mod_path = mod_path
        self.usmaps_path = usmaps_path
        self.output_dir = output_dir or dir_setup()
        
        # Initialize SimPy environment
        self.env = simpy.Environment()
        
        # Station configuration
        self.station_list = list(STATION_DIC.keys())
        self.station_idx_dic = dict(zip(self.station_list, 
                                       range(len(self.station_list))))
        
        # Resources (servers at each station)
        self.resource_list = []
        for station_name in self.station_list:
            server_count = STATION_DIC[station_name]["server_ct"]
            self.resource_list.append(simpy.Resource(self.env, server_count))
        
        # Tracking data structures
        self.time_stamp = []
        self.arc_dic = {}
        self.q_list = [[] for _ in self.station_list]
        self.q_list_time = [[] for _ in self.station_list]
        self.sex_dic = {}
        self.usmaps_dic = {}
        
        # Batch queues
        self.batch_bus_q = []
        self.batch_oath_q = []
    
    def calculate_service_time(self, station: str, cadet_id: int) -> float:
        """
        Calculate service time using triangular distribution.
        
        Args:
            station: Station name
            cadet_id: Cadet identifier
            
        Returns:
            Service time in hours
        """
        service_time_params = STATION_DIC[station]["service_time"]
        
        # Convert minutes to hours
        min_time = service_time_params[0] / 60
        mode_time = service_time_params[1] / 60
        max_time = service_time_params[2] / 60
        
        # Calculate triangular distribution parameters
        scale = max_time - min_time
        if scale == 0:
            c_param = 0
        else:
            c_param = (mode_time - min_time) / scale
        
        # Generate random service time
        service_time = stats.triang.rvs(c=c_param, loc=min_time, 
                                       scale=scale, size=1)[0]
        
        # Apply USMAPS adjustment if applicable
        if self.usmaps_dic[cadet_id] == 1:
            service_time *= STATION_DIC[station]["USMAPS_frac"]
        
        # Female cadets skip barber shop
        if self.sex_dic[cadet_id] == 0 and station == "CA 2 Barber Shop":
            service_time = 0
        
        return service_time
    
    def determine_next_station(self, station: str, cadet_id: int) -> int:
        """
        Determine the next station based on cadet characteristics.
        
        Args:
            station: Current station name
            cadet_id: Cadet identifier
            
        Returns:
            Index of next station
        """
        is_male = self.sex_dic[cadet_id] == 1
        is_usmaps = self.usmaps_dic[cadet_id] == 1
        is_modified_path = self.mod_path == 'mod'
        
        if is_male:
            if is_usmaps and is_modified_path:
                return STATION_DIC[station]["next_USMAPS_stn"]
            else:
                return STATION_DIC[station]["next_stn"]
        else:  # Female
            if is_usmaps and is_modified_path:
                return STATION_DIC[station]["next_USMAPS_fem_stn"]
            else:
                return STATION_DIC[station]["next_fem_stn"]
    
    def record_station_visit(self, cadet_id: int, station: str, 
                            finish_time: float, next_stn_idx: int):
        """
        Record data about a cadet's visit to a station.
        
        Args:
            cadet_id: Cadet identifier
            station: Station name
            finish_time: Time when service completes
            next_stn_idx: Index of next station
        """
        station_idx = self.station_idx_dic[station]
        resource = self.resource_list[station_idx]
        
        # Track arc (flow between stations)
        arc_key = f"{station_idx},{next_stn_idx}"
        self.arc_dic[arc_key] = self.arc_dic.get(arc_key, 0) + 1
        
        # Record timestamp data
        timestamp_record = [
            cadet_id,
            station_idx,
            len(resource.queue),
            resource.count,
            resource.capacity,
            station,
            finish_time,
            next_stn_idx,
            self.arc_dic[arc_key],
            resource.count
        ]
        self.time_stamp.append(timestamp_record)
        
        # Track queue lengths over time
        self.q_list[station_idx].append(len(resource.queue))
        self.q_list_time[station_idx].append(self.env.now[0] + SIMULATION_START_TIME)
    
    def generic_stn(self, cadet_id: int, station: str):
        """
        Process a cadet through a station.
        
        Args:
            cadet_id: Cadet identifier
            station: Station name
        """
        station_idx = self.station_idx_dic[station]
        service_time = self.calculate_service_time(station, cadet_id)
        
        # Request resource and process
        with self.resource_list[station_idx].request() as req:
            yield req
            finish_time = self.env.now[0] + service_time
            next_stn_idx = self.determine_next_station(station, cadet_id)
            self.record_station_visit(cadet_id, station, finish_time, next_stn_idx)
            yield self.env.timeout(service_time)
        
        # Route to next station
        if next_stn_idx > 0:
            self.route_to_next_station(cadet_id, next_stn_idx)
    
    def route_to_next_station(self, cadet_id: int, next_stn_idx: int):
        """
        Route cadet to the next station, handling batching if needed.
        
        Args:
            cadet_id: Cadet identifier
            next_stn_idx: Index of next station
        """
        if next_stn_idx == self.station_idx_dic["Bus Movement"]:
            self.batch_bus(cadet_id)
        elif next_stn_idx == self.station_idx_dic["TH 6 Oath"]:
            self.batch_oath(cadet_id)
        else:
            next_station = self.station_list[next_stn_idx]
            self.env.process(self.generic_stn(cadet_id, next_station))
    
    def batch_bus(self, cadet_id: int):
        """
        Batch cadets for bus movement to manage transportation efficiently.
        
        Args:
            cadet_id: Cadet identifier
        """
        self.batch_bus_q.append(cadet_id)
        
        # Check if batch is ready to process
        ike_idx = self.station_idx_dic["Ike 2 Scan-Out"]
        bus_idx = self.station_idx_dic["Bus Movement"]
        arc_key = f"{ike_idx},{bus_idx}"
        arc_count = self.arc_dic.get(arc_key, 0)
        
        batch_ready = (len(self.batch_bus_q) > BUS_BATCH_SIZE or 
                      arc_count == TOTAL_CUSTOMERS - 1)
        
        if batch_ready:
            for cdt in self.batch_bus_q:
                self.env.process(self.generic_stn(cdt, "Bus Movement"))
            self.batch_bus_q = []
    
    def batch_oath(self, cadet_id: int):
        """
        Batch cadets for oath ceremony.
        
        Args:
            cadet_id: Cadet identifier
        """
        self.batch_oath_q.append(cadet_id)
        
        # Calculate total cadets who have reached oath point
        lrc_idx = self.station_idx_dic["LRC Issue Point 6 687"]
        med_idx = self.station_idx_dic["TH 5 Med Screening 1"]
        oath_idx = self.station_idx_dic["TH 6 Oath"]
        
        arc_lrc_key = f"{lrc_idx},{oath_idx}"
        arc_med_key = f"{med_idx},{oath_idx}"
        
        try:
            arc_lrc_count = self.arc_dic.get(arc_lrc_key, 0)
            arc_med_count = self.arc_dic.get(arc_med_key, 0)
            arc_sum = arc_lrc_count + arc_med_count
        except:
            arc_sum = 0
        
        batch_ready = (len(self.batch_oath_q) > OATH_BATCH_SIZE or 
                      arc_sum == TOTAL_CUSTOMERS - 1)
        
        if batch_ready:
            for cdt in self.batch_oath_q:
                self.env.process(self.generic_stn(cdt, "TH 6 Oath"))
            self.batch_oath_q = []
    
    def generate_cadets(self):
        """
        Generate cadet arrivals over time.
        """
        count = 0
        start_time = 0
        female_count = 0
        usmaps_count = 0
        
        for cadet_id in range(1, TOTAL_CUSTOMERS):
            # Determine if cadet is USMAPS
            self.usmaps_dic[cadet_id] = 0
            if self._is_usmaps_cadet(cadet_id, usmaps_count):
                self.usmaps_dic[cadet_id] = 1
                usmaps_count += 1
            
            # Determine cadet gender (1=male, 0=female)
            self.sex_dic[cadet_id] = 1
            if cadet_id % 2 == 0 and female_count < FEMALE_COUNT_MAX:
                self.sex_dic[cadet_id] = 0
                female_count += 1
            
            # Generate inter-arrival time
            inter_arrival_time = stats.expon.rvs(loc=0, scale=(1/ARRIVAL_RATE), 
                                                 size=1)[0]
            yield self.env.timeout(inter_arrival_time)
            
            # Start cadet through first station
            self.env.process(self.generic_stn(cadet_id, self.station_list[0]))
            
            count += 1
            
            # Batch timing control
            if count == CUSTOMER_BATCH_SIZE:
                discount_time = self.env.now[0] - start_time
                if (1 - discount_time) > 0:
                    yield self.env.timeout(1 - discount_time)
                count = 0
                start_time = self.env.now[0]
                female_count = 0
    
    def _is_usmaps_cadet(self, cadet_id: int, usmaps_count: int) -> bool:
        """
        Determine if a cadet is USMAPS based on distribution strategy.
        
        Args:
            cadet_id: Cadet identifier
            usmaps_count: Current count of USMAPS cadets
            
        Returns:
            True if cadet is USMAPS
        """
        if usmaps_count >= USMAPS_COUNT_MAX:
            return False
        
        if self.usmaps_path == 'rand':
            return stats.uniform.rvs() < USMAPS_PROBABILITY
        elif self.usmaps_path == 'front':
            return cadet_id < USMAPS_COUNT_MAX
        elif self.usmaps_path == 'back':
            return cadet_id >= (TOTAL_CUSTOMERS - USMAPS_COUNT_MAX)
        
        return False
    
    def run(self):
        """
        Execute the simulation.
        """
        print(f"Starting simulation with USMAPS path: {self.usmaps_path}, "
              f"mod path: {self.mod_path}")
        
        self.env.process(self.generate_cadets())
        self.env.run()
        
        print("Simulation complete")
    
    def save_results(self):
        """
        Save simulation results to CSV files.
        """
        df = pd.DataFrame(self.time_stamp, columns=[
            "entity", "stn_idx", "q_length", "svc_count", "svc_capacity",
            "stn_nm", "time", "next_stn", "arc_ct", "svc_count_after"
        ])
        
        output_file = os.path.join(self.output_dir, "df_time_stamp.csv")
        df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        
        return df
    
    def plot_results(self, show_plots: bool = True):
        """
        Generate and save visualization of queue lengths.
        
        Args:
            show_plots: Whether to display plots interactively
        """
        df = pd.DataFrame(self.time_stamp, columns=[
            "entity", "stn_idx", "q_length", "svc_count", "svc_capacity",
            "stn_nm", "time", "next_stn", "arc_ct", "svc_count_after"
        ])
        
        final_time = round(df['time'].iloc[-1], 2)
        
        fig, ax = plt.subplots(nrows=4, ncols=4, figsize=(15, 12))
        fig.suptitle(f"{self.mod_path} {self.usmaps_path} | {final_time}", 
                    fontsize=24)
        
        for i in range(len(self.station_list) - 1):
            row = i // 4
            col = i % 4
            ax[row, col].scatter(self.q_list_time[i], self.q_list[i])
            ax[row, col].set_title(self.station_list[i])
        
        plt.tight_layout()
        
        filename = f"{self.mod_path}_{self.usmaps_path}.png"
        output_file = os.path.join(self.output_dir, filename)
        plt.savefig(output_file)
        
        if show_plots:
            plt.show()
        else:
            plt.close()
        
        print(f"Plot saved to {output_file}")


def parse_arguments():
    """
    Parse command line arguments.
    
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


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Create and run simulation
    sim = RDaySimulation(mod_path=args.mod, usmaps_path=args.usmaps)
    sim.run()
    
    # Save and plot results
    sim.save_results()
    sim.plot_results(show_plots=not args.no_show)
    
    # Save control file for analysis
    recent_run_file = os.path.join(sim.output_dir, "recent_run.txt")
    with open(recent_run_file, "w") as f:
        f.write(f"{args.mod} {args.usmaps}")


if __name__ == "__main__":
    main()