# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""This example:

1. Connects to the current model
2. Resets it
3. Deploys two charms and relates them
4. Waits for units to be idle, then exits

"""

import asyncio
import logging

from juju.model import Model, ModelObserver


class MyRemoveObserver(ModelObserver):
    async def on_change(self, delta, old, new, model):
        if delta.type == "remove":
            assert new.latest() == new
            assert new.next() is None
            assert new.dead
            assert new.current
            assert new.connected
            assert new.previous().dead
            assert not new.previous().current
            assert not new.previous().connected


class MyModelObserver(ModelObserver):
    _shutting_down = False

    async def on_change(self, delta, old, new, model):
        if model.units and model.all_units_idle() and not self._shutting_down:
            self._shutting_down = True
            logging.debug("All units idle, disconnecting")
            await model.reset(force=True)
            await model.disconnect()


async def main():
    model = Model()
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        model.add_observer(MyRemoveObserver())
        await model.reset(force=True)
        model.add_observer(MyModelObserver())

        ubuntu_app = await model.deploy(
            "ch:ubuntu",
            application_name="ubuntu",
            series="trusty",
            channel="stable",
        )
        ubuntu_app.on_change(
            asyncio.coroutine(
                lambda delta, old_app, new_app, model: print(
                    f"App changed: {new_app.entity_id}"
                )
            )
        )
        ubuntu_app.on_remove(
            asyncio.coroutine(
                lambda delta, old_app, new_app, model: print(
                    f"App removed: {old_app.entity_id}"
                )
            )
        )
        ubuntu_app.on_unit_add(
            asyncio.coroutine(
                lambda delta, old_unit, new_unit, model: print(
                    f"Unit added: {new_unit.entity_id}"
                )
            )
        )
        ubuntu_app.on_unit_remove(
            asyncio.coroutine(
                lambda delta, old_unit, new_unit, model: print(
                    f"Unit removed: {old_unit.entity_id}"
                )
            )
        )
        unit_a, _unit_b = await ubuntu_app.add_units(count=2)
        unit_a.on_change(
            asyncio.coroutine(
                lambda delta, old_unit, new_unit, model: print(
                    f"Unit changed: {new_unit.entity_id}"
                )
            )
        )
        await model.deploy(
            "ch:nrpe",
            application_name="nrpe",
            series="trusty",
            channel="stable",
            # subordinates must be deployed without units
            num_units=0,
        )
        my_relation = await model.relate(
            "ubuntu",
            "nrpe",
        )
        my_relation.on_remove(
            asyncio.coroutine(
                lambda delta, old_rel, new_rel, model: print(
                    f"Relation removed: {old_rel.endpoints}"
                )
            )
        )
    finally:
        await model.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ws_logger = logging.getLogger("websockets.protocol")
    ws_logger.setLevel(logging.INFO)
    asyncio.run(main())
