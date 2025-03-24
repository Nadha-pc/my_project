import os
from openai import OpenAI

# Load API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Set the environment variable OPENAI_API_KEY.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Available models: "gpt-4-1106-preview", "gpt-3.5-turbo-1106", or "davinci-codex"
MODEL_NAME = "GPT-4o"


def api_call(messages, model_name=MODEL_NAME, temperature=0.5, max_tokens=150):
    try:
        # Execute the chat completion using the chosen model
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,  # Values can range from 0.0 to 1.0
            max_tokens=max_tokens,  # Specifies the maximum length of the response
        )

        # Extract and return the response content
        if response.choices and hasattr(response.choices[0], 'message'):
            decision_message = response.choices[0].message
            decision = decision_message.content.strip() if hasattr(decision_message, 'content') else None
        else:
            decision = None

        return decision
    except Exception as e:
        raise Exception(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    messages_payload = [
        {"role": "system", "content": "You are a helpful and knowledgeable assistant."},
        {"role": "user", "content": "Please help me troubleshoot my JavaScript code."}
    ]

    # Example configuration: you might want to specify 'temperature' for more creative responses
    result = api_call(messages_payload, temperature=0.7, max_tokens=100)
    print(f"AI Analysis Result: '{result}'")
