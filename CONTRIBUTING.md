# Contributing to Prompt Security Fuzzer

Thank you for your interest in contributing to Prompt Security Fuzzer! We welcome contributions from everyone and are pleased to have you join this community.
This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

The Prompt Security project adheres to a code of conduct that you can read at [Code of Conduct](LINK_TO_CODE_OF_CONDUCT).
By participating in this project, you agree to abide by its terms.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.7 or later
- Git

### Setting Up Your Development Environment

1. **Fork the Repository**: Start by forking the repository on GitHub.

2. **Clone Your Fork**:
```bash
git clone https://github.com/prompt-security/ps-fuzz.git
cd ps-fuzz
```

### Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Unix or macOS
venv\Scripts\activate     # On Windows
```

### Install dependencies

Install the project dependencies in editable mode (with the '-e' argument).
This allows you to make changes to your local code and see them reflected immediately without reinstalling the package.

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Prepare environment variables and API keys

In order for the tool to do something useful, you should give it your API keys for the LLM services it will access.
By default, the tool uses OpenAI (api.openai.com) service. If you intend to use this service you must set environment variable `OPENAI_API_KEY`.
You can do it in one of two ways:
1. Directly
```bash
export OPENAI_API_KEY=sk-....
```

2. By creating a file named `.env` in current directory, with a content like this:
```
OPENAI_API_KEY=sk-....
```
The tool would automatically recognize that the file is present and will try to load the environment variables (including your API key) from it.

### Running the Tool

To run the tool from your development environment, you can use the command-line interface set up in the project.
Since the package is installed in editable mode (e.g. via `pip install -e ".[dev]"`), you can run the tool directly from the source code without
needing a separate installation step for testing changes.

To execute the tool, use the following command:
```bash
prompt-security-fuzzer --help
```

Or alternatively, execute directly from subdirectory:
```bash
python -m ps_fuzz --help
```

## Making Changes

1. Always create a new side-branch for your work.
```bash
git checkout -b your-branch-name
```

2. Make your changes to the code and add or modify unit tests as necessary.

3. Run tests again

Ensure all tests pass after your changes.
```bash
pytest
```

4. Commit Your Changes

Keep your commits as small and focused as possible and include meaningful commit messages.
```bash
git add .
git commit -m "Add a brief description of your change"
```

5. Push the changes you did to GitHub
```bash
git push origin your-branch-name
```

## Get Started with Your First Contribution: Adding a New Test

The easist way to contribute to ps-fuzz project is by creating a new test! You can see an example PR of a test here: [Contribute new test - base64_injection!](https://github.com/prompt-security/ps-fuzz/pull/19)
This can be easily acheived by:

#### 1. Create a Test File
* Navigate to the attacks directory. 
* Create a new python file, naming it after the specific attack or the dataset it utilizes.

#### 2. Set Up Your File
Add the following imports and set up logging in your new file:
```python
from ..chat_clients import ChatSession
from ..client_config import ClientConfig
from ..attack_config import AttackConfig
from ..test_base import TestBase, StatusUpdate
from ..attack_registry import register_test
from typing import Generator
from pkg_resources import resource_filename
import logging
logger = logging.getLogger(__name__)
```

#### 3. Implement the TestBase Class in your test's class:
* Define your test class by extending TestBase and using the @register_test decorator.
* Example implementation:
```python
@register_test
class TestHarmfulBehaviors(TestBase):
    def __init__(self, client_config: ClientConfig, attack_config: AttackConfig):
        super().__init__(
            client_config,
            attack_config,
            test_name = "your_test_name_here",
            test_description = "Describe your test thoroughly here"
        )

    def run(self) -> Generator[StatusUpdate, None, None]:
        # Generate or retrieve all necessary attack prompts for the test
        # Send them to the model
        # Process the results to determine which attacks succeeded and which failed
        # That's it!
```

#### 4. Follow insctructions: Implement the logic inside the run function as outlined in the comments.

#### 5. Add your attack file name to the attack loader file:
```python
from .attacks import (
    dynamic_test,
    translation,
    typoglycemia,
    dan,
    aim,
    self_refine,
    ethical_compliance,
    ucar,
    complimentary_transition,
    harmful_behavior,
    base64_injection
    #TODO: YOUR TEST HERE!
)
``` 

#### 6. Open a PR! Submit your changes for review by opening a pull request.

#### That’s all it takes to contribute a new test to the Prompt Security Fuzzer project!

## Submitting a pull request

1. Update your branch

Fetch any new changes from the base branch and rebase your branch.
```bash
git fetch origin
git rebase origin/main
```

2. Submit a Pull Request

Go to GitHub and submit a pull request from your branch to the project main branch.


3. Request Reviews

Request reviews from other contributors listed as maintainers. If you receive a feedback - make any necessary changes and push them.

4. Merge

Once your pull request is approved, it will be merged into the main branch.

## Additional Resources

Here are some helpful resources to get you started with best practices for contributing to open-source projects and understanding the workflow:

- [GitHub Flow](https://guides.github.com/introduction/flow/) - An introduction to the GitHub workflow, which explains branches, pull requests, and more.
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/) - A guide on how to write clear and concise commit messages, which are crucial for following the changes in a project.
- [Python Coding Style](https://pep8.org/) - Guidelines for writing clean and understandable Python code.

