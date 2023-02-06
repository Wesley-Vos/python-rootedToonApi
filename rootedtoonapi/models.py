"""Models for the rooted Toon."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from .const import (
    ACTIVE_STATE_HOLIDAY,
    BURNER_STATE_ON,
    BURNER_STATE_PREHEATING,
    BURNER_STATE_TAP_WATER,
    DEVICES,
    ENDPOINT_TO_DEVICES_MAPPING,
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
    convert_datetime_from_epoch,
    convert_kwh,
    convert_negative_none,
    convert_non_zero,
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


class Program:
    class Event:
        start_datetime: datetime
        end_datetime: Optional[datetime]
        state: str

        STATE_REMAPPING = {
            "Away": "Weg",
            "Sleep": "Slapen",
            "Comfort": "Comfort",
            "Active": "Thuis",
        }

        def __init__(self, start=None, state=None, end=None):
            self.start_datetime = start
            self.end_datetime = end
            self.state = state

        def _epoch_to_dt(self, epoch):
            return datetime.fromtimestamp(int(epoch), timezone.utc)

        def update_from_dict(self, data) -> Program.Event:
            self.start_datetime = self._epoch_to_dt(data["startTimeT"])
            self.end_datetime = self._epoch_to_dt(data["endTimeT"])
            self.state = self.STATE_REMAPPING[data["targetState"]]
            return self

    _events = [Event]

    @property
    def events(self) -> list[Event]:
        """Return a sorted list of events, ascending by start datetime"""
        return self._events

    def __init__(self) -> None:
        self._events = []

    def _create_event(self, data) -> Event:
        event = self.Event()
        return event.update_from_dict(data)

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this Program object with data from a dictionary."""
        self._events = [self._create_event(e) for e in data["programs"]]
        self._events.sort(key=lambda e: e.start_datetime)


@dataclass
class Thermostat:
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
    internal_program: Optional[Program] = None

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
        """Return if burner is pre-heating based on its state."""
        if self.burner_state is None:
            return None
        return self.burner_state == BURNER_STATE_ON

    @property
    def pre_heating(self) -> Optional[bool]:
        """Return if burner is pre-heating based on its state."""
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
        """Return if program mode is overridden."""
        if self.program_state is None:
            return None
        return self.program_state == PROGRAM_STATE_OVERRIDE

    @property
    def next_program_state(self) -> Optional[Program.Event]:
        return Program.Event(start=self.next_time, state=self.next_state)

    def update_program_from_dict(self, data: Dict[str, Any]) -> None:
        """Update the Program object with data from a dictionary."""
        if self.internal_program is None:
            self.internal_program = Program()
        self.internal_program.update_from_dict(data)

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this ThermostatInfo object with data from a dictionary."""

        self.active_state = process_data(
            data, "activeState", self.active_state, convert_negative_none
        )
        self.boiler_module_connected = True
        # self.boiler_module_connected = process_data(
        #     data, "boilerModuleConnected", self.boiler_module_connected, convert_boolean
        # )
        self.burner_state = process_data(data, "burnerInfo", self.burner_state, int)
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
            data, "currentModulationLevel", self.current_modulation_level, int
        )
        self.current_setpoint = process_data(
            data, "currentSetpoint", self.current_setpoint, convert_temperature
        )
        self.error_found = process_data(
            data, "errorFound", self.error_found, lambda x: int(x) != 255
        )
        # self.has_boiler_fault = process_data(
        #     data, "hasBoilerFault", self.has_boiler_fault, convert_boolean
        # )
        self.have_opentherm_boiler = True
        # self.have_opentherm_boiler = process_data(
        #     data, "haveOTBoiler", self.have_opentherm_boiler, convert_boolean
        # )
        self.holiday_mode = process_data(
            data, "activeState", self.holiday_mode, lambda x: x == ACTIVE_STATE_HOLIDAY
        )
        self.next_program = process_data(
            data, "nextProgram", self.next_program, convert_negative_none
        )
        self.next_setpoint = process_data(
            data, "nextSetpoint", self.next_setpoint, convert_temperature
        )
        self.next_state = process_data(
            data, "nextState", self.next_state, convert_negative_none
        )
        self.next_time = process_data(
            data, "nextTime", self.next_state, convert_datetime_from_epoch
        )
        self.opentherm_communication_error = process_data(
            data, "otCommError", self.opentherm_communication_error, convert_boolean
        )
        self.program_state = process_data(data, "programState", self.program_state, int)
        # self.real_setpoint = process_data(
        #     data, "realSetpoint", self.real_setpoint, convert_temperature
        # )


@dataclass
class Boiler:
    """Object holding Boiler information"""

    pressure: Optional[float] = None

    def available(self) -> bool:
        return self.pressure is not None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this GasUsage object with data from a dictionary."""

        if len(data.values()) > 0:
            pressure_value = list(data.values())[-1]
            self.pressure = convert_non_zero(pressure_value)


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

    @property
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

    @property
    def available(self) -> bool:
        return self._device_id is not None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this GasUsage object with data from a dictionary."""
        data = data.get(self._device_id)

        self.last_hour = process_data(data, self._key_flow, self.last_hour, convert_cm3)
        self.total = process_data(data, self._key_quantity, self.total, convert_cm3)


@dataclass
class SmartPlug:
    """Object holding Toon Smart Plug information."""

    _key_quantity = KEY_QUANTITY_ELECTRICITY
    _key_flow = KEY_FLOW_ELECTRICITY

    device_id: Optional[str] = None
    name: Optional[str] = None

    power: Optional[float] = None
    total: Optional[float] = None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this GasUsage object with data from a dictionary."""
        data = data.get(self.device_id)
        self.power = process_data(data, self._key_flow, self.power, float)
        self.total = process_data(data, self._key_quantity, self.total, convert_kwh)


