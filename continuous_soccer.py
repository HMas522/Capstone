"""
Purpose: Illustrate addition of continuous information. 

This is a simple example that uses a deque to store the last 15 minutes of
temperature readings for three locations.

The data is updated every minute.

Continuous information might also come from a database, a data lake, a data warehouse, or a cloud service.

----------------------------
Open API Football Information
-----------------------------

Go to: https://rapidapi.com/api-sports/api/api-football

And sign up for your own free account and API key. 

The key should be kept secret - do not share it with others.
Open Footbal API allows 30 free requests per min.
(That's about 125 per working hour, so comment it out when first testing. -weather API)

After everything works, and you have your own API key, uncomment it and use the real information.

-----------------------
Keeping Secrets Secret
-----------------------

Keep secrets in a .env file - load it, read the values.
Add the .env file to your .gitignore so you don't publish it to GitHub.
We usually include a .env-example file to illustrate the format.

"""


# Standard Library
import asyncio
from datetime import datetime
from pathlib import Path
import os
from random import randint

# External Packages
import pandas as pd
from collections import deque
from dotenv import load_dotenv

# Local Imports
from fetch import fetch_from_url
from util_logger import setup_logger

# Set up a file logger
logger, log_filename = setup_logger(__file__)

load_dotenv()
def get_API_key():
    # Keep secrets in a .env file - load it, read the values.
    # Load environment variables from .env file
    load_dotenv()
    key = os.getenv("OPEN_FOOTBALL_API_KEY")
    return key


async def get_temperature_from_openweathermap(lat, long):
    logger.info("Calling get_temperature_from_openweathermap for {lat}, {long}}")
    api_key = get_API_key()
    open_weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={api_key}&units=imperial"
    logger.info(f"Calling fetch_from_url for {open_weather_url}")
    result = await fetch_from_url(open_weather_url, "json")
    logger.info(f"Data from openweathermap: {result}")
    # temp_F = data["main"]["temp"]
    temp_F = randint(68, 77)
    return temp_F


# Function to create or overwrite the CSV file with column headings
def init_csv_file(file_path):
    df_empty = pd.DataFrame(
        columns=["Location", "Latitude", "Longitude", "Time", "Temp_F"]
    )
    df_empty.to_csv(file_path, index=False)


async def update_csv_soccer():
    """Update the CSV file with the latest soccer information."""
    logger.info("Calling update_csv_soccer")
    try:
        #Teams? = ["Kansas City US", "Denver US", "Maryville MO"]
        update_interval = 60  # Update every 1 minute (60 seconds)
        total_runtime = 15 * 60  # Total runtime maximum of 15 minutes
        num_updates = 10  # Keep the most recent 10 readings
        logger.info(f"update_interval: {update_interval}")
        logger.info(f"total_runtime: {total_runtime}")
        logger.info(f"num_updates: {num_updates}")

        # Use a deque to store just the last, most recent 10 readings in order
        records_deque = deque(maxlen=num_updates)

        fp = Path(__file__).parent.joinpath("data").joinpath("soccer.csv")

        # Check if the file exists, if not, create it with only the column headings
        if not os.path.exists(fp):
            init_csv_file(fp)

        logger.info(f"Initialized csv file at {fp}")

        for _ in range(num_updates):  # To get num_updates readings
            for location in locations:
                lat, long = lookup_lat_long(location)
                new_temp = await get_temperature_from_openweathermap(lat, long)
                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time
                new_record = {
                    "Location": location,
                    "Latitude": lat,
                    "Longitude": long,
                    "Time": time_now,
                    "Temp_F": new_temp,
                }
                records_deque.append(new_record)

            # Use the deque to make a DataFrame
            df = pd.DataFrame(records_deque)

            # Save the DataFrame to the CSV file, deleting its contents before writing
            df.to_csv(fp, index=False, mode="w")
            logger.info(f"Saving temperatures to {fp}")

            # Wait for update_interval seconds before the next reading
            await asyncio.sleep(update_interval)

    except Exception as e:
        logger.error(f"ERROR in update_csv_location: {e}")
