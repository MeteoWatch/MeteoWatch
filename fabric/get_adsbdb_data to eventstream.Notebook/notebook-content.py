# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse_name": "",
# META       "default_lakehouse_workspace_id": "",
# META       "known_lakehouses": [
# META         {
# META           "id": "1ae157b7-2c0f-4094-a65d-3ed712519a22"
# META         }
# META       ]
# META     },
# META     "environment": {
# META       "environmentId": "610f7f69-d66e-457c-a20b-dd6007c8030b",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# PARAMETERS CELL ********************

endpoint = "callsign"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#sample_data
# table_name: str = "bronze_adsbdb_flights"
# endpoint: str = "callsign"
# value: str = "ELY25"

# table_name: str = "bronze_adsbdb_aircraft"
# endpoint: str = "aircraft"
# value: str = "E80447"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import requests
import json
import logging
from time import time, sleep
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.eventhub import EventHubProducerClient, EventData

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


def get_api_data(endpoint: str, value: str, api_version: str = 'v0') -> str:
    logger.debug(f"Fetching {value} from endpoint {endpoint}.")
    base_url = f"https://api.adsbdb.com/{api_version}/{endpoint}/{value}"
    
    response = requests.get(base_url)
    
    if response.status_code == 200:
        return response.status_code, response.json()["response"][params["response_root"]]
    elif response.status_code == 404:
        return response.status_code, {"error": "Unknown value or endpoint"}
    elif response.status_code == 429:
        return response.status_code, {"error":"Too many requests"}
    else:
        return response.status_code, {"error": f"Failed to retrieve data. Status code: {response.status_code}"}

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

def send_data_to_eventstream(data) -> None: #todo: typehint kusto result object..
    start_time = time()
    logger.info("Starting pulling data from api and streaming to event stream...")
    for row in data:
        status_code, data = get_api_data(endpoint, row[0])
        if status_code == 429:
            logger.warning("Api limit reached. Breaking..")
            break
        if status_code == 200:
            data["valid"] = True
        else:
            data = {}
            data["valid"] = False
        data["id"] = row[0]
        producer.send_event(EventData(json.dumps(data)))
    producer.close()
    logger.info(f'Done with sending to eventstream. Took {time() - start_time}s.')

def stream_data():
    logger.info("Starting...")
    start = time()
    while(True):
        results = execute_query(params["fetch_query"])
        send_data_to_eventstream(results)
        t = 60 
        logger.info(f"Sleeping for {t}s.")
        sleep(t)
        running = time() - start
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

# CELL ********************

logger = get_logger()
timeout = 16 * 60 * 60 # first is hours
params_by_endpoint = {
    "response_root": {"callsign":"flightroute", "aircraft":"aircraft"},
    "eventstream_endpoint":{"aircraft": "Endpoint=sb://esehdewc8cyp64cyfd4y1nqt.servicebus.windows.net/;SharedAccessKeyName=key_fa9a7170-6fea-48b7-a20a-84abe170a37c;SharedAccessKey=9rSbzk0LMyWbYxAkouOAshSGWIKzwgZQF+AEhKs1w8M=;EntityPath=es_31f7655d-1027-4c63-8548-31e5e581cdee", "callsign": "Endpoint=sb://esehdewcb9054fdv27efrym3.servicebus.windows.net/;SharedAccessKeyName=key_c85f0ace-498e-4b98-bd2d-7ae54a924284;SharedAccessKey=QRIlDXowsKoJe1XGiENAYGXjspgFsvHL4+AEhFwWXAY=;EntityPath=es_d8d517dc-d2c5-4696-a462-1030af283a35"},
    "fetch_query": {"aircraft":"SilverOpenskynet | join kind=anti SilverAircrafts on icao24 | distinct icao24", "callsign":"SilverOpenskynet | join kind=anti SilverCallsigns on callsign | distinct callsign"} #todo: Swap back to silver for callsigns
    }
params = {key:val[endpoint] for key, val in params_by_endpoint.items()}
# The query URI for reading the data e.g. https://<>.kusto.data.microsoft.com.
kustoUri = "https://trd-kz4sd5vknmz3u5t26m.z2.kusto.fabric.microsoft.com"
# The database with data to be read.
database = "eh"
producer = EventHubProducerClient.from_connection_string(conn_str=params["eventstream_endpoint"])
#stream_data()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# # push some to eventstream for callsign to have proper data for configuration
# for call_sign in ["ELY25", "RCH230"]:
#     status_code, result = get_api_data("callsign", call_sign)
#     result["valid"] = True
#     result["id"] = call_sign
#     producer.send_event(EventData(json.dumps(result)))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
