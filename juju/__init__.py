# Copyright 2024 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
"""Python Library for Juju."""

try:
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()
except ImportError:
    pass
