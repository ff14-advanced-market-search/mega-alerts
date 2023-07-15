#!/usr/bin/python3
from __future__ import print_function
import time, json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from utils.api_requests import (
    get_wow_access_token,
    get_listings_single,
    get_update_timers,
)
from utils.helpers import (
    create_oribos_exchange_pet_link,
    create_oribos_exchange_item_link,
)
import utils.mega_data_setup


print("Sleep 10 sec on start to avoid spamming the api")
# time.sleep(10)

#### GLOBALS ####
alert_record = []
mega_data = utils.mega_data_setup.MegaData()


#### FUNCTIONS ####
def pull_single_realm_data(connected_id, access_token):
    auctions = get_listings_single(connected_id, access_token, mega_data.REGION)
    clean_auctions = clean_listing_data(auctions, connected_id)
    if not clean_auctions:
        return
    for auction in clean_auctions:
        if "itemID" in auction:
            id_msg = f"`itemID:` {auction['itemID']}\n"
            if str(auction["itemID"]) in mega_data.ITEM_NAMES:
                item_name = mega_data.ITEM_NAMES[str(auction["itemID"])]
                id_msg += f"`Name:` {item_name}\n"
        else:
            id_msg = f"`petID:` {auction['petID']}\n"
            if auction["petID"] in mega_data.PET_NAMES:
                pet_name = mega_data.PET_NAMES[auction["petID"]]
                id_msg += f"`Name:` {pet_name}\n"
        message = (
            "==================================\n"
            + f"`region:` {mega_data.REGION} "
            + f"`realmID:` {auction['realmID']} "
            + id_msg
            + f"[Undermine link]({auction['itemlink']})\n"
            + f"realmNames: {auction['realmNames']}\n"
        )
        if mega_data.WOWHEAD_LINK and auction["itemID"]:
            item_id = auction["itemID"]
            message += f"https://www.wowhead.com/item={item_id}"
        if "bid_prices" in auction:
            message += f"bid_prices: {auction['bid_prices']}\n"
        else:
            message += f"buyout_prices: {auction['buyout_prices']}\n"
        message += "==================================\n"
        if auction not in alert_record:
            mega_data.send_discord_message(message)
            alert_record.append(auction)


def clean_listing_data(auctions, connected_id):
    all_ah_buyouts, all_ah_bids = {}, {}
    pet_ah_buyouts, pet_ah_bids = {}, {}
    for item in auctions:
        item_id = item["item"]["id"]
        # regular items
        if item_id in mega_data.DESIRED_ITEMS and item_id != 82800:
            # idk why this is here, but have a feeling everything breaks without it
            price = 10000000 * 10000
            # if it has a bid use the bid price
            if "bid" in item.keys() and mega_data.SHOW_BIDPRICES == "true":
                price = item["bid"]
                # filter out items that are too expensive
                if price < mega_data.DESIRED_ITEMS[item_id] * 10000:
                    if item_id not in all_ah_bids.keys():
                        all_ah_bids[item_id] = [price / 10000]
                    elif price / 10000 not in all_ah_bids[item_id]:
                        all_ah_bids[item_id].append(price / 10000)
            if "buyout" in item.keys():
                price = item["buyout"]
                # filter out items that are too expensive
                if price < mega_data.DESIRED_ITEMS[item_id] * 10000:
                    if item_id not in all_ah_buyouts.keys():
                        all_ah_buyouts[item_id] = [price / 10000]
                    elif price / 10000 not in all_ah_buyouts[item_id]:
                        all_ah_buyouts[item_id].append(price / 10000)
        # all caged battle pets have item id 82800
        elif item_id == 82800:
            if item["item"]["pet_species_id"] in mega_data.DESIRED_PETS.keys():
                pet_id = item["item"]["pet_species_id"]
                # idk why this is here, but have a feeling everything breaks without it
                price = 10000000 * 10000
                if "bid" in item.keys() and mega_data.SHOW_BIDPRICES == "true":
                    price = item["bid"]
                    # filter out items that are too expensive
                    if price < mega_data.DESIRED_PETS[pet_id] * 10000:
                        if pet_id not in pet_ah_bids.keys():
                            pet_ah_bids[pet_id] = [price / 10000]
                        elif price / 10000 not in pet_ah_bids[pet_id]:
                            pet_ah_bids[pet_id].append(price / 10000)
                if "buyout" in item.keys():
                    price = item["buyout"]
                    # filter out items that are too expensive
                    if price < mega_data.DESIRED_PETS[pet_id] * 10000:
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
            f"no listings found matching items {mega_data.DESIRED_ITEMS} "
            + f"or pets {mega_data.DESIRED_PETS} on {connected_id} "
            + f"{mega_data.REGION}"
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
    realm_names = [
        name for name, id in mega_data.WOW_SERVER_NAMES.items() if id == connected_id
    ]
    for itemID, auction in all_ah_buyouts.items():
        # use instead of item name
        itemlink = create_oribos_exchange_item_link(
            realm_names[0], itemID, mega_data.REGION
        )
        results.append(
            results_dict(
                auction, itemlink, connected_id, realm_names, itemID, "itemID", "buyout"
            )
        )

    for petID, auction in pet_ah_buyouts.items():
        # use instead of item name
        itemlink = create_oribos_exchange_pet_link(
            realm_names[0], petID, mega_data.REGION
        )
        results.append(
            results_dict(
                auction, itemlink, connected_id, realm_names, petID, "petID", "buyout"
            )
        )

    if mega_data.SHOW_BIDPRICES == "true":
        for itemID, auction in all_ah_bids.items():
            # use instead of item name
            itemlink = create_oribos_exchange_item_link(
                realm_names[0], itemID, mega_data.REGION
            )
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
            itemlink = create_oribos_exchange_pet_link(
                realm_names[0], petID, mega_data.REGION
            )
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
        "region": mega_data.REGION,
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
            mega_data.send_discord_message(f"{upload_msg}```")
            upload_msg = "```"

    if upload_msg != "```":
        mega_data.send_discord_message(f"{upload_msg}```")


