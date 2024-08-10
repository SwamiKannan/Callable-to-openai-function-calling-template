from inspect import Parameter, signature
from copy import deepcopy
import textwrap
#from pydantic.v1 import validate_arguments
import inspect
from typing import Optional, Callable, Any, Type, Dict, Sequence, Set
from pydantic import create_model, BaseModel, Field
from pydantic.alias_generators import to_pascal