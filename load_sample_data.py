#!/usr/bin/env python3
import asyncio
import csv
from sqlmodel import Session, create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Village, Member
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./satsangee.db")

if DATABASE_URL.startswith("postgres"):
    if "sslmode=" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?")[0]
    
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def load_villages():
    async with async_session_maker() as session:
        with open('sample_villages.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                village = Village(
                    name=row['name'],
                    block=row['block'],
                    lat=float(row['lat']),
                    lng=float(row['lng']),
                    south=float(row['south']),
                    west=float(row['west']),
                    north=float(row['north']),
                    east=float(row['east']),
                    code_2011=row.get('code_2011', '')
                )
                session.add(village)
            await session.commit()
    print("✓ Loaded villages")


async def load_members():
    async with async_session_maker() as session:
        with open('sample_members.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                result = await session.execute(
                    select(Village).where(Village.name == row['village'])
                )
                village = result.scalar_one_or_none()
                
                if not village:
                    print(f"⚠ Village '{row['village']}' not found for member {row['full_name']}")
                    continue
                
                member = Member(
                    full_name=row['full_name'],
                    role=row['role'],
                    phone=row['phone'],
                    languages=row.get('languages', ''),
                    village_id=village.id,
                    verified=True
                )
                session.add(member)
            await session.commit()
    print("✓ Loaded members")


async def main():
    print("Loading sample data...")
    await load_villages()
    await load_members()
    print("✓ All sample data loaded successfully!")


if __name__ == '__main__':
    asyncio.run(main())
