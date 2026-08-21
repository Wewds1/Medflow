import asyncio
import os
import json
import redis.asyncio as redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

from database import async_session
from models import MedicationBatch, DispenseLog, BatchStatus
import services


# Load env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(str(env_path))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def process_prescription(payload: dict, db: AsyncSession):
    med_name = payload.get("medication_name")
    qty_needed = payload.get("quantity")
    patient_id = payload.get("patient_id")
    doctor_id = payload.get("doctor_id") # Using doctor_id as staff_id for now

    print(f"Processing prescription: {med_name} (qty: {qty_needed}) for patient {patient_id}")

    try:
        log = await services.dispense_medication(
            db=db,
            med_name=med_name,
            qty=qty_needed,
            patient_id=patient_id,
            staff_id=doctor_id
        )
        print(f"Successfully dispensed {qty_needed} of {med_name} from batch {log.batch_id}")
        return True
    except ValueError as e:
        print(f"Dispense Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


async def consume_events():
    print("Starting Pharmacy Event Consumer...")
    stream_name = "medflow_events"
    group_name = "pharmacy_group"

    # Create consumer group if it doesn't exist
    try:
        await redis_client.xgroup_create(stream_name, group_name, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "already exists" not in str(e):
            raise e

    while True:
        try:
            # Read new events
            # XREADGROUP GROUP pharmacy_group consumer1 COUNT 1 BLOCK 1000 STREAMS medflow_events >
            events = await redis_client.xreadgroup(group_name, "consumer1", {stream_name: ">"}, count=1, block=1000)

            for stream, messages in events:
                for msg_id, payload in messages:
                    event_type = payload.get("event_type")
                    if event_type == "prescription_created":
                        data = json.loads(payload.get("data", "{}"))

                        async with async_session() as db:
                            async with db.begin():
                                success = await process_prescription(data, db)
                                if success:
                                    await db.commit()

                        # Acknowledge the message
                        await redis_client.xack(stream_name, group_name, msg_id)
                        print(f"Acknowledged event {msg_id}")

        except Exception as e:
            print(f"Consumer Error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(consume_events())
