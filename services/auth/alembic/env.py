import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

config = context.config

# Add the src directory to sys.path so we can import our models
sys.path.append(os.path.join(os.getcwd(), "src"))

from database import Base
import models # Import models to register them with Base.metadata

# Override sqlalchemy.url in the ini file with the one from .env
database_url = os.getenv("DATABASE_URL")
if database_url:
    # Alembic expects a synchronous driver for migrations. 
    # Our .env has postgresql+asyncpg, we need to convert it to postgresql for alembic.
    sync_url = database_url.replace("postgresql+asyncpg", "postgresql")
    config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
else:
    run_migrations_online()
