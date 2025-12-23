"""
Statistical analysis and coordination metrics
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, Tuple


def calculate_statistics(time_series: Dict[str, list],
                        angular_velocity: Dict[str, Dict],
                        acceleration: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for the analysis

    Args:
        time_series: Time series data with spine_fe, pelvis_fe, relative_fe
        angular_velocity: Angular velocity data
        acceleration: Acceleration data

    Returns:
        dict: Statistics including ROM, coordination, distributions
    """

    # Convert to numpy arrays
    spine_fe = np.array(time_series['spine_fe'])
    pelvis_fe = np.array(time_series['pelvis_fe'])
    relative_fe = np.array(time_series['relative_fe'])

    # Basic angular metrics
    spine_stats = _calculate_angle_stats(spine_fe)
    pelvis_stats = _calculate_angle_stats(pelvis_fe)
    relative_stats = _calculate_angle_stats(relative_fe)

    # Add angular velocity metrics
    if 'spine' in angular_velocity and 'gyr_y' in angular_velocity['spine']:
        spine_gyr_y = np.array(angular_velocity['spine']['gyr_y'])
        spine_stats.update(_calculate_velocity_stats(spine_gyr_y))

    if 'pelvis' in angular_velocity and 'gyr_y' in angular_velocity['pelvis']:
        pelvis_gyr_y = np.array(angular_velocity['pelvis']['gyr_y'])
        pelvis_stats.update(_calculate_velocity_stats(pelvis_gyr_y))

    # Coordination analysis
    coordination = calculate_coordination(spine_fe, pelvis_fe)

    # Distribution analysis
    distribution = {
        'spine': _calculate_distribution_stats(spine_fe),
        'pelvis': _calculate_distribution_stats(pelvis_fe),
        'relative': _calculate_distribution_stats(relative_fe),
    }

    return {
        'spine': spine_stats,
        'pelvis': pelvis_stats,
        'relative': relative_stats,
        'coordination': coordination,
        'distribution': distribution,
    }


def _calculate_angle_stats(angles: np.ndarray) -> Dict[str, float]:
    """Calculate basic angle statistics"""

    return {
        'rom': round(float(np.max(angles) - np.min(angles)), 2),
        'mean': round(float(np.mean(angles)), 2),
        'std': round(float(np.std(angles)), 2),
        'max': round(float(np.max(angles)), 2),
        'min': round(float(np.min(angles)), 2),
    }


def _calculate_velocity_stats(velocity: np.ndarray) -> Dict[str, float]:
    """Calculate angular velocity statistics"""

    abs_vel = np.abs(velocity)

    return {
        'peak_angular_velocity': round(float(np.max(abs_vel)), 2),
        'mean_angular_velocity': round(float(np.mean(abs_vel)), 2),
        'rms_angular_velocity': round(float(np.sqrt(np.mean(velocity**2))), 2),
    }


def _calculate_distribution_stats(data: np.ndarray) -> Dict[str, Any]:
    """Calculate distribution statistics"""

    # Histogram data
    hist, bin_edges = np.histogram(data, bins=30)

    # Shapiro-Wilk normality test (if enough data)
    normality_p_value = None
    is_normal = None

    if len(data) >= 3:  # Minimum for Shapiro-Wilk test
        try:
            _, p_value = stats.shapiro(data)
            normality_p_value = round(float(p_value), 4)
            is_normal = bool(p_value > 0.05)  # Common threshold, convert to Python bool
        except:
            pass

    return {
        'histogram': {
            'counts': hist.tolist(),
            'bin_edges': bin_edges.tolist(),
        },
        'quartiles': {
            'q25': round(float(np.percentile(data, 25)), 2),
            'q50': round(float(np.percentile(data, 50)), 2),  # Median
            'q75': round(float(np.percentile(data, 75)), 2),
        },
        'normality_test': {
            'p_value': normality_p_value,
            'is_normal': is_normal,
        }
    }


def calculate_coordination(spine_angles: np.ndarray,
                          pelvis_angles: np.ndarray) -> Dict[str, Any]:
    """
    Calculate lumbo-pelvic coordination metrics

    Args:
        spine_angles: Spine FE angles
        pelvis_angles: Pelvis FE angles

    Returns:
        dict: Coordination metrics including R², correlation, contribution ratio
    """

    # Linear regression (pelvis predicts spine)
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        pelvis_angles, spine_angles
    )

    r_squared = r_value ** 2

    # Pearson correlation
    pearson_r, pearson_p = stats.pearsonr(spine_angles, pelvis_angles)

    # Contribution ratio
    spine_rom = np.max(spine_angles) - np.min(spine_angles)
    pelvis_rom = np.max(pelvis_angles) - np.min(pelvis_angles)
    total_rom = spine_rom + pelvis_rom

    if total_rom > 0:
        spine_contribution = spine_rom / total_rom
        pelvis_contribution = pelvis_rom / total_rom
    else:
        spine_contribution = 0.5
        pelvis_contribution = 0.5

    # Regression line data for plotting
    pelvis_range = np.array([pelvis_angles.min(), pelvis_angles.max()])
    regression_line = {
        'x': pelvis_range.tolist(),
        'y': (slope * pelvis_range + intercept).tolist(),
    }

    # Calculate residuals for confidence interval
    predicted = slope * pelvis_angles + intercept
    residuals = spine_angles - predicted
    residual_std = np.std(residuals)

    # 95% confidence interval (approximately ±2 standard errors)
    confidence_interval = {
        'upper': (slope * pelvis_range + intercept + 1.96 * residual_std).tolist(),
        'lower': (slope * pelvis_range + intercept - 1.96 * residual_std).tolist(),
    }

    return {
        'r_squared': round(float(r_squared), 3),
        'slope': round(float(slope), 3),
        'intercept': round(float(intercept), 3),
        'pearson_r': round(float(pearson_r), 3),
        'pearson_p': round(float(pearson_p), 4),
        'contribution_ratio': {
            'spine': round(float(spine_contribution), 3),
            'pelvis': round(float(pelvis_contribution), 3),
        },
        'regression_line': regression_line,
        'confidence_interval': confidence_interval,
    }


def calculate_cross_correlation(signal1: np.ndarray,
                               signal2: np.ndarray,
                               max_lag: int = 50) -> Dict[str, Any]:
    """
    Calculate cross-correlation between two signals

    Args:
        signal1: First signal
        signal2: Second signal
        max_lag: Maximum lag to compute

    Returns:
        dict: Cross-correlation data
    """

    # Normalize signals
    sig1_norm = (signal1 - np.mean(signal1)) / np.std(signal1)
    sig2_norm = (signal2 - np.mean(signal2)) / np.std(signal2)

    # Calculate cross-correlation
    correlation = np.correlate(sig1_norm, sig2_norm, mode='full')
    correlation = correlation / len(signal1)

    # Get relevant lags
    lags = np.arange(-max_lag, max_lag + 1)
    center = len(correlation) // 2
    correlation_subset = correlation[center - max_lag:center + max_lag + 1]

    # Find peak correlation and lag
    peak_idx = np.argmax(np.abs(correlation_subset))
    peak_lag = lags[peak_idx]
    peak_corr = correlation_subset[peak_idx]

    return {
        'lags': lags.tolist(),
        'correlation': correlation_subset.tolist(),
        'peak_lag': int(peak_lag),
        'peak_correlation': round(float(peak_corr), 3),
    }
