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
# META       "environmentId": "610f7f69-d66e-457c-a20b-dd6007c8030b",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# CELL ********************

%run get_adsbdb_data to eventstream {"endpoint":"aircraft"}

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

stream_data()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
