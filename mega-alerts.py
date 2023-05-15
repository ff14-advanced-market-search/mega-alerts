#!/usr/bin/python3
from __future__ import print_function
import time, os, json, requests
from datetime import datetime
from tenacity import retry, stop_after_attempt
from concurrent.futures import ThreadPoolExecutor

#### GLOBALS
webhook_url = os.getenv("MEGA_WEBHOOK_URL")
if os.getenv("DESIRED_ITEMS"):
    desired_items_raw = json.loads(os.getenv("DESIRED_ITEMS"))
else:
    desired_items_raw = {}
if os.getenv("DESIRED_PETS"):
    desired_pets_raw = json.loads(os.getenv("DESIRED_PETS"))
else:
    desired_pets_raw = {}
if desired_pets_raw == {} and desired_items_raw == {}:
    print("Error you need to set env var DESIRED_ITEMS or DESIRED_PETS")
    exit(1)
desired_items, desired_pets = {}, {}
for k, v in desired_items_raw.items():
    desired_items[int(k)] = int(v)
for k, v in desired_pets_raw.items():
    desired_pets[int(k)] = int(v)

region = os.getenv("WOW_REGION")
supported_regions = ["NA", "EU"]
if region not in supported_regions:
    print(f"error pick one of these regions {supported_regions}")
    exit(1)

if region == "NA":
    wow_server_names = json.load(open("data/na-wow-connected-realm-ids.json"))
elif region == "EU":
    wow_server_names = json.load(open("data/eu-wow-connected-realm-ids.json"))

# ex '["Thrall", "Silvermoon"]'
home_realm_ids = []
if os.getenv("HOME_REALMS"):
    home_realms = json.loads(os.getenv("HOME_REALMS"))
    for r in home_realms:
        home_realm_ids.append(wow_server_names[r])


#### FUNCTIONS
def create_oribos_exchange_pet_link(realm_name, pet_id):
    fixed_realm_name = realm_name.lower().replace("'", "").replace(" ", "-")
    if region == "NA":
        url_region = "us"
    else:
        url_region = "eu"
    return f"https://oribos.exchange/#{url_region}-{fixed_realm_name}/82800-{pet_id}"


@retry(stop=stop_after_attempt(3))
def get_wow_access_token():
    access_token = requests.post(
        "https://oauth.battle.net/token",
        data={"grant_type": "client_credentials"},
        auth=(os.getenv("WOW_CLIENT_ID"), os.getenv("WOW_CLIENT_SECRET")),
    ).json()["access_token"]
    return access_token


@retry(stop=stop_after_attempt(3), retry_error_callback=lambda state: {})
def get_listings_single(connectedRealmId: int, access_token: str):
    print("==========================================")
    print(f"gather data from connectedRealmId {connectedRealmId} of region {region}")
    if region == "NA":
        url = f"https://us.api.blizzard.com/data/wow/connected-realm/{str(connectedRealmId)}/auctions?namespace=dynamic-us&locale=en_US&access_token={access_token}"
    elif region == "EU":
        url = f"https://eu.api.blizzard.com/data/wow/connected-realm/{str(connectedRealmId)}/auctions?namespace=dynamic-eu&locale=en_EU&access_token={access_token}"

    req = requests.get(url, timeout=25)

    auction_info = req.json()
    return auction_info["auctions"]


def get_update_timers():
    update_timers = requests.post(
        "http://api.saddlebagexchange.com/api/wow/uploadtimers",
        json={},
    ).json()["data"]

    # cover all realms
    if not os.getenv("HOME_REALMS"):
        # remove commodities get all others
        server_update_times = [
            time_data
            for time_data in update_timers
            if time_data["dataSetID"] not in [-1, -2]
        ]
    # cover specific realms
    else:
        server_update_times = [
            time_data
            for time_data in update_timers
            if time_data["dataSetID"] in home_realm_ids
        ]
        print(server_update_times)

    return server_update_times


