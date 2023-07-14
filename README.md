# Alert Example
<img width="601" alt="image" src="https://user-images.githubusercontent.com/17516896/224507162-53513e8a-69ab-41e2-a5d5-ea4e51a9fc89.png">

# Setup

1. [Install Docker](https://docs.docker.com/engine/install/) used to run the sniper

2. Go to https://develop.battle.net/access/clients and create a client, get the blizzard oauth client and secret ids

<img width="1304" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/e954289a-ccbc-4afb-9f66-897bbc68f677">

<img width="633" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/595fee57-e0db-4910-995d-5b5ae48190a2">


4. Setup a discord channel with a webhook url for sending the alert messages

5. Download [the docker image](https://hub.docker.com/repository/docker/cohenaj194/mega-alerts/general), if on windows open a [command prompt](https://www.youtube.com/watch?v=uE9WgNr3OjM) to run this.

```
docker pull cohenaj194/mega-alerts
```

5. Make a json object with the item ids and prices that you want to snipe for!

This is what you will set for `DESIRED_ITEMS` or you can set `{}` if you only want to snipe pets.

* The item ids for items you want to snipe are as the keys
* and set the price in gold for each item as the value

For example the following looks for [item id 194641 (which is the elemental lariat)](https://undermine.exchange/#us-thrall/194641) for under 500k and another item for under 40k.

```
{"194641": 500000, "159840":40000}
```

You can find that id at the end of the undermine exchange link for the item https://undermine.exchange/#us-thrall/194641 or if you look it up on wowhead the url also has the item id https://www.wowhead.com/item=194641/design-elemental-lariat

6. Make a json object with the pet ids and prices that you want to snipe for!

This is what you will set for `DESIRED_PETS` or you can set `{}` if you only want to snipe regular items.

* The pet ids for items you want to snipe are as the keys
* and set the price in gold for each item as the value

For example the following looks for [pet species id 3390 (which is the Sophic Amalgamation)](https://undermine.exchange/#us-suramar/82800-3390) for under 3K.

```
{"3390": 3000}
```

You can find that id at the end of the undermine exchange link for the item next to `82800` (which is the item id for pet cages) https://undermine.exchange/#us-suramar/82800-3390.

7. If you only want to run the alerts on specific realms then make a json list of all the realm names and put it in a string:
```
'["Thrall", "Silvermoon"]'
```

8. If you want to run locally with python or pycharm, first clone the repo or [download the code](https://github.com/ff14-advanced-market-search/mega-alerts/archive/refs/heads/main.zip).  Then set all your user values in the data files under the [user_data/mega](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/) json files:

- [Set the item ids and prices you want](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/mega/desired_items.json)
- [Set the pet ids and prices you want](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/mega/desired_pets.json)
- [Set up all the other important details for alerts](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/mega/mega_data.json)

You can then run it with python or run locally with docker compose using:

```
docker compose up --build
```

Make sure the required packages are installed by running:

```
pip3 install -r requirements.txt
```

Then just run the [mega-alerts.py file](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/mega-alerts.py). To do this right click the mega alerts file and click run:

<img width="1046" alt="Screen Shot 2023-07-11 at 1 14 40 PM" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/d7363e3d-fef6-4a06-93ab-42ae38fa3ac0">

9. To run the docker container (go to 10. if you are running it with docker desktop) with the following env vars.

Make sure to set `WOW_REGION` with either `EU` or `NA`

If you want to snipe across all realms then do not add the `HOME_REALMS` env var.
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
If you want to snipe only on specific realms then add the `HOME_REALMS` env var in as a string:

```
docker run -dit \
    --name wow-test \
    --env MEGA_WEBHOOK_URL=$MEGA_WEBHOOK_URL \
    --env WOW_CLIENT_ID=$WOW_CLIENT_ID \
    --env WOW_CLIENT_SECRET=$WOW_CLIENT_SECRET \
    --env WOW_REGION=EU \
    --env DESIRED_ITEMS='{"194641": 500000, "159840":40000}' \
    --env DESIRED_PETS='{"3390": 2700}' \
    --env HOME_REALMS='["Thrall", "Silvermoon"]' \
    cohenaj194/mega-alerts
```

If you want it to trigger for all selected realms on a minute or several specific min of each hour you can trigger this with `EXTRA_ALERTS`:

```
docker run -dit \
    --name wow-test \
    --env MEGA_WEBHOOK_URL=$MEGA_WEBHOOK_URL \
    --env WOW_CLIENT_ID=$WOW_CLIENT_ID \
    --env WOW_CLIENT_SECRET=$WOW_CLIENT_SECRET \
    --env WOW_REGION=EU \
    --env DESIRED_ITEMS='{"194641": 500000, "159840":40000}' \
    --env DESIRED_PETS='{"3390": 2700}' \
    --env EXTRA_ALERTS='[15,45]'
    cohenaj194/mega-alerts
```

We also have the following optional env vars you can add in to change alert behavior:
- `--env SHOW_BID_PRICES=true` Bid prices below your price limit will also be shown.
- `--env WOWHEAD_LINK=true` Uses wowhead links instead of undermine and shows pictures, but the message length will be longer.
- `--env ADD_DELAY=30` By default triggers on the exact minute of the update and then sleeps for 30 seconds.  You can increase or decrease the sleep with this value.


10. In docker desktop download the image and run it 

<img width="1297" alt="image" src="https://user-images.githubusercontent.com/17516896/224506498-d385e177-4fd0-41fc-ae80-78e77b2e0c7b.png">

For the env vars set all the env vars you see in the `--env` lines in step 10 and then click run:

<img width="554" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/2fd6618b-1532-485c-8959-0c83f39ca7ea">


11. Alternatively you can try to run this in kubernetes on minikube to autorestart if the pods fail

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

# Simple Alerts

If you have trouble setting up mega alerts or making a battle.net oauth token you can use the [simple-alerts.py](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/mega-alerts.py) instead.

This is slower than mega alerts and can be out of sync at times, but it only requires a discord webhook url to run.

To set this up:

1. Add your webhook url and any extra alert times into the [user_data/simple/simple-alerts.json](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/simple/simple-alerts.json)

2. Generate your alert json using [our price alert webpage](https://saddlebagexchange.com/wow/price-alert) and then paste it into the [user_data/simple/simple-alerts.json](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/user_data/simple/simple-alerts.json).

3. Run the [simple-alerts.py](https://github.com/ff14-advanced-market-search/mega-alerts/blob/main/simple-alerts.py) script:

<img width="1043" alt="image" src="https://github.com/ff14-advanced-market-search/mega-alerts/assets/17516896/ab94648f-c900-40fe-af3b-51c04df12710">
