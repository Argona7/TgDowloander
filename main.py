import asyncio
from loguru import logger
from src import dump_channel

def main():
    try:
        asyncio.run(dump_channel())
    except KeyboardInterrupt:
        logger.warning("[interrupted] Остановлено пользователем.")
        raise SystemExit(130)

if __name__ == "__main__":
    main()