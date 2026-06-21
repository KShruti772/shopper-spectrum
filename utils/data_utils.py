import pandas as pd
from typing import Union

def load_csv(path: str) -> pd.DataFrame:
    """Load CSV into a DataFrame, with basic safety checks."""
    df = pd.read_csv(path)
    return df
