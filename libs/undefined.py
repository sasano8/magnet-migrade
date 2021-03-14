"""
>>> pprint.pprint(inspect.getmembers(None))
[('__bool__', <method-wrapper '__bool__' of NoneType object at 0x8ee2c0>),
 ('__class__', <class 'NoneType'>),
 ('__delattr__', <method-wrapper '__delattr__' of NoneType object at 0x8ee2c0>),
 ('__dir__', <built-in method __dir__ of NoneType object at 0x8ee2c0>),
 ('__doc__', None),
 ('__eq__', <method-wrapper '__eq__' of NoneType object at 0x8ee2c0>),
 ('__format__', <built-in method __format__ of NoneType object at 0x8ee2c0>),
 ('__ge__', <method-wrapper '__ge__' of NoneType object at 0x8ee2c0>),
 ('__getattribute__',
  <method-wrapper '__getattribute__' of NoneType object at 0x8ee2c0>),
 ('__gt__', <method-wrapper '__gt__' of NoneType object at 0x8ee2c0>),
 ('__hash__', <method-wrapper '__hash__' of NoneType object at 0x8ee2c0>),
 ('__init__', <method-wrapper '__init__' of NoneType object at 0x8ee2c0>),
 ('__init_subclass__',
  <built-in method __init_subclass__ of type object at 0x8ee2e0>),
 ('__le__', <method-wrapper '__le__' of NoneType object at 0x8ee2c0>),
 ('__lt__', <method-wrapper '__lt__' of NoneType object at 0x8ee2c0>),
 ('__ne__', <method-wrapper '__ne__' of NoneType object at 0x8ee2c0>),
 ('__new__', <built-in method __new__ of type object at 0x8ee2e0>),
 ('__reduce__', <built-in method __reduce__ of NoneType object at 0x8ee2c0>),
 ('__reduce_ex__',
  <built-in method __reduce_ex__ of NoneType object at 0x8ee2c0>),
 ('__repr__', <method-wrapper '__repr__' of NoneType object at 0x8ee2c0>),
 ('__setattr__', <method-wrapper '__setattr__' of NoneType object at 0x8ee2c0>),
 ('__sizeof__', <built-in method __sizeof__ of NoneType object at 0x8ee2c0>),
 ('__str__', <method-wrapper '__str__' of NoneType object at 0x8ee2c0>),
 ('__subclasshook__',
  <built-in method __subclasshook__ of type object at 0x8ee2e0>)]
"""


class Undefined:
    @property
    def __bool__(self):
        return False

    # @property
    # def __class__(self):
    #     return None.__class__

    def __delattr__(self, item):
        return None.__delattr__(item)

    __dir__ = None.__dir__
    __doc__ = None.__doc__
    __eq__ = None.__eq__
    __format__ = None.__format__
    __ge__ = None.__ge__
    __hash__ = None.__hash__
    __init__ = None.__init__
    __init_subclass__ = None.__init_subclass__
    __le__ = None.__le__
    __lt__ = None.__lt__
    __ne__ = None.__ne__
    __new__ = None.__new__
    __reduce__ = None.__reduce__
    __reduce_ex__ = None.__reduce_ex__
    __setattr__ = None.__setattr__
    __sizeof__ = None.__sizeof__
    __str__ = None.__str__
    __subclasshook__ = None.__subclasshook__
