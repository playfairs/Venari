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


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

load_dotenv(verbose=True)

intents = Intents.all()
intents.messages= True
intents.members = True
intents.presences = False

class Venari(AutoShardedBot):
    pool: Optional[Pool]
    boot: datetime
    redis: RedisConnection

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
        self.redis = RedisConnection(uri=getenv("REDIS_URI", "redis://localhost"))

    @property
    def ping(self):
        return round(self.latency * 1000)

    @property
    def booted(self):
        return format_dt(self.boot, style="R")

    async def load_extensions(self, directory: str = "root"):
        for module in glob.glob(f"{directory}/**/*.py", recursive=True):
            if module.endswith("__init__.py"):
                continue
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
                logger.exception(f"Unexpected error loading {module_path}: {e}")

    async def _load_database(self) -> Optional[Pool]:
        try:
            dsn = getenv("POSTGRES_DSN")
            if not dsn:
                logger.info("POSTGRES_DSN not set; skipping database initialization")
                return None

            pool = await create_pool(
                dsn=dsn,
                max_size=30,
                min_size=10,
            )
            logger.info("Database connection established")

            try:
                schema_path = pathlib.Path(__file__).resolve().parent / "schema" / "schema.sql"
                if schema_path.exists():
                    schema = schema_path.read_text()
                    if schema.strip():
                        await pool.execute(schema)  # type: ignore
                        logger.info("Database schema loaded")
                    else:
                        logger.warning("Database schema file is empty")
                else:
                    logger.info(f"Schema file not found at {schema_path}, skipping schema load")
            except Exception as se:
                logger.exception(f"Failed to load schema: {se}")

            return pool  # type: ignore
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return None

    async def setup_hook(self) -> None:
        await self.load_extensions()
        self.boot = datetime.now()
        self.pool = await self._load_database()
        await self.redis.connect()
        try:
            await self.load_extension("jishaku")
            logger.info("Loaded extension: jishaku")
        except Exception as e:
            logger.warning(f"Failed to load jishaku: {e}")

    async def on_command(self, ctx) -> None:
        logger.info(
            f"{ctx.author} ({ctx.author.id}) executed {ctx.command} in {ctx.guild} ({ctx.guild.id})"
        )

    async def on_command_error(self, ctx: Context, exception: CommandError) -> None:
        if type(exception) in (NotOwner, CheckFailure):
            return

        elif isinstance(exception, BotMissingPermissions):
            return await ctx.send(
            f"I'm missing permission: '{', '.join(p for p in exception.missing_permissions)}'" # type: ignore
            )