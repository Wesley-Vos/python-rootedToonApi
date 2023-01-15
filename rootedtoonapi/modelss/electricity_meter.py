from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional


from rootedtoonapi.const import (
    DEVICES,
    ENDPOINT_TO_DEVICES_MAPPING,
    KEY_FLOW_ELECTRICITY,
    KEY_QUANTITY_ELECTRICITY,
)
from rootedtoonapi.util import convert_kwh, process_data



@dataclass
class ElectricityMeter:
    """Object holding Toon power usage information."""

    _device_ids: Optional[Dict[str, str]] = field(default_factory=dict)
    _device_names = [
        "electricity_delivery_low",
        "electricity_delivery_high",
        "electricity_return_low",
        "electricity_return_high",
    ]
    _key_quantity = KEY_QUANTITY_ELECTRICITY
    _key_flow = KEY_FLOW_ELECTRICITY

    electricity_delivery_low: Optional[float] = None
    electricity_delivered_low: Optional[float] = None
    electricity_delivery_high: Optional[float] = None
    electricity_delivered_high: Optional[float] = None
    electricity_returned_low: Optional[float] = None
    electricity_return_low: Optional[float] = None
    electricity_returned_high: Optional[float] = None
    electricity_return_high: Optional[float] = None

    def determine_devices(self, devices_data):
        for device_id, device in devices_data.items():
            for device_name in self._device_names:
                device_types = DEVICES.get(device_name)
                if device.get("type") in device_types:
                    if device[self._key_quantity] != "NaN":
                        self._device_ids[device_name] = device_id

    def available(self) -> bool:
        return len(self._device_ids) > 0

    def endpoint_available(self, endpoint) -> bool:
        return all(
            map(
                lambda dev: dev in self._device_ids,
                ENDPOINT_TO_DEVICES_MAPPING[endpoint],
            )
        )

    @property
    def electricity_return(self) -> Optional[float]:
        if self.electricity_return_low is None or self.electricity_return_high is None:
            return None
        return self.electricity_return_low + self.electricity_return_high

    @property
    def electricity_delivery(self) -> Optional[float]:
        if (
            self.electricity_delivery_low is None
            or self.electricity_delivery_high is None
        ):
            return None
        return self.electricity_delivery_low + self.electricity_delivery_high

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this PowerUsage object with data from a dictionary."""

        for device_name, device_id in self._device_ids.items():
            value = process_data(
                data[device_id],
                self._key_flow,
                getattr(self, device_name),
                lambda x: int(float(x)),
            )
            setattr(self, device_name, value)

            name = device_name.replace("delivery", "delivered").replace(
                "return", "returned"
            )
            value = process_data(
                data[device_id], self._key_quantity, getattr(self, name), convert_kwh
            )
            setattr(self, name, value)

