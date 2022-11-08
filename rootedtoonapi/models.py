"""Models for the rooted Toon."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from .const import (
    ACTIVE_STATE_HOLIDAY,
    BURNER_STATE_ON,
    BURNER_STATE_PREHEATING,
    BURNER_STATE_TAP_WATER,
    DEVICES,
    KEY_FLOW_GAS,
    KEY_FLOW_ELECTRICITY,
    KEY_QUANTITY_GAS,
    KEY_QUANTITY_ELECTRICITY,
    PROGRAM_STATE_ON,
    PROGRAM_STATE_OVERRIDE,
)
from .util import (
    convert_boolean,
    convert_cm3,
    convert_datetime,
    convert_kwh,
    convert_negative_none,
    convert_temperature,
)


def process_data(
        data: Dict[str, Any],
        key: str,
        current_value: Any,
        conversion: Optional[Callable[[Any], Any]] = None,
) -> Any:
    """test."""
    if key not in data:
        return current_value

    if data[key] is None:
        return current_value

    if conversion is None:
        return data[key]

    return conversion(data[key])


@dataclass
class ThermostatInfo:
    """Object holding Toon thermostat information."""

    active_state: Optional[int] = None
    boiler_module_connected: Optional[bool] = None
    burner_state: Optional[int] = None
    current_display_temperature: Optional[float] = None
    current_humidity: Optional[int] = None
    current_modulation_level: Optional[int] = None
    current_setpoint: Optional[float] = None
    error_found: Optional[bool] = None
    has_boiler_fault: Optional[bool] = None
    have_opentherm_boiler: Optional[bool] = None
    holiday_mode: Optional[bool] = None
    next_program: Optional[int] = None
    next_setpoint: Optional[float] = None
    next_state: Optional[int] = None
    next_time: Optional[datetime] = None
    opentherm_communication_error: Optional[bool] = None
    program_state: Optional[int] = None
    real_setpoint: Optional[float] = None
    set_by_load_shifthing: Optional[int] = None

    last_updated_from_display: Optional[datetime] = None
    last_updated: datetime = datetime.utcnow()

    @property
    def burner(self) -> Optional[bool]:
        """Return if burner is on based on its state."""
        if self.burner_state is None:
            return None
        return bool(self.burner_state)

    @property
    def hot_tapwater(self) -> Optional[bool]:
        """Return if burner is on based on its state."""
        if self.burner_state is None:
            return None
        return self.burner_state == BURNER_STATE_TAP_WATER

    @property
    def heating(self) -> Optional[bool]:
        """Return if burner is pre heating based on its state."""
        if self.burner_state is None:
            return None
        return self.burner_state == BURNER_STATE_ON

    @property
    def pre_heating(self) -> Optional[bool]:
        """Return if burner is pre heating based on its state."""
        if self.burner_state is None:
            return None
        return self.burner_state == BURNER_STATE_PREHEATING

    @property
    def program(self) -> Optional[bool]:
        """Return if program mode is turned on."""
        if self.program_state is None:
            return None
        return self.program_state in [PROGRAM_STATE_ON, PROGRAM_STATE_OVERRIDE]

    @property
    def program_overridden(self) -> Optional[bool]:
        """Return if program mode is overriden."""
        if self.program_state is None:
            return None
        return self.program_state == PROGRAM_STATE_OVERRIDE

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this ThermostatInfo object with data from a dictionary."""

        self.active_state = process_data(
            data,
            "activeState",
            self.active_state,
            convert_negative_none
        )
        # self.boiler_module_connected = process_data(
        #     data, "boilerModuleConnected", self.boiler_module_connected, convert_boolean
        # )
        self.burner_state = process_data(
            data,
            "burnerInfo",
            self.burner_state,
            int)
        # self.current_humidity = process_data(
        #     data, "currentHumidity", self.current_humidity
        # )
        self.current_display_temperature = process_data(
            data,
            "currentTemp",
            self.current_display_temperature,
            convert_temperature,
        )
        self.current_modulation_level = process_data(
            data,
            "currentModulationLevel",
            self.current_modulation_level,
            int
        )
        self.current_setpoint = process_data(
            data,
            "currentSetpoint",
            self.current_setpoint,
            convert_temperature
        )
        self.error_found = process_data(
            data, "errorFound",
            self.error_found,
            lambda x: int(x) != 255
        )
        # self.has_boiler_fault = process_data(
        #     data, "hasBoilerFault", self.has_boiler_fault, convert_boolean
        # )
        # self.have_opentherm_boiler = process_data(
        #     data, "haveOTBoiler", self.have_opentherm_boiler, convert_boolean
        # )
        self.holiday_mode = process_data(
            data,
            "activeState",
            self.holiday_mode,
            lambda x: x == ACTIVE_STATE_HOLIDAY
        )
        self.next_program = process_data(
            data,
            "nextProgram",
            self.next_program,
            convert_negative_none
        )
        self.next_setpoint = process_data(
            data,
            "nextSetpoint",
            self.next_setpoint,
            convert_temperature
        )
        self.next_state = process_data(
            data,
            "nextState",
            self.next_state,
            convert_negative_none
        )
        self.next_time = process_data(
            data,
            "nextTime",
            self.next_state,
            convert_datetime
        )
        self.opentherm_communication_error = process_data(
            data,
            "otCommError",
            self.opentherm_communication_error,
            convert_boolean
        )
        self.program_state = process_data(
            data,
            "programState",
            self.program_state,
            int
        )
        # self.real_setpoint = process_data(
        #     data, "realSetpoint", self.real_setpoint, convert_temperature
        # )
        # self.set_by_load_shifthing = process_data(
        #     data, "setByLoadShifting", self.set_by_load_shifthing, convert_boolean
        # )
        #
        # self.last_updated_from_display = process_data(
        #     data,
        #     "lastUpdatedFromDisplay",
        #     self.last_updated_from_display,
        #     convert_datetime,
        # )
        # self.last_updated = datetime.utcnow()


