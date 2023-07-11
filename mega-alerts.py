#!/usr/bin/python3
from __future__ import print_function
import time, os, json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from utils.api_requests import (
    get_wow_access_token,
    get_listings_single,
    get_update_timers,
    send_discord_message,
    get_itemnames,
    get_petnames,
)
from utils.helpers import (
    create_oribos_exchange_pet_link,
    create_oribos_exchange_item_link,
)

#### GLOBALS ####
alert_record = []
item_names = get_itemnames()
pet_names = get_petnames()

#### CONTANTS ####
WEBHOOK_URL = os.getenv("MEGA_WEBHOOK_URL")
WOWHEAD_LINK = os.getenv("WOWHEAD_LINK")
SHOW_BIDPRICES = os.getenv("SHOW_BID_PRICES")

REGION = os.getenv("WOW_REGION")
EXTRA_ALERTS = os.getenv("EXTRA_ALERTS")
ADD_DELAY = os.getenv("ADD_DELAY")

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

if REGION == "NA" or REGION == "US":
    REGION = "NA"
    WOW_SERVER_NAMES = json.load(open("data/na-wow-connected-realm-ids.json"))
elif REGION == "EU":
    WOW_SERVER_NAMES = json.load(open("data/eu-wow-connected-realm-ids.json"))
else:
    print(f"error region is not valid choose NA, US or EU")
    exit(1)

home_realm_ids = []
if os.getenv("HOME_REALMS"):
    HOME_REALMS = json.loads(os.getenv("HOME_REALMS"))
    for r in HOME_REALMS:
        home_realm_ids.append(WOW_SERVER_NAMES[r])


#### FUNCTIONS ####
def pull_single_realm_data(connected_id, access_token):
    auctions = get_listings_single(connected_id, access_token, REGION)
    clean_auctions = clean_listing_data(auctions, connected_id)
    if not clean_auctions:
        return
    for auction in clean_auctions:
        if "itemID" in auction:
            id_msg = f"`itemID:` {auction['itemID']}\n"
            if str(auction["itemID"]) in item_names:
                item_name = item_names[str(auction["itemID"])]
                id_msg += f"`Name:` {item_name}\n"
        else:
            id_msg = f"`petID:` {auction['petID']}\n"
            if auction["petID"] in pet_names:
                pet_name = pet_names[auction["petID"]]
                id_msg += f"`Name:` {pet_name}\n"
        message = (
            "==================================\n"
            + f"`region:` {REGION} "
            + f"`realmID:` {auction['realmID']} "
            + id_msg
            + f"[Undermine link]({auction['itemlink']})\n"
            + f"realmNames: {auction['realmNames']}\n"
        )
        if WOWHEAD_LINK and auction["itemID"]:
            item_id = auction["itemID"]
            message += f"https://www.wowhead.com/item={item_id}"
        if "bid_prices" in auction:
            message += f"bid_prices: {auction['bid_prices']}\n"
        else:
            message += f"buyout_prices: {auction['buyout_prices']}\n"
        message += "==================================\n"
        if auction not in alert_record:
            send_discord_message(message, WEBHOOK_URL)
            alert_record.append(auction)


