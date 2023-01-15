from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from rootedtoonapi.util import convert_non_zero, process_data


@dataclass
class Boiler:
    """Object holding Boiler information"""

    pressure: Optional[float] = None

    def available(self) -> bool:
        return self.pressure is not None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this GasUsage object with data from a dictionary."""

        self.pressure = process_data(
            data, "boilerPressure", self.pressure, convert_non_zero
        )
