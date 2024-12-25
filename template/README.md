# Template to be followed for defining a function to be used
**This template is largely based on [Google's Python Style Guide
](https://google.github.io/styleguide/pyguide.html#383-functions-and-methods)** . A few examples are available [here](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

### With arguments
```
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
	"""
	#<Write function below>
	print('Function is being called')
	return (name+'_'+str(options))
```

### Without arguments
```
def get_name():
	"""
	This is the docstring of the function

	The string should contain valid, executable and pure Python code in markdown syntax.
	Code should also import any required Python packages.

	Args:

	Returns:
		str: A concatentation of the name and the option chosen

	"""
	print('Function is being called')
	return 'no arguments'
```
