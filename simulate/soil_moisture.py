"""Soil-moisture and crop-loss equations used by the simulation."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SoilMoistureModel:
    """Discrete soil-moisture dynamics for a group of farms."""

    root_zone_depth_mm: float = 600.0
    theta_min: float = 0.10
    theta_max: float = 0.25
    beta: float = 1.2
    percolation_rate: float = 0.01

    def __post_init__(self) -> None:
        if self.root_zone_depth_mm <= 0:
            raise ValueError("root_zone_depth_mm must be positive")
        if not 0 < self.theta_min < self.theta_max < 1:
            raise ValueError("moisture thresholds must satisfy 0 < min < max < 1")
        if self.beta < 1 or self.percolation_rate < 0:
            raise ValueError("beta must be at least 1 and percolation_rate non-negative")

    def crop_coefficient(self, progress: np.ndarray) -> np.ndarray:
        """Return Kc using the four wheat growth stages."""
        progress = np.clip(np.asarray(progress, dtype=float), 0.0, 1.0)
        coefficient = np.full(progress.shape, 0.3)
        initial = progress <= 0.25
        development = (progress > 0.25) & (progress <= 0.625)
        late = (progress > 0.625) & (progress <= 0.875)
        coefficient[initial] = 0.3 + 1.6 * progress[initial]
        coefficient[development] = 1.15
        coefficient[late] = 1.15 - 3.4 * (progress[late] - 0.625)
        return coefficient

    def wheat_coefficients(self, crop_age_weeks: np.ndarray) -> np.ndarray:
        """Farm-specific wheat Kc trajectory indexed by crop age."""
        age = np.asarray(crop_age_weeks, dtype=float)
        progress = np.clip(age / 24.0, 0.0, 1.0)
        return self.crop_coefficient(progress)

    def wheat_root_depth_mm(self, crop_age_weeks: np.ndarray) -> np.ndarray:
        """Stage-dependent effective wheat root depth."""
        age = np.asarray(crop_age_weeks, dtype=float)
        mature_depth = 800.0
        return mature_depth * np.clip(age / 8.0, 0.25, 1.0)

    def stress_weight(self, crop_age_weeks: np.ndarray) -> np.ndarray:
        """Yield sensitivity to low moisture during wheat critical stages."""
        age = np.asarray(crop_age_weeks, dtype=float)
        weights = np.full(age.shape, 0.5)
        weights[(age >= 5) & (age < 12)] = 1.0
        weights[(age >= 12) & (age < 20)] = 1.5
        weights[(age >= 20) & (age < 24)] = 0.75
        weights[age < 0] = 0.0
        weights[age >= 24] = 0.0
        return weights

    def update(
        self,
        theta: np.ndarray,
        irrigation_mm: np.ndarray,
        rainfall_mm: np.ndarray,
        week: int,
        total_weeks: int,
        growth_rate: np.ndarray,
    ) -> np.ndarray:
        """Apply percolation, evapotranspiration, irrigation, and rainfall."""
        if total_weeks < 1 or week < 1:
            raise ValueError("week and total_weeks must be positive")
        theta = np.asarray(theta, dtype=float)
        irrigation_mm = np.asarray(irrigation_mm, dtype=float)
        growth_rate = np.asarray(growth_rate, dtype=float)
        progress = growth_rate * week / total_weeks
        kc = self.crop_coefficient(progress)
        et0_mm = 15.0 + 15.0 * week / total_weeks
        after_losses = theta * np.exp(-self.percolation_rate) - kc * et0_mm / self.root_zone_depth_mm
        effective_irrigation = irrigation_mm / self.beta
        updated = after_losses + (effective_irrigation + rainfall_mm) / self.root_zone_depth_mm
        return np.clip(updated, 0.0, self.theta_max)
