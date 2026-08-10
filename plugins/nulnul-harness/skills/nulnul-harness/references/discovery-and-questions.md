# Discovery and questions

## Inspect first

Read only enough to answer these questions reliably:

- What does the project already do, and who appears to use it?
- What stack, commands, conventions, and deployment assumptions already exist?
- Which instructions, skills, agents, checks, and external services are already configured?
- Which prior runs, corrections, and quality measures show what works?
- What does the user's pending request change, and how can completion be observed?

Prefer repository evidence over questions. Do not ask for the language, framework, commands, or current behavior when files or safe read-only checks can reveal them.

## Ask only blockers

Ask a small batch only when the answer changes architecture, scope, safety, or the completion check. Typical blockers are:

- intended user or recurring product outcome when no reliable product evidence exists
- the first outcome that must work now when the request is too broad to implement
- a non-negotiable compatibility, time, cost, privacy, or deployment constraint
- permission to use credentials, external services, global configuration, deployment, or public writes
- a choice between materially different behaviors that the repository cannot resolve

An empty repository plus a broad request such as “build a useful app” always has a blocking product decision. Ask who the product is for and what recurring outcome it must enable. Do not resolve this with a creative default from another skill, and do not select a stack or create files before the answer.

Do not ask the user to design a harness, choose an agent count, enumerate skills, find plugins, or repeat facts already in the repository. Ask for a credential or external-service choice only after checking whether the project already records a safe choice.

## Continue safely

For helpful but non-blocking gaps, choose the narrowest reversible assumption, record it in the project contract, and proceed. If an assumption later proves wrong, update the nearest reusable rule and its regression check rather than stacking prompt exceptions.
