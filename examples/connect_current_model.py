# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""This is a very basic example that connects to the currently selected model
and prints the number of applications deployed to it.
"""

import asyncio
import logging

from juju.model import Model

log = logging.getLogger(__name__)


async def main():
    model = Model()
    try:
        # connect to the current model with the current user, per the Juju CLI
        await model.connect()
        print(f"There are {len(model.applications)} applications")
    finally:
        if model.is_connected():
            print("Disconnecting from model")
            await model.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
