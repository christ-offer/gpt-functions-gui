import openai 
from openai import OpenAIError
import logging

def regular_agent(
        prompt,
        conversation,
        system_message,
        model: str = "gpt-4-0613",
        temperature: float = 0.6,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages=[
                {"role": "system", "content": system_message},
            ] + conversation + [
                {"role": "user", "content": prompt}
            ],
        )
    except OpenAIError as error:
        logging.error(f"OpenAI API call failed: {str(error)}")
        return "OpenAI API call failed due to an internal server error.", conversation
    except openai.error.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        return "Failed to connect to OpenAI.", conversation
    except openai.error.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        return "Requests exceed OpenAI rate limit.", conversation
    return response["choices"][0]["message"], conversation