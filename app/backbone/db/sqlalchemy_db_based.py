from abc import abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Sequence,
    String,
    false,
    func,
    inspect,
    select,
    text,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Mapper,
    mapped_column,
)

# =========================================================
# SQLAlchemy Adapter - Async
# =========================================================


class SQLAlchemyAdapter:
    """
    SQLAlchemy Async Adapter

    مسئول:
    - ساخت AsyncEngine
    - ساخت AsyncSession
    - مدیریت Transaction
    - مدیریت Connection Pool
    - اجرای عملیات Async روی PostgreSQL
    """

    engine: Optional[AsyncEngine] = None

    session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def __init__(
        self,
        database_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow

    # =====================================================
    # Initialize
    # =====================================================

    def initialize(
        self,
        echo: bool = False,
    ):
        """
        راه‌اندازی Adapter
        """

        self.create_database_engine(echo=echo)

        self.create_session_factory()

        return self

    # =====================================================
    # Dispose
    # =====================================================

    async def dispose(self):
        """
        بستن AsyncEngine و آزاد کردن Connection Pool
        """

        if self.engine:

            await self.engine.dispose()

            self.engine = None

            self.session_factory = None

    # =====================================================
    # Create Async Engine
    # =====================================================

    def create_database_engine(
        self,
        echo: bool = False,
    ) -> AsyncEngine:

        self.engine = create_async_engine(
            self.database_url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            echo=echo,
        )

        return self.engine

    # =====================================================
    # Create Async Session Factory
    # =====================================================

    def create_session_factory(
        self,
    ):

        if not self.engine:

            raise RuntimeError(
                "ابتدا باید متد " "create_database_engine " "را صدا بزنید."
            )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        return self.session_factory

    # =====================================================
    # Transaction
    # =====================================================

    @asynccontextmanager
    async def transaction(
        self,
    ):

        if not self.session_factory:

            raise RuntimeError(
                "ابتدا باید متد " "create_session_factory " "را صدا بزنید."
            )

        async with self.session_factory() as session:

            try:

                yield session

                await session.commit()

            except SQLAlchemyError:

                await session.rollback()

                raise

            except Exception:

                await session.rollback()

                raise

    # =====================================================
    # Get Session
    # =====================================================

    @asynccontextmanager
    async def session(
        self,
    ):

        if not self.session_factory:

            raise RuntimeError(
                "ابتدا باید متد " "create_session_factory " "را صدا بزنید."
            )

        async with self.session_factory() as session:

            try:

                yield session

            finally:

                await session.close()

    # =====================================================
    # Enum Sync
    # =====================================================

    async def enums_sync(
        self,
    ):

        if not self.session_factory:

            raise RuntimeError("Session Factory ساخته نشده است.")

        # ---------------------------------------------
        # Sync Enum data inside PostgreSQL
        # ---------------------------------------------

        async with self.transaction() as session:

            await EnumMixin.sync_all_enums(session)

        # ---------------------------------------------
        # Generate Python Enum file
        # ---------------------------------------------

        if self.engine:

            await EnumMixin.generate_enums(self.engine)


# =========================================================
# Base Model
# =========================================================


class Base(DeclarativeBase):
    pass


# =========================================================
# ID Mixin
# =========================================================


class IdMixin:

    id: Mapped[int] = mapped_column(
        Sequence(
            "global_id_seq",
            start=10000,
            increment=1,
        ),
        primary_key=True,
        autoincrement=True,
    )


# =========================================================
# User Audit Mixin
# =========================================================


class UserAuditMixin:
    """
    ثبت کاربر ایجادکننده و ویرایش‌کننده
    """

    created_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    updated_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )


# =========================================================
# Timestamp Mixin
# =========================================================


class TimestampMixin:

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# =========================================================
# Soft Delete Mixin
# =========================================================


class SoftDeleteMixin:

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        index=True,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    def soft_delete(
        self,
    ) -> None:

        self.is_deleted = True

        self.deleted_at = datetime.now()


# =========================================================
# Utility Mixin
# =========================================================


class UtilityMixin:

    def __repr__(
        self,
    ) -> str:

        class_name = self.__class__.__name__
        mapper = inspect(self.__class__)
        columns = [col.key for col in mapper.primary_key]
        common_fields = [
            "name",
            "title",
            "username",
            "email",
        ]

        for field in common_fields:

            if hasattr(
                self,
                field,
            ):

                columns.append(field)

        field_strings = []

        for col in columns:

            value = getattr(
                self,
                str(col),
                None,
            )

            field_strings.append(f"{col}={value!r}")

        return f"<{class_name}" f"({', '.join(field_strings)})>"

    def to_dict(self) -> Dict[str, Any]:
        mapper: Mapper[Any] = inspect(self).mapper

        return {
            column.key: getattr(
                self,
                column.key,
            )
            for column in mapper.column_attrs
        }


