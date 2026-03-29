# AGENTS.md

This repository is a public-facing portfolio and landing page for the LeninKart platform.

## Purpose
- present the platform clearly for recruiters, reviewers, and collaborators
- summarize architecture, deployment flow, validation proof, and observability proof
- link to source repositories and final approved evidence

## Guardrails
- do not add secrets, tokens, passwords, internal credentials, or sensitive runtime values
- do not duplicate full source repositories into this repo
- do not turn this into a working runtime or deployment repo
- do not invent architecture that is not reflected in the real source repos
- do not replace the current GitOps/Jira-driven deployment model with a different story

## Content Rules
- prefer summaries, diagrams, links, and curated screenshots over raw implementation dumps
- preserve architecture truth:
  - service repos are CI only
  - deployment-poc is CD/control plane
  - leninkart-infra is the GitOps source of truth
  - ArgoCD reconciles GitOps changes
  - rollback is GitOps-based
- update docs and screenshots only from final approved or passing validation runs
- keep writing professional, concise, and reviewer-friendly

## Safe Update Scope
- README improvements
- curated docs under `docs/`
- curated screenshots under `screenshots/`
- repo links and architecture summaries

## Avoid
- stale failed-run screenshots presented as success proof
- raw scratch notes
- internal-only troubleshooting details unless clearly labeled as limitations
