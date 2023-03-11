from .colf_marshall import ColferMarshallerMixin
from .colf_unmarshall import ColferUnmarshallerMixin

from pydantic import BaseModel


class Colfer(BaseModel, ColferMarshallerMixin, ColferUnmarshallerMixin):
    pass