@dataclass
class SmartPlugs:
    """Object holding Toon Smart Plugs information."""

    devices_discovered = False
    devices: Optional[list[SmartPlug]] = None

    def determine_devices(self, data: Dict[str, Any]):
        self.devices = []
        for device_id, device in data.items():
            dev_id = device_id.split("dev_")[1]
            if not dev_id.startswith("3") and not dev_id.startswith("settings_device"):
                smart_plug = SmartPlug(
                    device_id=device_id, name=device.get("DeviceName")
                )
                self.devices.append(smart_plug)
        self.devices_discovered = True

    @property
    def available(self) -> bool:
        return len(self.devices) > 0

    @property
    def skip(self) -> bool:
        return self.devices_discovered and not self.available

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        if not self.devices_discovered:
            self.determine_devices(data)

        if self.available:
            """Update this SmartPlugs object with data from a dictionary."""
            for device in self.devices:
                device.update_from_dict(data)


class P1Meter:
    devices_discovered = False

    electricity_meter: ElectricityMeter
    gas_meter: GasMeter

    def __init__(self):
        """Initialize an empty RootedToonAPI Status class."""
        self.electricity_meter = ElectricityMeter()
        self.gas_meter = GasMeter()

    def determine_devices(self, data: Dict[str, Any]) -> None:
        self.electricity_meter.determine_devices(data)
        self.gas_meter.determine_device(data)
        self.devices_discovered = True

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        if not self.devices_discovered:
            self.determine_devices(data)

        if self.electricity_meter.available:
            self.electricity_meter.update_from_dict(data)
        if self.gas_meter.available:
            self.gas_meter.update_from_dict(data)

    @property
    def skip(self) -> bool:
        return self.devices_discovered and not any(
            (self.electricity_meter.available, self.gas_meter.available)
        )


class Devices:
    """Object holding all status information for this ToonAPI instance."""

    boiler: Boiler
    p1_meter: P1Meter
    thermostat: Thermostat
    smart_plugs: SmartPlugs

    def __init__(self):
        """Initialize an empty RootedToonAPI Status class."""
        self.boiler = Boiler()
        self.p1_meter = P1Meter()
        self.thermostat = Thermostat()
        self.smart_plugs = SmartPlugs()

    @property
    def has_meter_adapter(self):
        return not self.p1_meter.skip
