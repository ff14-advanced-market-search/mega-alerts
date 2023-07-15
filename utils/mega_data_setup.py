#!/usr/bin/python3
from __future__ import print_function
import os, json

from utils.api_requests import get_petnames, get_itemnames, send_discord_message


class MegaData:
    def __init__(self):
        raw_mega_data = json.load(open("user_data/mega/mega_data.json"))

        # set generic values usually in the env vars
        self.WOW_CLIENT_ID = self.__set_mega_vars("WOW_CLIENT_ID", raw_mega_data, True)
        self.WOW_CLIENT_SECRET = self.__set_mega_vars(
            "WOW_CLIENT_SECRET", raw_mega_data, True
        )
        self.WEBHOOK_URL = self.__set_mega_vars("MEGA_WEBHOOK_URL", raw_mega_data, True)
        self.WOWHEAD_LINK = self.__set_mega_vars("WOWHEAD_LINK", raw_mega_data)
        self.SHOW_BIDPRICES = self.__set_mega_vars("SHOW_BID_PRICES", raw_mega_data)
        self.REGION = self.__set_mega_vars("WOW_REGION", raw_mega_data, True)
        self.EXTRA_ALERTS = self.__set_mega_vars("EXTRA_ALERTS", raw_mega_data)
        self.ADD_DELAY = self.__set_mega_vars("ADD_DELAY", raw_mega_data)

        # get name dictionaries
        self.ITEM_NAMES = self.set_item_names()
        self.PET_NAMES = self.set_pet_names()

        # set servers to search
        self.HOME_REALMS = open("user_data/mega/home_realms.json").read()
        self.HOME_REALM_IDS = json.loads(self.HOME_REALMS)
        self.WOW_SERVER_NAMES = json.load(
            open(f"data/{self.REGION.lower()}-wow-connected-realm-ids.json")
        )

        if len(self.HOME_REALM_IDS) == 0:
            self.HOME_REALM_IDS = []
            if os.getenv("HOME_REALMS"):
                self.HOME_REALMS = json.loads(os.getenv("HOME_REALMS"))
                for r in self.HOME_REALMS:
                    self.HOME_REALM_IDS.append(self.WOW_SERVER_NAMES[r])

        # setup items to snipe
        self.DESIRED_ITEMS = self.set_desired_items("desired_items")
        self.DESIRED_PETS = self.set_desired_items("desired_pets")
        self.validate_snipe_lists()

    #### VARIABLE RELATED FUNCTIONS ####
    @staticmethod
    def __set_mega_vars(var_name, raw_mega_data, required=False):
        if len(raw_mega_data) != 0 and var_name in raw_mega_data.keys():
            print(f"loading {var_name} from user_data/mega/mega_data.json")
            var_value = raw_mega_data[var_name]
        elif os.getenv(var_name):
            print(f"loading {var_name} from environment variables")
            var_value = os.getenv(var_name)
        elif required:
            raise Exception(
                f"Error required variable {var_name} not found in env or mega_data.json"
            )
        else:
            print(f"Optional variable {var_name} not found in env or mega_data.json")
            var_value = None

        # need to do this no matter where we get the region from
        if var_name == "REGION":
            if var_value not in ["US", "EU", "NA"]:
                raise Exception(f"error {var_value} not a valid region")
            # for people who are confused about US vs NA, all our data uses NA
            if var_value == "US":
                var_value = "NA"

        return var_value

    def set_pet_names(self):
        return get_petnames(self.WOW_CLIENT_ID, self.WOW_CLIENT_SECRET)

    def set_item_names(self):
        return get_itemnames()

    def set_desired_items(self, item_list_name):
        file_name = f"{item_list_name}.json"
        env_var_name = item_list_name.upper()
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

    def validate_snipe_lists(self):
        if len(self.DESIRED_ITEMS) == 0 and len(self.DESIRED_PETS) == 0:
            error_message = "Error no snipe data found!\n"
            error_message += (
                "You need to set up your user_data/mega/desired_items.json "
            )
            error_message += "or user_data/mega/desired_pets.json\n"
            error_message += "You can also set env vars with the json for DESIRED_ITEMS or DESIRED_PETS"
            raise Exception(error_message)

    #### GENERAL USE FUNCTIONS ####
    def send_discord_message(self, message):
        send_discord_message(message, self.WEBHOOK_URL)
