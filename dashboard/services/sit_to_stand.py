"""
Sit-to-Stand Movement Analysis

This module provides analysis functions specifically for sit-to-stand movements,
including angle calculations, scoring metrics, and movement quality assessment.
"""

import numpy as np
from typing import Dict, Any
from scipy.spatial.transform import Rotation


def analyze_sit_to_stand(df_spine: 'pd.DataFrame', df_pelvis: 'pd.DataFrame') -> Dict[str, Any]:
    """
    Analyze a single sit-to-stand movement.

    Args:
        df_spine: DataFrame with spine sensor data (quaternions)
        df_pelvis: DataFrame with pelvis sensor data (quaternions)

    Returns:
        dict: Complete sit-to-stand analysis including:
            - lordosis_data: Lumbar lordosis angle time series and statistics
            - pelvic_rotation_data: Pelvic rotation metrics and score
            - trunk_lean_data: Trunk forward lean analysis and score
            - scores: Individual metric scores (0-100)
    """

    # Extract time data from DataFrame (convert microseconds to seconds)
    time_us = df_spine['SampleTimeFine'].values
    time_sec = (time_us - time_us[0]) / 1_000_000
    time_list = time_sec.tolist()

    # Calculate angles
    lordosis_angles = calculate_lumbar_lordosis(df_spine, df_pelvis)
    pelvic_rotation = calculate_pelvic_rotation(df_pelvis)
    trunk_lean = calculate_trunk_forward_lean(df_spine)

    # Calculate scores
    lordosis_score = calculate_lordosis_score(lordosis_angles)
    hip_hinge_score = calculate_hip_hinge_score(pelvic_rotation)
    trunk_lean_score = calculate_trunk_lean_strategy_score(trunk_lean)

    # Find peak trunk lean index and convert to actual time
    trunk_peak_idx = int(np.argmax(trunk_lean))
    trunk_peak_time = round(float(time_sec[trunk_peak_idx]), 2)

    # Compile results
    return {
        'lordosis_data': {
            'angles': lordosis_angles.tolist(),
            'time': time_list,
            'stats': {
                'mean': round(float(np.mean(lordosis_angles)), 2),
                'max': round(float(np.max(lordosis_angles)), 2),
                'min': round(float(np.min(lordosis_angles)), 2),
                'std': round(float(np.std(lordosis_angles)), 2),
            }
        },
        'pelvic_rotation_data': {
            'angles': pelvic_rotation.tolist(),
            'time': time_list,
            'range': round(float(np.max(pelvic_rotation) - np.min(pelvic_rotation)), 2),
            'peak': round(float(np.max(np.abs(pelvic_rotation))), 2),
        },
        'trunk_lean_data': {
            'angles': trunk_lean.tolist(),
            'time': time_list,
            'peak': round(float(np.max(trunk_lean)), 2),
            'peak_time': trunk_peak_time,
        },
        'scores': {
            'lordosis': lordosis_score,
            'hip_hinge': hip_hinge_score,
            'trunk_lean': trunk_lean_score,
        }
    }


def calculate_lumbar_lordosis(df_spine: 'pd.DataFrame', df_pelvis: 'pd.DataFrame') -> np.ndarray:
    """
    Calculate lumbar lordosis angle (relative angle between spine and pelvis).

    Lordosis = Spine FE - Pelvis FE
    Target: ≤0° (maintain neutral or flexed lumbar curve)

    Args:
        df_spine: Spine sensor DataFrame
        df_pelvis: Pelvis sensor DataFrame

    Returns:
        np.ndarray: Lordosis angles over time (degrees)
    """
    # Extract quaternions
    spine_quats = df_spine[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].values
    pelvis_quats = df_pelvis[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].values

    # Convert to Euler angles (XYZ convention, pitch is Y-axis rotation)
    spine_rotations = Rotation.from_quat(spine_quats[:, [1, 2, 3, 0]])  # scipy uses x,y,z,w
    pelvis_rotations = Rotation.from_quat(pelvis_quats[:, [1, 2, 3, 0]])

    spine_euler = spine_rotations.as_euler('xyz', degrees=True)
    pelvis_euler = pelvis_rotations.as_euler('xyz', degrees=True)

    # Extract pitch (Y-axis, flexion-extension)
    spine_fe = spine_euler[:, 1]
    pelvis_fe = pelvis_euler[:, 1]

    # Calculate relative angle (lordosis)
    lordosis = spine_fe - pelvis_fe

    return lordosis