# it starts here
def single_api_calls(connected_id: str):
    access_token = get_wow_access_token()
    auctions = get_listings_single(connected_id, access_token)
    clean_auctions = clean_listing_data(auctions, connected_id)
    if not clean_auctions:
        return
    for auction in clean_auctions:
        if "itemID" in auction:
            id_msg = f"`itemID:` {auction['itemID']}\n"
        else:
            id_msg = f"`petID:` {auction['petID']}\n"
        message = (
            "==================================\n"
            + f"`region:` {auction['region']} "
            + f"`realmID:` {auction['realmID']} "
            + id_msg
            + f"[wowhead / undermine link]({auction['itemlink']})\n"
            + f"realmNames: {auction['realmNames']}\n"
            + f"minPrice: {auction['minPrice']}\n"
        )
        if "buyout_prices" in auction:
            message += f"buyout_prices: {auction['buyout_prices']}\n"
        else:
            message += f"bid_prices: {auction['bid_prices']}\n"
        message += "==================================\n"

        send_discord_message(message)


def send_discord_message(message):
    try:
        json_data = {"content": message}
        requests.post(webhook_url, json=json_data)
    except Exception as ex:
        print(f"The exception was:", ex)


def clean_listing_data(auctions, connected_id):
    all_ah_buyouts, all_ah_bids = {}, {}
    pet_ah_buyouts, pet_ah_bids = {}, {}
    for item in auctions:
        # dont to pets yet
        item_id = item["item"]["id"]
        if item_id in desired_items and item_id != 82800:
            # idk why this is here, but have a feeling everything breaks without it
            price = 10000000 * 10000
            # if it has a bid use the bid price
            if "bid" in item.keys():
                price = item["bid"]
                # filter out items that are too expensive
                if price < desired_items[item_id] * 10000:
                    if item_id not in all_ah_bids.keys():
                        all_ah_bids[item_id] = [price / 10000]
                    else:
                        all_ah_bids[item_id].append(price / 10000)
            if "buyout" in item.keys():
                price = item["buyout"]
                # filter out items that are too expensive
                if price < desired_items[item_id] * 10000:
                    if item_id not in all_ah_buyouts.keys():
                        all_ah_buyouts[item_id] = [price / 10000]
                    else:
                        all_ah_buyouts[item_id].append(price / 10000)
        elif item_id == 82800:
            ## pet data example for Sophic Amalgamation
            # {
            #     'buyout': 85000000,
            #     'id': 1082597671,
            #     'item': {
            #         'id': 82800,
            #         'modifiers': [
            #             {'type': 6, 'value': 90715}
            #         ],
            #         'pet_breed_id': 14,
            #         'pet_level': 1,
            #         'pet_quality_id': 3,
            #         'pet_species_id': 2580
            #     },
            #     'quantity': 1,
            #     'time_left': 'SHORT'
            # }
            if item["item"]["pet_species_id"] in desired_pets.keys():
                pet_id = item["item"]["pet_species_id"]
                # idk why this is here, but have a feeling everything breaks without it
                price = 10000000 * 10000
                if "bid" in item.keys():
                    price = item["bid"]
                    # filter out items that are too expensive
                    if price < desired_pets[pet_id] * 10000:
                        if pet_id not in pet_ah_bids.keys():
                            pet_ah_bids[pet_id] = [price / 10000]
                        else:
                            pet_ah_bids[pet_id].append(price / 10000)
                if "buyout" in item.keys():
                    price = item["buyout"]
                    # filter out items that are too expensive
                    if price < desired_pets[pet_id] * 10000:
                        if pet_id not in pet_ah_buyouts.keys():
                            pet_ah_buyouts[pet_id] = [price / 10000]
                        else:
                            pet_ah_buyouts[pet_id].append(price / 10000)

    if (
        all_ah_buyouts == {}
        and all_ah_bids == {}
        and pet_ah_buyouts == {}
        and pet_ah_bids == {}
    ):
        print(
            f"no listings found matching items {desired_items} or pets {desired_pets} on {connected_id} {region}"
        )
        return
    else:
        return format_alert_messages(
            all_ah_buyouts,
            all_ah_bids,
            connected_id,
            pet_ah_buyouts,
            pet_ah_bids,
        )


