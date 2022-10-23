import json
import dataclasses
from enum import Enum


class DataclassEnumJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            d = dataclasses.asdict(o)
            for k, v in d.items():
                if isinstance(v, Enum):
                    d[k] = v.value
            return d
        return super().default(o)