def calculate_pelvic_rotation(df_pelvis: 'pd.DataFrame') -> np.ndarray:
    """
    Calculate pelvic rotation angle (pitch from pelvis sensor).

    Measures hip hinge utilization during sit-to-stand.
    Optimal range: 30-60° of pelvic rotation

    Args:
        df_pelvis: Pelvis sensor DataFrame

    Returns:
        np.ndarray: Pelvic rotation angles over time (degrees)
    """
    pelvis_quats = df_pelvis[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].values
    pelvis_rotations = Rotation.from_quat(pelvis_quats[:, [1, 2, 3, 0]])
    pelvis_euler = pelvis_rotations.as_euler('xyz', degrees=True)

    # Extract pitch angle (Y-axis)
    pelvic_rotation = pelvis_euler[:, 1]

    return pelvic_rotation


def calculate_trunk_forward_lean(df_spine: 'pd.DataFrame') -> np.ndarray:
    """
    Calculate trunk forward lean angle (absolute pitch from spine sensor).

    Measures trunk inclination strategy during sit-to-stand.

    Args:
        df_spine: Spine sensor DataFrame

    Returns:
        np.ndarray: Trunk lean angles over time (degrees)
    """
    spine_quats = df_spine[['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']].values
    spine_rotations = Rotation.from_quat(spine_quats[:, [1, 2, 3, 0]])
    spine_euler = spine_rotations.as_euler('xyz', degrees=True)

    # Extract pitch angle (Y-axis)
    trunk_lean = spine_euler[:, 1]

    return trunk_lean


def calculate_lordosis_score(lordosis_angles: np.ndarray) -> int:
    """
    Calculate lordosis maintenance score.

    Score = (% of movement with angle ≤0°) × 100

    Args:
        lordosis_angles: Array of lordosis angles

    Returns:
        int: Score from 0-100
    """
    frames_in_target = np.sum(lordosis_angles <= 0)
    total_frames = len(lordosis_angles)

    if total_frames == 0:
        return 0

    score = int((frames_in_target / total_frames) * 100)
    return max(0, min(100, score))  # Clamp to 0-100


def calculate_hip_hinge_score(pelvic_rotation: np.ndarray) -> int:
    """
    Calculate hip hinge utilization score.

    Optimal pelvic rotation range: 30-60°
    Score = 100 if within optimal range, scaled down otherwise

    Args:
        pelvic_rotation: Array of pelvic rotation angles

    Returns:
        int: Score from 0-100
    """
    rotation_range = np.max(pelvic_rotation) - np.min(pelvic_rotation)

    # Optimal range: 30-60 degrees
    optimal_min = 30
    optimal_max = 60

    if optimal_min <= rotation_range <= optimal_max:
        # Within optimal range
        score = 100
    elif rotation_range < optimal_min:
        # Insufficient hip hinge
        score = int((rotation_range / optimal_min) * 100)
    else:
        # Excessive rotation
        excess = rotation_range - optimal_max
        penalty = min(excess, 40)  # Max 40 point penalty
        score = 100 - int(penalty)

    return max(0, min(100, score))


def calculate_trunk_lean_strategy_score(trunk_lean: np.ndarray) -> int:
    """
    Calculate trunk lean strategy score.

    Based on:
    - Smooth progression (low acceleration variance)
    - Appropriate peak lean (20-45° forward)
    - Timing of peak (middle third of movement)

    Args:
        trunk_lean: Array of trunk lean angles

    Returns:
        int: Score from 0-100
    """
    peak_lean = np.max(trunk_lean)
    peak_idx = np.argmax(trunk_lean)
    total_frames = len(trunk_lean)

    # Component 1: Peak lean appropriateness (20-45° optimal)
    if 20 <= peak_lean <= 45:
        peak_score = 50
    elif peak_lean < 20:
        peak_score = int((peak_lean / 20) * 50)
    else:
        excess = peak_lean - 45
        penalty = min(excess, 25)
        peak_score = 50 - int(penalty)

    # Component 2: Timing of peak (middle third optimal)
    peak_position = peak_idx / total_frames
    if 0.33 <= peak_position <= 0.67:
        timing_score = 30
    else:
        # Distance from middle (0.5)
        distance = abs(peak_position - 0.5)
        timing_score = int(30 * (1 - min(distance * 2, 1)))

    # Component 3: Smoothness (low jerk)
    acceleration = np.gradient(np.gradient(trunk_lean))
    jerk = np.gradient(acceleration)
    smoothness = 1 / (1 + np.std(jerk))
    smoothness_score = int(smoothness * 20)

    total_score = peak_score + timing_score + smoothness_score

    return max(0, min(100, total_score))
