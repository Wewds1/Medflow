import asyncio
import os
import json
import redis.asyncio as redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

from database import async_session
from models import OutboxEvent

# Load env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(str(env_path))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def publish_events():
    print("Starting Outbox Publisher...")
    while True:
        try:
            async with async_session() as session:
                # 1. Fetch pending events
                result = await session.execute(
                    select(OutboxEvent).where(OutboxEvent.processed == 0).order_by(OutboxEvent.created_at)
                )
                events = result.scalars().all()

                for event in events:
                    # 2. Push to Redis Stream
                    # Stream name: medflow_events
                    # Payload: {event_type, data}
                    payload = {
                        "event_type": event.event_type,
                        "data": json.dumps(event.payload)
                    }
                    await redis_client.xadd("medflow_events", payload)

                    # 3. Mark as processed
                    event.processed = 1
                    event.processed_at = datetime.utcnow()

                await session.commit()

                if events:
                    print(f"Published {len(events)} events.")

        except Exception as e:
            print(f"Publisher Error: {e}")

        await asyncio.sleep(1) # Poll every second

if __name__ == "__main__":
    asyncio.run(publish_events())
