from inspect import Parameter, signature
from copy import deepcopy
import textwrap
#from pydantic.v1 import validate_arguments
import inspect
from typing import Optional, Callable, Any, Type, Dict, Sequence, Set
from pydantic import create_model, BaseModel, Field
from pydantic.alias_generators import to_pascal
import ast

def validate_call_model(f: Callable[..., Any], debug:bool=False) -> Type[BaseModel]:
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
		if debug:
			print('Type of validated model:\t', type(model))
			print('Fields of validated model',model.model_fields)
			print('Keys of fields of validated models',model.model_fields.keys())
			print('\n')
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

def dereference_refs_helper(obj, full_schema, skip_keys, processed_refs=None, debug=False):
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
					ref = retrieve_ref(v, full_schema, debug)
					full_ref = dereference_refs_helper(
						ref, full_schema, skip_keys, processed_refs, debug = debug
					)
					processed_refs.remove(v)
					return full_ref
				elif isinstance(v, (list, dict)):
					obj_out[k] = dereference_refs_helper(
						v, full_schema, skip_keys, processed_refs, debug = debug
					)
				else:
					obj_out[k] = v
			return obj_out
		elif isinstance(obj, list):
			return [
				dereference_refs_helper(el, full_schema, skip_keys, processed_refs, debug = debug)
				for el in obj
			]
		else:
			return obj
		
def retrieve_ref(path, schema, debug=False): #_retrieve_ref in langchain
		if debug:
			print('Original path in retrieve_ref:\t', path)
		components = path.split("/")  # path = '#/$defs/Bar' ; schema = {'$ref': '#/$defs/Bar'} in example
		if components[0] != "#":
			raise ValueError(
			"ref paths are expected to be URI fragments, meaning they should start with #."
		)
		out = schema
		if debug:
			print('Original schema in retrieve_ref:\t',out)
		for component in components[1:]: # [$defs,Bar]
			if debug:
				print('Component in retrieve_ref:\t', component)
			if component in out:
				out = out[component]
			elif component.isdigit() and int(component) in out:
				out = out[int(component)]
			else:
				raise KeyError(f"Reference '{path}' not found.")
		return deepcopy(out)

def remove_refs(json_schema, full_schema = None, processed_refs=None, debug=False): #_infer_skip_keys - For this example, it will return ['$defs']
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
					ref = retrieve_ref(v, full_schema, debug) # json_schema = {'$ref': '#/$defs/Bar'} in above example ,  v = '#/$defs/Bar'
					keys.append(v.split("/")[1])
					keys += remove_refs(ref, full_schema, processed_refs)
					print('Full ref in remove_refs if key == $ref:\t', keys)
				elif isinstance(v, (list, dict)):
					keys += remove_refs(v, full_schema, processed_refs)
					if debug:
						print('Full ref in remove_refs if key != $ref but dict:\t', keys)
		elif isinstance(json_schema, list):
			for el in json_schema:
				keys += remove_refs(el, full_schema, processed_refs)
			if debug:
				print('Keys if the schema is only a list:\t', keys)
		return keys


def remove_extraneous_keys(json_schema, debug=False):
	keys = remove_refs(json_schema)
	updated_json_schema1 = dereference_refs_helper(json_schema, None, keys,debug = debug)
	updated_json_schema1.pop('definitions', None) #remove the definitions key if it exists
	title = updated_json_schema1.pop('title', "") #extract title key
	default_description = updated_json_schema1.pop('description','') #extract function description
	return updated_json_schema1, title, default_description

