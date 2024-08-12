# Convert a Python function definition into its representation in the Openai tool calling template
![](images/cover.png)

 ## Introduction
 OpenAI has defined the LLM standard template for [tool calling](https://platform.openai.com/docs/assistants/tools/function-calling) . This helps multiple open-source fine tuners define the same standard template for their function calling models. It also helps inference support platforms like [Ollama](https://ollama.com/) and [Llama.cpp](https://github.com/ggerganov/llama.cpp) use these templates to execute function calls on their platforms. Hence, it is super useful to maintain this template for all model training and fine-tuning experiments.
 However, OpenAI weirdly, does not provide tools to directly convert a function definition into this template. Hence, everyone has to manually construct this template from their function, making that a time consuming process. An example of this template is as follows: <br />
 
```
tools=[
    {
      "type": "function",
      "function": {
        "name": "get_current_temperature",
        "description": "Get the current temperature for a specific location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g., San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["Celsius", "Fahrenheit"],
              "description": "The temperature unit to use. Infer this from the user's location."
            }
          },
          "required": ["location", "unit"]
        }
      }
    }
```
## Langchain
If you are using the Langchain framework, there is an in-built function called **convert_to_openai_function** . Hence, if you are already using Langchain, you can directly import this function as:
```
from langchain_core.utils.function_calling import convert_to_openai_function
```
This tool can convert both normal Python functions and tool objects. Tool objects are as:
```
from langchain.tools import tool

@tool
def function_example(*args, **kwargs) -> <return type>
    <doctype>

    Args:
      arg1:

    Returns:
      <return type>

openai_representation = convert_to_openai_function(function_example)
```
However, if you are not using Langchain, installing it for just this functionality makes no sense. This library acts as a substitute
## Details
This library is partially based on Langchain's convert_to_openai_function. However:
1. This is a stripped-down version of the 
