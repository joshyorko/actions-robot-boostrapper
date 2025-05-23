import os
import socket
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path
from typing import List

import black
import sema4ai_http
from pydantic import BaseModel
from sema4ai.actions import Response, action
from urllib3.exceptions import ConnectionError


class Secret(BaseModel):
    value: str = ""


@action
def run_shell_command(cmd: List[str], cwd: str = None) -> str:
    """
    MIGHTY GORILLA HELPER TO RUN RCC COMMANDS WITH POWER!
    
    Args:
        cmd: List of command parts to run
        cwd: Directory to run the command in (optional)
    
    Returns:
        Combined stdout and stderr from command
    
    Raises:
        subprocess.CalledProcessError: If command fails
    """
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    # Combine stdout and stderr for better error reporting
    output = result.stdout + result.stderr if result.stderr else result.stdout
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        print(f"Command failed with return code {result.returncode}")
        print(f"Command output: {output}")
    return Response(result=output)

# Add a non-decorated version for internal use

def _run(cmd: List[str], cwd: str = None) -> str:
    return run_shell_command(cmd, cwd=cwd)


# SCAFFOLDING & TEMPLATES ACTIONS 🦍
@action
def create_robot(template: str, directory: str) -> Response[str]:
    """
    CREATE NEW ROBOT WITH MIGHTY TEMPLATE!
    
    Args:
        template: Template to use (like "01-python")
        directory: Where to create robot
        
    Returns:
        Response with command output
    """
    output = _run(["rcc", "robot", "initialize", "--template", template, "--directory", directory])
    
    #need to check what the output is
    #check output results
    print(output)
    if "OK" in output:
        return Response(result=f"Robot created from template {template} in {directory}")
    else:
        return Response(error=f"Failed to create robot from template {template} here is the error: {output}")

@action 
def pull_robot(owner_repo: str, directory: str) -> Response[str]:
    """
    PULL ROBOT FROM REMOTE JUNGLE!
    
    Args:
        owner_repo: Git repo owner and repo name (like "user/repo")
        directory: Where to put robot
        
    Returns:
        Command output with success/failure status
    """
    try:
        output = _run(["rcc", "pull", f"github.com/{owner_repo}", "--directory", directory])
        print(f"Command output: {output}")
        
        # Check for specific success patterns in the output
        success_indicators = [
            "OK.",
            "Flattening path",
            "extracted files"
        ]
        
        if any(indicator in output for indicator in success_indicators):
            return Response(result=f"Robot successfully pulled from {owner_repo} into {directory}. Details: {output}")
        else:
            return Response(error=f"Failed to pull robot from {owner_repo}. Output: {output}")
    except Exception as e:
        return Response(error=f"Error pulling robot: {str(e)}")

# LISTING & RUNNING ACTIONS 🍌
@action
def list_templates() -> Response[str]:
    """
    SHOW ALL ROBOT TEMPLATES!
    
    Returns:
        Response with list of available templates
    """
    result = _run(["rcc", "robot", "initialize", "--list"])
    return Response(result=result)

@action
def pull_template(repo_url: str, directory: str) -> Response[str]:
    """
    GRAB TEMPLATE FROM GITHUB JUNGLE!
    
    Args:
        repo_url: Github repo URL with template
        directory: Where to put template
        
    Returns:
        Command output
    """
    return _run(["rcc", "pull", repo_url, "-d", directory])

@action
def create_from_template(template: str, directory: str) -> Response[str]:
    """
    MAKE NEW ROBOT FROM TEMPLATE!
    
    Args:
        template: Template name like python-minimal
        directory: Where to create robot
        
    Returns:
        Response with command output
    """
    result = _run(["rcc", "create", template, "-d", directory])
    return Response(result=result)

@action
def run_robot(task_name: str, robot_path: str) -> Response[str]:
    """
    RUN ONE TASK BY NAME!
    
    Args:
        task_name: Name of task to run
        robot_path: Path to robot directory
        
    Returns:
        Command output
    """
    return _run(["rcc", "run", "-r", f"{robot_path}/robot.yaml"])

@action
def task_testrun() -> str:
    """
    DO CLEAN TEST RUN!
    
    Returns:
        Test results output
    """
    return _run(["rcc", "task", "testrun"])

