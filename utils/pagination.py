from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 30

    def get_paginated_response(self, data):
        response_data = {
            "has_previous": self.offset > 0,
            "has_next": self.offset + self.limit < self.count,
            "count": self.count,
            "offset": self.offset,
            "results": data,
        }

        return Response(response_data)
