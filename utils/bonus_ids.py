from utils.api_requests import get_raidbots_bonus_ids


def get_bonus_ids():
    bonus_id_dict = get_raidbots_bonus_ids()
    # sockets are simple
    sockets = {k: v for k, v in bonus_id_dict.items() if "socket" in v.keys()}
    # ilvl is a bit weird but this seems to be it
    ilvl = {k: v for k, v in bonus_id_dict.items() if "base_level" in v.keys()}

    # the rest are buried in rawStats
    leech, avoidance, speed = {}, {}, {}
    for k, v in bonus_id_dict.items():
        if "rawStats" in v.keys():
            for stats in v["rawStats"]:
                if "Leech" in stats.values():
                    leech[k] = v
                if "Avoidance" in stats.values():
                    avoidance[k] = v
                if "RunSpeed" in stats.values():
                    speed[k] = v

    return {
        "sockets": sockets,
        "leech": leech,
        "avoidance": avoidance,
        "speed": speed,
        "ilvl": ilvl,
    }
