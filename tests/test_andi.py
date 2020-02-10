# -*- coding: utf-8 -*-
import inspect
from typing import Union, Optional, TypeVar, Type

import attr
import pytest

import andi


class Foo:
    pass


class Bar:
    pass


class Baz:
    pass


def test_andi():
    possible = {Foo, Bar, Baz}

    def func1(x: Foo):
        pass

    def func2():
        pass

    def func3(x: Bar, y: Foo):
        pass

    assert andi.inspect(func1) == {'x': [Foo]}
    assert andi.inspect(func2) == {}
    assert andi.inspect(func3) == {'x': [Bar], 'y': [Foo]}

    assert andi.to_provide(func1, possible) == {'x': Foo}
    assert andi.to_provide(func2, possible) == {}
    assert andi.to_provide(func3, possible) == {'x': Bar, 'y': Foo}

    # incomplete data
    assert andi.to_provide(func1, {Baz}) == {}
    assert andi.to_provide(func2, {Baz}) == {}
    assert andi.to_provide(func2, set()) == {}
    assert andi.to_provide(func3, {Baz}) == {}


def test_union():
    def func(x: Union[Foo, Bar]):
        pass

    assert andi.inspect(func) == {'x': [Foo, Bar]}

    assert andi.to_provide(func, {Foo, Bar}) == {'x': Foo}
    assert andi.to_provide(func, {Bar}) == {'x': Bar}
    assert andi.to_provide(func, {Baz}) == {}
    assert andi.to_provide(func, set()) == {}


def test_optional():
    def func(x: Optional[Foo]):
        pass

    assert andi.inspect(func) == {'x': [Foo, None]}

    assert andi.to_provide(func, {Foo, Bar}) == {'x': Foo}
    assert andi.to_provide(func, {Foo, Bar, None}) == {'x': Foo}
    assert andi.to_provide(func, {Bar}) == {}
    assert andi.to_provide(func, {Bar, None}) == {'x': None}


def test_optional_union():
    def func(x: Optional[Union[Foo, Baz]]):
        pass

    assert andi.inspect(func) == {'x': [Foo, Baz, None]}

    assert andi.to_provide(func, {Foo, Bar}) == {'x': Foo}
    assert andi.to_provide(func, {Baz, Foo, None}) == {'x': Foo}
    assert andi.to_provide(func, {Baz}) == {'x': Baz}
    assert andi.to_provide(func, {Bar}) == {}
    assert andi.to_provide(func, {Bar, None}) == {'x': None}
    assert andi.to_provide(func, {}) == {}
    assert andi.to_provide(func, {None}) == {'x': None}


def test_not_annotated():
    def func(x):
        pass

    assert andi.inspect(func) == {}


def test_string_types():
    def func(x: 'Bar'):
        pass
    assert andi.inspect(func) == {'x': [Bar]}
    assert andi.to_provide(func, {Foo, Bar}) == {'x': Bar}


def test_init_methods():
    class MyClass:
        def __init__(self, x: Foo):
            self.x = x

    assert andi.inspect(MyClass.__init__) == {'x': [Foo]}
    assert andi.to_provide(MyClass.__init__, {Foo, Bar}) == {'x': Foo}


def test_classmethod():
    T = TypeVar('T')

    class MyClass:
        @classmethod
        def from_foo(cls: Type[T], foo: Foo) -> T:
            return cls()

    assert andi.inspect(MyClass.from_foo) == {'foo': [Foo]}
    assert andi.to_provide(MyClass.from_foo, {Foo, Bar}) == {'foo': Foo}


@pytest.mark.xfail
def test_attrs_string_type_references():
    """ ``get_type_hint`` function fails on attrs classes that reference
    a type using a string (see class A below for an example). The reason
    is that ``__init__.__globals__`` original content is lost by attrs.
    See https://github.com/python-attrs/attrs/issues/593
    """
    @attr.s(auto_attribs=True)
    class A:
        b: 'B'

    @attr.s(auto_attribs=True)
    class B:
        a: A

    assert andi.inspect(B.__init__) == {'a': [A]}
    assert andi.inspect(A.__init__) == {'b': [B]}
