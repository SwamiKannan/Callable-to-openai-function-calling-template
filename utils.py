from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core._api.deprecation import LangChainDeprecationWarning
import ast
import os
import functions
#import functions_minr
import json
from typing import List
#from system_prompt import primary_prompt, example_prompt, prompt_instructions, prompt_schema
# from system_prompt_mine import prompt2_start, prompt2_end
from schema import SystemPromptTemplate, AgentSignature, FunctionSignature
import datetime
import shutil
import warnings

# see if we can get fields and schema directly from validate_fields() in pydantic v2

def fxn():
	warnings.warn("deprecated", LangChainDeprecationWarning)
with warnings.catch_warnings(action="ignore"):
	fxn()

warnings.filterwarnings("ignore")


def find_tools(functions_path = 'src//functions.py'):
	methods = []
	f = open(functions_path, 'r')
	text = f.read()
	p = ast.parse(text)
	for node in ast.walk(p):
		if isinstance(node, ast.FunctionDef):
			methods.append(node.name)
	return methods

def get_docstring(f:str) ->list: #Extracts the docstring of a given openai formatted function item
	name = f['function']['name']
	doctext = f['function']['description']
	ind1 = doctext.find('->')+len('->')
	start_ind = ind1+doctext[ind1:].find(' - ')+len(' - ')
	end_ind = doctext.find('Args')
	final_docstring = doctext[start_ind:end_ind].strip().replace('\n','').strip()
	return {name:final_docstring}

def get_functions(functions_path = 'src_ollama//functions.py') -> list:
	return	[{f:getattr(functions,f)} for f in find_tools(functions_path)]
	
def get_openai_tools(functions_path = 'src//functions.py', func_tools = None) -> List[dict]:
	tools=[convert_to_openai_function(t) for t in func_tools] if func_tools else [convert_to_openai_function(list(t.values())[0]) for t in get_functions(functions_path)]
	return tools

def get_system_prompt(tools,examples=False, use_template = False, template:dict = None,functions_path = 'src//functions.py', prompt_template:str = 'function'):
	if use_template and not template:
		raise Exception('if use_template is True, then a template should be provided. But no template provided')
	if prompt_template == 'function':
		from src_ollama.system_prompt_split import objective_prompt, example_prompt, prompt_instructions, prompt_schema, primary_prompt
		output_schema = FunctionSignature.model_json_schema()
	elif prompt_template == 'agent':
		from system_prompt_agent import objective_prompt, example_prompt, prompt_instructions,prompt_schema, primary_prompt
		output_schema = AgentSignature.model_json_schema() 
	schema = SystemPromptTemplate.model_json_schema()
	tools = tools# get_openai_tools(functions_path)
	date = datetime.date.today()
	primary_prompt = primary_prompt
	prompt_template=objective_prompt.format(date = date, tools = tools, schema=schema).replace('\n',' ')
	prompt_template = f"{prompt_template}"
	assert isinstance(prompt_template,str)
	# example_template = None if not examples else example_prompt.format(examples = example_prompt).replace('\n',' ')
	# example_template = None if not examples else f"{example_template}"
	schema_template = prompt_schema.format(schema = output_schema).replace('\n',' ')
	schema_template = f"{schema_template}"
	assert isinstance(schema_template,str)
	instruction_template = f"{prompt_instructions}"
	assert isinstance(instruction_template,str)
	#final_prompt=prompt_template+' '+example_template+' '+schema_template+' '+instruction_template if examples else prompt_template+' '+schema_template+' '+instruction_template
	final_prompt=primary_prompt+ prompt_template+' '+schema_template+instruction_template
	return final_prompt
	# else:
	#		 primary_prompt_template=template['primary_prompt']
	#		 primary_prompt_template = f"{primary_prompt_template}"
	#		 assert isinstance(primary_prompt_template,str)
	#		 prompt_template=template['objective'].format(date = date, tools = tools, schema=template['schema']).replace('\n',' ')
	#		 prompt_template = f"{prompt_template}"
	#		 assert isinstance(prompt_template,str)
	#		 example_template = None if not examples else template['example'].format(examples = example_prompt).replace('\n',' ')
	#		 example_template = None if not examples else f"{example_template}"
	#		 instruction_template = f"{template['instructions']}"
	#		 assert isinstance(instruction_template,str)
	#		 final_prompt=primary_prompt_template+' '+prompt_template+' '+example_template+' '+instruction_template if examples else primary_prompt_template+' '+prompt_template+' '+instruction_template
	#		 return final_prompt
		

# def get_system_prompt2(examples=False):
#		 tools=get_openai_tools()
#		 return prompt2_start+str(tools)+prompt2_end


