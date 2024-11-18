import re

class FunctionNameNotFoundError(Exception):
    pass

def isNestedArray(arr):
    if isinstance(arr, list):
        if all(isinstance(item, list) for item in arr):
            return True
        else:
            return False

def handleEdgecases(input_list, output_list):

    input_arr, output_arr = [], []

    if not isinstance(input_list, list) or not isinstance(output_list, list):
        raise ValueError("Both input_list and output_list must be lists")

    if isinstance(input_list, list):

        # for nested arrays
        if (isNestedArray(input_list)):

            for item in input_list:
                input_arr.append(item)

            # for nested array outputs
            if (isNestedArray(output_list)):
                for item in output_list:
                    output_arr.append(item)
                print(f'the input arr: {input_arr}\noutput_arr : {output_arr}')

            # for single array outputs
            else:
                output_arr.extend(output_list)
                print(f'the input arr: {input_arr}\noutput_arr : {output_arr}')



        # for single arrays
        else:

            input_arr.append(input_list)

            # for single outputs -> [1]
            if (len(output_list) == 1):

                output_arr.append(output_list[0])
                print(f'the input arr: {input_arr}\noutput_arr : {output_arr}')

            # for array outputs -> [1,2,3]
            else:

                output_arr.append(output_list)
                print(f'the input arr: {input_arr}\noutput_arr : {output_arr}')

    print(f'is equal : {len(input_arr) == len(output_arr)}')

    return input_arr, output_arr


def extract_function_name(user_code):
    try:
        match = re.search(r'def\s+(\w+)\s*\(', user_code)
        if match:
            function_name = match.group(1)
        else:
            raise FunctionNameNotFoundError("Function name not found in the provided code.")
    except re.error as e:
        print(f"Regex error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

    return function_name