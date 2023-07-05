from utils.api_requests import get_raidbots_bonus_ids


def get_bonus_ids():
    bonus_id_dict = get_raidbots_bonus_ids()
    # sockets are simple
    sockets = {k: v for k, v in bonus_id_dict.items() if "socket" in v.keys()}

    leech, avoidance, speed = {}, {}, {}
    ilvl_dict = {}

    for k, v in bonus_id_dict.items():
        if "rawStats" in v.keys():
            for stats in v["rawStats"]:
                if "Leech" in stats.values():
                    leech[k] = v
                if "Avoidance" in stats.values():
                    avoidance[k] = v
                if "RunSpeed" in stats.values():
                    speed[k] = v
        if "ilevel" in v.keys():
            ilvl = int(v["ilevel"].split("@")[0].strip())
            v["ilvl"] = ilvl
            if ilvl not in ilvl_dict.keys():
                ilvl_dict[ilvl] = []
            ilvl_dict[ilvl].append({k: v})

    return {"sockets": sockets, "leech": leech, "avoidance": avoidance, "speed": speed, "ilvl": ilvl_dict}
