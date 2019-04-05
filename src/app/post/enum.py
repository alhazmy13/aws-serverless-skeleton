from enum import Enum


class PostStatus(Enum):
    def __str__(self):
        return self.value

    @staticmethod
    def list():
        return list(map(lambda v: v.value, PostStatus))

    PUBLISHED = "PUBLISHED"
    DRAFT = "DRAFT"
