import discord
import webview
import time
import sys
from threading import Thread
import json
import asyncio
import functools

from .config import SECRET_TOKEN


class ConcordClient(discord.Client):
    def __init__(self, **args):
        super().__init__(**args)
        self._window = args['window']
        self._api = None

    async def on_ready(self):
        js = 'discordReadyHandler();'
        self._window.evaluate_js(js)
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if self._api.active_channel == message.channel:
            self._api.add_message(message)

    def attach_api(self, api):
        self._api = api


class JSAPI:

    def __init__(self):
        self._client = None
        self._window = None
        self._active_channel = None

    def get_guilds(self):
        for guild in self._client.guilds:
            js = "addGuild({0}, {1});".format(
                json.dumps(str(guild.id)),
                json.dumps(guild.name)
            )
            self._window.evaluate_js(js)

    def add_message(self, message):
        message = {
            'id': str(message.id),
            'author_name': message.author.name,
            'content': message.content,
            'created_at': message.created_at.timestamp(),
            'channel_id': str(message.channel.id)
        }

        js = "addMessage({0});".format(
            json.dumps(message)
        )
        self._window.evaluate_js(js)

    def add_channel(self, channel, read_messages_permission):
        channel = {
            'id': str(channel.id),
            'name': channel.name,
            'category_id': str(
                channel.category_id) if channel.category_id is not None else None,
            'read_messages_permission': read_messages_permission
        }

        js = "addChannel({0});".format(
            json.dumps(channel)
        )
        self._window.evaluate_js(js)

    def add_category(self, channel):
        channel = {
            'id': str(channel.id),
            'name': channel.name
        }

        js = "addCategory({0});".format(
            json.dumps(channel),
        )
        self._window.evaluate_js(js)

    @property
    def active_channel(self):
        return self._active_channel

    def set_active_channel(self, channel_id):
        self._active_channel = self._client.get_channel(int(channel_id))
        self._window.set_title("#" + self._active_channel.name +
                               " – " + self._active_channel.guild.name + " – Concord")

    def get_channels(self, guild_id):
        guild = self._client.get_guild(int(guild_id))
        channels = []
        categories = []
        for channel in guild.channels:

            if isinstance(channel, discord.TextChannel):
                channels.append(channel)
            elif isinstance(channel, discord.CategoryChannel):
                categories.append(channel)

        for category in sorted(categories, key=lambda category: category.position):
            self.add_category(category)

        for channel in sorted(channels, key=lambda channel: channel.position):
            member = guild.get_member(self._client.user.id)
            read_messages_permission = True
            try:
                read_messages_permission = channel.permissions_for(
                    member).read_messages
            except Exception as err:
                print('error while retrieving permissions:', err)
            self.add_channel(channel, read_messages_permission)

        raise Exception('no guild found with id ' + guild_id)
        print("no channel found")

    def get_messages(self, channel_id):
        channel = self._client.get_channel(int(channel_id))
        try:
            asyncio.run_coroutine_threadsafe(
                self.get_messages_coro(channel), self._client.loop)
        except Exception as err:
            print('exception:', err)

    def send_message(self, content):
        try:
            asyncio.run_coroutine_threadsafe(
                self._active_channel.send(content), self._client.loop)
        except Exception as err:
            print('exception:', err)

    def attach_client(self, client):
        self._client = client

    def attach_window(self, window):
        self._window = window

    async def get_messages_coro(self, channel):
        try:
            messages = await channel.history(limit=20, oldest_first=False).flatten()
        except Exception as err:
            print('error while retrieving messages:', err)
        for message in reversed(messages):
            self.add_message(message)


def discord_coroutine(client):
    return client.run(
        SECRET_TOKEN,
        bot=False)


def close(client):
    client.close()


def main():
    js_api = JSAPI()

    window = webview.create_window(
        'Concord',
        'ui/index.html',
        text_select=True,
        js_api=js_api
    )

    client = ConcordClient(window=window, fetch_offline_members=False)
    client.attach_api(js_api)

    js_api.attach_client(client)
    js_api.attach_window(window)

    discord_thread = Thread(target=discord_coroutine, args=(client,))
    discord_thread.daemon = True
    discord_thread.start()

    webview.start(debug=True)
    sys.exit()


if __name__ == "__main__":
    main()