# def get_system_prompt2():
#		 return prompt2_start+f"<tools> {get_openai_tools()} </tools>"+prompt2_end


def copy_and_rename(src_path, dest_path, new_name='functions.py'):
	# Copy the file
	shutil.copy(src_path, dest_path)
 
	# Rename the copied file
	new_path = f"{dest_path}/{new_name}"
	filename = src_path.split('\\')[-1]
	shutil.move(f"{dest_path}/{filename}", new_path)

def write_list_files(source_list, target_file):
	f = open(target_file,'a+', encoding='utf-8') if os.path.exists(target_file) else open(target_file,'w+', encoding='utf-8')
	for s in source_list:
		if isinstance(s ,set):
			print(s)
		f.write(json.dumps(s)+'\n')
	f.close()

def read_list_files(source_file):
	history =[]
	with open(source_file,'r', encoding='utf-8') as f:
		lines = f.read()
		for line in lines.split('\n')[:-1]:
			history.append(json.loads(line))
	return history

def is_server_alive(host, port):
	import socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		response = sock.connect_ex((host,port))
	except:
		return False

	#and then check the response...
	if response == 0:
		return True
	else:
		return False
# all_functions = get_openai_tools()
# all_docstrings = [get_docstring(fn) for fn in all_functions]








if __name__ == "__main__":
	from inspect import Parameter, signature
	from copy import deepcopy
	import textwrap
	#from pydantic.v1 import validate_arguments
	import inspect
	from typing import Optional, Callable, Any, Type
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

	def _rm_titles(kv: dict, prev_key: str = "", ) -> dict:
		new_kv = {}
		for k, v in kv.items():
			if k == "title":
				if isinstance(v, dict) and prev_key == "properties" and "title" in v.keys():
					new_kv[k] = _rm_titles(v, k)
				else:
					continue
			elif isinstance(v, dict):
				new_kv[k] = _rm_titles(v, k)
			else:
				new_kv[k] = v
		return new_kv
	


	def retrieve_ref(path, dict): #_retrieve_ref in langchain
		components = path.split("/")
		if components[0] != "#":
			raise ValueError(
			"ref paths are expected to be URI fragments, meaning they should start "
			"with #."
		)
		out = schema
		for component in components[1:]:
			if component in out:
				out = out[component]
			elif component.isdigit() and int(component) in out:
				out = out[int(component)]
			else:
				raise KeyError(f"Reference '{path}' not found.")
		return deepcopy(out)
			

	def remove_refs(json_schema): #_dereference_refs_helper
		if processed_refs is None:
			processed_refs = set()
		keys = []
		if isinstance(json_schema, dict):
			for k, v in json_schema.items():
				if k == "$ref":
					if v in processed_refs:
						continue
					processed_refs.add(v)
					ref = retrieve_ref(v, json_schema)
					full_ref = remove_refs(
                    ref, json_schema, processed_refs
                	)
					processed_refs.remove(v)
					return full_ref
					# keys.append(v.split("/")[1])
					# keys += remove_refs(ref, json_schema, processed_refs)
				elif isinstance(v, (list, dict)):
					json_schema[k] = remove_refs(v, json_schema, processed_refs)
				else:
					json_schema[k] = v
			return json_schema
		elif isinstance(json_schema, list):
			for el in json_schema:
				keys += remove_refs(el, json_schema, processed_refs)
		return keys


	x = get_functions() #Getting dict of attributes of all functions
	print('All functions:\n',x)
	print('\n')
	pri = list(x[1].values())[0] # Get first function attribute
