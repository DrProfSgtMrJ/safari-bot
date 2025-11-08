import asyncio
from sqlalchemy import text
from db.db import AsyncSessionLocal

async def run_sql_file(path: str):
    async with AsyncSessionLocal() as session:
        with open(path, "r", encoding="utf-8") as f:
            sql_script = f.read()
            
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

        for stmt in statements:
            print(f"Executing:\n{stmt}\n")
            await session.execute(text(stmt))
        await session.commit()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("usage: poetry run python tools/run_sql_file.py <path_to_sql_file>")
        sys.exit(1)
    sql_path = sys.argv[1]
    asyncio.run(run_sql_file(sql_path))
