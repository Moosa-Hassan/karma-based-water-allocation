"""Soil-moisture and crop-loss equations used by the simulation."""
from dataclasses import dataclass
from typing import NamedTuple
import numpy as np


class SoilWaterBalance(NamedTuple):
    """Result of a soil moisture update step."""
    theta: np.ndarray
    drainage_mm: np.ndarray
    et_mm: np.ndarray
    ks: np.ndarray  # water-stress coefficient


@dataclass(frozen=True)
class SoilMoistureModel:
    """Discrete soil-moisture dynamics for a group of farms."""

    root_zone_depth_mm: float = 800.0
    theta_wp: float = 0.10  # wilting point
    theta_fc: float = 0.28  # field capacity
    beta: float = 1.25  # Hassan et al.: beta = 100/efficiency
    drainage_coeff: float = 0.5  # fraction of excess water above FC that drains
    p_mad: float = 0.55  # management allowable depletion fraction for wheat

    def __post_init__(self) -> None:
        if self.root_zone_depth_mm <= 0:
            raise ValueError("root_zone_depth_mm must be positive")
        if not 0 < self.theta_wp < self.theta_fc < 1:
            raise ValueError("moisture thresholds must satisfy 0 < wp < fc < 1")
        if self.beta < 1.0:
            raise ValueError("beta must be >= 1 (Hassan et al.: beta = 100/x for x% efficiency)")
        if not 0 <= self.drainage_coeff <= 1:
            raise ValueError("drainage_coeff must be in [0, 1]")
        if not 0 < self.p_mad < 1:
            raise ValueError("p_mad must be in (0, 1)")

    def crop_coefficient(self, progress: np.ndarray) -> np.ndarray:
        """Return Kc using FAO-56 four wheat growth stages."""
        progress = np.clip(np.asarray(progress, dtype=float), 0.0, 1.0)
        coefficient = np.full(progress.shape, 0.3)

        # Initial stage (0-0.20): Kc ≈ 0.4
        initial = progress <= 0.20
        coefficient[initial] = 0.4

        # Development stage (0.20-0.55): Kc ramps from 0.4 to 1.15
        development = (progress > 0.20) & (progress <= 0.55)
        coefficient[development] = 0.4 + (1.15 - 0.4) * (progress[development] - 0.20) / (0.55 - 0.20)

        # Mid-season stage (0.55-0.85): Kc ≈ 1.15
        mid = (progress > 0.55) & (progress <= 0.85)
        coefficient[mid] = 1.15

        # Late season (0.85-1.0): Kc declines from 1.15 to 0.3
        late = progress > 0.85
        coefficient[late] = 1.15 - (1.15 - 0.3) * (progress[late] - 0.85) / (1.0 - 0.85)

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
        root_depth_mm: np.ndarray,
        crop_age_weeks: np.ndarray,
        total_weeks: int,
        week: int,
    ) -> SoilWaterBalance:
        """Apply percolation, evapotranspiration, irrigation, and rainfall.

        Returns a SoilWaterBalance with:
        - theta: updated soil moisture (dimensionless)
        - drainage_mm: water drained below root zone (mm)
        - et_mm: actual evapotranspiration (mm)
        - ks: water-stress coefficient [0, 1]
        """
        if total_weeks < 1 or week < 1:
            raise ValueError("week and total_weeks must be positive")

        theta = np.asarray(theta, dtype=float)
        irrigation_mm = np.asarray(irrigation_mm, dtype=float)
        rainfall_mm = np.asarray(rainfall_mm, dtype=float)
        root_depth_mm = np.asarray(root_depth_mm, dtype=float)
        crop_age_weeks = np.asarray(crop_age_weeks, dtype=float)

        # Get crop coefficients
        progress = np.clip(crop_age_weeks / 24.0, 0.0, 1.0)
        kc = self.crop_coefficient(progress)

        # Reference ET (mm/week) - seasonal variation for Punjab wheat
        et0_mm = 15.0 + 15.0 * week / total_weeks

        # Convert theta to water depth (mm)
        water_mm = theta * root_depth_mm

        # 1. Gross application -> effective + deep percolation loss
        effective_irr_mm = irrigation_mm / self.beta
        loss_irr_mm = irrigation_mm - effective_irr_mm

        # 2. Add water to soil
        water_mm += effective_irr_mm + rainfall_mm

        # 3. Drainage above field capacity (fast, FC-limited)
        fc_water_mm = self.theta_fc * root_depth_mm
        drainage_mm = self.drainage_coeff * np.maximum(0.0, water_mm - fc_water_mm)
        water_mm -= drainage_mm

        # 4. Water-stress coefficient (FAO-56)
        taw_mm = (self.theta_fc - self.theta_wp) * root_depth_mm  # total available water
        raw_mm = water_mm - self.theta_wp * root_depth_mm  # readily available water
        ks = np.clip(raw_mm / ((1 - self.p_mad) * taw_mm), 0.0, 1.0)

        # 5. Water-limited, stress-adjusted ET
        potential_et_mm = ks * kc * et0_mm
        max_extractable_mm = np.maximum(0.0, water_mm - self.theta_wp * root_depth_mm)
        et_mm = np.minimum(potential_et_mm, max_extractable_mm)
        water_mm -= et_mm

        # 6. Convert back to theta; floor at wilting point (physical limit)
        theta_new = np.clip(water_mm / root_depth_mm, self.theta_wp, self.theta_fc)

        return SoilWaterBalance(
            theta=theta_new,
            drainage_mm=drainage_mm + loss_irr_mm,  # total drainage for recharge
            et_mm=et_mm,
            ks=ks,
        )
