# Overview
MeteoWatch is a realtime intelligence solution based on open aviation data that monitors flights in regards to weather hazards. MeteoWatch was build during the [Microsoft Fabric and AI Learning Hackathon](https://microsoftfabric.devpost.com/).

# What it does
The system consumes data from openskynet, adsdb and aviationweather. Using this data MeteoWatch knows the current position of aircrafts and their flight route. Further the systems knows the area where weather hazards so called SIGMETs (Significant Meteorological Information) are reported. MeteoWatch then calculates whether a flight will be affected by a Sigmet and creates a warning message in natural language. This message could be tailored and send to a specific aircraft. Further MeteoWatch contains a dashboard where related stakeholders like air control or pilots are presented the flight route and affecting weather hazards as well as other useful information. 

![uc](docs/usecase.drawio.png)

![dashboard](docs/Dashboard.png)

# How we built it
The ingestion is built with notebooks. All the data is available via web apis. We send the data to eventstream to ingest it into an eventhouse. Simply put we build a real time intelligence medaillon architecture. We use update policies to do basic transformations and cleanup from bronze to silver layer. On top of the silver layer we use materialized views to create geometries in different formats, calculate intersections, track alarms, aggregate to newest information, etc.. We then use a notebook to send the alarms to azure openai api to create more meaningful warning messages. These are send to eventstream and from their to reflex, where alerting via email, teams message, etc. could be configured. Further we build a dashboard on top of the gold layer where all the geometries (positions, trajectories, hazards) as well as other useful information are displayed.

![architecture](docs/archi.drawio.png)