"""Base class for water allocation mechanisms."""
import numpy as np
from abc import ABC, abstractmethod


class Mechanism(ABC):
    """Abstract base class for water allocation mechanisms."""

    def __init__(self, num_farmers: int, area: np.ndarray):
        self.num_farmers = num_farmers
        self.area = area

    @abstractmethod
    def allocate(
        self,
        demand: np.ndarray,
        canal_supply: float,
        week: int,
        theta: np.ndarray,
        theta_min: np.ndarray,
        theta_max: np.ndarray,
        stage_weight: np.ndarray,
        active: np.ndarray,
        state: dict
    ) -> tuple[np.ndarray, dict]:
        """
        Allocate surface water to farmers.

        Returns:
            surface: Array of allocated surface water (acre-mm).
            state: Updated state dictionary.
        """
        pass
