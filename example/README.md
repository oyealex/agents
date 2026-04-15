# Example Configs

`agents.full.yaml` is a reference configuration for the YAML-only runtime configuration model.

It demonstrates:

- `settings:` as the single runtime configuration source
- Explicit `${VAR}` references for secrets only
- SQLite defaults and commented PostgreSQL switching
- API host/port/reload and CORS settings
- Multiple LLM resources with `ChatOpenAI` kwargs
- A calculator tool provider
- Inline prompts and `system_prompt_file`
- Configured `skills` and `memory` paths
- Subagents
- Built-in tool toggles
- Tool event content limits
- `create_kwargs` passthrough

Run examples:

```bash
OPENAI_API_KEY=... agents default --agent-config ./example/agents.full.yaml
OPENAI_API_KEY=... agents research_assistant --agent-config ./example/agents.full.yaml --user-id demo
OPENAI_API_KEY=... agents-api --agent default --agent-config ./example/agents.full.yaml
```

The example stores runtime data outside `example/`:

```text
data/example-agent.sqlite3
data/example-sessions/
```
