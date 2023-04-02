from pyrogram import Client
from apscheduler.job import Job

from avitobot.custom_types import UserId
from avitobot.services import track_request
from avitobot import (
    settings,
    scheduler,
    user_ping,
    user_interval,
    ping_jobs,
    user_track_request,
    track_request_jobs
)


def start_ping_job(client: Client, user_id: UserId) -> Job:
    return scheduler.add_job(send_ping, "interval", hours=4, args=(client, user_id))


def start_pings(client: Client) -> None:
    for user_id in user_ping:
        ping_jobs[user_id] = start_ping_job(client, user_id)


def start_track_request_job(client: Client, user_id: UserId):
    minutes = user_interval.get(user_id)
    if not minutes:
        minutes = settings.DEFAULT_INTERVAL
    return scheduler.add_job(track_request, "interval", minutes=minutes, args=(
                                                            client, user_id))


def start_track_requests(client: Client):
    for user_id in user_track_request:
        track_request_jobs[user_id] = start_track_request_job(client, user_id)


async def send_ping(client: Client, user_id: UserId) -> None:
    await client.send_message(user_id, "Бот жив.")
