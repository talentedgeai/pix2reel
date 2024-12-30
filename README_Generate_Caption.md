## OpenAI API Key Setup

To use the `shorten_captions_and_create_hashtags` function, you need an OpenAI API key. There are two ways to provide the key:

### Option 1: Environment Variable (Recommended)

Set the OpenAI API key as an environment variable before running your script:

```bash
# For macOS/Linux
export OPENAI_API_KEY='your_openai_api_key'

# For Windows (Command Prompt)
set OPENAI_API_KEY=your_openai_api_key

# For Windows (PowerShell)
$env:OPENAI_API_KEY='your_openai_api_key'
```

### Option 2: Passing API Key Directly

You can also pass the API key directly to the function:

```python
from pix2reel import shorten_captions_and_create_hashtags

# Passing API key as an argument
result = shorten_captions_and_create_hashtags(
    input_text="Your long caption", 
    api_key="your_openai_api_key"
)
```

## Example Usage

```python
from pix2reel import shorten_captions_and_create_hashtags

# Using environment variable
result = shorten_captions_and_create_hashtags("Your long caption")

# Or passing API key directly
result = shorten_captions_and_create_hashtags(
    "Your long caption", 
    api_key="your_openai_api_key"
)
```

## Notes

- Always keep your API key confidential
- Ensure you have an active OpenAI API subscription
- The function will raise a `ValueError` if no API key is found