#### MAIN ####
def main():
    global alert_record
    update_timers = get_update_timers(mega_data.HOME_REALM_IDS, mega_data.REGION)
    while True:
        current_min = int(datetime.now().minute)
        # clear out the alert record once an hour
        if current_min == 0:
            print("\n\nClearing Alert Record\n\n")
            alert_record = []
        # get new update timers once per hour
        if current_min == 1:
            update_timers = get_update_timers(
                mega_data.HOME_REALM_IDS, mega_data.REGION
            )

        matching_realms = [
            realm["dataSetID"]
            for realm in update_timers
            if realm["lastUploadMinute"] <= current_min <= realm["lastUploadMinute"] + 5
        ]
        # mega wants extra alerts
        if mega_data.EXTRA_ALERTS:
            extra_alert_mins = json.loads(mega_data.EXTRA_ALERTS)
            if current_min in extra_alert_mins:
                matching_realms = [realm["dataSetID"] for realm in update_timers]

        if matching_realms != []:
            if mega_data.ADD_DELAY:
                try:
                    delay = int(mega_data.ADD_DELAY)
                    print(f"sleeping for {delay} seconds for ADD_DELAY")
                    time.sleep(delay)
                except Exception as e:
                    print(
                        f"ADD_DELAY must be an integer, got {mega_data.ADD_DELAY}:\n{e}"
                    )
                    exit(1)
            else:
                # auto sleep 30 sec
                delay = 30
                print(f"sleeping for {delay} seconds for ADD_DELAY")
                time.sleep(delay)

            access_token = get_wow_access_token(
                mega_data.WOW_CLIENT_ID,
                mega_data.WOW_CLIENT_SECRET,
            )
            pool = ThreadPoolExecutor(max_workers=16)
            for connected_id in matching_realms:
                pool.submit(pull_single_realm_data, connected_id, access_token)
            pool.shutdown(wait=True)
            # home realms will spam so sleep
            if mega_data.HOME_REALMS:
                time.sleep(25)
        else:
            print(
                f"waiting for a match in update time to run check on items {mega_data.DESIRED_ITEMS} "
                + f"or pets {mega_data.DESIRED_PETS}, none found triggering at {datetime.now()}"
            )
            time.sleep(20)


def main_single():
    # run everything once slow
    access_token = get_wow_access_token(
        mega_data.WOW_CLIENT_ID, mega_data.WOW_CLIENT_SECRET
    )
    for connected_id in set(mega_data.WOW_SERVER_NAMES.values()):
        pull_single_realm_data(connected_id, access_token)


def main_fast():
    # run everything once fast
    access_token = get_wow_access_token(
        mega_data.WOW_CLIENT_ID, mega_data.WOW_CLIENT_SECRET
    )
    pool = ThreadPoolExecutor(max_workers=16)
    for connected_id in set(mega_data.WOW_SERVER_NAMES.values()):
        pool.submit(pull_single_realm_data, connected_id, access_token)
    pool.shutdown(wait=True)


mega_data.send_discord_message("starting mega alerts")
# main()

## for debugging
main_single()
# main_fast()
