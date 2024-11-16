import re
import logging

class FunctionNameNotFoundError(Exception):
    pass

def isNestedArray(arr):
    if isinstance(arr, list):
        return all(isinstance(item, list) for item in arr)
    return False

def handleEdgecases(input_list, output_list):
    input_arr, output_arr = [], []

    if not isinstance(input_list, list) or not isinstance(output_list, list):
        raise ValueError("Both input_list and output_list must be lists")

    if isinstance(input_list, list):
        if isNestedArray(input_list):
            for item in input_list:
                input_arr.append(item)
            if isNestedArray(output_list):
                for item in output_list:
                    output_arr.append(item)
            else:
                output_arr.extend(output_list)
        else:
            input_arr.append(input_list)
            if len(output_list) == 1:
                output_arr.append(output_list[0])
            else:
                output_arr.append(output_list)

    logging.info(f"Processed edge cases: input_arr={input_arr}, output_arr={output_arr}")
    return input_arr, output_arr

def extract_function_name(user_code):
    try:
        match = re.search(r'def\s+(\w+)\s*\(', user_code)
        if match:
            return match.group(1)
        else:
            raise FunctionNameNotFoundError("Function name not found in the provided code.")
    except re.error as e:
        raise e
    except Exception as e:
        raise e
