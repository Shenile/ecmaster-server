import logging, time
from typing import Callable, List, Dict, Any

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# timer decorator to measure execution time .,
def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        execution_time_ms = round(execution_time_ms, 4)
        return result, execution_time_ms

    return wrapper

class Testing:
    def __init__(self):
        self.tests: List[Dict[str, Any]] = []

    def create_testcase(self, input: List[Any], output: Any):
        test = {'input': {'nums': input}, 'output': output}
        self.tests.append(test)

    def run_tests(self, function: Callable[[List[Any]], Any]) -> List[Dict[str, Any]]:
        results = {"results": [], "tests_summary": {}}

        # Don't delete the test inputs and test outputs they're for Quick test Feature
        tests_summary = {"passed": 0,
                        "failed": 0,
                        "test_inputs": [],
                        "test_outputs": []
                       }

        decorated_function = timer(function)
        for i, test in enumerate(self.tests):
            arr = test['input']['nums']
            expected_output = test['output']

            result = {'test_case': i + 1,
                      'status': '',
                      'error': '',
                      'execution_time' : None,
                      'test_input' : '',
                      'test_output' : ''}

            # storing the input , output test_cases ..,
            result['test_input'] = arr
            result['test_output']= expected_output

            try:
                received_output, execution_time = decorated_function(arr)

                # saving execution time
                result['execution_time'] = execution_time

                if expected_output == received_output:
                    result['status'] = 'Passed'
                    tests_summary['passed'] += 1
                else:
                    result['status'] = 'Failed'
                    tests_summary['failed'] += 1
                    result['error'] = f"Expected {expected_output}, but got {received_output}"

            except Exception as e:

                result['status'] = 'Failed'
                tests_summary['failed'] += 1
                result['error'] = f"An ERROR occured : {str(e)}"
                raise e

            results['results'].append(result)
            tests_summary['test_inputs'].append(arr)
            tests_summary['test_outputs'].append(expected_output)

        results['tests_summary'] = tests_summary
        return results
