# Sample exercise in executing script

## 1. Sample function with multiple arguments:
#### Function to be processed
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
#### Parsing and processing the function
##### 1. Parsing to the format of langchain's convert_to_openai_tool()
```
# Setting get_tool_format = True allows returns the json format similar to that is returned when langchain's convert_to_openai_tool() is called with one minor change. The argument descriptions are incorporated within the arguments dictionary.
# Setting the get_langchain_format = True adds all descriptions in the function description instead as per the langchain format
dict_test= get_json_schema(get_name,get_tool_format= True, get_langchain_format=True)
print(dict_test)
```
#### Output (unformatted)
```
{'name': 'get_name', 'description': 'This is the docstring of the function The string should contain valid, executable and pure Python code in markdown syntax.\nCode should also import 
any required Python packages.', 'parameters': {'properties': {'name': {'default': 'Swaminathan', 'description': 'The name of the person', 'type': 'string'}, 'options': {'default': '1', 
'description': 'The options that needs to be provided to the user', 'enum': ['1', '2', '3', '4'], 'type': 'string'}}, 'type': 'object'}}
```
#### Output (manually formatted for clarity)
```
{
  "type": "function",
  "function": {
    "name": "get_name",
    "description": "\nThis is the docstring of the function\n\nThe string should contain valid, executable and pure Python code in markdown syntax.\nCode should also import any required Python packages.\n\nArgs:\n\tname : The name of the person \n\toptions : The options that needs to be provided to the user\n\nReturns:\n\tstr: A concatentation of the name and the option chosen\n\nNote:\n\tUse this function with caution, as executing arbitrary code can pose security risks.\n",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "default": "Swaminathan",
          "type": "string"
        },
        "options": {
          "default": "1",
          "enum": [
            "1",
            "2",
            "3",
            "4"
          ],
          "type": "string"
        }
      }
    }
  }
}
```
##### 2. Parsing to the format of langchain's convert_to_openai_function()
```
# Setting get_tool_format = False allows returns the json format similar to that is returned when langchain's convert_to_openai_tool() is called.
dict_test= get_json_schema(get_name,get_tool_format= False, get_langchain_format=False)
print(dict_test)
```
#### Output (unformatted)
```
{'name': 'get_name', 'description': 'This is the docstring of the function The string should contain valid, executable and pure Python code in markdown syntax.\nCode should also import 
any required Python packages.', 'parameters': {'properties': {'name': {'default': 'Swaminathan', 'description': 'The name of the person', 'type': 'string'}, 'options': {'default': '1', 
'description': 'The options that needs to be provided to the user', 'enum': ['1', '2', '3', '4'], 'type': 'string'}}, 'type': 'object'}}
```
#### Output (manually formatted for clarity)
```
{
  "name": "get_name",
  "description": "This is the docstring of the function The string should contain valid, executable and pure Python code in markdown syntax.\nCode should also import any required Python packages.",
  "parameters": {
    "properties": {
      "name": {
        "default": "Swaminathan",
        "description": "The name of the person",
        "type": "string"
      },
      "options": {
        "default": "1",
        "description": "The options that needs to be provided to the user",
        "enum": [
          "1",
          "2",
          "3",
          "4"
        ],
        "type": "string"
      }
    },
    "type": "object"
  }
}
```
## 2. Sample function with no arguments:
#### Function to be processed
```
def get_name():
	"""
	This is the docstring of the function

	The string should contain valid, executable and pure Python code in markdown syntax.
	Code should also import any required Python packages.

	Args:

	Returns:
		str: A concatentation of the name and the option chosen

	Note:
		Use this function with caution, as executing arbitrary code can pose security risks.
	"""
	print('Function is being called')
	return 'no arguments'
```
#### Parsing and processing the function
##### 1. Parsing to the format of langchain's convert_to_openai_tool()
```
# Setting get_tool_format = True allows returns the json format similar to that is returned when langchain's convert_to_openai_tool() is called with one minor change. The argument descriptions are incorporated within the arguments dictionary.
# Setting the get_langchain_format = True adds all descriptions in the function description instead as per the langchain format
dict_test= get_json_schema(get_name,get_tool_format= True, get_langchain_format=True)
print(dict_test)
```
#### Output (unformatted)
```
{'type': 'function', 'function': {'name': 'get_name', 'description': 'This is the docstring of the function\n\nThe string should contain valid, executable and pure Python code in markdown syntax.\nCode should also import any required Python packages.\n\nArgs:\n\nReturns:\n    str: A concatentation of the name and the option chosen\n\nNote:\n    Use this function with 
caution, as executing arbitrary code can pose security risks.', 'parameters': {'type': 'object', 'properties': {}}}
```
#### Output (manually formatted for clarity)
```
{
  "type": "function",
  "function": {
    "name": "get_name",
    "description": "\nThis is the docstring of the function\n\nThe string should contain valid, executable and pure Python code in markdown syntax.\nCode should also import any required Python packages.\n\nArgs:\n\nReturns:\n\tstr: A concatentation of the name and the option chosen\n\nNote:\n\tUse this function with caution, as executing arbitrary code can pose security risks.\n",
    "parameters": {
      "type": "object",
      "properties": {}
    }
  }
}
```
##### 2. Parsing to the format of langchain's convert_to_openai_function()
```
# Setting get_tool_format = False allows returns the json format similar to that is returned when langchain's convert_to_openai_tool() is called.
dict_test= get_json_schema(get_name,get_tool_format= False, get_langchain_format=False)
print(dict_test)
```
#### Output (unformatted)
```
{'name': 'get_name', 'description': 'This is the docstring of the function\t\tThe string should contain valid, executable and pure Python code in markdown syntax.\t\tCode should also import any required Python packages.', 'parameters': {'type': 'object', 'properties': {}}}
```
#### Output (manually formatted for clarity)
```
{
  "name": "get_name",
  "description": "This is the docstring of the function\t\tThe string should contain valid, executable and pure Python code in markdown syntax.\t\tCode should also import any required Python packages.",
  "parameters": {
    "type": "object",
    "properties": {}
  }
}
```
