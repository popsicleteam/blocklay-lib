import asyncio
import sys
import time

import machine

from .builtin import pin
from .event import Event
from .variable_db import VariableDb

__all__ = (
    "Event",
    "VariableDb",
    # core
    "call",
    "stop",
    "task",
    "start",
    "shutdown",
    # helpers
    "time_meter",
    "reset_time_meter",
    "create_timer",
    "loop_demon",
    # built-in blocks
    "pin",
)

FRAME_MS = 5

_task_groups = {}
_event_groups = {}
_timers = {}

_data = VariableDb()
_time_meter = 0

asyncio.new_event_loop()


def __getattr__(attr):
    if attr == "data":
        return _data

    raise AttributeError(attr)


def call(task_script, *args):
    if type(task_script) is str:
        event = _event_groups.setdefault(task_script, Event())
        event.set()
    else:
        event_loop = asyncio.get_event_loop()
        task_group_name = task_script.__globals__["__file__"]
        task_group = _task_groups.setdefault(task_group_name, [])
        task_group.append(event_loop.create_task(task_script(*args)))


def stop(task_group_name):
    task_group = _task_groups.setdefault(task_group_name, [])
    current_task = asyncio.current_task()
    for task in task_group:
        if task is not current_task:
            task.cancel()
    task_group.clear()
    task_group.append(current_task)


def event_task(event_name):
    def task_wrap(task_script):
        task_group_name = task_script.__globals__["__file__"]
        _task_groups.setdefault(task_group_name, [])

        event = _event_groups.setdefault(event_name, Event())

        async def script():
            while True:
                await event.wait()
                call(task_script)
                await asyncio.sleep_ms(FRAME_MS)
                event.clear()

        call(script)

    return task_wrap


def flag_task(flag, once=True):
    def task_wrap(task_script):
        task_group_name = task_script.__globals__["__file__"]
        _task_groups.setdefault(task_group_name, [])

        async def script():
            is_called = False
            while True:
                if await flag():
                    if not is_called:
                        call(task_script)
                        is_called = once
                else:
                    is_called = False
                await asyncio.sleep_ms(FRAME_MS)

        call(script)

    return task_wrap


def task(event_flag=None, **kwargs):
    if type(event_flag) is str:
        return event_task(event_flag)

    if callable(event_flag):
        return flag_task(event_flag, **kwargs)

    return call


def reset():
    event_loop = asyncio.get_event_loop()
    event_loop.stop()
    event_loop.close()

    for mod_name in sys.modules.keys():
        mod = sys.modules[mod_name]
        if "__file__" in mod.__dict__ and mod.__file__ in _task_groups:
            del sys.modules[mod_name]
    _task_groups.clear()
    print(".", end="")

    _event_groups.clear()
    print(".", end="")

    for timer in _timers.values():
        timer.deinit()
        print(".", end="")
    _timers.clear()
    print(".", end="")

    _data.clear()
    print(".", end="")


def start(task_script=None):
    event_loop = asyncio.get_event_loop()
    _time_meter = time.ticks_ms()
    try:
        if task_script is not None and type(task_script) != str:
            call(task_script)
        event_loop.run_forever()
    except KeyboardInterrupt:
        print("Shutdown.", end="")
    finally:
        reset()
        if type(task_script) == str and task_script in sys.modules:
            del sys.modules[task_script]
        print(".Bye!")


def shutdown():
    raise KeyboardInterrupt


def time_meter():
    return time.ticks_diff(time.ticks_ms(), _time_meter)


def reset_time_meter():
    global _time_meter
    _time_meter = time.ticks_ms()


def create_timer():
    try:
        timer = machine.Timer()
    except:
        id = len(_timers)
        timer = machine.Timer(id)
    _timers[timer] = timer
    return timer


async def loop_demon():
    await asyncio.sleep(0)
