from openai import OpenAI
import os

def shorten_captions_and_create_hashtags(input_text, api_key=None):
    # Check if the input text is too long
    if len(input_text) <= 50:
        return input_text, ""

    # Define the prompt for summarizing and generating a hashtag
    prompt = (
        f"Summarize the following text into fewer than 50 characters and generate a hashtag under 20 characters:\n\n"
        f"Text: {input_text}\n"
        f"Summary:"
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
        max_tokens=50,
        temperature=0.7,
    )

    # Extract the response text
    result_text = response.choices[0].message.content.strip()
    summary, hashtag = result_text.split("#") if "#" in result_text else (result_text, "")

    return summary.strip(), f"#{hashtag.strip()}" if hashtag else ""
