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
# META     }
# META   }
# META }

# CELL ********************

# Install in env after..
!pip install azure-eventhub openai azure-kusto-data

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import logging
from time import time, sleep
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.eventhub import EventHubProducerClient, EventData
from datetime import datetime, timedelta, timezone
import pytz
from openai import AzureOpenAI, RateLimitError
import json
import os

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

ENDPOINT = "https://mango-bush-0a9e12903.5.azurestaticapps.net/api/v1"
API_KEY = "a50557c0-d215-4767-93f0-485e14fa8a35"
API_VERSION = "2024-02-01"
MODEL_NAME = "gpt-4-turbo-2024-04-09"
# The query URI for reading the data e.g. https://<>.kusto.data.microsoft.com.
kustoUri = "https://trd-kz4sd5vknmz3u5t26m.z2.kusto.fabric.microsoft.com"
# The database with data to be read.
database = "eh"
producer = EventHubProducerClient.from_connection_string(conn_str="Endpoint=sb://esehdewc6ry5766k5x2e83t3.servicebus.windows.net/;SharedAccessKeyName=key_52e9c2ee-3788-4e26-ac04-392337f4739f;SharedAccessKey=7jTS8gT07txjNnhV20VZHa7bCrahtRYWb+AEhLMcsts=;EntityPath=es_fb3931b1-6cee-4098-94c9-ceafed418b04")
client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version=API_VERSION)

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

def execute_query(query: str): # returns kusto resultset, to lazy to lookup for hint
    logger.info(f"Executing query on eventhouse: {query}")
    # The access credentials.
    accessToken = mssparkutils.credentials.getToken(kustoUri)
    # Create a Kusto connection string
    kcsb = KustoConnectionStringBuilder.with_aad_application_token_authentication(kustoUri, accessToken)
    # Create a Kusto client
    client = KustoClient(kcsb)

    # Execute the query
    results = client.execute(database, query).primary_results[0]
    logger.info(f"Retrieved {results.rows_count} records.")
    return results


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

logger = get_logger()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

start_delay_minutes=5
last_max_timestamp = (datetime.now(pytz.UTC) - timedelta(minutes=start_delay_minutes))
while True:
    alarms = execute_query(f"GoldAlarmsFirstUpdate | where alarm_silver_timestamp  > todatetime(\"{last_max_timestamp}\") | join kind=inner GoldFlights on icao24, callsign | project-away icao241, callsign1 | join kind=inner GoldWeather on isigmetId|project callsign, isigmetId, icao24, rawSigmet, alarm_silver_timestamp")
    left = len(alarms)
    for alarm in alarms:
        alarm = alarm.to_dict()

        if alarm["alarm_silver_timestamp"] > last_max_timestamp:
            last_max_timestamp = alarm["alarm_silver_timestamp"]
        
        MESSAGES = [
            {"role": "system", "content": "You are an ATC (Air Traffic Control). You inform a pilot because he is affected by a SIGMET warning. Structure your message according to standard phraseology as outlined by the International Civil Aviation Organization (ICAO)."},
            {"role": "user", "content": f"Raw SIGMET warning: {alarm['rawSigmet']}. \n Aircraft Callsign: {alarm['callsign']}"},
        ]
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=MESSAGES,
                max_tokens=300
            )
        except RateLimitError:
            logger.warning("API Limit reached. Sleeping for 60s and retrying. %d messages left", left)
            sleep(60)
            try:
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=MESSAGES,
                    max_tokens=300)
            except RateLimitError:
                #Workaround so it doesnt cancel when rate limit is hit even after sleeping
                continue
                
        left-=1
        alarm["msg"] = completion.choices[0].message.content
        alarm["alarm_silver_timestamp"] = alarm["alarm_silver_timestamp"].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        producer.send_event(EventData(json.dumps(alarm)))
    logger.info("Processed %s alarm messages. Sleeping for 10s", len(alarms))
    sleep(10)


# !TODO!: Also send the text message to text to speech service, save as file or so in Lakehouse afterwards.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
