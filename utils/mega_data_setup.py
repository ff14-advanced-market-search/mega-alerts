#!/usr/bin/python3
from __future__ import print_function
import os, json

from utils.api_requests import get_petnames, get_itemnames


class MegaData:
    def __init__(self):
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
            self.WOW_CLIENT_ID = os.getenv("WOW_CLIENT_ID")
            self.WOW_CLIENT_SECRET = os.getenv("WOW_CLIENT_SECRET")
            self.WEBHOOK_URL = os.getenv("MEGA_WEBHOOK_URL")
            self.WOWHEAD_LINK = os.getenv("WOWHEAD_LINK")
            self.SHOW_BIDPRICES = os.getenv("SHOW_BID_PRICES")
            self.REGION = os.getenv("WOW_REGION")
            self.EXTRA_ALERTS = os.getenv("EXTRA_ALERTS")
            self.ADD_DELAY = os.getenv("ADD_DELAY")

        # get name dictionaries
        self.ITEM_NAMES = self.get_item_names()
        self.PET_NAMES = self.get_pet_names()

        # need to do this no matter where we get the region from
        if self.REGION not in ["US", "EU", "NA"]:
            print(f"error {self.REGION} not a valid region")
            exit(1)
        if self.REGION == "US":
            self.REGION = "NA"

        self.WOW_SERVER_NAMES = json.load(
            open(f"data/{self.REGION.lower()}-wow-connected-realm-ids.json")
        )

        self.HOME_REALMS = open("user_data/mega/home_realms.json").read()
        self.HOME_REALM_IDS = json.loads(self.HOME_REALMS)
        if len(self.HOME_REALM_IDS) == 0:
            self.HOME_REALM_IDS = []
            if os.getenv("HOME_REALMS"):
                self.HOME_REALMS = json.loads(os.getenv("HOME_REALMS"))
                for r in self.HOME_REALMS:
                    self.HOME_REALM_IDS.append(self.WOW_SERVER_NAMES[r])

        #### ITEM SNIPE SETUP ###
        self.DESIRED_ITEMS = self.set_desired_items("desired_items.json", "DESIRED_ITEMS")
        self.DESIRED_PETS = self.set_desired_items("desired_pets.json", "DESIRED_PETS")
        if len(self.DESIRED_ITEMS) == 0 and len(self.DESIRED_PETS) == 0:
            print("Error no snipe data found!")
            print(
                "You need to set up your user_data/mega/desired_items.json or user_data/mega/desired_pets.json"
            )
            print(
                "You can also set env vars with the json for DESIRED_ITEMS or DESIRED_PETS"
            )
            exit(1)

    def get_pet_names(self):
        return get_petnames(self.WOW_CLIENT_ID, self.WOW_CLIENT_SECRET)

    def get_item_names(self):
        return get_itemnames()

    def set_desired_items(self, file_name, env_var_name):
        desired_items_raw = json.load(open(f"user_data/mega/{file_name}"))
        # if file is not set use env var
        if len(desired_items_raw) == 0:
            print(
                f"no desired items found in user_data/mega/{file_name} pulling from env vars"
            )
            if os.getenv(env_var_name):
                desired_items_raw = json.loads(os.getenv(env_var_name))
            else:
                desired_items_raw = {}
        desired_items = {}
        for k, v in desired_items_raw.items():
            desired_items[int(k)] = int(v)
        return desired_items
