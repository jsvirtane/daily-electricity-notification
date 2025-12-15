import base64
import json
import os
import sys
from datetime import datetime, timedelta
from typing import TypedDict
from dotenv import load_dotenv
import requests

from authenticate import authenticate

sys.path.append("../pycaruna")
from pycaruna import CarunaPlus, TimeSpan


load_dotenv()


class ConsumptionData(TypedDict):
    timestamp: str
    totalConsumption: float | None


def is_target_date(obj, target_date: datetime) -> bool:
    """Check if the object's timestamp matches the target date."""
    if "timestamp" in obj and obj["timestamp"]:
        obj_date = datetime.fromisoformat(obj["timestamp"][:10])
        return obj_date.date() == target_date.date()
    return False


def send_error_notification(message: str) -> None:
    """Send an error notification using ntfy.sh."""
    topic = os.getenv("NTFY_TOPIC")
    requests.post(
        f"https://ntfy.sh/{topic}",
        data=message.encode(encoding="utf-8"),
        headers={
            "Title": "Virhe kulutustietojen haussa!",
            "Tags": "rotating_light",
        },
    )


def get_yesterday_consumption() -> ConsumptionData | None:
    """Fetch yesterday's energy consumption data."""
    auth = authenticate()
    token = auth.get("token")
    customer_id = auth.get("customer_id")

    if token is None:
        send_error_notification("Autentikointi epäonnistui")

    if customer_id is None:
        send_error_notification("Autentikointi epäonnistui: asiakas-ID puuttuu.")

    # Create a Caruna Plus client
    client = CarunaPlus(token)

    # Get metering points (assets)
    metering_points = client.get_assets(customer_id)
    asset_id = metering_points[0]["assetId"]

    # Calculate yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    year = yesterday.year
    month = yesterday.month
    day = yesterday.day

    # API will return data for the whole month of the given date
    energy_data = client.get_energy(
        customer_id, asset_id, TimeSpan.MONTHLY, year, month, day
    )

    # Find and return yesterday's consumption data
    yesterdays_consumption_data = next(
        iter([data for data in energy_data if is_target_date(data, yesterday)]), None
    )
    if yesterdays_consumption_data:
        return {
            "timestamp": yesterdays_consumption_data["timestamp"],
            "totalConsumption": yesterdays_consumption_data["totalConsumption"],
        }

    return None


if __name__ == "__main__":
    try:
        yesterday_data = get_yesterday_consumption()
        topic = os.getenv("NTFY_TOPIC")

        if yesterday_data:
            # format date DD.MM.YYYY
            date = datetime.fromisoformat(
                yesterday_data.get("timestamp")[:10]
            ).strftime("%d.%m.%Y")
            title = "Sähkön kulutustiedot"
            encoded_title = (
                f"=?UTF-8?B?{base64.b64encode(title.encode('utf-8')).decode('ascii')}?="
            )
            requests.post(
                f"https://ntfy.sh/{topic}",
                data=f"📅 {date}\n⚡️ {yesterday_data.get('totalConsumption')} kWh".encode(
                    encoding="utf-8"
                ),
                headers={
                    "Title": encoded_title,
                    "Tags": "electric_plug",
                },
            )
        else:
            send_error_notification("Eilisen kulutustietoja ei löytynyt.")
    except Exception as e:
        send_error_notification(f"Odottamaton virhe kulutustietojen haussa: {str(e)}")
