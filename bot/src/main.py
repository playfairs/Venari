from base.bot import Venari
import asyncio
import dotenv
import os

dotenv.load_dotenv()

async def main():
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("Token not found in environment variables")
    
    async with Venari() as venari:
        await venari.start(token)

if __name__ == "__main__":
    asyncio.run(main())