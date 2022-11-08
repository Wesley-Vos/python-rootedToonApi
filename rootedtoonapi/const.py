"""Constants for the Quby ToonAPI."""

ACTIVE_STATE_AWAY = 3
ACTIVE_STATE_COMFORT = 0
ACTIVE_STATE_HOLIDAY = 4
ACTIVE_STATE_HOME = 1
ACTIVE_STATE_NONE = -1
ACTIVE_STATE_OFF = -1
ACTIVE_STATE_SLEEP = 2

BURNER_STATE_OFF = 0
BURNER_STATE_ON = 1
BURNER_STATE_PREHEATING = 3
BURNER_STATE_TAP_WATER = 2

ENERGY_DEVICE = "hdrv_zwave"

DEVICES = {
    "gas": ["gas", "HAE_METER_v2_1", "HAE_METER_v3_1", "HAE_METER_v4_1"],
    "electricity_usage_low_tarrif": ["elec_delivered_lt", "HAE_METER_v2_5", "HAE_METER_v3_6", "HAE_METER_v3_5",
                                     "HAE_METER_v4_6", "HAE_METER_HEAT_5", ],
    "electricity_usage_high_tarrif": ["elec_delivered_nt", "HAE_METER_v2_3", "HAE_METER_v3_3", "HAE_METER_v3_4",
                                      "HAE_METER_v4_4", "HAE_METER_HEAT_3", ],
    "electricity_production_low_tarrif": ["elec_received_lt", "HAE_METER_v2_6", "HAE_METER_v3_7", "HAE_METER_v4_7", ],
    "electricity_production_high_tarrif": ["elec_received_nt", "HAE_METER_v2_4", "HAE_METER_v3_5", "HAE_METER_v4_5", ],
}

KEY_FLOW_ELECTRICITY = "CurrentElectricityFlow"
KEY_FLOW_GAS = "CurrentGasFlow"
KEY_QUANTITY_ELECTRICITY = "CurrentElectricityQuantity"
KEY_QUANTITY_GAS = "CurrentGasQuantity"

HEATING_TYPE_GAS = 1

PROGRAM_STATE_OFF = 0
PROGRAM_STATE_ON = 1
PROGRAM_STATE_OVERRIDE = 2

THERMOSTAT_DEVICE = "happ_thermstat"

TOON_API_BASE_PATH = "/"
TOON_API_SCHEME = "http"
