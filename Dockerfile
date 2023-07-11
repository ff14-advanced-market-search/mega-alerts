# syntax=docker/dockerfile:1

# Alpine is chosen for its small footprint
# compared to Ubuntu

FROM python:3.7-alpine3.16

RUN apk -v --update add \
      python3 \
      py-pip \
      bash \
      && \
      pip3 install --upgrade \
      requests \
      tenacity \
      && \
      apk -v --purge del && \
      rm /var/cache/apk/*

WORKDIR /app
RUN mkdir /app/data/
RUN mkdir /app/user_data/
RUN mkdir /app/user_data/mega/
RUN mkdir /app/user_data/simple/
RUN mkdir /app/utils/
COPY ./mega-alerts.py /app/
COPY ./utils/* /app/utils/
COPY ./data/* /app/data/
COPY ./user_data/mega/* /app/user_data/mega/
COPY ./user_data/simple/* /app/user_data/simple/
COPY ./run /app/
RUN chmod +x /app/*

CMD /app/run

## run local
#  docker run -dit \
#      --name wow-test \
#      --env WOW_REGION=NA \
#      --env DESIRED_ITEMS='{"194641": 500000, "159840":40000}' \
#      --env DESIRED_PETS='{"3390": 2700}' \
#      --env MEGA_WEBHOOK_URL=$MEGA_WEBHOOK_URL \
#      --env WOW_CLIENT_ID=$WOW_CLIENT_ID \
#      --env WOW_CLIENT_SECRET=$WOW_CLIENT_SECRET \
#      cohenaj194/mega-alerts
