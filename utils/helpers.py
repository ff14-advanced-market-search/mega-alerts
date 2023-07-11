import json


def create_oribos_exchange_pet_link(realm_name, pet_id, region):
    fixed_realm_name = realm_name.lower().replace("'", "").replace(" ", "-")
    if region == "NA":
        url_region = "us"
    else:
        url_region = "eu"
    return f"https://oribos.exchange/#{url_region}-{fixed_realm_name}/82800-{pet_id}"


def create_oribos_exchange_item_link(realm_name, item_id, region):
    fixed_realm_name = realm_name.lower().replace("'", "").replace(" ", "-")
    if region == "NA":
        url_region = "us"
    else:
        url_region = "eu"
    return f"https://oribos.exchange/#{url_region}-{fixed_realm_name}/{item_id}"


na_wow_server_names = json.load(open("data/na-wow-connected-realm-ids.json"))
na_wow_server_ids = list(set(na_wow_server_names.values()))

eu_wow_server_names = json.load(open("data/eu-wow-connected-realm-ids.json"))
eu_wow_server_ids = list(set(eu_wow_server_names.values()))


def get_wow_realm_names_by_id(realmID):
    # fix the region info if the addon says its US and not NA
    if realmID in na_wow_server_ids:
        realm_ids = na_wow_server_ids
        realm_data = na_wow_server_names
    elif realmID in eu_wow_server_ids:
        realm_ids = eu_wow_server_ids
        realm_data = eu_wow_server_names
    else:
        print(f"realm id not found {realmID}")
        exit(1)

    # make realm name list by id
    realms_by_id = {}
    for id in realm_ids:
        realms_by_id[id] = []

    for name, id in realm_data.items():
        realms_by_id[id].append(name)

    return realms_by_id[realmID]
