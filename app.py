import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import json
import os
from validator import validate_and_process_input_output, ValidationException
from userInputs_edge_case_handler import handleEdgecases, extract_function_name, FunctionNameNotFoundError
from ai_test_case_generator import ask_ai

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def handle_test_execution(user_code, input_list, output_list):
    """Handle the logic of running tests on the user code"""
    try:
        # Validate and process inputs and outputs
        input_array, output_array = handleEdgecases(input_list, output_list)

        # Extract function name
        function_name = extract_function_name(user_code)

        # Create temporary files for user code and test data
        temp_code_filename, temp_data_filename = create_temp_files(user_code, input_array, output_array)

        # Run the test
        result = run_tests(temp_code_filename, temp_data_filename, function_name)

        # Clean up temporary files
        os.remove(temp_code_filename)
        os.remove(temp_data_filename)

        return result

    except (ValidationException, ValueError, FunctionNameNotFoundError, Exception) as e:
        logging.error(f"Error occurred: {str(e)}")
        return {"error": str(e)}


def create_temp_files(user_code, input_array, output_array):
    """Create temporary files for code and test data"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp_code_file:
        temp_code_file.write(user_code.encode())
        temp_code_filename = temp_code_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_data_file:
        temp_data_file.write(json.dumps({'inputs': input_array, 'outputs': output_array}).encode())
        temp_data_filename = temp_data_file.name

    return temp_code_filename, temp_data_filename

def run_tests(temp_code_filename, temp_data_filename, function_name):
    """Run tests using subprocess and return the result"""
    try:
        result = subprocess.run(
            ['python', 'run_tests.py', temp_code_filename, temp_data_filename, function_name or ''],
            capture_output=True, text=True
        )

        stdout_output = result.stdout.strip()
        stderr_output = result.stderr.strip()

        # Decode JSON result
        try:
            result_json = json.loads(stdout_output) if stdout_output else {
                "error": "No output received from subprocess"}
        except json.JSONDecodeError as e:
            result_json = {"error": f"JSON decoding error: {e}"}

        return result_json, stderr_output
    except Exception as e:
        return {"error": f"Subprocess execution failed: {e}"}, str(e)


@app.route('/', methods=['GET'])
def home():
    logging.info("Home route accessed")
    return jsonify({'result': 'Hello I am Edge Case Master, a handy tool for quick edge case creation and validation',
                    "developer": "Shenile A"}), 200


@app.route('/runtests', methods=['POST'])
def execute_code():
    data = request.json
    user_code = data.get('code', '')
    input_str = data.get('inputString', '')
    output_str = data.get('outputString', '')

    try:
        # Validate and process inputs and outputs
        input_list, output_list = validate_and_process_input_output(input_str, output_str)
    except ValidationException as e:
        logging.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    result_json, stderr_output = handle_test_execution(user_code, input_list, output_list)

    if "error" in result_json:
        return jsonify(result_json), 400

    logging.info(f'result_json {result_json}')
    return jsonify({
        "results": result_json.get("results", []),
        "tests_summary": result_json.get("tests_summary", {}),
        "err": stderr_output
    }), 200

@app.route('/ask_ai', methods=['POST'])
def generate_test_case():
    data = request.json
    code = data.get('code', '')

    # Log the received code (log only the first 30 characters of the code to prevent over-exposure of sensitive code)
    logging.info(f"Received request to generate test cases with code: {code[:30]}...")

    try:
        # Log before calling ask_ai to generate test cases
        logging.info("Calling ask_ai to generate test cases.")
        test_cases = ask_ai(code)
        logging.info(f"Generated test cases: {test_cases[:5]}...")  # Log a preview of the first 5 test cases to avoid large logs
    except Exception as e:
        logging.error(f"Error occurred while generating test cases: {str(e)}")
        return jsonify({"err": "Something went wrong ..,"}), 500

    # Return the response with the generated test cases
    logging.info("Successfully generated test cases.")
    return jsonify({
        "test_cases": test_cases
    }), 200


if __name__ == '__main__':
    app.run(port=5000)