@dataclass
class PowerUsage:
    """Object holding Toon power usage information."""

    _device_ids: Optional[Dict[str, str]] = field(default_factory=dict)
    _device_names = [
        "electricity_usage_low_tarrif",
        "electricity_usage_high_tarrif",
        "electricity_production_low_tarrif",
        "electricity_production_high_tarrif"
    ]
    _key_quantity = KEY_QUANTITY_ELECTRICITY
    _key_flow = KEY_FLOW_ELECTRICITY

    electricity_usage_low_tarrif: Optional[float] = None
    electricity_used_low_tarrif: Optional[float] = None
    electricity_usage_high_tarrif: Optional[float] = None
    electricity_used_high_tarrif: Optional[float] = None
    electricity_produced_low_tarrif: Optional[float] = None
    electricity_production_low_tarrif: Optional[float] = None
    electricity_produced_high_tarrif: Optional[float] = None
    electricity_production_high_tarrif: Optional[float] = None

    def determine_devices(self, devices_data):
        for device_id, device in devices_data.items():
            for device_name in self._device_names:
                print(device_name)
                device_types = DEVICES.get(device_name)
                if device.get("type") in device_types:
                    if device[self._key_quantity] != "NaN":
                        self._device_ids[device_name] = device_id

    # @property
    # def day_usage(self) -> Optional[float]:
    #     """Calculate day total usage."""
    #     if self.day_high_usage is None or self.day_low_usage is None:
    #         return None
    #     return round(self.day_high_usage + self.day_low_usage, 2)
    #
    # @property
    # def day_to_grid_usage(self) -> Optional[float]:
    #     """Calculate day total to grid."""
    #     if self.day_usage is None or self.day_produced_solar is None:
    #         return None
    #     return abs(min(0.0, round(self.day_usage - self.day_produced_solar, 2)))
    #
    # @property
    # def day_from_grid_usage(self) -> Optional[float]:
    #     """Calculate day total to grid."""
    #     if self.day_produced_solar is None or self.day_usage is None:
    #         return None
    #     return abs(min(0.0, round(self.day_produced_solar - self.day_usage, 2)))
    #
    # @property
    # def current_covered_by_solar(self) -> Optional[int]:
    #     """Calculate current solar covering current usage."""
    #     if self.current_solar is None or self.current is None:
    #         return None
    #     return min(100, round((self.current_solar / self.current) * 100))

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this PowerUsage object with data from a dictionary."""

        for device_name, device_id in self._device_ids.items():
            value = process_data(data[device_id], self._key_flow, getattr(self, device_name), lambda x: int(float(x)))
            setattr(self, device_name, value)

            name = device_name.replace("usage", "used").replace("production", "produced")
            value = process_data(data[device_id], self._key_quantity, getattr(self, name), convert_kwh)
            setattr(self, name, value)


@dataclass
class GasUsage:
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

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this GasUsage object with data from a dictionary."""
        data = data.get(self._device_id)

        self.last_hour = process_data(data, self._key_flow, self.last_hour, convert_cm3)
        self.total = process_data(data, self._key_quantity, self.total, convert_cm3)


class Status:
    """Object holding all status information for this ToonAPI instance."""

    thermostat: ThermostatInfo = ThermostatInfo()
    power_usage: PowerUsage = PowerUsage()
    gas_usage: GasUsage = GasUsage()
    devices_set = False

    last_updated_from_display: Optional[datetime] = None
    last_updated: datetime = datetime.utcnow()
    server_time: Optional[datetime] = None

    def __init__(self):
        """Initialize an empty RootedToonAPI Status class."""

    def update_from_dict(self, data: Dict[str, Any]) -> Status:
        """Update the status object with data received from the ToonAPI."""
        if "thermostatInfo" in data:
            self.thermostat.update_from_dict(data["thermostatInfo"])
        # if "powerUsage" in data:
        #     self.power_usage.update_from_dict(data["powerUsage"])
        # if "gasUsage" in data:
        #     self.gas_usage.update_from_dict(data["gasUsage"])
        if "lastUpdateFromDisplay" in data:
            self.last_updated_from_display = convert_datetime(
                data["lastUpdateFromDisplay"]
            )
        if "serverTime" in data:
            self.server_time = convert_datetime(data["serverTime"])
        self.last_updated = datetime.utcnow()

        return self