def get_arguments_and_descriptions(fn:Callable, debug=False): #t BE FORMATTED
	docstring = inspect.getdoc(fn)
	name = fn.__name__
	print('Inspect.getdoc:\t',docstring) #gets the entire docstring of the function
	blocks = docstring.split("\n\n")
	print('Docstring Blocks:\t', blocks)
	descriptors = []
	args_block = None
	past_descriptors = False
	for block in blocks:
		if block.strip().startswith("Args:"):
			args_block = block
			break
		elif block.strip().startswith("Returns:") or block.startswith("Example:"):         # Don't break in case Args come after 
			past_descriptors = True
		elif not past_descriptors:
			descriptors.append(block)
		else:
			continue
	if debug:
		print('Descriptors:\t',descriptors)
		print('String descriptors:\t',' '.join(descriptors))
	arg_descriptions = {}
	if debug:
		print('args block:\t',args_block)
	if args_block:
		arg = None
		for line in args_block.split("\n")[1:]:
			if ":" in line:
				arg, desc = line.split(":", maxsplit=1)
				if debug:
					print('Description before stripping arg types',arg)
				arg = arg.split('(')[0]
				arg_descriptions[arg.strip()] = desc.strip()
				if debug:
					print('Description after stripping arg types',arg)
			elif arg:
				if debug:
					print('No desc')
				arg_descriptions[arg.strip()] += " " + line.strip()
	if debug:
		print('Arg descriptions:\t',arg_descriptions)
		print('\n')
	return (name, ' '.join(descriptors), arg_descriptions)
	
def update_pydantic_model_schema(pydantic_model:BaseModel, fn:Callable, name:str, descriptors:str, arg_descriptions:dict, debug:bool=False):
	if debug:
		print('**** Extracting details of the validated model ****') #Basically model created from the pydantic version of the function directly
		print('Validated model schema:\t', pydantic_model.model_json_schema())
	schema = pydantic_model.model_json_schema()["properties"]
	if debug:
		print('Properties of validated model:\t', schema)
		print('**** getting the details from the signature() fn of inspect')
	sig_params = signature(fn).parameters  # Basically from the inspect.signature part
	if debug:
		print('Validated model keys:\t',sig_params)
		print('****Creating a dict that has { key=sig_params.items.keys() i.e. inspect.signature and value = schema[key] where schema is what we get from the validated models schama properties entity}')
	field_names={}
	for k,v in sig_params.items():
		if debug:
			print(f'Key:\t',k,'\tValue:\t',v)
			print('V name:\t',v.name)
			print({k:schema[k]})  # {k = 'query' value = schema['query'] i.e. {'title': 'Query', 'type': 'string'}}
			print('\n')
		field_names.update({k:schema[k]})
	if debug:
		print('Field names', field_names)
		print('\n')
		print('*** Updating the pydantic model Field object with the detauls from the field names')
		print('Fields of validated model:\t', pydantic_model.model_fields)
	fields = {}
	for fieldname in field_names:
		if debug:
			print('Field name:\t', fieldname) #'query'
		model_field = pydantic_model.model_fields[fieldname]
		if debug:
			print('All model fields:\t', pydantic_model.model_fields)
			print('Model field:\t',model_field)
			print('Type of model field:\t',type(model_field))
			print('is field required:\t', model_field.is_required)
			print('Outer type????:\t', model_field.annotation)
			print('Detailed annotations',model_field.__annotations__)
		if model_field.is_required and not 'None' in str(model_field.annotation): #get the field type only if it is mandatory else set it as Optional[dtype]
			t = model_field.annotation
		else:
			t = Optional[model_field.annotation]
		if debug:
			print('t:\t',t)
			print('Arg descriptions:\t',arg_descriptions)
			print('field name:\t',fieldname) #{'query': (<class 'str'>, FieldInfo(default=Ellipsis, description='The search query.', extra={}))}
		if arg_descriptions and fieldname in arg_descriptions:
			if debug:
				print('Field. field_info',model_field.from_field(fieldname))
				print('Field. field_info description',model_field.description)
			model_field.description=arg_descriptions[fieldname]
			if debug:
				print('Field. field_info post updation',model_field.description)
		else:
			print('Not present')
		fields[fieldname] = (t, model_field)
	print('Final fields:\t', fields) # {'query': (<class 'str'>, FieldInfo(default=Ellipsis, description='The search query.', extra={}))}
	if debug:
		for field_name_key in fields:
			print('Type of final fields:\t', type(fields[field_name_key][1]))
	try:
		final_model = create_model(name, **fields)
	except Exception as e:
		print('Final model could not be created:Exception\t',e)
	if debug:
		print('Initial final model type:\t', type(final_model))
		print('Initial final model doc:\t', dict[final_model])
		print('Descriptors to go into the model:\t', descriptors)
	final_model.__doc__ = ''.join(descriptors).strip()	
	if debug:
		print('Func desc as per validated model\t:', final_model.__doc__)
		print('Does the final model have the attribute model_json_schema:\t',hasattr(final_model, "model_json_schema"))
	schema = final_model.model_json_schema()
	if debug:
		print('Final schema:\t', schema)
	return schema, final_model

