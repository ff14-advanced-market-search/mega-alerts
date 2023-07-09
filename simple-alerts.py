#!/usr/bin/python3
from __future__ import print_function
import os, json, time
from datetime import datetime

from utils.api_requests import (
    get_update_timers,
    send_discord_message,
    simple_snipe,
)

#### GLOBALS ####
alert_record = []
webhook_url = os.getenv("MEGA_WEBHOOK_URL")
price_alert_data = json.load(open("data/region_snipe.json"))
region = price_alert_data["region"]
# mega wants extra alerts
extra_alert_mins = []
if os.getenv("EXTRA_ALERTS"):
    extra_alert_mins = json.loads(os.getenv("EXTRA_ALERTS"))


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
    global item_names

    while True:
        update_time = get_update_timers([-1, -2], region, True)[0]["lastUploadMinute"]
        current_min = int(datetime.now().minute)
        # clear out the alert record once an hour
        if current_min == 0:
            print("\n\nClearing Alert Record\n\n")
            alert_record = []

        if (
            update_time + 3 <= current_min <= update_time + 7
            or current_min in extra_alert_mins
        ):
            format_discord_message()
            time.sleep(60)
        else:
            print(f"at {datetime.now()}, waiting for {update_time}")
            time.sleep(60)


def test():
    format_discord_message()


send_discord_message("starting mega alerts", webhook_url)
main()

## for debugging
# test()
