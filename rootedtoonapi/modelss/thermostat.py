from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


from rootedtoonapi.const import (
    ACTIVE_STATE_HOLIDAY,
    BURNER_STATE_ON,
    BURNER_STATE_PREHEATING,
    BURNER_STATE_TAP_WATER,
    PROGRAM_STATE_ON,
    PROGRAM_STATE_OVERRIDE,
)
from rootedtoonapi.util import convert_boolean, convert_datetime, convert_negative_none, convert_temperature, process_data


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
            data, "nextTime", self.next_state, convert_datetime
        )
        self.opentherm_communication_error = process_data(
            data, "otCommError", self.opentherm_communication_error, convert_boolean
        )
        self.program_state = process_data(data, "programState", self.program_state, int)
        # self.real_setpoint = process_data(
        #     data, "realSetpoint", self.real_setpoint, convert_temperature
        # )

