from imports import *

from base.redis import RedisConnection
from dotenv import load_dotenv
from os import getenv
from discord.ext.commands import (
    BotMissingPermissions,
    Context,
    CommandError,
    NotOwner,
    CheckFailure
)
from config import DISCORD

logger = getLogger(__name__)

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

load_dotenv(verbose=True)

intents = Intents.all()
intents.messages= True
intents.members = True
intents.presences = False

class Venari(AutoShardedBot):
    pool: Pool
    bool: datetime
    redis: RedisConnection(uri=getenv("REDIS_URI", "redis://localhost"))

    def __init__(self) -> None:
        super().__init__(
            command_prefix=(DISCORD.PREFIX), # type: ignore
            case_insensitive=True,
            intents=intents,
            allowed_mentions=AllowedMentions(
                everyone=False, users=True, roles=False, replied_user=True
            ),
            help_command=None,
            activity=CustomActivity(name=">_<"),
            owner_ids=[
                785042666475225109, # @playfairs
                608450597347262472, # @bevlynous
            ],
        )
        self._uptime = time.time()

    @property
    def ping(self):
        return round(self.latency * 1000)

    @property
    def booted(self):
        return format_dt(self.boot, style="R")

    async def load_extensions(self, directory: str = "cogs"):
        for module in glob.glob(f"{directory}/**/*.py", recursive=True):
            module_path = (
                module.replace("/", ".")
                .replace("\\", ".")
                .replace(".__init__", "")[:-3]
            )
            try:
                await self.load_extension(module_path)
                logger.info(f"Loaded Cog: {module_path}")
            except ExtensionFailed:
                logger.warning(f"Cog failed to load: {module}")
            except Exception as e:
                pass

async def _load_database(self) -> Pool:
    try:
        pool = await create_pool(
            dsn="postgresql://postgres:admin@localhost/postgres",
            max_size=30,
            min_size=10,
        )
        logger.info("Database connection established")

        with open(
            ['src' , 'base' , 'schema' , 'schema.sql'], "r"
        ) as file:
            schema = file.read()
            if schema.strip():
                await pool.execute(schema)  # type: ignore
                logger.info("Database schema loaded")
            else:
                logger.warning("Database schema file is empty")
            file.close()

        return pool  # type: ignore
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        raise e