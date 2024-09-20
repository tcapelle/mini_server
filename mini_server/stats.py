import time
from collections import deque, Counter
import asyncio
import logging

class Stats:
    def __init__(self, window_size, print_interval=20):
        self.window_size = window_size
        self.print_interval = print_interval
        self.request_times = deque(maxlen=window_size)
        self.user_requests = deque(maxlen=window_size)
        self.unique_users = Counter()

    def record_request(self, user_ip):
        current_time = time.time()
        self.request_times.append(current_time)
        self.user_requests.append((current_time, user_ip))
        self.unique_users[user_ip] += 1

    def calculate_request_stats(self):
        if not self.request_times:
            return 0, 0

        current_time = time.time()
        one_minute_ago = current_time - 60

        relevant_requests = [t for t in self.request_times if t > one_minute_ago]
        requests_last_minute = len(relevant_requests)

        rps = requests_last_minute / 60
        rpm = requests_last_minute

        return rps, rpm

    def calculate_unique_users(self, time_window=3600):
        current_time = time.time()
        cutoff_time = current_time - time_window
        recent_users = set(ip for t, ip in self.user_requests if t > cutoff_time)
        return len(recent_users)

    async def print_stats_periodically(self):
        while True:
            await asyncio.sleep(self.print_interval)
            rps, rpm = self.calculate_request_stats()
            unique_users_hour = self.calculate_unique_users(3600)  # Last hour
            unique_users_day = self.calculate_unique_users(86400)  # Last 24 hours

            logging.info("PERIODIC STATS:")
            logging.info(f"Current RPS: {rps:.2f}")
            logging.info(f"RPM: {rpm}")
            logging.info(f"Unique users (last hour): {unique_users_hour}")
            logging.info(f"Unique users (last 24 hours): {unique_users_day}")