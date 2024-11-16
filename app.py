import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import json
import os
from validator import validate_and_process_input_output, ValidationException
from userInputs_edge_case_handler import handleEdgecases, extract_function_name, FunctionNameNotFoundError

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def home():
    logging.info("Home route accessed")
    return jsonify({'result': 'Hello I am Edge Case Master, a handy tool for quick edge case creation and validation', "founder": "Shenile A"}), 200

@app.route('/runtests', methods=['POST'])
def execute_code():
    data = request.json
    user_code = data.get('code', '')
    input_str = data.get('inputString', '')
    output_str = data.get('outputString', '')

    try:
        input_list, output_list = validate_and_process_input_output(input_str, output_str)
    except ValidationException as e:
        logging.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    try:
        input_array, output_array = handleEdgecases(input_list, output_list)
    except ValueError as e:
        logging.error(f"Edge case handling error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    try:
        function_name = extract_function_name(user_code)
    except FunctionNameNotFoundError as e:
        logging.error(f"Function name extraction error: {str(e)}")
        return jsonify({"err": str(e)}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"err": str(e)}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp_code_file:
        temp_code_file.write(user_code.encode())
        temp_code_filename = temp_code_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_data_file:
        temp_data_file.write(json.dumps({'inputs': input_array, 'outputs': output_array}).encode())
        temp_data_filename = temp_data_file.name

    try:
        result = subprocess.run(
            ['python', 'run_tests.py', temp_code_filename, temp_data_filename, function_name or ''],
            capture_output=True, text=True
        )

        stdout_output = result.stdout.strip()
        stderr_output = result.stderr.strip()

        os.remove(temp_code_filename)
        os.remove(temp_data_filename)

        try:
            result_json = json.loads(stdout_output) if stdout_output else {"error": "No output received from subprocess"}
        except json.JSONDecodeError as e:
            result_json = {"error": f"JSON decoding error: {e}"}

    except Exception as e:
        result_json = {"error": f"Subprocess execution failed: {e}"}
        stderr_output = str(e)

    logging.info(f"Test results: {result_json['results']['result']}")
    logging.info(f"Test summary: {result_json['results']['testSummary']}")

    return jsonify({
        "results": result_json["results"]["result"],
        "testSummary": result_json["results"]["testSummary"],
        'err': stderr_output
    }), 200

if __name__ == '__main__':
    app.run(port=5000)
