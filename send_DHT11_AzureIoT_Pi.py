# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import asyncio
import time
import uuid
import sys
import Adafruit_DHT
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

async def read_temp_humidity():
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    # print('Temp={0:0.1f}°C  Humidity={1:0.1f}%'.format(temperature, humidity))
    return round(temperature,1), round(humidity,1)

async def send_recurring_telemetry(device_client):
    # Connect the client.
    await device_client.connect()

    # Send recurring telemetry
    while True:
        temperature, humidity = await read_temp_humidity()
        msg_txt_formatted = '{{"temperature": {temperature}, "humidity": {humidity}}}'
        data = msg_txt_formatted.format(temperature=temperature, humidity=humidity)
        msg = Message(data)
        msg.content_encoding = "utf-8"
        msg.content_type = "application/json"
        if temperature > 30:
            msg.custom_properties["temperatureAlert"] = "true"
        print("sending message - " + str(data))
        await device_client.send_message(msg)
        time.sleep(3)


def main():
    # The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
    conn_str = "<your_device_connection_string>"
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    print("IoTHub Device Client Recurring Telemetry Sample")
    print("Press Ctrl+C to exit")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(send_recurring_telemetry(device_client))
    except KeyboardInterrupt:
        print("User initiated exit")
    except Exception:
        print("Unexpected exception!")
        raise
    finally:
        loop.run_until_complete(device_client.shutdown())
        loop.close()


if __name__ == "__main__":
    main()