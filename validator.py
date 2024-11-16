import json
import logging

class ValidationException(Exception):
    pass

def validate_and_process_input_output(input_str, output_str):
    try:
        input_list = json.loads(input_str)
        output_list = json.loads(output_str)

        if not isinstance(input_list, list) or not isinstance(output_list, list):
            raise ValidationException("Both input and output should be lists of cases.")

        logging.info(f"Validation successful: input_list={input_list}, output_list={output_list}")
        return input_list, output_list

    except json.JSONDecodeError as e:
        logging.error(f"Error in JSON parsing: {str(e)}")
        raise ValidationException("Error in parsing JSON input or output strings.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise ValidationException(str(e))
