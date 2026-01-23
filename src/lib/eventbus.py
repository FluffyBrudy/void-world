from collections import defaultdict
from typing import Any, Callable, DefaultDict, Set


class __EventBus:
    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, Set[Callable[..., Any]]] = defaultdict(set)

    def subscribe(self, event: str, cb: Callable[..., Any]):
        self._subscribers[event].add(cb)

    def unsubscribe(self, event: str, cb: Callable[..., Any]):
        self._subscribers.pop(event)

    def emit(self, event: str, **payload):
        for cb in self._subscribers[event].copy():
            cb(**payload)
            print(payload)


event_bus = __EventBus()
