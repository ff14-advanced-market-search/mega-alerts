#!/usr/bin/python3
from __future__ import print_function
import os, json


class mega_data:
    def __init__(self, use_file: bool = False):
        #### CONTANTS ####
        raw_mega_data = json.load(open("user_data/mega/mega_data.json"))

        # load from file if setup
        if len(raw_mega_data) != 0:
            print("loading mega data from user_data/mega/mega_data.json")
            self.WOW_CLIENT_ID = raw_mega_data["WOW_CLIENT_ID"]
            self.WOW_CLIENT_SECRET = raw_mega_data["WOW_CLIENT_SECRET"]
            self.WEBHOOK_URL = raw_mega_data["MEGA_WEBHOOK_URL"]
            self.WOWHEAD_LINK = raw_mega_data["WOWHEAD_LINK"]
            self.SHOW_BIDPRICES = raw_mega_data["SHOW_BID_PRICES"]
            self.REGION = raw_mega_data["WOW_REGION"]
            self.EXTRA_ALERTS = raw_mega_data["EXTRA_ALERTS"]
            self.ADD_DELAY = raw_mega_data["ADD_DELAY"]

        # get from env if not file is empty
        else:
            print(
                "no mega data found in user_data/mega/mega_data.json pulling from env vars"
            )
            self.WEBHOOK_URL = os.getenv("MEGA_WEBHOOK_URL")
            self.WOWHEAD_LINK = os.getenv("WOWHEAD_LINK")
            self.SHOW_BIDPRICES = os.getenv("SHOW_BID_PRICES")
            self.REGION = os.getenv("WOW_REGION")
            self.EXTRA_ALERTS = os.getenv("EXTRA_ALERTS")
            self.ADD_DELAY = os.getenv("ADD_DELAY")
            self.WOW_CLIENT_ID = os.getenv("WOW_CLIENT_ID")
            self.WOW_CLIENT_SECRET = os.getenv("WOW_CLIENT_SECRET")

        # need to do this no matter where we get the region from
        if self.REGION == "NA" or self.REGION == "US":
            self.REGION = "NA"
            self.WOW_SERVER_NAMES = json.load(
                open("data/na-wow-connected-realm-ids.json")
            )
        elif self.REGION == "EU":
            self.WOW_SERVER_NAMES = json.load(
                open("data/eu-wow-connected-realm-ids.json")
            )
        else:
            print(f"error region is not valid choose NA, US or EU")
            exit(1)

        self.HOME_REALMS = open("user_data/mega/home_realms.json").read()
        self.HOME_REALM_IDS = json.loads(self.HOME_REALMS)
        if len(self.HOME_REALM_IDS) == 0:
            self.HOME_REALM_IDS = []
            if os.getenv("HOME_REALMS"):
                self.HOME_REALMS = json.loads(os.getenv("HOME_REALMS"))
                for r in self.HOME_REALMS:
                    self.HOME_REALM_IDS.append(self.WOW_SERVER_NAMES[r])

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
            print(
                "You can also set env vars with the json for DESIRED_ITEMS or DESIRED_PETS"
            )
            exit(1)

        # fix the json dict keys from strings to ints
        self.DESIRED_ITEMS, self.DESIRED_PETS = {}, {}
        for k, v in desired_items_raw.items():
            self.DESIRED_ITEMS[int(k)] = int(v)
        for k, v in desired_pets_raw.items():
            self.DESIRED_PETS[int(k)] = int(v)
