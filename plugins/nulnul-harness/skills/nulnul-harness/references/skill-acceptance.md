# Skill selection and follow-up cases

Use when creating or adapting a skill for a material recurring job. Extend existing acceptance evidence, not the Gate hierarchy: Setup, Natural Selection, and adoption retain activation, rollback, and live-state ownership.

Before evaluation, freeze 3-20 distinct development prompts and expected selection decisions against the exact candidate digest. Include a positive use case, a near-miss that must skip the skill, and a follow-up that retains the right context and uses it. Start from `assets/skill-cases.template.json`; replace its deliberately invalid all-zero digest with the actual frozen digest. Prompts must represent the project, not generic keyword matching.

Execute each prompt on the inspected host through the existing permitted task path. Record actual selection, the candidate digest, and the authoritative completion check, not predicted behavior. A printed capability path is not selection evidence. Check results, permissions, required fields, and follow-up behavior; preserve useful passing regressions.

```bash
python3 <skill>/scripts/workflow_delivery.py score-cases skill-cases.json observations.json
```

The observations file is a JSON list. Each observation supplies `case_id`, `candidate_digest`, boolean `used_capability`, `check_status`, and `check_id`. A counted case needs the exact frozen digest, expected use/skip decision, `check_status: "verified"`, and a 64-character lowercase hexadecimal check ID. Missing observations, malformed references, wrong selection, failed or unknown checks do not pass. Duplicate case IDs are rejected.

This scorer checks completeness, decision alignment, and reference shape only. It does not run a model, authenticate a trace, resolve a Foundation receipt, or judge answer quality. The existing acceptance owner must resolve the real immutable Foundation check and candidate linkage before granting credit. Fabricated identifiers, advisory workflow receipts, and development scores cannot replace that evidence.

Return observations to the existing task evidence owner. Route reproducible nonpass results through the Coach/proposal loop; a candidate cannot approve itself. Preserve the accepted capability until normal acceptance and live-cycle requirements pass. Topology changes also use Agent Evolution.

These exposed cases are development regressions, never sealed holdouts. Do not select candidates on a final holdout, remove passing assertions to make tests harder, or recycle retired cases. Personal/core transfer claims retain their preregistration and independent Gates.

Design input: [skill testing guidance](https://github.com/revfactory/harness/blob/cceac68ea1d0ad198ef4b7b906cd238375836387/skills/harness/references/skill-testing-guide.md). Prompt categories do not override evidence ownership or holdout rules.
