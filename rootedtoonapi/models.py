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
    convert_datetime,
    convert_kwh,
    convert_negative_none,
    convert_non_zero,
    convert_temperature,
)

from .modelss.boiler import Boiler
from .modelss.electricity_meter import ElectricityMeter
from .modelss.gas_meter import GasMeter
from .modelss.thermostat import Thermostat

class Devices:
    """Object holding all status information for this ToonAPI instance."""

    devices_discovered = False

    boiler: Boiler
    electricity_meter: ElectricityMeter
    gas_meter: GasMeter
    thermostat: Thermostat

    def __init__(self):
        """Initialize an empty RootedToonAPI Status class."""
        self.boiler = Boiler()
        self.electricity_meter = ElectricityMeter()
        self.gas_meter = GasMeter()
        self.thermostat = Thermostat()

    @property
    def has_meter_adapter(self):
        return self.electricity_meter.available() and self.gas_meter.available()