# ROBOT-SCOPED ACTIONS 🍌
@action
def initialize_robot(robot_name: str, template: str) -> Response[str]:
    """
    MAKE NEW ROBOT WITH NAME AND TEMPLATE!
    
    Args:
        robot_name: Name for new robot
        template: Template to use for robot
        
    Returns:
        Response with command output
    """
    result = _run(["rcc", "robot", "init", "--name", robot_name, "--template", template])
    return Response(result=result)

@action
def robot_dependencies() -> Response[str]:
    """
    CHECK ROBOT NEEDS BANANAS!
    
    Returns:
        Response with dependencies check output
    """
    result = _run(["rcc", "robot", "dependencies"])
    return Response(result=result)

@action 
def robot_diagnostics() -> Response[str]:
    """
    CHECK IF ROBOT HEALTHY!
    
    Returns:
        Response with diagnostics output
    """
    result = _run(["rcc", "robot", "diagnostics"])
    return Response(result=result)

@action
def wrap_robot() -> Response[str]:
    """
    PACK ROBOT IN BANANA LEAF!
    
    Returns:
        Response with wrap output
    """
    result = _run(["rcc", "robot", "wrap"])
    return Response(result=result)

@action
def unwrap_robot(artifact: str) -> Response[str]:
    """
    UNWRAP ROBOT FROM BANANA LEAF!
    
    Args:
        artifact: Path to wrapped robot artifact
        
    Returns:
        Command output
    """
    return _run(["rcc", "robot", "unwrap", "--artifact", artifact])

# LOCAL EXECUTION ACTIONS 🦍


@action
def run_task(task_name: str) -> Response[str]:
    """
    MAKE ROBOT DO SPECIFIC TASK!
    
    Args:
        task_name: Name of task to run
        
    Returns:
        Response with task output 
    """
    result = _run(["rcc", "run", "--task", task_name])
    return Response(result=result)

@action
def list_tasks() -> Response[str]:
    """
    SHOW ALL TASKS ROBOT CAN DO!
    
    Returns:
        Response with tasks list
    """
    result = _run(["rcc", "task", "list"])
    return Response(result=result)




@action
def script_in_robot(command: str) -> str:
    """
    RUN COMMAND IN ROBOT HOME!
    
    Args:
        command: Shell command to run
        
    Returns:
        Command output
    """
    return _run(["rcc", "run", "--", command])





# DOCS & HELP ACTIONS 🦍
@action
def docs_list() -> Response[str]:
    """
    SHOW ALL DOCUMENTATION!
    
    Returns:
        Response with docs list
    """
    result = _run(["rcc", "docs", "list"])
    return Response(result=result)

@action
def docs_recipes() -> Response[str]:
    """
    SHOW ROBOT RECIPES!
    
    Returns:
        Response with recipes list
    """
    result = _run(["rcc", "docs", "recipes"])
    return Response(result=result)

@action
def docs_changelog() -> Response[str]:
    """
    SHOW WHAT CHANGED!
    
    Returns:
        Response with changelog
    """
    result = _run(["rcc", "docs", "changelog"])
    return Response(result=result)




@action
def help() -> Response[str]:
    """
    SHOW ALL HELP!
    
    Returns:
        Response with help text
    """
    result = _run(["rcc", "--help"])
    return Response(result=result)


@action
def bootstrap_action_package(action_package_name: str) -> Response[str]:
    """
    This action sets up an action package in the home directory of the user under the "actions_bootstrapper" folder.

    Args:
        action_package_name: Name of the action package

    Returns:
        The full path of the bootstrapped action package.
    """
    home_directory = os.path.expanduser("~")

    new_action_package_path = os.path.join(home_directory, "actions_bootstrapper")

    os.makedirs(new_action_package_path, exist_ok=True)

    command = f"action-server new --name '{action_package_name}' --template minimal"
    subprocess.run(command, shell=True, cwd=new_action_package_path)

    full_action_path = get_action_package_path(action_package_name)

    # SMASH MORE UPDATES INTO BOOTSTRAP!
    update_action_package_dependencies(action_package_name, action_package_dependencies_code="")
    update_action_code(action_package_name, action_code="")  
    update_action_package_action_dev_data(action_package_name, "", "")

    return Response(
        result=f"Action successfully bootstrapped! Code available at {full_action_path}"
    )


def find_available_port(start_port: int) -> int:
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except socket.error:
                port += 1


