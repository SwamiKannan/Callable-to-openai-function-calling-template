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

def remove_titles(kv: dict, prev_key: str = "", ) -> dict: #_infer_skip_keys from langchain
		new_kv = {}
		for k, v in kv.items():
			if k == "title":
				if isinstance(v, dict) and prev_key == "properties" and "title" in v.keys():
					new_kv[k] = remove_titles(v, k)
				else:
					continue
			elif isinstance(v, dict):
				new_kv[k] = remove_titles(v, k)
			else:
				new_kv[k] = v
		return new_kv

def dereference_refs_helper(obj, full_schema, skip_keys, processed_refs=None):
		'''
		Will remove from the obj schema the entire key, value pair where the key==skip_key
		'''
		full_schema = obj if not full_schema else full_schema
		if processed_refs is None:
			processed_refs = set()

		if isinstance(obj, dict):
			obj_out = {}
			for k, v in obj.items():
				if k in skip_keys:
					obj_out[k] = v
				elif k == "$ref":
					if v in processed_refs:
						continue
					processed_refs.add(v)
					ref = retrieve_ref(v, full_schema)
					full_ref = dereference_refs_helper(
						ref, full_schema, skip_keys, processed_refs
					)
					processed_refs.remove(v)
					return full_ref
				elif isinstance(v, (list, dict)):
					obj_out[k] = dereference_refs_helper(
						v, full_schema, skip_keys, processed_refs
					)
				else:
					obj_out[k] = v
			return obj_out
		elif isinstance(obj, list):
			return [
				dereference_refs_helper(el, full_schema, skip_keys, processed_refs)
				for el in obj
			]
		else:
			return obj
		
def retrieve_ref(path, schema): #_retrieve_ref in langchain
		print('Original path in retrieve_ref:\t', path)
		components = path.split("/")  # path = '#/$defs/Bar' ; schema = {'$ref': '#/$defs/Bar'} in example
		if components[0] != "#":
			raise ValueError(
			"ref paths are expected to be URI fragments, meaning they should start with #."
		)
		out = schema
		print('Original schema in retrieve_ref:\t',out)
		for component in components[1:]: # [$defs,Bar]
			print('Component in retrieve_ref:\t', component)
			if component in out:
				out = out[component]
			elif component.isdigit() and int(component) in out:
				out = out[int(component)]
			else:
				raise KeyError(f"Reference '{path}' not found.")
		return deepcopy(out)
        
def remove_refs(json_schema, full_schema = None, processed_refs=None): #_infer_skip_keys - For this example, it will return ['$defs']
		'''
		refs format is used when one class's object is used as another's variable. A typical json format using this would be:
		{
			'$defs': {'Bar': {'properties': {}, 'title': 'Bar', 'type': 'object'}},
			'properties': {'x': {'$ref': '#/$defs/Bar'}},
			'required': ['x'],
			'title': 'Foo',
			'type': 'object',
		}
		where a Bar object is an instancevariable of class Foo
		'''
		full_schema = full_schema if full_schema else json_schema
		if processed_refs is None:
			processed_refs = set()
		keys = []
		if isinstance(json_schema, dict):
			for k, v in json_schema.items(): 
				if k == "$ref":
					if v in processed_refs:
						continue
					processed_refs.add(v)
					ref = retrieve_ref(v, full_schema) # json_schema = {'$ref': '#/$defs/Bar'} in above example ,  v = '#/$defs/Bar'
					keys.append(v.split("/")[1])
					keys += remove_refs(ref, full_schema, processed_refs)
					print('Full ref in remove_refs if key == $ref:\t', keys)
				elif isinstance(v, (list, dict)):
					keys += remove_refs(v, full_schema, processed_refs)
					print('Full ref in remove_refs if key != $ref but dict:\t', keys)
		elif isinstance(json_schema, list):
			for el in json_schema:
				keys += remove_refs(el, full_schema, processed_refs)
			print('Keys if the schema is only a list:\t', keys)