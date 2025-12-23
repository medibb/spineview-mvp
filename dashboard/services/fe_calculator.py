"""
Flexion-Extension (FE) angle calculator
Calculates spine, pelvis, and relative FE angles
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .quaternion import quaternion_to_euler_df
from .csv_parser import synchronize_dataframes


def calculate_fe_angles(spine_df: pd.DataFrame,
                       pelvis_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate Flexion-Extension angles for spine and pelvis

    Args:
        spine_df: DataFrame with spine sensor data (quaternions)
        pelvis_df: DataFrame with pelvis sensor data (quaternions)

    Returns:
        dict: Dictionary containing:
            - time_series: Time and angle data
            - angular_velocity: Gyr data
            - acceleration: Acc data
            - metadata: Processing information
    """

    # Synchronize the two dataframes
    spine_sync, pelvis_sync = synchronize_dataframes(spine_df, pelvis_df)

    # Convert quaternions to Euler angles for both
    spine_euler = quaternion_to_euler_df(spine_sync, prefix='')
    pelvis_euler = quaternion_to_euler_df(pelvis_sync, prefix='')

    # Extract Pitch angles (Flexion-Extension)
    # Pitch is the sagittal plane rotation (forward/backward bending)
    spine_fe = spine_euler['Pitch'].values
    pelvis_fe = pelvis_euler['Pitch'].values

    # Calculate relative FE angle (spine - pelvis)
    relative_fe = spine_fe - pelvis_fe

    # Convert time from microseconds to seconds
    time_us = spine_sync['SampleTimeFine'].values
    time_sec = (time_us - time_us[0]) / 1_000_000

    # Prepare time series data
    time_series = {
        'time': time_sec.tolist(),
        'spine_fe': spine_fe.tolist(),
        'pelvis_fe': pelvis_fe.tolist(),
        'relative_fe': relative_fe.tolist(),
    }

    # Prepare angular velocity data
    angular_velocity = {
        'spine': _extract_sensor_data(spine_sync, 'Gyr'),
        'pelvis': _extract_sensor_data(pelvis_sync, 'Gyr'),
    }

    # Prepare acceleration data
    acceleration = {
        'spine': _extract_sensor_data(spine_sync, 'Acc'),
        'pelvis': _extract_sensor_data(pelvis_sync, 'Acc'),
    }

    # Add acceleration magnitude
    if all(f'Acc_{axis}' in spine_sync.columns for axis in ['X', 'Y', 'Z']):
        acceleration['spine']['magnitude'] = np.sqrt(
            spine_sync['Acc_X']**2 +
            spine_sync['Acc_Y']**2 +
            spine_sync['Acc_Z']**2
        ).tolist()

    if all(f'Acc_{axis}' in pelvis_sync.columns for axis in ['X', 'Y', 'Z']):
        acceleration['pelvis']['magnitude'] = np.sqrt(
            pelvis_sync['Acc_X']**2 +
            pelvis_sync['Acc_Y']**2 +
            pelvis_sync['Acc_Z']**2
        ).tolist()

    # Metadata
    metadata = {
        'duration_sec': round(float(time_sec[-1]), 2),
        'total_samples': len(time_sec),
        'sample_rate': round(len(time_sec) / time_sec[-1], 1) if time_sec[-1] > 0 else 0,
    }

    return {
        'time_series': time_series,
        'angular_velocity': angular_velocity,
        'acceleration': acceleration,
        'metadata': metadata,
    }


def _extract_sensor_data(df: pd.DataFrame, sensor_type: str) -> Dict[str, list]:
    """
    Extract sensor data (Gyr or Acc) from DataFrame

    Args:
        df: DataFrame with sensor columns
        sensor_type: 'Gyr' or 'Acc'

    Returns:
        dict: Dictionary with x, y, z components
    """

    data = {}

    for axis in ['X', 'Y', 'Z']:
        col_name = f'{sensor_type}_{axis}'
        if col_name in df.columns:
            data[f'{sensor_type.lower()}_{axis.lower()}'] = df[col_name].tolist()
        else:
            data[f'{sensor_type.lower()}_{axis.lower()}'] = []

    return data


def calculate_rom(angles: np.ndarray) -> float:
    """
    Calculate Range of Motion (ROM)

    Args:
        angles: Array of angles in degrees

    Returns:
        float: ROM (max - min)
    """

    return float(np.max(angles) - np.min(angles))


def calculate_angular_metrics(angles: np.ndarray) -> Dict[str, float]:
    """
    Calculate angular metrics (mean, std, max, min, ROM)

    Args:
        angles: Array of angles in degrees

    Returns:
        dict: Statistical metrics
    """

    return {
        'rom': round(calculate_rom(angles), 2),
        'mean': round(float(np.mean(angles)), 2),
        'std': round(float(np.std(angles)), 2),
        'max': round(float(np.max(angles)), 2),
        'min': round(float(np.min(angles)), 2),
    }


def calculate_velocity_metrics(gyr_y: np.ndarray) -> Dict[str, float]:
    """
    Calculate angular velocity metrics

    Args:
        gyr_y: Angular velocity in sagittal plane (deg/s)

    Returns:
        dict: Velocity metrics
    """

    abs_gyr = np.abs(gyr_y)

    return {
        'peak_angular_velocity': round(float(np.max(abs_gyr)), 2),
        'mean_angular_velocity': round(float(np.mean(abs_gyr)), 2),
        'rms_angular_velocity': round(float(np.sqrt(np.mean(gyr_y**2))), 2),
    }
