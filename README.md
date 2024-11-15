![Logo](docs/MeteoWatchWide.jpg)
# 🌐MeteoWatch: Real-time Aviation Weather Intelligence

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Airplane.png" alt="Airplane" width="25" height="25" /> Overview
MeteoWatch is a real-time intelligence solution designed to monitor flights for potential weather hazards. Developed during the [Microsoft Fabric and AI Learning Hackathon](https://microsoftfabric.devpost.com/), MeteoWatch leverages Microsoft Fabric and Azure OpenAI to enhance aviation safety awareness.

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Compass.png" alt="Compass" width="25" height="25" /> What it does
![Use Case Diagram](docs/Usecase.png)

MeteoWatch integrates data from [Openskynetwork](https://opensky-network.org/), [Adsdb](https://www.adsbdb.com/), and [AviationWeather](https://aviationweather.gov/) to provide:

- 🛩️ Real-time tracking of aircraft positions and flight routes
- 🌪️ Monitoring of areas with reported SIGMETs (Significant Meteorological Information)
- ⚠️ Calculation of potential SIGMET impacts on flights
- 💬 Generation of warning messages for affected aircraft
- 📊 A dashboard for stakeholders such as air traffic controllers and pilots

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Glowing%20Star.png" alt="Glowing Star" width="25" height="25" /> Preview

### 🚨 Generated Alarms by OpenAI
![Alarm System](./docs/AlarmsGIF.gif)


### 📊 Dashboard in Power BI
![Dashboard](./docs/DashboardGIF.gif)

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Hand%20gestures/Raising%20Hands.png" alt="Raising Hands" width="25" height="25" /> How we built it

MeteoWatch utilizes a combination of technologies:

1. 📥 **Data Ingestion**: Notebooks extract data from web APIs into an EventStream, which feeds an EventHouse.
2. 🏗️ **Architecture**: Implements a real-time intelligence medallion architecture.
3. 🔄 **Data Transformation**: Update policies process data from bronze to silver layers.
4. 🧮 **Data Processing**: Materialized views in gold on top of the silver layer handle geometries, intersections, alarms, and data aggregation.
5. 🤖 **AI Integration**: Azure OpenAI API is used to generate warning messages.
6. 🚨 **Alert System**: EventStream sends alerts to Reflex for notification distribution.
7. 📈 **Visualization**: A dashboard in Power BI built on the gold layer displays relevant information.

![Architecture Diagram](docs/archi.drawio.png)

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Rocket.png" alt="Rocket" width="25" height="25" /> Installation Guide for Microsoft Fabric

To set up MeteoWatch:

1. 🏗️ Create a new Microsoft Fabric workspace
2. 🔀 Fork or import this repository into Azure DevOps or GitHub.
3. 🔗 Link the `fabric` folder to your workspace
4. 🏠 Set up an EventHouse and KQL database
5. 📜 Create KQL database artifacts using provided querysets: `weather`, `aircrafts`, `callsigns`, `openskynet`, `flights`, `alarms`, `shapes`
6. 🌊 Create 5 EventStreams with custom endpoint sources: `openskynet-es`, `weather-es`, `callsigns-es`, `aircrafts-es`, `alarms-es`
7. 🔄 Update and run ingestion notebooks
8. 🔌 Configure ingestion EventStream sinks to corresponding bronze tables (direct ingestion)
9. 🔑 Update and run the `send_alerts` notebook
10. ⚡ Create a Reflex based on the alarms EventStream (`alarms-es`)
11. 🔍 Open report/semantic model and resolve any connection/reference issues

After completing these steps, your MeteoWatch system should be operational. 🎉
