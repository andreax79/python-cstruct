# Python-CStruct

Convert C struct/union definitions into Python classes with methods for
serializing/deserializing.

The usage is very simple: create a class subclassing cstruct.MemCStruct
and add a C struct/union definition as a string in the `__struct__` field.

The C struct/union definition is parsed at runtime and the struct format string
is generated. The class offers the method `unpack` for deserializing
an array of bytes into a Python object and the method `pack` for
serializing the values into an array of bytes.