def get_json_schema(pri:Callable, debug = False, get_tool_format= True, get_langchain_format=True):
	args = inspect.getfullargspec(pri).args
	if debug:
		print('Inspect function:\t', inspect.getfullargspec(pri).args)
	if len(args)>0:
		print('len args > 0')
		validated_model = validate_call_model(pri, debug)
		anno = inspect.get_annotations(pri)
		if debug:
			print('Annotations:\t', anno) # returns{'query': <class 'str'>, 'return': <class 'dict'>}
			print('Annotation type:\t', type(anno))
			print('\n')
		name, descriptors, argument_descriptions = get_arguments_and_descriptions(pri, debug=debug)
		print('Descriptors before updating pydantic_model_scheme:\n', descriptors)
		interim_schema , interim_model = update_pydantic_model_schema(validated_model, pri, name, descriptors, argument_descriptions, debug)
		print('Before removing extraneous keys:\t',descriptors)
		if debug:
			print('***** Removing any $refs from the json schema (Refer function defintion for details)')
		updated_schema, title, description = remove_extraneous_keys(interim_schema)
		print('After removing extaneous keys:\t', description)
		removed_title = remove_titles(updated_schema)
		removed_title.pop('description',None)
		print('Interim model.doc', interim_model.__doc__)
		final_dict = {"name": name or title,
				"description": interim_model.__doc__ or description,
				"parameters":removed_title if interim_schema else updated_schema}
		print('\n\nFinal dict with arguments\n', final_dict)
	else:
		print('len args <= 0')
		dict_text = get_docstring(pri)
		print(dict_text.items())
		(name, doctext) = list(dict_text.items())[0]
		print('Doctext:\n', doctext)
		final_dict = {
			"name":name,
			"description":doctext,
			"parameters":
			{
				"type":"object",
				"properties":{}
			}
		}
	if not get_tool_format:
		return final_dict
	else:
		final_dict = convert_json_to_tool_format(final_dict)
		if not get_langchain_format:
			return final_dict
		else:
			docx = pri.__doc__
			while '\t\t' in docx:
				docx = docx.replace('\t\t','')
			docx = docx.replace('\n\n\t','\n\n')
			final_dict['function']['description'] = docx
			properties = final_dict['function']['parameters']['properties']
			for k in properties.keys():
				properties[k].pop('description',None)
			final_dict['function']['parameters']['properties'] = properties
			return final_dict
            
def get_docstring(f:Callable) ->list: #Extracts the docstring of a given openai formatted function object
	name = f.__name__
	doctext = f.__doc__
	ind1 = doctext.find('->')+len('->')
	start_ind = ind1+doctext[ind1:].find(' - ')+len(' - ')
	end_ind = doctext.find('Args')
	final_docstring = doctext[start_ind:end_ind].strip().replace('\n','')
	print('\n\n\nFinal docstring:\n', final_docstring,'\n\n\n')
	return {name:final_docstring}
    
def convert_json_to_tool_format(func_dict:dict):
	dict_json = {}
	dict_json['type'] = 'function'
	# dict_main is a sub dict which has the name, description and initiating parameters
	dict_main = {'name':func_dict['name'],'description':func_dict['description'], 'parameters':{}}
	properties = func_dict['parameters']['properties']
	reqd_flag = func_dict['parameters']['required'] if 'required' in func_dict['parameters'] else None
	params = {'type':'object', 'properties':properties}
    if reqd_flag:
            params.update({'required':reqd_flag})
        dict_main['parameters'] = params
        dict_json['function'] = dict_main
        print('func dict keys:\t',func_dict.keys())
        dict_json = json.loads(str(dict_test).replace("\'",'"'))

	return dict_json

#testing
if __name__=="__main__":
	pass