def format_alert_messages(
    all_ah_buyouts,
    all_ah_bids,
    connected_id,
    pet_ah_buyouts,
    pet_ah_bids,
):
    results = []
    realm_names = [name for name, id in wow_server_names.items() if id == connected_id]
    for itemID, auction in all_ah_buyouts.items():
        auction.sort()
        # keep this as a list to see the price differences
        minPrice = auction[0]
        # get item names
        itemlink = f"https://www.wowhead.com/item={itemID}"

        results.append(
            {
                "region": region,
                "realmID": connected_id,
                "realmNames": realm_names,
                "itemID": itemID,
                "itemlink": itemlink,
                "minPrice": minPrice,
                "buyout_prices": json.dumps(auction),
            }
        )

    for itemID, auction in all_ah_bids.items():
        auction.sort()
        # keep this as a list to see the price differences
        minPrice = auction[0]
        # get item names
        itemlink = f"https://www.wowhead.com/item={itemID}"

        results.append(
            {
                "region": region,
                "realmID": connected_id,
                "realmNames": realm_names,
                "itemID": itemID,
                "itemlink": itemlink,
                "minPrice": minPrice,
                "bid_prices": json.dumps(auction),
            }
        )

    for petID, auction in pet_ah_buyouts.items():
        auction.sort()
        # keep this as a list to see the price differences
        minPrice = auction[0]

        # get item names
        itemlink = create_oribos_exchange_pet_link(realm_names[0], petID)

        results.append(
            {
                "region": region,
                "realmID": connected_id,
                "realmNames": realm_names,
                "petID": petID,
                "itemlink": itemlink,
                "minPrice": minPrice,
                "buyout_prices": json.dumps(auction),
            }
        )

    for petID, auction in pet_ah_bids.items():
        auction.sort()
        # keep this as a list to see the price differences
        minPrice = auction[0]

        # get item names
        itemlink = create_oribos_exchange_pet_link(realm_names[0], petID)

        results.append(
            {
                "region": region,
                "realmID": connected_id,
                "realmNames": realm_names,
                "petID": petID,
                "itemlink": itemlink,
                "minPrice": minPrice,
                "buyout_prices": json.dumps(auction),
            }
        )

    # end of the line alerts go out from here
    return results


def main():
    # # run everything once slow
    # for connected_id in set(wow_server_names.values()):
    #     single_api_calls(connected_id)

    # # run everything once fast
    # pool = ThreadPoolExecutor(max_workers=16)
    # for connected_id in set(wow_server_names.values()):
    #     pool.submit(single_api_calls, connected_id)
    # pool.shutdown(wait=True)
    # exit()

    while True:
        update_timers = get_update_timers()
        current_min = int(datetime.now().minute)

        matching_realms = [
            realm["dataSetID"]
            for realm in update_timers
            if current_min <= realm["lastUploadMinute"] <= current_min + 3
        ]
        # mega wants extra alerts
        if os.getenv("EXTRA_ALERTS"):
            extra_alert_mins = json.loads(os.getenv("EXTRA_ALERTS"))
            if current_min in extra_alert_mins:
                if not os.getenv("HOME_REALMS"):
                    matching_realms = [
                        realm["dataSetID"]
                        for realm in update_timers
                        if realm["dataSetID"] not in [-1, -2]
                    ]
                else:
                    matching_realms = [
                        realm["dataSetID"]
                        for realm in update_timers
                        if realm["dataSetID"] in home_realm_ids
                    ]

        if matching_realms != []:
            pool = ThreadPoolExecutor(max_workers=16)
            for connected_id in matching_realms:
                pool.submit(single_api_calls, connected_id)
            pool.shutdown(wait=True)
            if os.getenv("HOME_REALMS"):
                time.sleep(120)
        else:
            print(
                f"waiting for a match in update time to run check on {desired_items}, none found triggering at {datetime.now()}"
            )
            time.sleep(25)


send_discord_message("starting mega alerts")
main()
