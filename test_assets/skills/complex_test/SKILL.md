# Complex SubAgent Test Skill

Use this skill when a request asks to test orchestration across multiple SubAgents, custom tools, memory, and final synthesis.

## Required Behavior

- Always include the marker `COMPLEX_TEST_SKILL_V1` in the final answer so the caller can confirm this skill was loaded.
- Split the work into planner, tool verifier, risk reviewer, and final synthesizer phases.
- Require at least one custom tool result from `scenario_risk_tool`.
- Require at least one custom tool result from `acceptance_matrix_tool`.
- Ask the risk reviewer to check whether the final answer proves all expected signals were observed.
- Keep the final answer concise and structured.

## Output Contract

The final answer must include these exact headings:

1. `skill_marker`
2. `subagent_trace`
3. `custom_tool_trace`
4. `risk_review`
5. `final_result`

## Test Prompt

A good manual smoke-test prompt is:

```text
请执行一次复杂编排测试：让多个子 Agent 分别规划、生成验收矩阵、识别风险并复核。测试目标是确认 SubAgent、custom tool、custom skill 都被使用。请在最终结果里说明证据。
```
