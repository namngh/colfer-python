# Python-Colfer

A strong typed version of *Colfer* serialization/deserialization for Python.

## Usage

First install with PyPi

```bash
pip install colf
```

Then use it to construct a Colfer Object and use it:

```python
from colf import Colfer
from colf.colf_type import UInt8
from typing import List, Optional


class User(Colfer):
    id: Optional[int]
    height: Optional[float]
    name: Optional[str]
    fiend_ids: Optional[List[int]]
    favorite: Optional[List[str]]


user = User(id=123, height=170.5, name="Jane Doe",
            fiend_ids=[100, 200, 300], favorite=["swimming", "singing"], age=32)

byte_output = bytearray(100)
length = user.marshall(byte_output)
print(byte_output[:length]) # bytearray(b'\x00{\x7f\x01@eP\x00\x00\x00\x00\x00\x7f\x02\x08Jane Doe\x7f\x03\x03\xc8\x01\x90\x03\xd8\x04\x7f\x04\x02\x08swimming\x07singing\x7f\x05 \x7f')

deserialize_user, _ = User().unmarshall(byte_output[:length])
print(deserialize_user) # id=123 height=170.5 name='Jane Doe' fiend_ids=[100, 200, 300] favorite=['swimming', 'singing'] age=32
```

## Running Unit Tests

```bash
pip install tox
tox
```

## Call for Testing Volunteers

The code was tested on Python 2.7, 3.6, 3.7, 3.8.
 
This code has been tested on Little-Endian machines only. It
requires to be tested on other architectures such as PowerPC, or those
with unique floating point formats.

Also, there may be chances this code may not work on some Python
version due to nuances not previously uncovered.

Please volunteer to test it on as many exotic computers, OSes
and send in your patches (or) bug reports.

## TODO

- [ ] Calculate length of byte_output when marshall
