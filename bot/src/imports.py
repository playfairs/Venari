import glob
import os
import pathlib
import time

from typing import (
    Dict,
    List,
    Optional,
    Union,
)
from datetime import (
    datetime,
    timedelta,
)
from discord import (
    AllowedMentions,
    CustomActivity,
    Embed,
    Forbidden,
    Guild,
    Intents,
    Invite,
    Member,
    Message,
)
from discord.utils import format_dt
from discord.ext.commands import (
    AutoShardedBot,
    CommandError,
    CheckFailure,
    ChannelNotFound,
    CommandNotFound,
    CommandOnCooldown,
    ExtensionFailed,
    MissingPermissions,
    MinimalHelpCommand,
    NotOwner,
    RoleNotFound,
    UserNotFound,
    ThreadNotFound,
    when_mentioned_or,
)

from loguru import logger
from asyncpg import Pool, create_pool
from collections import defaultdict
from psutil import Process
import psutil
import random