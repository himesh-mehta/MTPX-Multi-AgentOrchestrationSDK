# MTP Tool Call Syntax

This file is the model-facing reference for how an LLM should request tools in MTP.

## First Rule

Use the provider's native tool/function calling channel whenever the provider supports it. Do not write tool calls as normal assistant text unless the provider has failed to emit native tool calls and the adapter explicitly supports an inline fallback.

A final answer must not contain raw `<tool_call>` blocks, JSON plans, or pseudo-code tool invocations. Tool calls are for the runtime; final answers are for the user.

## Native Function Call Shape

For OpenAI-compatible providers, Groq, OpenRouter, DeepSeek, SambaNova, Cerebras, TogetherAI, FireworksAI, LM Studio, and Xiaomi, the model should emit native function calls with:

```json
{
  "name": "file.read_file",
  "arguments": {
    "path": "src/mtp/agent_os/app.py",
    "start_line": 1,
    "end_line": 120,
    "reasoning": "Read the Streamlit app before editing it."
  }
}
```

The runtime converts the provider-native call into:

```json
{
  "id": "call_1",
  "name": "file.read_file",
  "arguments": {
    "path": "src/mtp/agent_os/app.py",
    "start_line": 1,
    "end_line": 120
  },
  "depends_on": []
}
```

The `reasoning` argument is optional and should be a short decision summary. It is not private chain-of-thought. If the target tool schema does not define `reasoning`, MTP removes it before handler execution.

## Argument Rules

Tool arguments must match the advertised JSON schema exactly.

- Strings use JSON strings: `"src/main.py"`.
- Booleans use JSON booleans: `true` or `false`, not `"True"`.
- Integers and numbers use JSON numbers: `50`, not `"50"`.
- Objects and arrays must be valid JSON values.
- Use relative paths from the configured working directory unless the tool explicitly supports absolute paths.
- Do not invent parameters. Unknown parameters can cause validation failures.

Bad:

```json
{
  "name": "file.list_files",
  "arguments": {
    "path": "C:\\Users\\prajw\\Downloads\\MTP",
    "recursive": "True",
    "workdir": "C:\\Users\\prajw\\Downloads\\MTP"
  }
}
```

Good:

```json
{
  "name": "file.list_files",
  "arguments": {
    "path": ".",
    "recursive": true,
    "reasoning": "Inspect the project tree before choosing files."
  }
}
```

## Dependencies And `$ref`

When one tool needs the output of another tool, use `$ref` to refer to the prior call id.

```json
{
  "batches": [
    {
      "mode": "sequential",
      "calls": [
        {
          "id": "call_1",
          "name": "file.search_in_files",
          "arguments": {
            "pattern": "chat_input",
            "path": "src",
            "reasoning": "Find Streamlit input handling."
          }
        },
        {
          "id": "call_2",
          "name": "file.read_file",
          "arguments": {
            "path": {
              "$ref": "call_1"
            },
            "reasoning": "Read the matching file after search identifies it."
          },
          "depends_on": [
            "call_1"
          ]
        }
      ]
    }
  ]
}
```

Use parallel calls only when they are independent. Use sequential calls when later calls require earlier results.

## Inline Fallback Syntax

Inline fallback exists only to recover when a provider/model emits text instead of native tool calls. It is not the preferred syntax.

Supported fallback format:

```xml
<tool_call>
  <function=file.read_file>
    <parameter=path>src/mtp/agent_os/app.py</parameter>
    <parameter=start_line>1</parameter>
    <parameter=end_line>120</parameter>
  </function>
</tool_call>
```

MTP currently normalizes common aliases:

- `bash`, `shell`, `run_command` -> `shell.run_command`
- `read_file` -> `file.read_file`
- `write_file` -> `file.write_file`
- `list_files` -> `file.list_files`
- `search_files`, `search_in_files` -> `file.search_in_files`

The inline fallback coerces scalar values using the target schema when available. For example, `True` becomes `true` for boolean parameters. Unknown shell working-directory parameters such as `workdir` and `cwd` are dropped because `shell.run_command` already runs inside the configured tool base directory.

## Built-In Tool Examples

List files:

```json
{
  "name": "file.list_files",
  "arguments": {
    "path": ".",
    "recursive": false,
    "limit": 200,
    "reasoning": "Inspect the project root."
  }
}
```

Read a bounded file range:

```json
{
  "name": "file.read_file",
  "arguments": {
    "path": "src/mtp/agent_os/app.py",
    "start_line": 1,
    "end_line": 160,
    "reasoning": "Review current Streamlit state handling."
  }
}
```

Search files:

```json
{
  "name": "file.search_in_files",
  "arguments": {
    "pattern": "pending_prompt|chat_input|run_events",
    "path": "src",
    "max_results": 50,
    "reasoning": "Find the run loop and input handling."
  }
}
```

Write a file:

```json
{
  "name": "file.write_file",
  "arguments": {
    "path": "docs/NOTE.md",
    "content": "# Note\n\nText.\n",
    "append": false,
    "reasoning": "Create the requested documentation."
  }
}
```

Run shell command:

```json
{
  "name": "shell.run_command",
  "arguments": {
    "command": "pytest tests/test_agent_os_app.py",
    "reasoning": "Verify the Streamlit app regression tests."
  }
}
```

Run Python:

```json
{
  "name": "python.run_code",
  "arguments": {
    "code": "result = 2 + 2",
    "return_variable": "result",
    "reasoning": "Compute a small deterministic value."
  }
}
```

Terminate autoresearch:

```json
{
  "name": "agent.terminate",
  "arguments": {
    "reason": "The task is complete and tests passed.",
    "summary": "Implemented the fix and verified it with targeted tests."
  }
}
```

Use `agent.terminate` only when autoresearch mode is enabled.
