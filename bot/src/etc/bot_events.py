from discord.ext.commands import Cog, CommandError
from discord import utils, Guild, Client, Embed, File, Message
from lib.patch.context import Context
import re
import asyncio
from aiomisc.backoff import asyncretry
from io import BytesIO
import os
from aiohttp import ClientSession
import humanize