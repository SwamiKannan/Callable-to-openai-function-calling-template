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
dict_test= get_json_schema(get_name)
print(dict_test)
```
