from .hub import Hub

class Connection:
    def __init__(self, start: Hub, end: Hub) -> None:
        self.start = start
        self.end = end
        self.active = True

    def deactivate(self):
        self.active = False

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.start.name} - {self.end.name}"