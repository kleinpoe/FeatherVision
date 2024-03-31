from datetime import timedelta

from tinydb_serialization import Serializer


class TimeDeltaSerializer(Serializer):
    OBJ_CLASS = timedelta  # The class this serializer handles

    def encode(self, obj:timedelta):
        return str(obj.total_seconds())

    def decode(self, s):
        return timedelta(seconds=float(s))