from backbone.db.sqlalchemy_db_based import EnumMixin, SQLAlchemyAdapter
from bootstrap.locator import script
import asyncio


async def main():
    async with script() as loc:
        sqlAlchemyAdapter: SQLAlchemyAdapter = loc.get("SQLAlchemyAdapter")
        with sqlAlchemyAdapter.session_factory() as session:
            EnumMixin.sync_all_enums(session)


if __name__ == "__main__":
    asyncio.run(main())
