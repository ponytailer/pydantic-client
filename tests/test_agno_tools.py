import inspect
from typing import List, Dict

from pydantic import BaseModel
from pydantic_client.tools import agno


def test_get_parameter_type_basic_types():
    import inspect

    def func(a: str, b: int, c: float, d: bool, e: list, f: dict):
        pass

    sig = inspect.signature(func)
    results = {name: agno._get_parameter_type(param) for name, param in sig.parameters.items()}
    assert results['a'] == 'string'
    assert results['b'] == 'integer'
    assert results['c'] == 'number'
    assert results['d'] == 'boolean'
    assert results['e'] == 'array'
    assert results['f'] == 'object'


def test_get_parameter_type_pydantic_model():
    import inspect

    class Foo(BaseModel):
        x: int

    def func(a: Foo):
        pass

    sig = inspect.signature(func)
    result = agno._get_parameter_type(sig.parameters['a'])
    assert result == 'object'


def test_create_agno_tool_parameters_and_types():
    class Bar(BaseModel):
        value: int

    def test_func(x: str, y: int, z: Bar):
        """Test func
        :param x: some string
        :param y: some int
        :param z: bar object
        """
        pass

    tool_def = agno.create_agno_tool(test_func)
    assert tool_def['name'] == "test_func"
    assert tool_def['description'].startswith("Test func")
    params = tool_def['parameters']
    assert params['x']['type'] == "string"
    assert params['y']['type'] == "integer"
    assert params['z']['type'] == "object"
    assert "properties" in params['z']
    assert params['z']['properties']['value']['type'] == 'integer'
    assert params['x']['description'] == "some string"
    assert params['z']['description'] == "bar object"


def test_register_agno_tool_decorator_sets_attribute():
    def foo(x: int):
        """My foo
        :param x: some int
        """
        pass

    decorated = agno.register_agno_tool("desc...")(foo)
    assert hasattr(decorated, "_agno_tool")
    tool = decorated._agno_tool
    assert tool['description'].startswith("desc")
    assert tool['parameters']['x']['type'] == "integer"


def test_register_agno_tool_decorator_call():
    called = {}

    @agno.register_agno_tool("desc")
    def bar(x: int):
        called['ok'] = x
        return x + 1

    result = bar(3)
    assert called['ok'] == 3
    assert result == 4


def test_get_parameter_type_list_and_dict():
    def func(a: List[str], b: Dict[str, int]):
        pass
    sig = inspect.signature(func)
    assert agno._get_parameter_type(sig.parameters['a']) == 'array'
    assert agno._get_parameter_type(sig.parameters['b']) == 'object'


def test_get_parameter_type_non_type_annotation():
    param = inspect.Parameter('x', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=None)
    assert agno._get_parameter_type(param) == 'string'


def test_create_agno_tool_skips_self():
    class Foo:
        def method(self, x: int):
            """Test method
            :param x: some int
            """
            pass
    tool_def = agno.create_agno_tool(Foo.method)
    assert 'self' not in tool_def['parameters']
    assert 'x' in tool_def['parameters']