def clean_listing_data(auctions, connected_id):
    all_ah_buyouts, all_ah_bids = {}, {}
    pet_ah_buyouts, pet_ah_bids = {}, {}
    for item in auctions:
        item_id = item["item"]["id"]
        # regular items
        if item_id in desired_items and item_id != 82800:
            # idk why this is here, but have a feeling everything breaks without it
            price = 10000000 * 10000
            # if it has a bid use the bid price
            if "bid" in item.keys() and SHOW_BIDPRICES == "true":
                price = item["bid"]
                # filter out items that are too expensive
                if price < desired_items[item_id] * 10000:
                    if item_id not in all_ah_bids.keys():
                        all_ah_bids[item_id] = [price / 10000]
                    elif price / 10000 not in all_ah_bids[item_id]:
                        all_ah_bids[item_id].append(price / 10000)
            if "buyout" in item.keys():
                price = item["buyout"]
                # filter out items that are too expensive
                if price < desired_items[item_id] * 10000:
                    if item_id not in all_ah_buyouts.keys():
                        all_ah_buyouts[item_id] = [price / 10000]
                    elif price / 10000 not in all_ah_buyouts[item_id]:
                        all_ah_buyouts[item_id].append(price / 10000)
        # all caged battle pets have item id 82800
        elif item_id == 82800:
            if item["item"]["pet_species_id"] in desired_pets.keys():
                pet_id = item["item"]["pet_species_id"]
                # idk why this is here, but have a feeling everything breaks without it
                price = 10000000 * 10000
                if "bid" in item.keys() and SHOW_BIDPRICES == "true":
                    price = item["bid"]
                    # filter out items that are too expensive
                    if price < desired_pets[pet_id] * 10000:
                        if pet_id not in pet_ah_bids.keys():
                            pet_ah_bids[pet_id] = [price / 10000]
                        elif price / 10000 not in pet_ah_bids[pet_id]:
                            pet_ah_bids[pet_id].append(price / 10000)
                if "buyout" in item.keys():
                    price = item["buyout"]
                    # filter out items that are too expensive
                    if price < desired_pets[pet_id] * 10000:
                        if pet_id not in pet_ah_buyouts.keys():
                            pet_ah_buyouts[pet_id] = [price / 10000]
                        elif price / 10000 not in pet_ah_buyouts[pet_id]:
                            pet_ah_buyouts[pet_id].append(price / 10000)

    if (
        all_ah_buyouts == {}
        and all_ah_bids == {}
        and pet_ah_buyouts == {}
        and pet_ah_bids == {}
    ):
        print(
            f"no listings found matching items {desired_items} or pets {desired_pets} on {connected_id} {REGION}"
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
    realm_names = [name for name, id in WOW_SERVER_NAMES.items() if id == connected_id]
    for itemID, auction in all_ah_buyouts.items():
        # use instead of item name
        itemlink = create_oribos_exchange_item_link(realm_names[0], itemID, REGION)
        results.append(
            results_dict(
                auction, itemlink, connected_id, realm_names, itemID, "itemID", "buyout"
            )
        )

    for petID, auction in pet_ah_buyouts.items():
        # use instead of item name
        itemlink = create_oribos_exchange_pet_link(realm_names[0], petID, REGION)
        results.append(
            results_dict(
                auction, itemlink, connected_id, realm_names, petID, "petID", "buyout"
            )
        )

    if SHOW_BIDPRICES == "true":
        for itemID, auction in all_ah_bids.items():
            # use instead of item name
            itemlink = create_oribos_exchange_item_link(realm_names[0], itemID, REGION)
            results.append(
                results_dict(
                    auction,
                    itemlink,
                    connected_id,
                    realm_names,
                    itemID,
                    "itemID",
                    "bid",
                )
            )

        for petID, auction in pet_ah_bids.items():
            # use instead of item name
            itemlink = create_oribos_exchange_pet_link(realm_names[0], petID)
            results.append(
                results_dict(
                    auction, itemlink, connected_id, realm_names, petID, "petID", "bid"
                )
            )

    # end of the line alerts go out from here
    return results


def results_dict(auction, itemlink, connected_id, realm_names, id, idType, priceType):
    auction.sort()
    minPrice = auction[0]
    return {
        "region": REGION,
        "realmID": connected_id,
        "realmNames": realm_names,
        f"{idType}": id,
        "itemlink": itemlink,
        "minPrice": minPrice,
        f"{priceType}_prices": json.dumps(auction),
    }


def send_upload_timer_message(update_timers):
    update_timers.sort(key=lambda x: x["lastUploadMinute"])
    upload_msg = "```"
    for realm_info in update_timers:
        if realm_info not in alert_record:
            upload_msg += (
                f"{realm_info['lastUploadMinute']} : {realm_info['dataSetName']}\n"
            )
            alert_record.append(realm_info)
        if len(upload_msg) > 1500:
            send_discord_message(f"{upload_msg}```", WEBHOOK_URL)
            upload_msg = "```"

    if upload_msg != "```":
        send_discord_message(f"{upload_msg}```", WEBHOOK_URL)


#### MAIN ####
def main():
    global alert_record
    global item_names
    update_timers = get_update_timers(home_realm_ids, REGION)
    while True:
        current_min = int(datetime.now().minute)
        # clear out the alert record once an hour
        if current_min == 0:
            print("\n\nClearing Alert Record\n\n")
            alert_record = []
        # get new update timers once per hour
        if current_min == 1:
            update_timers = get_update_timers(home_realm_ids, REGION)
        # update item names once per hour
        if current_min == 2:
            item_names = get_itemnames()

        matching_realms = [
            realm["dataSetID"]
            for realm in update_timers
            if realm["lastUploadMinute"] <= current_min <= realm["lastUploadMinute"] + 5
        ]
        # mega wants extra alerts
        if EXTRA_ALERTS:
            extra_alert_mins = json.loads(EXTRA_ALERTS)
            if current_min in extra_alert_mins:
                matching_realms = [realm["dataSetID"] for realm in update_timers]

        if matching_realms != []:
            if ADD_DELAY:
                try:
                    delay = int(ADD_DELAY)
                    print(f"sleeping for {delay} seconds")
                    time.sleep(delay)
                except Exception as e:
                    print(f"ADD_DELAY must be an integer, got {ADD_DELAY}:\n{e}")
                    exit(1)
            else:
                # auto sleep 30 sec
                delay = 30
                print(f"sleeping for {delay} seconds")
                time.sleep(delay)

            access_token = get_wow_access_token()
            pool = ThreadPoolExecutor(max_workers=16)
            for connected_id in matching_realms:
                pool.submit(pull_single_realm_data, connected_id, access_token)
            pool.shutdown(wait=True)
            # home realms will spam so sleep
            if HOME_REALMS:
                time.sleep(25)
        else:
            print(
                f"waiting for a match in update time to run check on items {desired_items} or pets {desired_pets}, none found triggering at {datetime.now()}"
            )
            time.sleep(20)


def main_single():
    # run everything once slow
    access_token = get_wow_access_token()
    for connected_id in set(WOW_SERVER_NAMES.values()):
        pull_single_realm_data(connected_id, access_token)


def main_fast():
    # run everything once fast
    access_token = get_wow_access_token()
    pool = ThreadPoolExecutor(max_workers=16)
    for connected_id in set(WOW_SERVER_NAMES.values()):
        pool.submit(pull_single_realm_data, connected_id, access_token)
    pool.shutdown(wait=True)


send_discord_message("starting mega alerts", WEBHOOK_URL)
main()

## for debugging
# main_single()
# main_fast()
