# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "environment": {
# META       "environmentId": "9d577547-4476-47a5-9e6e-bbc8ecda5cbb",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# CELL ********************

import requests
import time
from geojson import Polygon
import logging
from azure.eventhub import EventData, EventHubProducerClient
import json
from geojson_rewind import rewind

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

logger = get_logger()
timeout = 8 * 60 * 60 # first is hours

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

def get_new_sigmet():
    base_sigmet = requests.get("https://aviationweather.gov/api/data/isigmet?format=json").json()
    logger.info(f"Got {len(base_sigmet)} SIGMET reports")

    #create geojson polygon
    for sigmet in base_sigmet:
        sigmet["polygon"] = rewind(Polygon([[(coord["lon"], coord["lat"]) for coord in sigmet["coords"]]]))
    logger.info(f"Created GeoJSON polygon for all reports")
    return base_sigmet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

def send_to_eventstream(relevant_sigmet):
    producer = EventHubProducerClient.from_connection_string(
        conn_str="Endpoint=sb://esehdewcn0bg1scw7mva77gn.servicebus.windows.net/;SharedAccessKeyName=key_f6249834-a453-88ae-98dc-25a87c9ce07d;SharedAccessKey=LlfSiSbfILewajiXFxW93bqqVxMvlCO6W+AEhMMRLSk=;EntityPath=es_d87d3257-3e4b-4231-a738-f3a53231480b"
    )
    with producer:
        event_data_batch = producer.create_batch()
        for sigmet in relevant_sigmet:
            event_data_batch.add(EventData(json.dumps(sigmet)))

        logger.info("Sending data to eventstream...")
        producer.send_batch(event_data_batch)
        logger.info("Done with sending.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

logger.info("Starting...")
start = time.time()
while(True):
    relevant_sigmet = get_new_sigmet()
    send_to_eventstream(relevant_sigmet)
    logger.info("Sleeping for 1 minute")
    time.sleep(60)
    running = time.time() - start
    if running > timeout:
        logger.info("Timeout exceeded. Aborting.")
        break
    else:
        logger.info(f"Continuing...~{int(timeout-running)}s left until timeout.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
