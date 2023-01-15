from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional


from rootedtoonapi.const import (
    DEVICES,
    KEY_FLOW_GAS,
    KEY_QUANTITY_GAS,
)

from rootedtoonapi.util import convert_cm3, process_data


@dataclass
class GasMeter:
    """Object holding Toon gas usage information."""

    _device_id: Optional[str] = None
    _device_name = "gas"
    _key_quantity = KEY_QUANTITY_GAS
    _key_flow = KEY_FLOW_GAS

    last_hour: Optional[float] = None
    total: Optional[float] = None

    def determine_device(self, devices_data):
        for device_id, device in devices_data.items():
            if device.get("type") in DEVICES[self._device_name]:
                if device[self._key_quantity] != "NaN":
                    self._device_id = device_id

    def available(self) -> bool:
        return self._device_id is not None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this GasUsage object with data from a dictionary."""
        data = data.get(self._device_id)

        self.last_hour = process_data(data, self._key_flow, self.last_hour, convert_cm3)
        self.total = process_data(data, self._key_quantity, self.total, convert_cm3)

