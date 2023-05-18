import requests, os
from tenacity import retry, stop_after_attempt


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

    req = requests.get(url, timeout=25)

    auction_info = req.json()
    return auction_info["auctions"]


def get_update_timers(home_realm_ids, region):
    update_timers = requests.post(
        "http://api.saddlebagexchange.com/api/wow/uploadtimers",
        json={},
    ).json()["data"]

    # cover all realms
    if home_realm_ids == []:
        # remove commodities get all others
        server_update_times = [
            time_data
            for time_data in update_timers
            if time_data["dataSetID"] not in [-1, -2]
            and time_data["region"] == region
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
