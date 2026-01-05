# R-Day Simulation

A discrete-event simulation built with SimPy to model the West Point R-Day (Reception Day) cadet processing workflow.

## Overview

This simulation models the flow of new cadets through various processing stations on R-Day, including:
- Smart card issuance
- Medical screening
- Immunizations
- Uniform issue
- Administrative processing
- And more...

The simulation supports different scenarios for USMAPS (United States Military Academy Preparatory School) cadets and includes gender-specific routing.

## Project Structure

```
rday-simulation/
├── README.md
├── requirements.txt
├── .gitignore
├── config.py              # Configuration and constants
├── models.py              # Data models and structures
├── simulation.py          # Main simulation logic
├── analysis.py            # Results analysis and visualization
├── main.py                # Entry point
└── output/                # Generated results (not tracked)
    ├── df_time_stamp.csv
    ├── df_time_stamp_max.csv
    ├── *.png (queue plots)
    └── simulation.log
```

## Installation

### Requirements
- Python 3.8+
- Required packages listed in `requirements.txt`

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd rday-simulation

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the simulation with default parameters:
```bash
python main.py
```

### Command Line Options

```bash
python main.py --usmaps STRATEGY --mod PATH [OPTIONS]

Required Arguments:
  --usmaps {rand,front,back}  USMAPS cadet distribution strategy
                              rand:  Random distribution (25% probability)
                              front: First 200 cadets are USMAPS
                              back:  Last 200 cadets are USMAPS

  --mod {mod,std}            Routing modification
                              mod: Use modified USMAPS routing
                              std: Use standard routing

Optional Arguments:
  --output-dir PATH          Output directory (default: ./output)
  --no-show                  Don't display plots (only save)
  --log-level LEVEL          Logging level: DEBUG, INFO, WARNING, ERROR
  -h, --help                 Show help message
```

### Examples

```bash
# Standard run with random USMAPS distribution
python main.py --usmaps rand --mod std

# Modified path with USMAPS cadets at the front
python main.py --usmaps front --mod mod

# Run without displaying plots, with debug logging
python main.py --usmaps back --mod std --no-show --log-level DEBUG

# Specify custom output directory
python main.py --usmaps rand --mod std --output-dir ./results/run1
```

## Configuration

Edit `config.py` to modify:
- Number of customers (`TOTAL_CUSTOMERS`)
- Arrival rates (`ARRIVAL_RATE`)
- Batch sizes for bus and oath processing
- Station definitions (servers, service times, routing)
- File paths

### Station Configuration

Each station is defined with:
- `server_ct`: Number of parallel servers
- `service_time`: [min, mode, max] in minutes (triangular distribution)
- `next_stn`: Next station index for male cadets
- `next_fem_stn`: Next station index for female cadets
- `USMAPS_frac`: Service time multiplier for USMAPS cadets
- `next_USMAPS_stn`: Next station for USMAPS male cadets (modified path)
- `next_USMAPS_fem_stn`: Next station for USMAPS female cadets (modified path)

## Output Files

The simulation generates several output files in the specified output directory:

- **df_time_stamp.csv**: Complete event log with all station visits
- **df_time_stamp_max.csv**: Maximum completion time per station
- **station_max_times.txt**: Comma-separated list of max times
- **[mod]_[usmaps].png**: Queue length visualization plots
- **recent_run.txt**: Configuration of the most recent run
- **simulation.log**: Detailed execution log

## Key Features

- **Discrete Event Simulation**: Built on SimPy for accurate event-driven modeling
- **Gender-Specific Routing**: Different paths for male and female cadets
- **USMAPS Support**: Special handling for USMAPS cadets with reduced service times
- **Batch Processing**: Realistic batching for bus movement and oath ceremonies
- **Queue Tracking**: Real-time queue length monitoring at all stations
- **Comprehensive Analysis**: Automated statistics and visualizations

## Understanding the Results

### Queue Length Plots
The main output visualization shows queue lengths over time for each station. This helps identify:
- Bottlenecks in the process
- Peak congestion times
- Underutilized stations

### Completion Time
The total time for all cadets to complete R-Day processing, displayed in the plot title and summary.

### Event Log
The CSV files provide detailed timing information for every customer at every station, useful for:
- Detailed process analysis
- Validation and verification
- Custom post-processing

## Extending the Simulation

### Adding a New Station

1. Add station definition to `STATIONS` dict in `config.py`
2. Update routing in existing stations to connect to the new station
3. No code changes needed in `simulation.py` - it's data-driven!

### Modifying Service Times

Edit the `service_time` array in `config.py` for any station:
```python
"Station Name": {
    "service_time": [min_minutes, mode_minutes, max_minutes],
    # ...
}
```

### Adding New Customer Attributes

1. Add field to `Customer` class in `models.py`
2. Update customer generation in `RDaySimulation.generate_customers()`
3. Use attribute in routing or service time calculations

## Development

### Running Tests
```bash
# To be implemented
pytest tests/
```

### Code Style
The project follows PEP 8 style guidelines. Format code with:
```bash
black *.py
```

## Troubleshooting

**Issue**: `FileNotFoundError` for base path
- **Solution**: Update `BASE_PATH` in `config.py` to match your directory structure

**Issue**: Plots not displaying
- **Solution**: Ensure matplotlib backend is properly configured, or use `--no-show` flag

**Issue**: Simulation runs slowly
- **Solution**: Reduce `TOTAL_CUSTOMERS` in `config.py` for testing

## License

[Add your license here]

## Contact

[Add contact information]

## Acknowledgments

- Built with [SimPy](https://simpy.readthedocs.io/) - Discrete event simulation framework
- Developed for West Point R-Day process optimization
