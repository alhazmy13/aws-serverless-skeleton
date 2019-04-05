from src.app.post.model import PostModel
from src.common.decorator import api_response


class ListService(object):
    def __init__(self, offset=None, limit=None):
        self.offset = offset
        self.limit = limit

    @api_response()
    def execute(self):
        return self.find_all()

    def find_all(self):
        results = []
        count = 0
        for post in PostModel.scan():
            if self.limit is not None and int(self.limit) <= len(results):
                break
            if self.offset is None or int(self.offset) <= count:
                results.append(post)
            count += 1
        return results
