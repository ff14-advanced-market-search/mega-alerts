#!/usr/bin/python3
from __future__ import print_function
import os, json, time
from datetime import datetime

from utils.api_requests import (
    get_update_timers,
    send_discord_message,
    simple_snipe,
)

print("Sleep 10 sec on start to avoid spamming the api")
time.sleep(10)

#### GLOBALS ####
alert_record = []
price_alert_data = json.load(open("user_data/simple/region_snipe.json"))
if len(price_alert_data) == 0:
    print(
        "Error please generate your snipe data at: https://saddlebagexchange.com/wow/price-alert"
    )
    print("Then paste it into user_data/simple/region_snipe.json")
    exit(1)
region = price_alert_data["region"]

simple_snipe_info = json.load(open("user_data/simple/simple_snipe_info.json"))
# remove homeRealmName if players insert it from the website
if "homeRealmName" in simple_snipe_info:
    del simple_snipe_info["homeRealmName"]

webhook_url = simple_snipe_info["MEGA_WEBHOOK_URL"]
# default to env var if not set in json
if not webhook_url:
    webhook_url = os.getenv("MEGA_WEBHOOK_URL")
# allow extra alerts to be empty
extra_alert_mins = simple_snipe_info["EXTRA_ALERTS"]


def format_discord_message():
    global alert_record
    snipe_data = simple_snipe(price_alert_data)
    if not snipe_data:
        send_discord_message(
            f"An error occured got empty response {snipe_data}", webhook_url
        )
        return
    if "matching" not in snipe_data:
        send_discord_message(f"No matching snipes found", webhook_url)
        return
    if len(snipe_data["matching"]) == 0:
        send_discord_message(f"No matching snipes found", webhook_url)
        return

    for auction in snipe_data["matching"]:
        message = (
            "==================================\n"
            + f"`item:` {auction['item_name']}\n"
            + f"`price:` {auction['ah_price']}\n"
            + f"`desired_state`: {auction['desired_state']}\n"
            + f"`itemID:` {auction['item_id']}\n"
            + f"[Undermine link]({auction['link']})\n"
            + f"realmNames: {auction['realm_names']}\n"
            + "==================================\n"
        )
        if auction not in alert_record:
            send_discord_message(message, webhook_url)
            alert_record.append(auction)


#### MAIN ####
def main():
    global alert_record
    update_time = get_update_timers(region, True)[0]["lastUploadMinute"]
    while True:
        current_min = int(datetime.now().minute)

        # clear out the alert record once an hour
        if current_min == 0:
            print("\n\nClearing Alert Record\n\n")
            alert_record = []
        # update the update min once per hour
        if current_min == 1:
            update_time = get_update_timers(region, True)[0]["lastUploadMinute"]

        # check the upload min up 3 to 5 min after the commodities trigger
        if (
            update_time + 3 <= current_min <= update_time + 7
            or current_min in extra_alert_mins
        ):
            format_discord_message()
            time.sleep(60)
        else:
            print(f"at {datetime.now()}, waiting for {[update_time]+extra_alert_mins}")
            time.sleep(60)


def test():
    format_discord_message()


send_discord_message("starting simple alerts", webhook_url)
main()

## for debugging
# test()