def get_action_package_path(action_package_name: str) -> str:
    home_directory = os.path.expanduser("~")

    new_action_package_path = os.path.join(home_directory, "actions_bootstrapper")

    full_action_path = os.path.join(new_action_package_path, action_package_name)

    return full_action_path


@action
def update_action_package_dependencies(
    action_package_name: str, action_package_dependencies_code: str
) -> Response[str]:
    """
    Update the action package dependencies (package.yaml) for
    a specified action package.

    Args:
        action_package_name: The name of the action package.
        action_package_dependencies_code: The YAML content to
            write into the package.yaml file.

    Returns:
        A success message.
    """

    package_yaml_path = os.path.join(
        os.path.expanduser("~"),
        "actions_bootstrapper",
        action_package_name,
        "package.yaml",
    )

    package_yaml = open(package_yaml_path, "w")
    try:
        package_yaml.write(action_package_dependencies_code)
    finally:
        package_yaml.close()

    return Response(
        result=f"Successfully updated the package dependencies at: {package_yaml_path}"
    )


@action
def update_action_package_action_dev_data(
    action_package_name: str,
    action_package_action_name: str,
    action_package_dev_data: str,
) -> Response[str]:
    """
    Update the action package dev data for a specified action package.

    Args:
        action_package_name: The name of the action package.
        action_package_action_name: The name of the action for which the devdata is intended
        action_package_dev_data: The JSON content to write into the dev data for this specific action

    Returns:
        Whether the dev data was successfully updated or not.

    """

    full_action_path = get_action_package_path(action_package_name)

    dev_data_path = os.path.join(full_action_path, "devdata")

    os.makedirs(dev_data_path, exist_ok=True)

    file_name = f"input_{action_package_action_name}.json"
    file_path = os.path.join(dev_data_path, file_name)

    with open(file_path, "w") as file:
        try:
            file.write(action_package_dev_data)
        finally:
            file.close()

    return Response(
        result=f"dev data for {action_package_action_name} in the action package {action_package_name} successfully created!"
    )