# =========================================================
# Table Mixin
# =========================================================


class TableMixin(
    Base,
    IdMixin,
    TimestampMixin,
    SoftDeleteMixin,
    UtilityMixin,
    UserAuditMixin,
):

    __abstract__ = True


# =========================================================
# Enum Mixin
# =========================================================


class EnumMixin(TableMixin):

    __abstract__ = True

    title: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    value: Mapped[str] = mapped_column(
        String(100),
    )

    # =====================================================
    # Enum Map
    # =====================================================

    @classmethod
    @abstractmethod
    def get_enum_map(
        cls,
    ) -> Dict[str, str]:

        pass

    # =====================================================
    # Sync One Enum
    # =====================================================

    @classmethod
    async def sync_enum(
        cls,
        session: AsyncSession,
    ) -> None:

        target_map = cls.get_enum_map()

        stmt = select(cls)

        result = await session.execute(stmt)

        current_records = result.scalars().all()

        db_records_by_title = {rec.title: rec for rec in current_records}

        # ---------------------------------------------
        # Create or update records
        # ---------------------------------------------

        for title, value in target_map.items():

            if title in db_records_by_title:

                record = db_records_by_title[title]

                # Restore soft deleted enum

                if record.is_deleted:

                    record.is_deleted = False

                    record.deleted_at = None

                # Update value

                if record.value != value:

                    record.value = value

            else:

                new_enum = cls(
                    title=title,
                    value=value,
                )

                session.add(new_enum)

        for (
            title,
            record,
        ) in db_records_by_title.items():

            if title not in target_map and not record.is_deleted:

                record.soft_delete()

    # =====================================================
    # Sync All Enums
    # =====================================================

    @classmethod
    async def sync_all_enums(
        cls,
        session: AsyncSession,
    ) -> None:

        subclasses = cls.__subclasses__()

        if not subclasses:
            return

        for subclass in subclasses:

            if not hasattr(
                subclass,
                "get_enum_map",
            ):
                continue

            await subclass.sync_enum(session)

    # =====================================================
    # Generate Python Enums
    # =====================================================

    @staticmethod
    async def generate_enums(
        engine: AsyncEngine,
    ) -> None:

        CURRENT_DIR = Path(__file__).resolve().parent

        OUTPUT_FILE = CURRENT_DIR.parent / "db_enums_generated.py"

        # ---------------------------------------------
        # Async Connection
        # ---------------------------------------------

        async with engine.connect() as connection:

            # -----------------------------------------
            # inspect() is a synchronous SQLAlchemy API
            # -----------------------------------------

            all_tables = await connection.run_sync(
                lambda sync_connection: inspect(sync_connection).get_table_names()
            )

            # -----------------------------------------
            # Find Enum tables
            # -----------------------------------------

            enum_tables = [table for table in all_tables if table.endswith("_enum")]

            if not enum_tables:

                print("هیچ جدولی با پسوند " "_enum پیدا نشد.")

                return

            generated_code = [
                "# This file is auto-generated. " "Do not modify manually.\n",
                "from enum import Enum\n\n",
            ]

            # -----------------------------------------
            # Read Enum tables
            # -----------------------------------------

            for table_name in enum_tables:

                class_name = "".join(
                    part.capitalize() for part in table_name.split("_")
                )

                generated_code.append(f"class " f"{class_name}" f"(str, Enum):")

                query = text(f"""
                    SELECT value, title
                    FROM "{table_name}"
                    WHERE is_deleted = false
                    ORDER BY id
                    """)

                result = await connection.execute(query)

                rows = result.fetchall()

                if not rows:

                    generated_code.append("    pass\n")

                    continue

                for row in rows:

                    value = row[0]
                    title = row[1] or ""

                    enum_name = title.upper()

                    generated_code.append(f'    {enum_name} = "{value}"  # {title}')
                generated_code.append("\n")

        # ---------------------------------------------
        # Write generated file
        # ---------------------------------------------

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as f:

            f.write("\n".join(generated_code))

        print("فایل اینام‌ها با موفقیت " f"در مسیر '{OUTPUT_FILE}' " "تولید شد.")
