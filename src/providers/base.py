from abc import ABC, abstractmethod
from typing import Any, Dict


class WeatherProvider(ABC):
    name = "unknown"

    @abstractmethod
    def get_forecast(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Return weather data in the AIR-COUPLE internal format."""


class AirQualityProvider(ABC):
    name = "unknown"

    @abstractmethod
    def get_air_quality(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Return air-quality data in the AIR-COUPLE internal format."""
