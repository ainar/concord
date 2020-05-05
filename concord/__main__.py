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
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        self._api.add_message(message)

    def attach_api(self, api):
        self._api = api


class JSAPI:

    def __init__(self):
        self._client = None
        self._window = None

    def get_guilds(self):
        for guild in self._client.guilds:
            js = "addGuild({0}, {1});".format(
                json.dumps(str(guild.id)),
                json.dumps(guild.name)
            )
            self._window.evaluate_js(js)

    def add_message(self, message):
        js = "addMessage({0}, {1}, {2}, {3});".format(
            json.dumps(str(message.id)),
            json.dumps(message.author.name),
            json.dumps(message.content),
            message.created_at.timestamp()
        )
        self._window.evaluate_js(js)

    def get_channels(self, guild_id):
        for guild in self._client.guilds:
            if str(guild.id) == guild_id:
                for channel in guild.channels:
                    js = "addChannel({0}, {1});".format(
                        json.dumps(str(channel.id)),
                        json.dumps(channel.name)
                    )
                    self._window.evaluate_js(js)
                return
        raise Exception('no guild found with id ' + guild_id)
        print("no channel found")

    def get_messages(self, channel_id):
        channel = self._client.get_channel(int(channel_id))
        try:
            messages_future = asyncio.run_coroutine_threadsafe(
                self.get_messages_coro(channel), self._client.loop)
        except Exception as err:
            print('exception:', err)

    def attach_client(self, client):
        self._client = client

    def attach_window(self, window):
        self._window = window

    def log(self, message):
        print(message)

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
