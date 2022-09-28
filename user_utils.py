from typing import List, Optional
import pandas as pd


def hash_password(password: str) -> str:
    return password


def verify_password(hashed_password: str, normal_password: str) -> bool:
    return hash_password(normal_password) == hashed_password


def write_to_csv(
    pd_dataframe: pd.DataFrame,
    csv_file_name: str,
    header: Optional[List[str]],
    mode: str,
) -> None:
    pd_dataframe.to_csv(
        csv_file_name,
        sep=",",
        mode=mode,
        header=header,
        index=False,
    )
