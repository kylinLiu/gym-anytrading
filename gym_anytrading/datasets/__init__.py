from .utils import load_dataset as _load_dataset
from .utils import load_dataset_online,get_kzz_miniute


# Load FOREX datasets
FOREX_EURUSD_1H_ASK = _load_dataset('FOREX_EURUSD_1H_ASK', 'Time')

# Load Stocks datasets
STOCKS_GOOGL = _load_dataset('STOCKS_GOOGL', 'Date')
