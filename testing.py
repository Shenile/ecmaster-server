import logging
from typing import Callable, List, Dict, Any

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Testing:
    def __init__(self):
        self.tests: List[Dict[str, Any]] = []

    def create_testcase(self, input: List[Any], output: Any):
        test = {'input': {'nums': input}, 'output': output}
        self.tests.append(test)

    def run_tests(self, function: Callable[[List[Any]], Any]) -> List[Dict[str, Any]]:
        results = {"result": [], "testSummary": {}}
        test_summary = {"passed": 0, "failed": 0, "test_inputs": [], "test_outputs": []}

        for i, test in enumerate(self.tests):
            arr = test['input']['nums']
            expected_output = test['output']
            result = {'test_case': i + 1, 'status': '', 'error': ''}

            try:
                received_output = function(arr)
                if expected_output == received_output:
                    result['status'] = 'Passed'
                    test_summary['passed'] += 1
                else:
                    result['status'] = 'Failed'
                    test_summary['failed'] += 1
                    result['error'] = f"Expected {expected_output}, but got {received_output}"

            except Exception as e:
                result['status'] = 'Failed'
                result['error'] = str(e)

            results['result'].append(result)
            test_summary['test_inputs'].append(arr)
            test_summary['test_outputs'].append(expected_output)

        results['testSummary'] = test_summary
        logging.info(f"Test summary: {test_summary}")
        return results
