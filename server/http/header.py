from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Header:
    name: bytes
    value: bytes
