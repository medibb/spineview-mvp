"""
Quaternion to Euler angle conversion
Following aerospace conventions (ZYX rotation order)
"""

import numpy as np
import pandas as pd
from typing import Tuple, Union


def quaternion_to_euler(qw: Union[float, np.ndarray],
                       qx: Union[float, np.ndarray],
                       qy: Union[float, np.ndarray],
                       qz: Union[float, np.ndarray]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert quaternion to Euler angles (Roll, Pitch, Yaw)

    Convention:
    - Roll (X-axis): Rotation around X-axis
    - Pitch (Y-axis): Rotation around Y-axis (FLEXION-EXTENSION)
    - Yaw (Z-axis): Rotation around Z-axis

    Args:
        qw: Quaternion W component (scalar)
        qx: Quaternion X component
        qy: Quaternion Y component
        qz: Quaternion Z component

    Returns:
        tuple: (roll, pitch, yaw) in degrees

    Formula:
        Roll  = atan2(2(qw*qx + qy*qz), 1 - 2(qx² + qy²))
        Pitch = asin(2(qw*qy - qz*qx))  ← FLEXION-EXTENSION
        Yaw   = atan2(2(qw*qz + qx*qy), 1 - 2(qy² + qz²))
    """

    # Convert to numpy arrays if not already
    qw = np.asarray(qw)
    qx = np.asarray(qx)
    qy = np.asarray(qy)
    qz = np.asarray(qz)

    # Roll (X-axis rotation)
    roll = np.arctan2(
        2 * (qw * qx + qy * qz),
        1 - 2 * (qx**2 + qy**2)
    )

    # Pitch (Y-axis rotation) - FLEXION-EXTENSION
    # Clamp to avoid numerical issues with asin
    pitch_arg = 2 * (qw * qy - qz * qx)
    pitch_arg = np.clip(pitch_arg, -1.0, 1.0)
    pitch = np.arcsin(pitch_arg)

    # Yaw (Z-axis rotation)
    yaw = np.arctan2(
        2 * (qw * qz + qx * qy),
        1 - 2 * (qy**2 + qz**2)
    )

    # Convert from radians to degrees
    roll_deg = np.degrees(roll)
    pitch_deg = np.degrees(pitch)
    yaw_deg = np.degrees(yaw)

    return roll_deg, pitch_deg, yaw_deg


def quaternion_to_euler_df(df: pd.DataFrame,
                           prefix: str = '') -> pd.DataFrame:
    """
    Convert quaternion columns in DataFrame to Euler angles

    Args:
        df: DataFrame with Quat_W, Quat_X, Quat_Y, Quat_Z columns
        prefix: Optional prefix for output column names

    Returns:
        pd.DataFrame: Original DataFrame with added Roll, Pitch, Yaw columns
    """

    # Check required columns
    required_cols = ['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    # Calculate Euler angles
    roll, pitch, yaw = quaternion_to_euler(
        df['Quat_W'].values,
        df['Quat_X'].values,
        df['Quat_Y'].values,
        df['Quat_Z'].values
    )

    # Add to DataFrame
    result_df = df.copy()
    result_df[f'{prefix}Roll'] = roll
    result_df[f'{prefix}Pitch'] = pitch
    result_df[f'{prefix}Yaw'] = yaw

    return result_df


def normalize_quaternion(qw: np.ndarray, qx: np.ndarray,
                        qy: np.ndarray, qz: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Normalize quaternion to unit length

    Args:
        qw, qx, qy, qz: Quaternion components

    Returns:
        tuple: Normalized (qw, qx, qy, qz)
    """

    magnitude = np.sqrt(qw**2 + qx**2 + qy**2 + qz**2)

    # Avoid division by zero
    magnitude = np.where(magnitude < 1e-10, 1.0, magnitude)

    return (
        qw / magnitude,
        qx / magnitude,
        qy / magnitude,
        qz / magnitude
    )


def quaternion_magnitude(qw: Union[float, np.ndarray],
                        qx: Union[float, np.ndarray],
                        qy: Union[float, np.ndarray],
                        qz: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate quaternion magnitude

    Args:
        qw, qx, qy, qz: Quaternion components

    Returns:
        Quaternion magnitude |q| (should be ≈ 1.0 for normalized quaternions)
    """

    return np.sqrt(qw**2 + qx**2 + qy**2 + qz**2)
