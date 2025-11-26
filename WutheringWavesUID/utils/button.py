from gsuid_core.message_models import Button
from gsuid_core.sv import get_plugin_available_prefix

PREFIX = get_plugin_available_prefix("WutheringWavesUID")


class WavesButton(Button):
    prefix = PREFIX
