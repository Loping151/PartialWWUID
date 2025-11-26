from gsuid_core.models import Event


def ruser_id(ev: Event) -> str:
    from ..wutheringwaves_config.wutheringwaves_config import (
        WutheringWavesConfig,
    )

    AtCheck = WutheringWavesConfig.get_config("AtCheck").data
    if AtCheck:
        return ev.at if ev.at else ev.user_id
    else:
        return ev.user_id


def is_valid_at(ev: Event) -> bool:
    return ev.user_id != ruser_id(ev)
