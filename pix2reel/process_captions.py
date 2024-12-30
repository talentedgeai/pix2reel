from openai import OpenAI
import os

def shorten_captions_and_create_hashtags(input_text, api_key=None):
    """
    Summarize text(s) into concise captions and generate related hashtags using OpenAI.
    
    Args:
        input_text (str or list[str]): The original text(s) to be summarized
        api_key (str, optional): OpenAI API key. If not provided, 
            the function will attempt to read from the OPENAI_API_KEY environment variable.
    
    Returns:
        A list of strings, each containing summary and hashtag
    
    Raises:
        ValueError: If no OpenAI API key is found in arguments or environment
    """
    # Handle single string input for backward compatibility
    if isinstance(input_text, str):
        # Prepare for single text processing
        texts = [input_text]
    else:
        # Handle list input
        texts = input_text
        
    # Prepare the prompt for batch processing
    prompt = (
        "For each text, provide a summary under 50 characters and a hashtag under 20 characters. "
        "Format your response as:\n"
        "Text 1: [Summary 1] #[Hashtag 1]\n"
        "Text 2: [Summary 2] #[Hashtag 2]\n"
        "...\n\n"
        + "\n".join(f"Text {i+1}: {text}" for i, text in enumerate(texts))
    )

    # Use provided API key, or fall back to environment variable
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "OpenAI API key not provided. "
            "Please pass the key as an argument or set OPENAI_API_KEY environment variable."
        )

    # Call the OpenAI API
    client = OpenAI(
        api_key=api_key,
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=200,
        temperature=0.7,
    )

    # Extract the response text
    result_text = response.choices[0].message.content.strip()
    
    # Parse the results
    processed_results = []
    for line in result_text.split('\n'):
        if ':' in line:
            parts = line.split(':', 1)[1].strip().split('#')
            summary = parts[0].strip()
            hashtag = f"#{parts[1].strip()}" if len(parts) > 1 else ""
            processed_results.append(f"{summary} {hashtag}".strip())
    
    # Return based on input type
    return processed_results
