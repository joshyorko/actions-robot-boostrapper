This runbook is intended for automation engineers and Python developers embarking on Robocorp robot projects and Sema4.ai action development.

## Runbook

This runbook covers two key workflows:

1. **Robocorp Robot Lifecycle** using the RCC CLI (`rcc robot initialize`, dependency management, testing, packaging, and deployment to Control Room).
2. **Sema4.ai Action Development** within Microsoft VSCode using the Sema4.ai VSCode extension.

---

### Part A: Robocorp Robot Lifecycle (RCC CLI)

This section focuses on the RCC-driven robot lifecycle, providing necessary context and prerequisites before developing Sema4.ai actions in Part B.

**Objective**: Automate scaffolding, configuration, testing, packaging, and deployment of Robocorp robots.

#### 1. Scaffold a New Robot Project

1. List available templates:

   ```bash
   rcc robot initialize --list
   ```
2. Prompt user for:

   * **Robot name** (directory)
   * **Template** (e.g., `03-python-workitems`)
3. Initialize the robot:

   ```bash
   rcc robot initialize --template <template> --directory <robot_name>
   # or short form:
   rcc robot init -t <template> -d <robot_name>
   ```
4. Change into the project directory:

   ```bash
   cd <robot_name>
   ```

#### 2. Configure Python Dependencies

1. Ask user for extra libraries (e.g., `pandas`, `requests`).
2. For each library:

   ```bash
   rcc robot libs -a <library_name>
   ```
3. Review the updated environment:

   ```bash
   cat conda.yaml
   ```

#### 3. Open Interactive Shell for Local Edits

1. Describe that this command opens an interactive environment for editing code and configuration files.
2. Run shell:

   ```bash
   rcc task shell
   ```
3. Exit when done (`exit` or `Ctrl-D`).

#### 4. Execute Local Tests

1. Inform user of test run.
2. Run robot:

   ```bash
   rcc run
   ```
3. Execute test tasks:

   ```bash
   rcc task testrun
   ```
4. Display pass/fail summary and logs.

#### 5. Package the Robot

1. Inform packaging step.
2. Wrap robot:

   ```bash
   rcc robot wrap
   ```
3. Confirm artifact location (`./artifacts/robot_name.zip`).

#### 6. Register and Push to Control Room

1. Prompt for workspace name.
2. Register in Control Room:

   ```bash
   rcc cloud new --workspace <workspace> <robot_name>
   ```
3. Push to Control Room:

   ```bash
   rcc cloud push --workspace <workspace> <robot_name>
   ```
4. Confirm registration and push status.

#### 7. Verify Deployment

1. Ask user to log into Control Room via browser.
2. Navigate to **Robots** and locate the new robot.
3. Check version, last update time, and status.

##### Custom Robot Tasks

* Edit `robot.yaml`:

  ```yaml
  tasks:
    My Task:
      shell: python -m robot --report NONE --outputdir output --logtitle "Task log" tasks/my_task.robot
  ```
* Create `.robot` files in `tasks/` with Robot Framework syntax.

##### Best Practices

* Use descriptive names.
* Keep tasks single-purpose.
* Leverage built-in and Robocorp libraries.
* Implement robust error handling and logging.
* Use variables/config files for flexibility.

##### Error Handling

###### RCC Failures

* Capture exit code, show stderr, suggest fixes (`--force`, update `rcc`).

###### Control Room Issues

* Check network connectivity, verify workspace name & permissions, regenerate API key.

###### Dependency Conflicts

* Review `conda.yaml` for conflicting versions, suggest compatible versions, guide manual edits.

###### Test Failures

* Display detailed logs, highlight failing tests, suggest debugging steps.

---

### Part B: Sema4.ai Action Development (VSCode)

**Objective**: Create and manage Sema4.ai Actions using the VSCode extension.

#### Prerequisites

* Install the **Sema4.ai VSCode extension**: [https://marketplace.visualstudio.com/items?itemName=sema4ai.sema4ai](https://marketplace.visualstudio.com/items?itemName=sema4ai.sema4ai)

#### 1. Looking up APIs

Whenever writing an action for a specific API:

* Fetch the API docs URL with Google.
* Read and extract relevant info before coding.

#### 2. Managing Dependencies (`package.yaml`)

* If a Python dependency is needed, update or create `package.yaml` with:

  ```yaml
  name: <short_name>
  description: <brief description>
  version: 0.0.1
  documentation: <documentation_url>
  dependencies:
    conda-forge:
      - python=3.10.14
    pypi:
      - <package>=<version>
  packaging:
    exclude:
      - ./.git/**
      - ./.vscode/**
      - ./devdata/**
      - ./output/**
      - ./venv/**
      - ./**/*.pyc
      - ./**/*.zip
      - ./**/.env
  ```

#### 3. Writing Actions (`@action`)

* Use the `@action` decorator:

  ```python
  from sema4ai.actions import action, Secret
  import os

  @action
  def greeting(name: str) -> str:
      """
      Greet a user by name.

      Args:
          name (str): The user name.

      Returns:
          str: A greeting message.
      """
      return f"Hello, {name}!"
  ```
* **Supported types**: `int`, `float`, `str`, `bool`, and `Secret` (last argument).

#### 4. Using Secrets

* For sensitive data, use `Secret`:

  ```python
  @action
  def call_api(url: str, api_key: Secret = Secret.model_validate(os.getenv('API_KEY', ''))) -> str:
      key = api_key.value
      # use `key` to call the API
      return result
  ```

#### 5. Creating Test Input Data

* In `devdata/`, add `input_<function_name>.json`:

  ```json
  {
    "param1": "value1",
    "api_key": "<secret>"
  }
  ```
* Ensure keys match function argument names.

#### 6. Review Code

* Ask the user: "Any changes before gathering secrets?"
* If no secrets, skip to creating actions.

#### 7. Gather Secrets

* List all `Secret` parameters found.
* Prompt user for each secret’s value before validating.

#### 8. Creating Actions

Run these steps one at a time, confirming success:

1. **Bootstrap Action Package**

   * Inform: "Bootstrapping action package..."
   * Call: `bootstrap_action_package`
   * Retry until success before proceeding.

2. **Update Actions** (parallel, with retries up to 3 each)

   * `update_action_package_dependencies`
   * `update_action_code`
   * `update_action_package_action_dev_data`

#### 9. Review Code in VSCode

* Ask: "Open code in VSCode?"
* If yes: `open_action_code`

#### 10. Updating Action Code

* After any code change, restart action server:

  ```bash
  stop_action_server
  start_action_server
  ```

#### 11. Completing Your Work

* Ask: "Anything else I can help with?"
* If no, then `stop_action_server` and end session.
