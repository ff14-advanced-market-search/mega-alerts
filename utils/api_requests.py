import json
from datetime import datetime

import requests, os
from tenacity import retry, stop_after_attempt

from utils.helpers import get_wow_realm_names_by_id


def send_discord_message(message, webhook_url):
    try:
        json_data = {"content": message}
        requests.post(webhook_url, json=json_data)
    except Exception as ex:
        print(f"The exception was:", ex)


@retry(stop=stop_after_attempt(3))
def get_wow_access_token(client_id, client_secret):
    access_token = requests.post(
        "https://oauth.battle.net/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    ).json()["access_token"]
    return access_token


@retry(stop=stop_after_attempt(3), retry_error_callback=lambda state: {})
def get_listings_single(connectedRealmId: int, access_token: str, region: str):
    print("==========================================")
    print(f"gather data from connectedRealmId {connectedRealmId} of region {region}")
    if region == "NA":
        url = f"https://us.api.blizzard.com/data/wow/connected-realm/{str(connectedRealmId)}/auctions?namespace=dynamic-us&locale=en_US&access_token={access_token}"
    elif region == "EU":
        url = f"https://eu.api.blizzard.com/data/wow/connected-realm/{str(connectedRealmId)}/auctions?namespace=dynamic-eu&locale=en_EU&access_token={access_token}"
    else:
        print(
            f"{region} is not yet supported, reach out for us to add this region option"
        )
        exit(1)

    req = requests.get(url, timeout=25)

    if "Last-Modified" in dict(req.headers):
        try:
            last_modified = dict(req.headers)["Last-Modified"]
            local_update_timers(connectedRealmId, last_modified, region)
        except Exception as ex:
            print(f"The exception was:", ex)

    auction_info = req.json()
    return auction_info["auctions"]


def local_update_timers(dataSetID, lastUploadTimeRaw, region):
    tableName = f"{dataSetID}_singleMinPrices"
    dataSetName = get_wow_realm_names_by_id(dataSetID)

    lastUploadMinute = int(lastUploadTimeRaw.split(":")[1])
    # fix this later
    lastUploadUnix = int(
        datetime.strptime(lastUploadTimeRaw, "%a, %d %b %Y %H:%M:%S %Z").timestamp()
    )

    new_realm_time = {
        "dataSetID": dataSetID,
        "dataSetName": dataSetName,
        "lastUploadMinute": lastUploadMinute,
        "lastUploadTimeRaw": lastUploadTimeRaw,
        "lastUploadUnix": lastUploadUnix,
        "region": region,
        "tableName": tableName,
    }

    # open file
    update_timers = json.load(open("data/upload_timers.json"))
    update_timers["data"] = [
        realm_time
        for realm_time in update_timers["data"]
        if realm_time["dataSetID"] != dataSetID
    ]
    update_timers["data"].append(new_realm_time)

    # write to file again with new data
    with open("data/upload_timers.json", "w") as outfile:
        json.dump(update_timers, outfile, indent=2)


def get_update_timers(home_realm_ids, region, simple_snipe=False):
    ## new method
    if not os.path.exists("data/upload_timers.json"):
        print("initial run create upload timers file")
        with open("data/upload_timers.json", "w") as outfile:
            json.dump({}, outfile, indent=2)

    # get from api once and then file every time after
    update_timers = json.load(open("data/upload_timers.json"))
    if len(update_timers) == 0:
        update_timers = requests.post(
            "http://api.saddlebagexchange.com/api/wow/uploadtimers",
            json={},
        ).json()
        with open("data/upload_timers.json", "w") as outfile:
            json.dump(update_timers, outfile, indent=2)

    if "data" in update_timers:
        update_timers = update_timers["data"]
    else:
        print(
            "error no data found in update timers reach out on the discord: https://discord.gg/Pbp5xhmBJ7"
        )
        exit(1)

    ## old method
    # get from api every time
    # update_timers = requests.post(
    #     "http://api.saddlebagexchange.com/api/wow/uploadtimers",
    #     json={},
    # ).json()

    # cover all realms
    if home_realm_ids == []:
        # remove commodities get all others
        server_update_times = [
            time_data
            for time_data in update_timers
            if time_data["dataSetID"] not in [-1, -2] and time_data["region"] == region
        ]
    # cover specific realms
    elif simple_snipe:
        if region == "EU":
            update_id = -2
        else:
            update_id = -1
        server_update_times = [
            time_data
            for time_data in update_timers
            if time_data["dataSetID"] == update_id
        ]
    else:
        server_update_times = [
            time_data
            for time_data in update_timers
            if time_data["dataSetID"] not in [-1, -2]
            and time_data["dataSetID"] in home_realm_ids
            and time_data["region"] == region
        ]
        print(server_update_times)

    return server_update_times


def get_itemnames():
    item_names = requests.post(
        "http://api.saddlebagexchange.com/api/wow/itemnames",
        json={"return_all": True},
    ).json()

    return item_names


def get_petnames(client_id, client_secret):
    access_token = get_wow_access_token(client_id, client_secret)
    pet_info = requests.get(
        f"https://us.api.blizzard.com/data/wow/pet/index?namespace=static-us&locale=en_US&access_token={access_token}"
    ).json()["pets"]
    pet_info = {pet["id"]: pet["name"] for pet in pet_info}
    return pet_info


def simple_snipe(json_data):
    snipe_results = requests.post(
        "http://api.saddlebagexchange.com/api/wow/regionpricecheck",
        json=json_data,
    ).json()

    return snipe_results
