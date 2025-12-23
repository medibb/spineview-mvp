"""
CSV Parser for Movella DOT IMU sensor data
Handles trailing commas and various CSV formats
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import io


def parse_movella_csv(file_path_or_buffer) -> pd.DataFrame:
    """
    Parse Movella DOT CSV format

    Args:
        file_path_or_buffer: File path (str) or file-like object

    Returns:
        pd.DataFrame: Parsed data with columns:
            - PacketCounter
            - SampleTimeFine
            - Quat_W, Quat_X, Quat_Y, Quat_Z
            - Acc_X, Acc_Y, Acc_Z
            - Gyr_X, Gyr_Y, Gyr_Z
            - Status

    Raises:
        ValueError: If required columns are missing
        pd.errors.ParserError: If CSV parsing fails
    """

    try:
        # Read CSV with pandas, handling trailing commas
        df = pd.read_csv(
            file_path_or_buffer,
            skipinitialspace=True,  # Strip leading spaces
            skip_blank_lines=True,
            encoding='utf-8',
            on_bad_lines='warn'  # Warn on bad lines instead of failing
        )

        # Remove any completely empty columns (from trailing commas)
        df = df.dropna(axis=1, how='all')

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # Verify required columns exist
        required_columns = ['SampleTimeFine', 'Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        # Convert to appropriate data types
        df['SampleTimeFine'] = pd.to_numeric(df['SampleTimeFine'], errors='coerce')

        for col in ['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Optional columns
        for col in ['Acc_X', 'Acc_Y', 'Acc_Z', 'Gyr_X', 'Gyr_Y', 'Gyr_Z']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove rows with NaN in critical columns
        df = df.dropna(subset=['SampleTimeFine', 'Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z'])

        # Validate quaternion normalization (|q| ≈ 1)
        quat_magnitude = np.sqrt(
            df['Quat_W']**2 + df['Quat_X']**2 +
            df['Quat_Y']**2 + df['Quat_Z']**2
        )

        # Check if quaternions are normalized (within tolerance)
        if not np.allclose(quat_magnitude, 1.0, atol=0.1):
            # Normalize quaternions if needed
            df['Quat_W'] = df['Quat_W'] / quat_magnitude
            df['Quat_X'] = df['Quat_X'] / quat_magnitude
            df['Quat_Y'] = df['Quat_Y'] / quat_magnitude
            df['Quat_Z'] = df['Quat_Z'] / quat_magnitude

        return df

    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse CSV file: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing CSV file: {str(e)}")


def get_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract metadata from parsed DataFrame

    Args:
        df: Parsed DataFrame

    Returns:
        dict: Metadata including sample count, duration, sample rate
    """

    if df.empty:
        return {
            'total_samples': 0,
            'duration_sec': 0,
            'sample_rate': 0,
            'start_time': 0,
            'end_time': 0,
        }

    # Calculate time statistics
    start_time = df['SampleTimeFine'].iloc[0]
    end_time = df['SampleTimeFine'].iloc[-1]
    duration_us = end_time - start_time
    duration_sec = duration_us / 1_000_000  # Convert microseconds to seconds

    # Estimate sample rate
    total_samples = len(df)
    sample_rate = total_samples / duration_sec if duration_sec > 0 else 0

    return {
        'total_samples': total_samples,
        'duration_sec': round(duration_sec, 2),
        'sample_rate': round(sample_rate, 1),
        'start_time': start_time,
        'end_time': end_time,
    }


def synchronize_dataframes(df1: pd.DataFrame, df2: pd.DataFrame,
                          time_column: str = 'SampleTimeFine') -> tuple:
    """
    Synchronize two DataFrames by interpolating to common timestamps

    Args:
        df1: First DataFrame (spine data)
        df2: Second DataFrame (pelvis data)
        time_column: Name of time column

    Returns:
        tuple: (synchronized_df1, synchronized_df2) with matching timestamps
    """

    # Get common time range
    start_time = max(df1[time_column].min(), df2[time_column].min())
    end_time = min(df1[time_column].max(), df2[time_column].max())

    # Filter to common time range
    df1_filtered = df1[(df1[time_column] >= start_time) & (df1[time_column] <= end_time)]
    df2_filtered = df2[(df2[time_column] >= start_time) & (df2[time_column] <= end_time)]

    # Use the timestamps from the dataframe with more samples
    if len(df1_filtered) >= len(df2_filtered):
        common_times = df1_filtered[time_column].values
        base_df = df1_filtered
        interp_df = df2_filtered
        swap = False
    else:
        common_times = df2_filtered[time_column].values
        base_df = df2_filtered
        interp_df = df1_filtered
        swap = True

    # Interpolate the other dataframe to match timestamps
    interp_df_sync = pd.DataFrame({time_column: common_times})

    for col in interp_df.columns:
        if col != time_column:
            interp_df_sync[col] = np.interp(
                common_times,
                interp_df[time_column].values,
                interp_df[col].values
            )

    # Reset index
    base_df = base_df.reset_index(drop=True)
    interp_df_sync = interp_df_sync.reset_index(drop=True)

    # Return in correct order
    if swap:
        return interp_df_sync, base_df
    else:
        return base_df, interp_df_sync
