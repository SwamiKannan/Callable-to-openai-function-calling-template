from inspect import Parameter, signature
from copy import deepcopy
import textwrap
#from pydantic.v1 import validate_arguments
import inspect
from typing import Optional, Callable, Any, Type, Dict, Sequence, Set
from pydantic import create_model, BaseModel, Field
from pydantic.alias_generators import to_pascal

def validate_call_model(f: Callable[..., Any]) -> Type[BaseModel]:
		signature = inspect.signature(f)
		parameters = signature.parameters
		field_definitions: dict[str, Any] = {}
		for name, param in parameters.items():
			annotation, default = param.annotation, param.default
			if annotation is param.empty:
				annotation = Any
			if default is param.empty:
				default = Field(...)
			field_definitions[name] = (annotation, default)

		model = create_model(to_pascal(f.__name__), __module__=str(f.__module__), **field_definitions)
		return model