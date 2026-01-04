import math
from typing import Tuple, Union

from pygame import Vector2


TVectorParams = Union[Tuple[int, int] | Vector2]


def get_vector_direction(source: TVectorParams, target: TVectorParams):
    """source is an entity coming towards target
    lets say enemy is coming towards us from src to target then
    we perform targe-source, hopefully i assume thats valid
    """
    dx = target[0] - source[0]
    dy = target[1] - source[1]
    distance = math.hypot(dx, dy)

    if distance == 0:
        return (0.0, 0.0)

    return (round(dx / distance, 2), round(dy / distance, 2))


def circle_collision(source: TVectorParams, target: TVectorParams, *rr: float):
    assert len(rr) > 0
    dx = target[0] - source[0]
    dy = target[1] - source[1]
    distance = (dx**2) + (dy**2)
    return [distance <= r**2 for r in rr]
