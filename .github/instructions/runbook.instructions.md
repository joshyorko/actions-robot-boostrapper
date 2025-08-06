---
applyTo: '**'
---
This runbook is intended for automation engineers and Python developers embarking on Robocorp robot projects and Sema4.ai action development.

## Runbook

This runbook covers two key workflows:

1. **Robocorp Robot Lifecycle** using Python functions from `actions.py` (e.g., `create_robot`, `list_templates`, `run_task`, etc.).
2. **Sema4.ai Action Development** within Microsoft VSCode using the Sema4.ai VSCode extension.

---

### Part A: Robocorp Robot Lifecycle (LLM Tool Calls)

This section focuses on the Robocorp robot lifecycle, but **the LLM must only call the available Python functions (actions) from `actions.py` to perform all automation. Do not use RCC CLI commands.**

**Objective**: Automate scaffolding, configuration, testing, packaging, and deployment of Robocorp robots by calling the correct Python tool functions.

#### 1. Scaffold a New Robot Project

1. List available templates:
   - Call `list_templates()`
2. Prompt user for:
   - **Robot name** (directory)
   - **Template** (e.g., `03-python-workitems`)
3. Initialize the robot:
   - Call `create_robot(template, directory)`
4. (Optional) Pull a robot from GitHub:
   - Call `pull_robot(owner_repo, directory)`

#### 2. Configure Python Dependencies

- (If needed) Call `robot_dependencies()` to check dependencies.
- (If needed) Call `robot_diagnostics()` to check robot health.

#### 3. List and Run Tasks

- List available tasks:
  - Call `list_tasks()`
- Run the robot:
  - Call `run_robot()`
- Run a specific task:
  - Call `run_task(task_name)`
- Run test tasks:
  - Call `task_testrun()`

#### 4. Package and Unwrap Robot

- Package the robot:
  - Call `wrap_robot()`
- Unwrap a robot artifact:
  - Call `unwrap_robot(artifact)`

#### 5. Documentation and Help

- Show documentation:
  - Call `docs_list()`
- Show recipes:
  - Call `docs_recipes()`
- Show changelog:
  - Call `docs_changelog()`
- Show help:
  - Call `help()`

#### 6. Best Practices

- Use descriptive names for robots and tasks.
- Keep tasks single-purpose.
- Use error handling and logging in your robot code.
- Use variables/config files for flexibility.

#### 7. Error Handling

- If a function call fails, capture the error and suggest next steps or retries.
- For dependency or diagnostics issues, call `robot_dependencies()` or `robot_diagnostics()` and report the results.



#### 8. Updating robot.yaml and conda.yaml

- When creating or updating a robot ensure all 'Tasks' are added to the `robot.yaml` file.:

  ```yaml
# For more details on the format and content:
# https://github.com/robocorp/rcc/blob/master/docs/recipes.md#what-is-in-robotyaml

tasks:
  <task_name>:
    shell: python -m robocorp.tasks run tasks.py -t <task_name>

environmentConfigs:
  - environment_windows_amd64_freeze.yaml
  - environment_linux_amd64_freeze.yaml
  - environment_darwin_amd64_freeze.yaml
  - conda.yaml

artifactsDir: output

PATH:
  - .
PYTHONPATH:
  - .
ignoreFiles:
  - .gitignore

- If a Python dependency is needed for a task/robot, update or create `conda.yaml` with:

  ```yaml

channels:
  - conda-forge

dependencies:
  - python=3.12.8                 # https://pyreadiness.org/3.10
  - uv=0.6.11                     # https://github.com/astral-sh/uv
  - pip:
    - robocorp==3.0.0             # https://pypi.org/project/robocorp
    - <package>==<version>

  ```
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

* If a Python dependency is needed, update or create `package.yaml` with.:

  ```yaml
  name: <short_name>
  description: <brief description>
  version: 0.0.1
  documentation: <documentation_url>
  dependencies:
    conda-forge:
      - python=3.10.14
    pypi:
      - sema4ai-actions
      - <package>=<version>
  packaging:
    exclude:
      - ./.git/**
      - ./.vscode/**
      - ./devdata/**
      - ./output/**
      - ./venv/**
      - ./**/*.pycA
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

---

### File Management for Safe Edits

Before updating any file (such as actions.py or other code/config files), always use the `get_file_contents` action to retrieve and review the current contents. This ensures that updates are context-aware and do not overwrite existing code or comments.

**Recommended workflow for code or config updates:**
1. Use `get_file_contents` with the target file path to fetch the latest file contents.
2. Review the file and generate only the necessary changes (patch-style edits).
3. Apply the update, ensuring only the intended sections are changed and all other content is preserved.

This approach prevents accidental overwrites and supports collaborative, incremental development.
