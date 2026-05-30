import os
from dotenv import load_dotenv

load_dotenv()
print(f"DEBUG: Connecting to {os.getenv('DATABASE_URL')}")

import asyncio
from app.database import engine

async def test():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(__import__('sqlalchemy').text('SELECT 1'))
            print('✅ Database terkoneksi!' if result.scalar() == 1 else '❌ Gagal')
    except Exception as e:
        print(f"❌ ERROR: {e}")

asyncio.run(test())

