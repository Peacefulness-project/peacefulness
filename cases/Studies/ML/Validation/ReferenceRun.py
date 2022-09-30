# The reference run to be compared with ML-trained strategies
from cases.Studies.ML. SimulationScript import create_simulation
import datetime

reference_start_date = datetime.datetime(year=2018, month=1, day=1, hour=0)
run_length = 8760 * 2  # 2 full years

create_simulation(reference_start_date, run_length)