#		for t in x: < - This is True
#				print(callable(t))
	print(convert_to_openai_function(pri))
	print('\n\n\n\n\n\n')
	print('Function:\t',pri)
	print('Inspect function:\t', inspect.getfullargspec(pri).args)
	validated_model = validate_call_model(pri)
	print('Type of validated model:\t', type(validated_model))
	print('Fields of validated model',validated_model.model_fields)
	print('Keys of fields of validated models',validated_model.model_fields.keys())
	print('\n')
	 #returns {'query': ModelField(name='query', type=str, required=True), 'v__duplicate_kwargs': ModelField(name='v__duplicate_kwargs', type=Optional[List[str]], required=False, default=None), 'args': ModelField(name='args', type=Optional[List[Any]], required=False, default=None), 'kwargs': ModelField(name='kwargs', type=Optional[Mapping[Any, Any]], required=False, default=None)}
	anno = inspect.get_annotations(pri)
	print('Annotations:\t', anno) # returns{'query': <class 'str'>, 'return': <class 'dict'>}
	print('Annotation type:\t', type(anno))
	print('\n')

	# ALL THIS IS FOR GETTING THE APPROPRIATE ARGUMENTS !! 
	print('*****Getting all the arguments and arg descriptions***** from inspect()') #This should be done only if there are args right ? No, we need the function description. Unless we use our docstring function for that
	docstring = inspect.getdoc(pri)
	name = pri.__name__
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
		elif block.strip().startswith("Returns:") or block.startswith("Example:"):
			past_descriptors = True
		# Don't break in case Args come after
		elif not past_descriptors:
			descriptors.append(block)
		else:
			continue
	print('Descriptors:\t',descriptors)
	print('String descriptors:\t',' '.join(descriptors))
	arg_descriptions = {}
	print('args block:\t',args_block)
	if args_block:
		arg = None
		for line in args_block.split("\n")[1:]:
			if ":" in line:
				arg, desc = line.split(":", maxsplit=1)
				print('Description before stripping arg types',arg)
				arg = arg.split('(')[0]
				print('Description after stripping arg types',arg)
				arg_descriptions[arg.strip()] = desc.strip()
			elif arg:
				print('No desc')
				arg_descriptions[arg.strip()] += " " + line.strip()
	print('Arg descriptions:\t',arg_descriptions)
	print('\n')

	
	print('**** Extracting details of the validated model ****') #Basically model created from the pydantic version of the function directly
	print('Validated model schema:\t', validated_model.model_json_schema())
	schema = validated_model.model_json_schema()["properties"]
	print('Properties of validated model:\t', schema)

	print('**** getting the details from the signature() fn of inspect')
	sig_params = signature(pri).parameters  # Basically from the inspect.signature part
	print('Validated model keys:\t',sig_params)

	print('****Creating a dict that has { key=sig_params.items.keys() i.e. inspect.signature and value = schema[key] where schema is what we get from the validated models schama properties entity}')
	field_names={}
	for k,v in sig_params.items():
		print(f'Key:\t',k,'\tValue:\t',v)
		print('V name:\t',v.name)
		print({k:schema[k]})  # {k = 'query' value = schema['query'] i.e. {'title': 'Query', 'type': 'string'}}
		print('\n')
		field_names.update({k:schema[k]})
	print('Field names', field_names)
	print('\n')
	print('*** Updating the pydantic model Field object with the detauls from the field names')
	print('Fields of validated model:\t', validated_model.model_fields)
	fields = {}
	for fieldname in field_names:
		print('Field name:\t', fieldname) #'query'
		model_field = validated_model.model_fields[fieldname]
		print('All model fields:\t', validated_model.model_fields)
		print('Model field:\t',model_field)
		print('Type of model field:\t',type(model_field))
		print('is field required:\t', model_field.is_required)
		print('Outer type????:\t', model_field.annotation)
		print('Detailed annotations',model_field.__annotations__)
		if model_field.is_required and not 'None' in str(model_field.annotation): #get the field type only if it is mandatory else set it as Optional[dtype]
			t = model_field.annotation
		else:
			t = Optional[model_field.annotation]
		print('t:\t',t)
		print('Arg descriptions:\t',arg_descriptions)
		print('field name:\t',fieldname) #{'query': (<class 'str'>, FieldInfo(default=Ellipsis, description='The search query.', extra={}))}
		if arg_descriptions and fieldname in arg_descriptions:
			print('Field. field_info',model_field.from_field(fieldname))
			print('Field. field_info description',model_field.description)
			model_field.description=arg_descriptions[fieldname]
			print('Field. field_info post updation',model_field.description)
		else:
			print('Not present')
		fields[fieldname] = (t, model_field)
	print('Final fields:\t', fields) # {'query': (<class 'str'>, FieldInfo(default=Ellipsis, description='The search query.', extra={}))}
	print('Type of final fields:\t', type(fields['query'][1]))
	try:
		final_model = create_model(name, **fields)
	except Exception as e:
		print('Final model could not be created:Exception\t',e)
	print('Initial final model type:\t', type(final_model))
	print('Initial final model doc:\t', dict[final_model])
	print('Descriptors to go into the model:\t', descriptors)
	final_model.__doc__ = ' '.join(descriptors).strip()	
	print('Func desc as per validated model\t:', final_model.__doc__)
	print('Does the final model have the attribute model_json_schema:\t',hasattr(final_model, "model_json_schema"))

	 #Converting to openai schema
	schema = final_model.model_json_schema(mode = 'serialization')
	print('Final schema:\t', schema)

	titles_params = _rm_titles(schema)
	print('Remove titles?:\t',titles_params)
	