from dataclasses import dataclass


@dataclass
class Raid:
    gym_name: str = None
    level: int = None
    end: any = None
    hatching: any = None
    boss: str = None

    @property
    def is_hatched(self) -> bool:
        return self.hatching is None

    @property
    def is_egg(self) -> bool:
        return self.hatching is not None
