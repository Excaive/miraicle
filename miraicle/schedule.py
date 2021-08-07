"""
使用方法：
    @miraicle.scheduled_job(miraicle.Scheduler.every().second)
    @miraicle.scheduled_job(miraicle.Scheduler.every(10).seconds)
    @miraicle.scheduled_job(miraicle.Scheduler.every(30).minutes)
    @miraicle.scheduled_job(miraicle.Scheduler.every().minute.at('::30'))
    @miraicle.scheduled_job(miraicle.Scheduler.every().hour.at(':12:34'))
    @miraicle.scheduled_job(miraicle.Scheduler.every().day.at('20'))
    @miraicle.scheduled_job(miraicle.Scheduler.every().sunday.at('11:45:14'))
"""

import datetime
import calendar
import warnings
from typing import List, Optional


class Scheduler:
    jobs: List['Job'] = []

    @staticmethod
    def every(interval: int = 1):
        job = Job(interval)
        return job

    def run(self, bot):
        for job in self.jobs:
            if job.time_up():
                if job.time_unexpired():
                    job.execute(bot)
                job.update_time()

    async def async_run(self, bot):
        for job in self.jobs:
            if job.time_up():
                if job.time_unexpired():
                    await job.async_execute(bot)
                job.update_time()


class Job:
    def __init__(self, interval: int):
        self.interval = interval
        self.unit = None
        self.start_day = None
        self.at_time: Optional[datetime.time] = None

        self.func = None
        self.last_run: Optional[datetime.datetime] = None
        self.next_run: Optional[datetime.datetime] = None

    def __repr__(self):
        return f'<Job:{self.func} | {self.interval} {self.unit} | last {self.last_run} | next {self.next_run}>'

    def time_up(self):
        return self.next_run < datetime.datetime.now()

    def time_unexpired(self):
        return datetime.datetime.now() < self.next_run + datetime.timedelta(minutes=1)

    def execute(self, bot):
        self.func(bot)

    async def async_execute(self, bot):
        await self.func(bot)

    @property
    def second(self):
        if self.interval != 1:
            warnings.warn('请使用 seconds 来替代 second')
        self.unit = 'seconds'
        return self

    @property
    def seconds(self):
        if self.interval == 1:
            warnings.warn('请使用 second 来替代 seconds')
        self.unit = 'seconds'
        return self

    @property
    def minute(self):
        if self.interval != 1:
            warnings.warn('请使用 minutes 来替代 minute')
        self.unit = 'minutes'
        return self

    @property
    def minutes(self):
        if self.interval == 1:
            warnings.warn('请使用 minute 来替代 minutes')
        self.unit = 'minutes'
        return self

    @property
    def hour(self):
        if self.interval != 1:
            warnings.warn('请使用 hours 来替代 hour')
        self.unit = 'hours'
        return self

    @property
    def hours(self):
        if self.interval == 1:
            warnings.warn('请使用 hour 来替代 hours')
        self.unit = 'hours'
        return self

    @property
    def day(self):
        if self.interval != 1:
            warnings.warn('请使用 days 来替代 day')
        self.unit = 'days'
        return self

    @property
    def days(self):
        if self.interval == 1:
            warnings.warn('请使用 day 来替代 days')
        self.unit = 'days'
        return self

    @property
    def week(self):
        if self.interval != 1:
            warnings.warn('请使用 weeks 来替代 week')
        self.unit = 'weeks'
        return self

    @property
    def weeks(self):
        if self.interval == 1:
            warnings.warn('请使用 week 来替代 weeks')
        self.unit = 'weeks'
        return self

    @property
    def monday(self):
        self.start_day = calendar.MONDAY
        return self.week if self.interval == 1 else self.weeks

    @property
    def tuesday(self):
        self.start_day = calendar.TUESDAY
        return self.week if self.interval == 1 else self.weeks

    @property
    def wednesday(self):
        self.start_day = calendar.WEDNESDAY
        return self.week if self.interval == 1 else self.weeks

    @property
    def thursday(self):
        self.start_day = calendar.THURSDAY
        return self.week if self.interval == 1 else self.weeks

    @property
    def friday(self):
        self.start_day = calendar.FRIDAY
        return self.week if self.interval == 1 else self.weeks

    @property
    def saturday(self):
        self.start_day = calendar.SATURDAY
        return self.week if self.interval == 1 else self.weeks

    @property
    def sunday(self):
        self.start_day = calendar.SUNDAY
        return self.week if self.interval == 1 else self.weeks

    def at(self, time_str: str):
        time_split = time_str.split(':')
        time_split_len = len(time_split)
        hour = minute = second = 0
        if time_split_len >= 1:
            hour = int(time_split[0]) if time_split[0] else 0
        if time_split_len >= 2:
            minute = int(time_split[1]) if time_split[1] else 0
        if time_split_len >= 3:
            second = int(time_split[2]) if time_split[2] else 0
        self.at_time = datetime.time(hour=hour, minute=minute, second=second)
        return self

    def initialize(self, func):
        self.func = func
        next_run = datetime.datetime.now().replace(microsecond=0)
        if not self.at_time:
            if self.unit == 'weeks':
                while next_run.weekday() != self.start_day:
                    next_run += datetime.timedelta(days=1)
        else:
            if self.unit == 'seconds':
                ...
            elif self.unit == 'minutes':
                next_run = next_run.replace(second=self.at_time.second)
            elif self.unit == 'hours':
                next_run = next_run.replace(minute=self.at_time.minute,
                                            second=self.at_time.second)
            elif self.unit == 'days':
                next_run = next_run.replace(hour=self.at_time.hour,
                                            minute=self.at_time.minute,
                                            second=self.at_time.second)
            elif self.unit == 'weeks':
                while next_run.weekday() != self.start_day:
                    next_run += datetime.timedelta(days=1)
                next_run = next_run.replace(hour=self.at_time.hour,
                                            minute=self.at_time.minute,
                                            second=self.at_time.second)
        while next_run < datetime.datetime.now():
            next_run = self.__calculate_next(next_run)
        self.next_run = next_run

    def update_time(self):
        self.last_run = self.next_run
        while self.next_run < datetime.datetime.now():
            self.next_run = self.__calculate_next(self.last_run)

    def __calculate_next(self, time):
        return time + datetime.timedelta(**{self.unit: self.interval})


def scheduled_job(job: Job):
    def wrapper(func):
        job.initialize(func)
        Scheduler.jobs.append(job)
        return func

    return wrapper
