<div align="center">


# Prompt Security Fuzzer

### **Test your system prompt and make your GenAI apps safe and secure**
</div>


This interactive tool assesses the security of your GenAI application's system prompt against various dynamic LLM-based attacks. It provides a security evaluation based on the outcome of these attack simulations, enabling you to strengthen your system prompt as needed.

The Prompt Fuzzer dynamically tailors its tests to your application's unique configuration and domain.

The Fuzzer also includes a Playground chat interface, giving you the chance iteratively improve your system prompt, hardening it against a wide spectrum of generative AI attacks.

<br>
Brought to you by Prompt Security, the One-Stop Platform for GenAI Security.
<br><br>
<img src="https://assets-global.website-files.com/656f4138f2ff78452cf12053/6579d515910b3aa1c0bd7433_Prompt%20Logo%20Main.svg">

<br><br>
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/prompt-security/badge/?version=latest)](http://prompt-security-fuzzer.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://badge.fury.io/py/prompt-security.svg)](https://badge.fury.io/py/prompt-security)
![Python package](https://github.com/prompt-security/ps-fuzz/actions/workflows/tests.yml/badge.svg)

</div>


## Get started
1. Download the repository
2. Configuration: input your system prompt, Target LLM Provider + LLM Model name (i.e. the one your GenAI app is using). The default is OpenAI provider and "gpt-3.5-turbo" model.
3. Start testing
4. Test yourself with the Playground! Iterate as many times are you like until your system prompt is secure.




## Know before you test
Using the Prompt Fuzzer will lead to the consumption of tokens.

To set up the OpenAI key, you should set an environment variable named `OPENAI_API_KEY` and set it to your OpenAI API key.
An easy way to add the key permanently is to create a file named '.env' in the current directory and set the `OPENAI_API_KEY` there.
<a id="llm-providers"></a>

## Supported LLM Providers
We're fully LLM agnostic.


## Sample system prompts
Run tests against the system prompt (in non-interactive batch mode):
```
prompt_security_fuzzer.py -b ./system_prompt.examples/medium_system_prompt.txt
```

The system prompt examples (of various strengths) can be found in the subdirectory `system_prompt.examples`


<a id="usage"></a>
## Simulated Attack Details
We use a dynamic testing approach, where we get the necessary context from your System Prompt and based on that adapt the fuzzing process.

- **Amnesia**: Causes the LLM to forget or disregard system prompt instructions, leading to unrelated outputs.
- **Authoritative Role Impersonation**: Impersonates an authoritative role to misdirect the LLM's outputs.
- **Contextual Redirection**: Tricks the LLM into adopting a specific role that may bypass preset restrictions.
- **Affirmative Suffix**: Exploits a vulnerability to elicit affirmative responses for prohibited content.
- **System Prompt Stealer**: Attempts to extract the LLM's internal configuration or sensitive information.
- **Linguistic Evasion**: Uses non-English languages to bypass preset restrictions or focus.
- **Typoglycemia Attack**: Exploits text processing vulnerabilities by omitting random characters, causing incorrect responses.
- **Do Anything Now Jailbreak (DAN)**: Tests LLM resilience against performing forbidden activities through roleplay.
- **AIM Jailbreak**: Probes ethical compliance by eliciting instructions on illegal activities via Machiavelli roleplay.
- **Self Refine**: Attempts to bypass system prompts by refining responses towards unethical directions.
- **Ethical Compliance**: Evaluates resistance to discussing harmful or inappropriate content about sensitive topics.
- **UCAR**: Assesses LLM adherence to content restrictions when asked to ignore such filters.
- **Complimentary Transition**: Tests ability to maintain content standards when switching topics after a compliment.
- **Harmful Behavior**: Challenges the LLM with prompts from a harmful behavior dataset.

## What’s next on the roadmap?

- [ ]  We’ll continuously add more attack types to ensure your GenAI apps stay ahead of the latest threats
- [ ]  We’ll continue evolving the reporting capabilities to enrich insights and add smart recommendations on how to harden the system prompt
- [ ]  We’ll be adding a Google Colab Notebook for added easy testing
- [ ]  Turn this into a community project! We want this to be useful to everyone building GenAI applications. If you have attacks of your own that you think should be a part of this project, please contribute! This is how: https://github.com/prompt-security/ps-fuzz/blob/main/CONTRIBUTING.md
