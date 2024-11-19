import os
import re
import json
import logging
import time
from dotenv import load_dotenv
from mistralai import Mistral

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # in seconds (initial delay between retries)


def get_test_cases(user_code, client, model):
    logging.info("Generating test cases with the provided user code.")
    prompt = f"""
    Given the following Python function, generate 10-15 important test cases. Each test case should contain simple inputs (e.g., lists with at most 15 elements), and focus on edge cases, error handling, and boundary conditions.

    Python code:
    {user_code}

    Response format:
    [
        {{"input": <input>, "expected_output": <output>}},
        {{"input": <input>, "expected_output": <output>}},
        ...
    ]
    """
    try:
        chat_response = client.chat.complete(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt,
            }]
        )
        response = chat_response.choices[0].message.content
        logging.info("Test cases generated successfully.")
        return response
    except Exception as e:
        logging.error(f"Error generating test cases: {e}")
        return None


def clean_json(json_string):
    """
    Clean and format a potentially malformed JSON string.
    """
    json_string = re.sub(r'ValueError', '"ValueError"', json_string)
    json_string = re.sub(r',\s*([\]}])', r'\1', json_string)
    json_string = json_string.replace('\n', '').replace('\r', '')
    return json_string


def extract_inputs_outputs(response):
    """
    Extract inputs and outputs from the AI response.
    Returns a list of dictionaries with "input" and "expected_output".
    """
    logging.info("Extracting inputs and outputs from AI response.")

    if not response:
        logging.error("Empty response from AI model.")
        return None

    # Extract test case data
    match = re.search(r'\[.*\]', response, re.DOTALL)
    if not match:
        logging.error("Could not find valid test cases in the AI response.")
        return None

    json_string = match.group(0)
    json_string = clean_json(json_string)

    # Parse the cleaned JSON string into a Python object
    try:
        test_cases = json.loads(json_string)
        logging.info(f"Extracted {len(test_cases)} test cases.")
        return test_cases
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return None


def send_to_client(test_cases):
    """
    Send the extracted test cases (inputs and outputs) to the client.
    """
    if test_cases is None:
        logging.error("No valid test cases to send to the client.")
        return None

    try:
        # You can use an API or socket to send this data to the client
        # For illustration, we'll just log the output
        logging.info(f"Sending {len(test_cases)} test cases to the client.")

        # Here you'd replace with actual sending logic (API call, socket, etc.)
        # For example:
        # client.send(json.dumps(test_cases))

        return test_cases  # Return the test cases to simulate sending to the client
    except Exception as e:
        logging.error(f"Error sending test cases to client: {e}")
        return None


def ask_ai(user_code):
    load_dotenv()

    api_key = os.getenv("API_KEY")
    if not api_key:
        logging.error("API_KEY is missing or invalid.")
        return None

    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)

    logging.info("Starting the AI test case generation process.")
    retries = 0

    while retries < MAX_RETRIES:
        try:
            ai_response = get_test_cases(user_code, client, model)

            if not ai_response:
                logging.error("Received an empty or invalid response from AI.")
                return None

            test_cases = extract_inputs_outputs(ai_response)
            if test_cases is None:
                logging.error("Failed to generate valid test cases.")
                return None

            return send_to_client(test_cases)

        except json.JSONDecodeError as e:
            retries += 1
            logging.error(f"JSONDecodeError occurred. Retrying {retries}/{MAX_RETRIES}...")
            if retries < MAX_RETRIES:
                time.sleep(RETRY_DELAY * retries)  # Exponential backoff
            else:
                logging.error("Max retries reached. Unable to parse AI response.")
                return None

        except Exception as e:
            logging.error(f"Unexpected error in AI test case generation: {e}")
            return None
