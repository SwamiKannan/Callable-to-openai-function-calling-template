# Sample exercise in executing script

### Sample function with multiple arguments:
```
# Sample function to process
def get_name(name:str = 'Swaminathan', options:Literal['1','2','3','4'] = '1'):
		"""
		This is the docstring of the function

		The string should contain valid, executable and pure Python code in markdown syntax.
		Code should also import any required Python packages.

		Args:
			name : The name of the person 
			options : The options that needs to be provided to the user

		Returns:
			str: A concatentation of the name and the option chosen

		Note:
			Use this function with caution, as executing arbitrary code can pose security risks.
		"""
		print('Function is being called')
		return (name+'_'+str(options))
```

```
# Parsing and processing the function
# Setting get_tool_format = True allows returns the json format similar to that is returned when langchain's convert_to_openai_tool() is called with one minor change. The argument descriptions are incorporated within the arguments dictionary.
# Setting the get_langchain_format = True adds all descriptions in the function description instead as per the langchain format
dict_test= get_json_schema(get_name,get_tool_format= True, get_langchain_format=True)
print(dict_test)
```
```
