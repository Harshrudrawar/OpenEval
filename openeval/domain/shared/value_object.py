from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """
    Marker base class for immutable value objects.

    Equality is structural.
    """