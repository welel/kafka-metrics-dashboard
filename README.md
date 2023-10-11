<h2 align="center">Kafka Metrics</h2>

<p align="center">Gain Insights into Kafka Topics with Real-time Metric Monitoring.</p>

This web service facilitates the monitoring of Kafka Topic metrics, encompassing key indicators such as the **total number of messages, messages processed, messages queued, the velocity of incoming tasks for a topic, task processing speed, and timestamps indicating the initiation and completion processing times of a topic.** Additionally, the service offers **visual representation through informative charts**. The charts provide insights into progress, with one aspect showing **the message count and the other detailing the speed of load and processing**. Furthermore, each topic is assigned a **status, indicating its current state as active, completed, or inactive**.

</br>

## :chart_with_upwards_trend: Metrics

**Header**

<p align="left"><img src="https://i.ibb.co/QM26JCz/Group-2top.png" alt="Header"  border="0" /></p>

1. Topic statuses (active, done, inactive).
2. Total number of messages in topics (total, processed, remaining).

</br>

**Topics accordion**

<p align="left"><img src="https://i.ibb.co/j5xKFHQ/Group-3accordion.png" alt="Accordion"  border="0" /></p>

1. A topic's icon indicates its status.
2. A topic label.
3. A real topic name.
4. The progress in percent.

</br>

**Topic card**

<p align="left"><img src="https://i.ibb.co/MDZj2CV/Group-5card.png" alt="NoteD. Home"  border="0" /></p>

1. Total, processed, remaining number of messages.
2. Topic's load and processing speeds.
3. A pie chart indicates the progress.
4. Estimated processing duration.
5. Start and estimated end timestamps.
6. A load and processing speed chart.
7. A total, processed, remaining number of messages chart.


<br>

## 🛠️ Tech stack

- Python 3.10
- FastAPI
- SQLAlchemy 2.*
- uvicorn
- Bootstrap
- Docker/Docker-compose

</br>


## 🏗️ Installation

1. The project uses an external SQL database that is compatible with SQLAlchemy. You should create your own Kafka metrics collector to collect Kafka metrics. The database should already be created and filled with data before running the project. The database configuration is placed in the `.env.dist` file. Insert metrics updates every 10 seconds for each topic.

    The database schema:

    ```sql
    CREATE TABLE IF NOT EXISTS collector_offser (
        id SERIAL PRIMARY KEY,
        name character varying(64) NOT NULL,
        processed integer NOT NULL,
        remaining integer NOT NULL,
        requested timestamp with time zone NOT NULL DEFAULT NOW()
    )
    ```
    - **name** - A topic name.
    - **processed** - Current number of processed topic messages.
    - **remaining** - Current number of remaining topic messages.
    - **requested** - A timestamp when the current topic state was inserted. 


2. Clone or download the repository.
   
3. Fill `.env.dist` file with required data and rename it to `.env`.

4. Run the docker compose file. After creating containers, wait for metrics server initialization (around 1 minute).

    ```bash
    docker compose up --build
    ```

5. Go to the URL http://localhost:8000.
