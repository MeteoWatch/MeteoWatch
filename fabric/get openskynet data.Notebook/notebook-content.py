# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "1ae157b7-2c0f-4094-a65d-3ed712519a22",
# META       "default_lakehouse_name": "lh",
# META       "default_lakehouse_workspace_id": "109a0cee-98b2-43dd-8ee0-b554d34509db"
# META     },
# META     "environment": {
# META       "environmentId": "86cc5bca-63ce-47f2-af6e-76cad74dd5a4",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# CELL ********************

from azure.eventhub import EventHubProducerClient, EventData
import requests
import logging
from time import time, sleep
import json
from requests.auth import HTTPBasicAuth

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


def get_logger() -> logging.Logger:
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt=FORMAT)
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)
    logger = logging.getLogger("dajoma")
    logger.setLevel(logging.INFO)
    return logger


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

logger = get_logger()
producer = EventHubProducerClient.from_connection_string(
    conn_str="Endpoint=sb://esehdewckwp0o2kltlf21wni.servicebus.windows.net/;SharedAccessKeyName=key_9ae1efcc-055f-40a4-9fc1-2be0cca5e3b6;SharedAccessKey=F3LUIQIFLl4GHCReux3Ewri/p6eSyXhq3+AEhO9xteg=;EntityPath=es_1fe50121-6dd6-4860-8b3e-ea0925d2362d"
)
col_names = [
    "icao24",
    "callsign",
    "origin_country",
    "time_position",
    "last_contact",
    "longitude",
    "latitude",
    "baro_altitude",
    "on_ground",
    "velocity",
    "true_track",
    "vertical_rate",
    "sensors",
    "geo_altitude",
    "squawk",
    "spi",
    "position_source",
]
timeout = 16 * 60 * 60  # first is hours

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Inspired by: https://github.com/microsoft/Fabric-RTA-FlightStream/blob/main/artifacts/notebooks/LiveStream.py


def get_data_from_openskynetwork() -> list:
    logger.info("Pulling data from openskynetwork.")
    l = requests.get(
        "https://opensky-network.org/api/states/all",
        auth=HTTPBasicAuth("user", "psw"),
    ).json()["states"]
    logger.info(f"Data has {len(l)} entries.")
    return l


def send_data_to_eventstream(l: list) -> None:
    start_time = time()
    logger.info("Starting streaming data to event stream...")
    event_data_batch = producer.create_batch()
    for i, row in enumerate(l):
        msg = json.dumps({col_names[i]: row[i] for i in range(len(row))})
        event_data_batch.add(EventData(msg))
        # prior to hitting the max by 5k, send the current and recreate batch.
        if (
            event_data_batch.size_in_bytes
            >= event_data_batch.max_size_in_bytes - 5000
        ):
            logger.info(f"Sending...")
            producer.send_batch(event_data_batch)
            logger.info(f"{i} messages sent from batch.")
            event_data_batch = producer.create_batch()
    logger.info("Sending for the last time.")
    producer.send_batch(event_data_batch)
    producer.close()
    logger.info(
        f"Done with sending batch to eventstream. Took {time() - start_time}s."
    )


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

logger.info("Starting...")
start = time()
while True:
    data = get_data_from_openskynetwork()
    send_data_to_eventstream(data)
    t = 120
    logger.info(f"Sleeping for {t}s.")
    sleep(t)
    running = time() - start
    if running > timeout:
        logger.info("Timeout exceeded. Aborting.")
        break
    else:
        logger.info(
            f"Continuing...~{int(timeout-running)}s left until timeout."
        )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
