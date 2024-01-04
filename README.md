# mega-alerts

A super fast Blizzard AH sniper created by Saddlebag Exchange

**Please dontate to our patreon so we can keep the project running.  If you need help setting it up, our creator will personally help any patreon subscribers.**

https://www.patreon.com/indopan

[Current Docker versions](https://hub.docker.com/repository/docker/cohenaj194/mega-alerts/tags?page=1&ordering=last_updated):
```
cohenaj194/mega-alerts:latest
cohenaj194/mega-alerts:1.7
cohenaj194/mega-alerts:1.6
cohenaj194/mega-alerts:1.5
cohenaj194/mega-alerts:1.4
cohenaj194/mega-alerts:1.3
cohenaj194/mega-alerts:1.2
cohenaj194/mega-alerts:1.1
cohenaj194/mega-alerts:1.0
```

Last Stable Version: `1.7`

# Alert Example
<img width="601" alt="image" src="https://user-images.githubusercontent.com/17516896/224507162-53513e8a-69ab-41e2-a5d5-ea4e51a9fc89.png">

# Software Setup

1. [Install Docker](https://docs.docker.com/engine/install/) used to run the sniper

2. Go to https://develop.battle.net/access/clients and create a client, get the blizzard oauth client and secret ids.  You will use these values for the `WOW_CLIENT_ID` and `WOW_CLIENT_SECRET` later on.

<img width="1304" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/e954289a-ccbc-4afb-9f66-897bbc68f677">

<img width="633" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/595fee57-e0db-4910-995d-5b5ae48190a2">


3. [Setup a discord channel with a webhook url for sending the alert messages](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) You will use this for the `MEGA_WEBHOOK_URL` later on.

4. Download [the docker image](https://hub.docker.com/repository/docker/cohenaj194/mega-alerts/general), if on windows open a [command prompt](https://www.youtube.com/watch?v=uE9WgNr3OjM) to run this.

```
docker pull cohenaj194/mega-alerts
```

# Item Selection
1. If you have specific items and prices you want, then make a json object with the item ids and prices that you want to snipe for!

This is what you will set for `DESIRED_ITEMS` or you can set `{}` if you only want to snipe pets.

* The item ids for items you want to snipe are as the keys
* and set the price in gold for each item as the value

For example the following looks for [item id 194641 (which is the elemental lariat)](https://undermine.exchange/#us-thrall/194641) for under 500k and another item for under 40k.

```
{"194641": 500000, "159840":40000}
```

[Paste that into this json checker if you want to make sure your json is valid](https://jsonlint.com/)

You can find that id at the end of the undermine exchange link for the item https://undermine.exchange/#us-thrall/194641 or if you look it up on wowhead the url also has the item id https://www.wowhead.com/item=194641/design-elemental-lariat

[You can also use our item id to name lookup tool, which makes this even easier.](https://temp.saddlebagexchange.com/itemnames)

2.  If you have specific pets and prices you want, then make a json object with the pet ids and prices that you want to snipe for!

This is what you will set for `DESIRED_PETS` or you can set `{}` if you only want to snipe regular items.

* The pet ids for items you want to snipe are as the keys
* and set the price in gold for each item as the value

For example the following looks for [pet species id 3390 (which is the Sophic Amalgamation)](https://undermine.exchange/#us-suramar/82800-3390) for under 3K.

```
{"3390": 3000}
```

You can find that id at the end of the undermine exchange link for the item next to `82800` (which is the item id for pet cages) https://undermine.exchange/#us-suramar/82800-3390.

3. If you want to snipe based on ilvl, leech, speed, avoidance or sockets then setup the json object for that:

We now have an extra option similar to the `DESIRED_ITEMS` or `DESIRED_PETS` for sniping items based on ilvl.  This also lets you search for items with specific item levels and leech, sockets, speed or avoidance.

To enable this set the env var `DESIRED_ILVL` with json similar to the following. This example looks for items with over an ilvl of 360 with a speed stat:

```
{"ilvl": 424, "buyout": 1000, "sockets": false, "speed": true, "leech": false, "avoidance": false}
```

If we change this to and set `"sockets": true` then it will show items over an ilvl of 360 with a speed stat or a socket:

```
{"ilvl": 424, "buyout": 1000, "sockets": true, "speed": true, "leech": false, "avoidance": false}
```

4. If you want to run locally with python or pycharm, first clone the repo or [download the code](https://github.com/ff14-advanced-market-search/mega-alerts/archive/refs/heads/main.zip).  Then set all your user values in the data files under the [user_data/mega](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/) json files:

- [Set the item ids and prices you want](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/mega/desired_items.json)
- [Set the pet ids and prices you want](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/mega/desired_pets.json)
- [Set the ilvl and price info for snipe by ilvl and stats](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/mega/desired_ilvl.json)
- [Set up all the other important details for alerts](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/mega/mega_data.json)


Even if you are not going to run directly in python then you should still save this somewhere in a text file.


# How to run the alerts

With whatever method you choose you will provide all the details the code needs in *Environmental Variables*.  You must provide at least the following:

- `MEGA_WEBHOOK_URL`
- `WOW_CLIENT_ID`
- `WOW_CLIENT_SECRET`
- `WOW_REGION` either `EU` or `NA`
- Then for your snipe method you must provide at least one correct json data for `DESIRED_ITEMS`, `DESIRED_PETS` or `DESIRED_ILVL`

We also have the following **optional** env vars you can add in to change alert behavior, but you dont need to as all have default values when not manually set:
- `DEBUG="true"` This will instantly trigger a scan on all realms against your inputs, this will only run once and then exit the script or container so use it to debug and make sure your data is working.
- `SHOW_BID_PRICES=true` Bid prices below your price limit will also be shown (default false)
- `WOWHEAD_LINK=true` Uses wowhead links instead of undermine and shows pictures, but the message length will be longer (default false)
- `SCAN_TIME_MIN=-1` increase or decrease the minutes before or at the data update time to start scanning (default to keep scanning 1 min after the data updates).
- `SCAN_TIME_MAX=1` increase or decrease the minutes after the data updates to stop scanning (default to keep scanning 3 min after the data updates).
- `MEGA_THREADS=100` increase or decrease the threadcount (default to scan 48 realms at once)(more threads = faster scans, but doing more threads then realms is pointless).
- `REFRESH_ALERTS="false"` if set to false then you will not see the same alert more than once (default true)
- `NO_RUSSIAN_REALMS="true"` set this to true if you are on EU and do not want to get alerts from russian realms


## Different ways to run mega alerts

1.  Running with docker desktop is the simplist and most stable method.  It will be easiest for windows users.

In docker desktop download the image and click `run` to run it.  It will then give you the option to add variables.

<img width="1297" alt="image" src="https://user-images.githubusercontent.com/17516896/224506498-d385e177-4fd0-41fc-ae80-78e77b2e0c7b.png">

Click to add more variables in and put the variable names in with your values

<img width="530" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/1ad70ad7-67db-45a2-b665-a5d33a192de1">

2. If you are able do run a docker run command directly on your command line then that will be even easier than option 1 as you can just save your run command and paste it in the command line.

Make sure to set `WOW_REGION` with either `EU` or `NA`

```
docker run -dit \
    --name wow-test \
    --env MEGA_WEBHOOK_URL=$MEGA_WEBHOOK_URL \
    --env WOW_CLIENT_ID=$WOW_CLIENT_ID \
    --env WOW_CLIENT_SECRET=$WOW_CLIENT_SECRET \
    --env WOW_REGION=EU \
    --env DESIRED_ITEMS='{"194641": 500000, "159840":40000}' \
    --env DESIRED_PETS='{"3390": 2700}' \
    cohenaj194/mega-alerts
```

3. You can also try running with docker-compose which will automatically pick up values if you set them in the json files (mentioned in step 4 of the `Item Selection` section of the guide)

You can then run it with docker compose using:

```
docker compose up --build
```

4. You can run it with python on your computer with pycharm

Make sure the required packages are installed by running:

```
pip3 install -r requirements.txt
```

Then just run the [mega-alerts.py file](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/mega-alerts.py). To do this right click the mega alerts file and click run:

<img width="1046" alt="Screen Shot 2023-07-11 at 1 14 40 PM" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/d7363e3d-fef6-4a06-93ab-42ae38fa3ac0">


5. Alternatively you can try to run this in kubernetes on minikube to autorestart if the pods fail

If you can run shell and python locally please run this instead of using kubernetes as you can easily exit it by hitting "control" + "c" on your keyboard:

```
bash auto_restart.sh
```

[Download and start minikube](https://kubernetes.io/docs/tutorials/hello-minikube/) with:

```
minikube start
```

Then update the [https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/kube-manifest.yml](kube-manifest.yml) with your own environmental variables:

``` 
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mega-alerts
spec:
  selector:
    matchLabels:
      run: mega-alerts
  replicas: 1
  template:
    metadata:
      labels:
        run: mega-alerts
    spec:
      containers:
      - name: mega-alerts
        image: cohenaj194/mega-alerts
        env:
        - name: MEGA_WEBHOOK_URL
          value: "https://discord.com/api/webhooks/12345678/foobar"
        # EU or NA
        - name: WOW_REGION
          value: "NA"
        - name: WOW_CLIENT_ID
          value: 123456789asdfghjk
        - name: WOW_CLIENT_SECRET
          value: 123456789asdfghjk
        - name: DESIRED_ITEMS
          value: '{"194641": 500000, "159840":40000}'
        - name: DESIRED_PETS
          value: '{"3390": 2700}'
```

Once you do that just run:

```
kubectl apply -f kube-manifest.yml
```

To update to the latest container version of mega alerts run:

```
kubectl rollout restart deployment/mega-alerts
```

You can then view the logs with:

```
pod_name=$(kubectl get pods | grep -v NAME | awk '{print $1}')
kubectl logs $pod_name 
```

# How to update versions

To update to the latest code version in docker desktop click the 3 dots next to the latest `cohenaj194/mega-alerts` image and then click **pull**.

<img width="1260" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/ba861fe2-eb42-4594-bff4-b722dd5c1548">


To update to the latest code version in docker you can also run the following command in your terminal or windows command line:

```
docker pull cohenaj194/mega-alerts
```

To update python if you are running it locally go to the folder with mega-alerts and run the following:

```
git checkout main
git pull
```

# Simple Alerts

If you have trouble setting up mega alerts or making a battle.net oauth token you can use the [simple-alerts.py](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/mega-alerts.py) instead.

This is slower than mega alerts and can be out of sync at times, but it only requires a discord webhook url to run.

To set this up:

1. Add your webhook url and any extra alert times into the [user_data/simple/simple-alerts.json](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/simple/simple-alerts.json)

2. Generate your alert json using [our price alert webpage](https://saddlebagexchange.com/wow/price-alert) and then paste it into the [user_data/simple/simple-alerts.json](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/simple/simple-alerts.json).

3. Run the [simple-alerts.py](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/simple-alerts.py) script:

<img width="1043" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/ab94648f-c900-40fe-af3b-51c04df12710">

# Snipe by ilvl and tertiary stats

We now have an extra option similar to the `DESIRED_ITEMS` or `DESIRED_PETS` for sniping items based on ilvl.  This also lets you search for items with specific item levels and leech, sockets, speed or avoidance.

To enable this set the env var `DESIRED_ILVL` with json similar to the following. 

This example will snipe anything based on ilvl (just make sure all the stats are set to false for ilvl alone):

```
{
  "ilvl": 420,
  "buyout": 1000,
  "sockets": false,
  "speed": false,
  "leech": false,
  "avoidance": false,
  "item_ids": [204423, 204410]
}
```

<img width="680" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/722e828d-fdbf-485e-82b5-b8bc08827e3a">


This example looks for items with over an ilvl of 360 with a speed stat because `"speed": true`:

```
{
  "ilvl": 424,
  "buyout": 1000,
  "sockets": false,
  "speed": true,
  "leech": false,
  "avoidance": false,
  "item_ids": [204966, 204920]
}
```

<img width="460" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/1a7250be-e1fe-41f9-b056-a2dc3cfd3abe">


If we change this and also set `"sockets": true` then it will show items over an ilvl of 360 with a speed stat or a socket:

```
{
  "ilvl": 424,
  "buyout": 1000,
  "sockets": true,
  "speed": true,
  "leech": false,
  "avoidance": false,
  "item_ids": [204948, 204951, 204965]
}
```

<img width="353" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/53418363-caa7-4a71-b388-a270aef464eb">


You can also remove the `item_ids` or leave it empty to snipe for all items at that ilvl (warning this may spam so many messages it breaks your webhook, if that happens just make a new webhook):

```
{
  "ilvl": 424,
  "buyout": 1000,
  "sockets": false,
  "speed": false,
  "leech": false,
  "avoidance": false
}
```
