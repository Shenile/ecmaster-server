import sys
import json
import importlib.util
import traceback
import logging
from typing import Callable, List, Dict, Any
from testing import Testing

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def import_user_code(code_file: str):
    spec = importlib.util.spec_from_file_location("user_module", code_file)
    user_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(user_module)
    return user_module

def read_test_data(data_file: str) -> Dict[str, List[Any]]:
    with open(data_file, 'r') as f:
        return json.load(f)

def main():
    if len(sys.argv) != 4:
        logging.error("Usage error: Usage: python run_tests.py <user_code_file> <test_data_file> <function_name>")
        sys.exit(1)

    code_file = sys.argv[1]
    data_file = sys.argv[2]
    function_name = sys.argv[3]

    # response structure
    response = {
        "results" : None,
        "tests_summary" : None
    }
    try:
        user_code = import_user_code(code_file)
        test_data = read_test_data(data_file)
        tester = Testing()

        input_data = test_data.get('inputs', [])
        output_data = test_data.get('outputs', [])

        if len(input_data) != len(output_data):
            raise ValueError("Mismatch between input_array and output_array lengths.")

        for i in range(len(input_data)):
            tester.create_testcase(input_data[i], output_data[i])

        if hasattr(user_code, function_name):
            function = getattr(user_code, function_name)
            test_results = tester.run_tests(function)
            response['results'] = test_results['results']
            response['tests_summary'] = test_results['tests_summary']


        logging.info(f"Test results: {response['results']}")
        print(json.dumps(response))

    except Exception as e:
        error_message = f"Error: {str(e)}"
        logging.error(f"Test execution failed: {str(e)}")
        print(json.dumps({"compilation_error" : True, "err": error_message}))

if __name__ == "__main__":
    main()