@action
def start_action_server(action_package_name: str, secrets: str) -> str:
    """
    This action starts the bootstrapped action package.

    Args:
        action_package_name: Name of the action package
        secrets: A JSON dictionary where each key is the secret name and the value is the secret value

    Returns:
        The address of the running action package.
    """

    print(f"Starting action server for package: {action_package_name}")

    full_action_path = get_action_package_path(action_package_name)
    print(f"Full action package path: {full_action_path}")

    if not os.path.exists(full_action_path):
        print(f"Action package '{full_action_path}' does not exist.")
        return f"Action package '{full_action_path}' does not exist."

    start_port = 8080
    available_port = find_available_port(start_port)
    print(f"Found available port: {available_port}")

    # Command to start the server using the script
    script_path = Path(__file__).parent / "start_action_server.py"
    start_command = [
        sys.executable,
        str(script_path),
        str(full_action_path),
        str(available_port),
        secrets,
    ]
    print(f"Start command: {start_command}")

    process = subprocess.Popen(
        start_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    print("Subprocess started.")

    timeout = 60
    start_time = time.time()
    url = f"http://localhost:{available_port}"

    time.sleep(1.0)
    log_path = Path(full_action_path) / "action_server.log"
    print(f"Log path: {log_path}")

    while True:
        if time.time() - start_time > timeout:
            stop_action_server(url)
            stdout_content = process.stdout.read().decode() if process.stdout else ""
            stderr_content = process.stderr.read().decode() if process.stderr else ""
            print("Process timed out.")
            print("Stdout:")
            print(stdout_content)
            print("Stderr:")
            print(stderr_content)
            return f"Process timed out.\n\nStdout:\n{stdout_content}\n\nStderr:\n{stderr_content}"
        if log_path.exists():
            with open(log_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if url in line:
                        print(f"Action Server started at {url}")
                        return f"Action Server started at {url}"
                    if "Error executing action-server" in line:
                        stdout_content = (
                            process.stdout.read().decode() if process.stdout else ""
                        )
                        stderr_content = (
                            process.stderr.read().decode() if process.stderr else ""
                        )
                        print("Failed to start.")
                        print("Stdout:")
                        print(stdout_content)
                        print("Stderr:")
                        print(stderr_content)
                        return f"Failed to start.\n\nStdout:\n{stdout_content}\n\nStderr:\n{stderr_content}"
        time.sleep(1.0)
        print("Process exit status: {process.poll()}")
        print("Checking log file...")


@action
def stop_action_server(action_server_url: str) -> str:
    """
    This action shutdowns the running action package.

    Args:
        action_server_url: URL of the running action package

    Returns:
        Whether the shutdown was successful or not
    """

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = sema4ai_http.post(
            f"{action_server_url}/api/shutdown", headers=headers
        )
    except ConnectionError:
        return "Could not connect to the server"

    if response.status_code == 200:
        return "Successfully shutdown the action server"
    else:
        print("POST request failed.")
        print("Status code:", response.status_code)
        print("Response content:", response.text)
        return "Failed to stop the action server"


@action
def update_action_code(action_package_name: str, action_code: str) -> Response[str]:
    """
    Replaces actions.py content with the provided input.

    Args:
        action_package_name: The directory for the action to update
        action_code: The source code to place into the actions.py

    Returns:
        A success message.
    """

    # Format the code using black
    formatted_code = black.format_str(action_code, mode=black.FileMode())

    actions_py_path = os.path.join(
        os.path.expanduser("~"),
        "actions_bootstrapper",
        action_package_name,
        "actions.py",
    )

    actions_py = open(actions_py_path, "w")
    try:
        actions_py.write(formatted_code)
    finally:
        actions_py.close()

    return Response(result=f"Successfully updated the actions at {actions_py_path}")


@action
def open_action_code(action_package_name: str) -> str:
    """
    This action opens the code of the action package with VSCode.

    Args:
        action_package_name: Name of the action package

    Returns:
        A message indicating success or detailed error information.
    """

    full_action_path = get_action_package_path(action_package_name)

    if not os.path.exists(full_action_path):
        return f"Error: Action package '{action_package_name}' does not exist at path {full_action_path}."

    command = ["code", full_action_path]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return (
            f"Error: Failed to open the action package '{action_package_name}' with VSCode. "
            f"Subprocess returned non-zero exit status {e.returncode}. "
            "Ensure VSCode is installed and the 'code' command is available in your PATH."
        )
    except FileNotFoundError:
        return (
            "Error: 'code' command not found. "
            "Ensure VSCode is installed and the 'code' command is available in your PATH."
        )
    except Exception as e:
        return f"Unexpected error: {str(e)}. " "Please check your setup and try again."

    return f"{action_package_name} code opened with VSCode."


@action
def get_action_run_logs(action_server_url: str, run_id: str) -> Response[str]:
    """
    Returns action run logs in plain text by requesting them from the
    provided action server URL.

    Args:
        action_server_url: The URL (base path) to the action server.
        run_id: The ID of the run to fetch logs for.

    Returns:
        The plain text from the output logs of the run.
    """

    artifact = "__action_server_output.txt"

    target_url = urllib.parse.urljoin(
        action_server_url,
        f"/api/runs/{run_id}/artifacts/text-content?artifact_names={artifact}",
    )

    response = sema4ai_http.get(target_url)

    payload = response.json()
    output = payload[artifact]

    return Response(result=output)


@action
def get_action_run_logs_latest(action_server_url: str) -> Response[str]:
    """
    Returns action run logs in plain text by requesting them from the
    provided action server URL. Requests the latest run's logs.

    Args:
        action_server_url: The URL (base path) to the action server.

    Returns:
        The plain text from the output logs of the run.
    """

    runs_list_url = urllib.parse.urljoin(action_server_url, "/api/runs")

    runs_response = sema4ai_http.get(runs_list_url)
    runs_payload = runs_response.json()

    last_run = runs_payload[-1]

    return Response(result=get_action_run_logs(action_server_url, last_run["id"]))


@action
def get_file_contents(action_package_name: str, file_name: str = "actions.py") -> Response[str]:
    """
    Return the contents of a file in the action package directory (default: actions.py).
    Args:
        action_package_name: Name of the action package (directory under actions_bootstrapper)
        file_name: Name of the file to read (default: actions.py)
    Returns:
        Response with file contents or error if not found
    """
    file_path = os.path.join(
        os.path.expanduser("~"),
        "actions_bootstrapper",
        action_package_name,
        file_name,
    )
    if not os.path.exists(file_path):
        return Response(error=f"File not found: {file_path}")
    try:
        with open(file_path, "r") as f:
            contents = f.read()
        return Response(result=contents)
    except Exception as e:
        return Response(error=f"Error reading file: {e}")
