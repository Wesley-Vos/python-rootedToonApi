# pylint: disable=W0621
"""Asynchronous Python client for a rooted Toon"""

import asyncio

from rootedtoonapi import Toon

from rootedtoonapi.const import ACTIVE_STATE_AWAY, PROGRAM_STATE_ON, PROGRAM_STATE_OFF


async def main():
    """Show example on using the ToonAPI."""
    async with Toon(host="192.168.1.45") as toon:
        pass
        # status = await toon.update_climate()
        # print(status.gas_usage)
        # print(status.thermostat)

        # await toon.set_active_state(ACTIVE_STATE_AWAY)
        # await toon.set_hvac_mode(PROGRAM_STATE_ON)

        # status = await toon.update_climate()
        # print(status.gas_usage)
        # print(status.thermostat)

        # print(status.power_usage)

        status = await toon.update_energy_meter()
        print(status.gas_meter)
        print(status.electricity_meter)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
