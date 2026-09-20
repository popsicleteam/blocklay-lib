import asyncio
import time

import machine

from .event import Event
from .lib import pin

__all__ = (
    "Event",
    # core
    "call",
    "stop",
    "task",
    "start",
    "shutdown",
    # helpers
    "create_timer",
    "time_meter",
    "reset_time_meter",
    "loop_demon",
    # built-in libraries
    "pin",
)

FRAME_MS = 5

_task_groups = None
_event_groups = None
_variables = None
_timers = None

_time_meter = 0


asyncio.new_event_loop()


def __getattr__(attr):
    return _variables.get(attr, 0) if _variables is not None else 0


def __setattr__(attr, value):
    global _variables
    if _variables is None:
        _variables = {}
    if value is None:
        _variables.pop(attr, None)
    else:
        _variables[attr] = value


def call(task_script, *args):
    if type(task_script) is str:
        global _event_groups
        if _event_groups is None:
            _event_groups = {}

        event = _event_groups.setdefault(task_script, Event())
        event.set()
    else:
        global _task_groups
        if _task_groups is None:
            _task_groups = {}

        event_loop = asyncio.get_event_loop()
        task_group_name = task_script.__globals__["__file__"]
        task_group = _task_groups.setdefault(task_group_name, [])
        task_group.append(event_loop.create_task(task_script(*args)))


def stop(task_group_name):
    if _task_groups is not None:
        task_group = _task_groups.setdefault(task_group_name, [])
        current_task = asyncio.current_task()
        for task in task_group:
            if task is not current_task:
                task.cancel()
        task_group.clear()
        task_group.append(current_task)


def event_task(event_name):
    global _event_groups
    if _event_groups is None:
        _event_groups = {}

    def task_wrap(task_script):
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

    global _task_groups, _event_groups, _variables, _timers
    if _task_groups is not None:
        _task_groups.clear()
        _task_groups = None
        print(".", end="")

    if _event_groups is not None:
        _event_groups.clear()
        _event_groups = None
        print(".", end="")

    if _variables is not None:
        _variables.clear()
        _variables = None
        print(".", end="")

    if _timers is not None:
        for timer in _timers.values():
            timer.deinit()
            print(".", end="")
        _timers.clear()
        _timers = None
        print(".", end="")


def start(task_script=None):
    event_loop = asyncio.get_event_loop()
    _time_meter = time.ticks_ms()
    try:
        if task_script is not None:
            call(task_script)
        event_loop.run_forever()
    except KeyboardInterrupt:
        print("Shutdown.", end="")
    finally:
        reset()
        print(".Bye!")


def shutdown():
    raise KeyboardInterrupt


def create_timer():
    global _timers
    if _timers is None:
        _timers = {}
    try:
        timer = machine.Timer()
    except:
        id = len(_timers)
        timer = machine.Timer(id)
    _timers[timer] = timer
    return timer


def time_meter():
    return time.ticks_diff(time.ticks_ms(), _time_meter)


def reset_time_meter():
    global _time_meter
    _time_meter = time.ticks_ms()


async def loop_demon():
    await asyncio.sleep(0)
