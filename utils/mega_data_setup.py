#!/usr/bin/python3
from __future__ import print_function
import os, json

from utils.api_requests import (
    get_itemnames,
    get_petnames,
)

#### CONTANTS ####
raw_mega_data = json.load(open("user_data/mega/mega_data.json"))

# load from file if setup
if len(raw_mega_data) != 0:
    print("loading mega data from user_data/mega/mega_data.json")
    WOW_CLIENT_ID = raw_mega_data["WOW_CLIENT_ID"]
    WOW_CLIENT_SECRET = raw_mega_data["WOW_CLIENT_SECRET"]
    WEBHOOK_URL = raw_mega_data["MEGA_WEBHOOK_URL"]
    WOWHEAD_LINK = raw_mega_data["WOWHEAD_LINK"]
    SHOW_BIDPRICES = raw_mega_data["SHOW_BID_PRICES"]
    REGION = raw_mega_data["WOW_REGION"]
    EXTRA_ALERTS = raw_mega_data["EXTRA_ALERTS"]
    ADD_DELAY = raw_mega_data["ADD_DELAY"]

# get from env if not file is empty
else:
    print("no mega data found in user_data/mega/mega_data.json pulling from env vars")
    WEBHOOK_URL = os.getenv("MEGA_WEBHOOK_URL")
    WOWHEAD_LINK = os.getenv("WOWHEAD_LINK")
    SHOW_BIDPRICES = os.getenv("SHOW_BID_PRICES")

    REGION = os.getenv("WOW_REGION")
    EXTRA_ALERTS = os.getenv("EXTRA_ALERTS")
    ADD_DELAY = os.getenv("ADD_DELAY")

    WOW_CLIENT_ID = os.getenv("WOW_CLIENT_ID")
    WOW_CLIENT_SECRET = os.getenv("WOW_CLIENT_SECRET")

# need to do this no matter where we get the region from
if REGION == "NA" or REGION == "US":
    REGION = "NA"
    WOW_SERVER_NAMES = json.load(open("data/na-wow-connected-realm-ids.json"))
elif REGION == "EU":
    WOW_SERVER_NAMES = json.load(open("data/eu-wow-connected-realm-ids.json"))
else:
    print(f"error region is not valid choose NA, US or EU")
    exit(1)

HOME_REALMS = open("user_data/mega/home_realms.json").read()
home_realm_ids = json.loads(HOME_REALMS)
if len(home_realm_ids) == 0:
    home_realm_ids = []
    if os.getenv("HOME_REALMS"):
        HOME_REALMS = json.loads(os.getenv("HOME_REALMS"))
        for r in HOME_REALMS:
            home_realm_ids.append(WOW_SERVER_NAMES[r])


#### ITEM SNIPE SETUP ###
desired_items_raw = json.load(open("user_data/mega/desired_items.json"))
desired_pets_raw = json.load(open("user_data/mega/desired_pets.json"))

# if file is not set use env var
if len(desired_items_raw) == 0:
    print(
        "no desired items found in user_data/mega/desired_items.json pulling from env vars"
    )
    if os.getenv("DESIRED_ITEMS"):
        desired_items_raw = json.loads(os.getenv("DESIRED_ITEMS"))
    else:
        desired_items_raw = {}

# if file is not set use env var
if len(desired_pets_raw) == 0:
    print(
        "no desired pets found in user_data/mega/desired_pets.json pulling from env vars"
    )
    if os.getenv("DESIRED_PETS"):
        desired_pets_raw = json.loads(os.getenv("DESIRED_PETS"))
    else:
        desired_pets_raw = {}

if desired_pets_raw == {} and desired_items_raw == {}:
    print("Error no snipe data found!")
    print(
        "You need to set up your user_data/mega/desired_items.json or user_data/mega/desired_pets.json"
    )
    print("You can also set env vars with the json for DESIRED_ITEMS or DESIRED_PETS")
    exit(1)

# fix the json dict keys from strings to ints
desired_items, desired_pets = {}, {}
for k, v in desired_items_raw.items():
    desired_items[int(k)] = int(v)
for k, v in desired_pets_raw.items():
    desired_pets[int(k)] = int(v)
