# LeninKart Platform Portfolio

A public showcase repository for the LeninKart platform, with linked source repos, final architecture docs, curated proof assets, and validation-backed delivery evidence.

## Portfolio Note

This repository is a portfolio and landing page, not a runtime repository. The working source repos are linked separately, and this repo focuses on architecture, delivery design, validation proof, observability proof, and final curated evidence.

## One-Line Summary

LeninKart demonstrates how to separate service CI from deployment control, route deployment intent through Jira, reconcile runtime state through GitOps and ArgoCD, and prove the result with browser-based validation and observability evidence.

## Why This Platform Was Built

This project was built to solve a practical platform problem: application repositories should build deployable artifacts, but deployment control, rollout safety, rollback, and operator feedback should live in a separate control plane.

The result is a platform that is easier to reason about, safer to operate, and easier to explain to engineers, reviewers, and interviewers.

## Quick Flow

```text
Service CI -> latest_tags.yaml -> Jira ticket -> deployment-poc -> leninkart-infra -> ArgoCD -> validation -> observability -> success or rollback
```

## Architecture Overview

LeninKart is split into four major layers:

- Service layer: frontend, product-service, and order-service build and publish images on `dev`
- Control layer: `deployment-poc` on `main` resolves Jira requests, writes GitOps, tracks state, and performs rollback
- GitOps/runtime layer: `leninkart-infra` on `dev` defines desired state, and ArgoCD reconciles it into the Kubernetes cluster
- Validation/evidence layer: `project-validation` on `main` proves the workflow, application behavior, GitOps state, and observability state

Approved architecture assets:
- [Main platform architecture](architecture/leninkart-platform-architecture.png)
- [Runtime and infrastructure deep dive](architecture/leninkart-platform-runtime-deepdive-gui.png)
- [Master architecture documentation](docs/PLATFORM_ARCHITECTURE_MASTER.md)

## Deployment Flow

The deployment model is intentionally strict:

1. A developer commits to a service repo on `dev`
2. Service CI builds and pushes an image tagged with the GitHub Actions run id
3. Service CI updates `deployment-poc/config/latest_tags.yaml`
4. An operator creates a Jira ticket in `SCRUM`
5. The `deploy-from-jira` workflow is started manually with that ticket key
6. `deployment-poc` resolves `latest`, `latest-dev`, alias versions, or explicit tags
7. `deployment-poc` updates the correct `values-dev.yaml` in `leninkart-infra/dev`
8. ArgoCD reconciles the GitOps change and the control plane verifies `Synced` + `Healthy`
9. Jira receives lifecycle comments and final deployment feedback

## Automatic Rollback Flow

Rollback is GitOps-based, not UI-based.

If a deployment fails after a new version is pushed to GitOps, `deployment-poc`:
- detects the failed deployment outcome
- reads the previous known-good deployment state
- writes the previous stable tag back into the GitOps values file
- pushes a rollback commit to `leninkart-infra/dev`
- waits for ArgoCD to reconcile the rollback
- posts rollback-aware Jira feedback

This keeps `leninkart-infra` as the only deployment truth source even during recovery.

## Deployment Outcomes

### Success
- target version resolves correctly
- GitOps values are updated or verified
- ArgoCD reaches `Synced` + `Healthy`
- Jira receives completion feedback

### Already Deployed
- the requested version is already the active version
- the workflow exits cleanly after verification
- Jira still receives accurate no-op style feedback

### Failed
- the requested deployment does not reach a verified healthy state
- Jira receives failure reporting
- validation reports show the exact failure reason

### Rolled Back
- the requested deployment failed
- automatic rollback restored the previous stable GitOps state
- ArgoCD reconciled the restored version
- Jira reflects failure with recovery, not fake success

## Repository Responsibilities

| Repo | Branch | Role | Owns |
| --- | --- | --- | --- |
| `deployment-poc` | `main` | Deployment control plane | Jira orchestration, version resolution, GitOps writes, state/locks, rollback, Jira feedback |
| `leninkart-infra` | `dev` | GitOps source of truth | ArgoCD apps, Helm values, platform manifests, desired runtime state |
| `leninkart-frontend` | `dev` | Frontend service | UI code, image build, latest-tag metadata publish |
| `leninkart-product-service` | `dev` | Product service | Product API code, image build, latest-tag metadata publish |
| `leninkart-order-service` | `dev` | Order service | Order API code, image build, latest-tag metadata publish |
| `kafka-platform` | `main` | Messaging runtime | External Kafka runtime and Kafka metrics endpoint |
| `observability-stack` | `main` | Observability bootstrap | Generated Grafana/Prometheus/Loki/Tempo/Promtail values and alerting assets |
| `project-validation` | `main` | Validation layer | Browser proof, GitOps proof, ArgoCD proof, app flow proof, observability proof |

More detail:
- [Repository links and descriptions](links.md)
- [Deployment control plane deep dive](docs/DEPLOYMENT_CONTROL_PLANE.md)

## Validation and Proof

`project-validation` provides the proof layer for this platform. It validates:
- service CI proof for latest-tag publication
- deployment workflow proof
- GitOps commit proof
- ArgoCD application proof
- application user flow proof
- observability proof
- rollback proof

Key reports included here:
- [Full platform architecture master doc](docs/PLATFORM_ARCHITECTURE_MASTER.md)
- [Deployment control plane deep dive](docs/DEPLOYMENT_CONTROL_PLANE.md)
- [Final Jira-driven E2E validation report](docs/FINAL_JIRA_DRIVEN_E2E_VALIDATION_REPORT.md)
- [Final rollback validation report](docs/FINAL_ROLLBACK_VALIDATION_REPORT.md)

## Observability

The implemented observability stack is:
- Grafana
- Prometheus
- Loki
- Tempo
- Promtail
- Kafka JMX metrics integration

This repo reflects the actual code and runtime model. It does not rename the stack into a different platform story.

Observability proof included here covers:
- dashboards
- logs
- metrics targets
- traces
- Kafka-focused dashboard evidence

## Key Features

- Jira-driven deployment control plane
- strict CI/CD separation
- latest-tag metadata model for human-friendly deployment requests
- GitOps deployment through `leninkart-infra`
- ArgoCD reconciliation with verified status
- end-to-end validation with real UI proof
- observability-backed validation
- automatic GitOps rollback on deployment failure
- Jira-aware rollback reporting

## Repo Links

See [links.md](links.md) for the clean repository index.

## Screenshots / Evidence

Curated evidence in this repo:
- [CI proof](screenshots/ci/)
- [Deployment proof](screenshots/deployment/)
- [ArgoCD proof](screenshots/argocd/)
- [Application proof](screenshots/application/)
- [Observability proof](screenshots/observability/)
- [Secrets proof](screenshots/secrets/)
- [Messaging proof](screenshots/messaging/)

## What This Demonstrates as an Engineer

This portfolio shows practical engineering work across:
- platform architecture and separation of concerns
- GitOps-based deployment design
- deployment safety, idempotency, and rollback
- Jira-integrated operational workflows
- validation systems that produce real evidence instead of hand-wavy claims
- observability integration as part of deployment confidence

## Future Improvements

The current platform is intentionally realistic rather than overbuilt. Natural next steps include:
- automatic Jira-to-workflow trigger instead of manual `workflow_dispatch`
- progressive delivery strategies such as canary or blue/green
- richer deployment smoke tests in the control plane
- stronger staging and production environment separation
- more compact public deployment-flow diagram assets
