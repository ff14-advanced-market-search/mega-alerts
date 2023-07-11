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
def get_wow_access_token():
    access_token = requests.post(
        "https://oauth.battle.net/token",
        data={"grant_type": "client_credentials"},
        auth=(os.getenv("WOW_CLIENT_ID"), os.getenv("WOW_CLIENT_SECRET")),
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
        last_modified = dict(req.headers)["Last-Modified"]
        local_update_timers(connectedRealmId, last_modified, region)

    auction_info = req.json()
    return auction_info["auctions"]


def local_update_timers(dataset, lastUploadTimeRaw, region):
    # (dataSetID INT PRIMARY KEY, tableName VARCHAR(255), dataSetName VARCHAR(255), region VARCHAR(255), lastUploadTimeRaw VARCHAR(255), lastUploadMinute INT, lastUploadUnix BIGINT)

    dataSetID = dataset
    tableName = f"{dataset}_singleMinPrices"
    dataSetName = get_wow_realm_names_by_id(dataset)

    lastUploadMinute = int(lastUploadTimeRaw.split(":")[1])
    # fix this later
    lastUploadUnix = int(
        datetime.strptime(lastUploadTimeRaw, "%a, %d %b %Y %H:%M:%S %Z").timestamp()
    )

    print("raw api data for", tableName, "last updated", lastUploadTimeRaw)

    # create values
    val_list = [
        (
            str(dataSetID),
            tableName,
            json.dumps(dataSetName),
            region,
            str(lastUploadTimeRaw),
            str(lastUploadMinute),
            str(lastUploadUnix),
        )
    ]


def get_update_timers(home_realm_ids, region):
    # update_timers = requests.post(
    #     "http://api.saddlebagexchange.com/api/wow/uploadtimers",
    #     json={},
    # ).json()["data"]
    update_timers = json.load(open("data/upload_timers.json"))["data"]

    # cover all realms
    if home_realm_ids == []:
        # remove commodities get all others
        server_update_times = [
            time_data
            for time_data in update_timers
            if time_data["dataSetID"] not in [-1, -2] and time_data["region"] == region
        ]
    # cover specific realms
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


def get_petnames():
    access_token = get_wow_access_token()
    pet_info = requests.get(
        f"https://us.api.blizzard.com/data/wow/pet/index?namespace=static-us&locale=en_US&access_token={access_token}"
    ).json()["pets"]
    pet_info = {pet["id"]: pet["name"] for pet in pet_info}
    return pet_info
