from .abstract import AbstractCEnum


class CEnum(AbstractCEnum):
    @classmethod
    def sizeof(cls) -> int:
        "Type size (in bytes)"
        return cls.__size__
