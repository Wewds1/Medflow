import asyncio
import asyncpg

async def create_db():
    # Connect to the default 'postgres' database to create 'db_auth'
    conn = await asyncpg.connect(user='postgres', password='postgres', database='postgres', host='127.0.0.1')
    try:
        await conn.execute('CREATE DATABASE db_auth')
        print("Database 'db_auth' created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_db())
