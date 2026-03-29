# LeninKart Platform Architecture Master

## 1. Overview

## Quick Reference

### Repo Summary

| Repo | Branch | Role | Owns | Does Not Own |
| --- | --- | --- | --- | --- |
| `deployment-poc` | `main` | Deployment control plane | Jira orchestration, version resolution, GitOps writes, deployment state, rollback, Jira feedback | Image builds, business logic, service runtime code |
| `leninkart-infra` | `dev` | GitOps source of truth | ArgoCD apps, Helm values, platform manifests, runtime desired state | CI image publishing, Jira orchestration, deployment decisions |
| `leninkart-frontend` | `dev` | Frontend service | UI code, Docker build, latest-tag metadata publish | GitOps writes, ArgoCD deployment control |
| `leninkart-product-service` | `dev` | Product API service | Product backend code, Docker build, latest-tag metadata publish | GitOps writes, deployment orchestration |
| `leninkart-order-service` | `dev` | Order API service | Order backend code, Docker build, latest-tag metadata publish | GitOps writes, deployment orchestration |
| `kafka-platform` | `main` | External messaging runtime | Docker Compose Kafka runtime, topic bootstrapping, Kafka JMX metrics | Kubernetes GitOps rollout control, service CI |
| `observability-stack` | `main` | Observability bootstrap workspace | Generated Grafana/Prometheus/Loki/Tempo/Promtail values, alerting and dashboard bootstrap | Application deployment orchestration, image builds |
| `project-validation` | `main` | Validation and evidence layer | Playwright validation, GitOps/ArgoCD proof, observability proof, reports | Deployment decision-making, GitOps writes, image builds |

### Quick Flow

```text
Service CI -> latest_tags.yaml -> Jira ticket -> deployment-poc -> leninkart-infra -> ArgoCD -> validation -> observability -> success or rollback
```

LeninKart is a local, GitOps-driven platform for building, deploying, validating, and observing a small multi-service e-commerce system. It combines application repositories, a separate deployment control plane, a GitOps infrastructure repository, Kubernetes runtime services, an external Kafka runtime, an observability bootstrap workspace, and a validation/evidence layer.

The platform solves a specific operational problem: it separates build concerns from deployment concerns. Service repositories produce deployable images and latest-tag metadata. A dedicated control-plane repository (`deployment-poc`) owns deployment orchestration, GitOps writes, Jira lifecycle feedback, safety controls, and rollback. `leninkart-infra` remains the single desired-state source of truth for the dev environment, and ArgoCD is responsible for reconciling that desired state into the live cluster.

At a high level, the platform works like this:

1. A developer commits to a service repository on `dev`.
2. Service CI builds and pushes a Docker image.
3. Service CI publishes the latest built tag into `deployment-poc/config/latest_tags.yaml`.
4. An operator raises a Jira ticket in the `SCRUM` project.
5. The `deployment-poc` GitHub Actions workflow is started manually with that ticket key.
6. The deployment control plane resolves the exact target version, writes the GitOps values file in `leninkart-infra/dev`, and waits for ArgoCD reconciliation.
7. Jira receives progress and final feedback.
8. `project-validation` proves the run end-to-end with browser evidence, GitOps proof, ArgoCD proof, application proof, observability proof, and reports.
9. If deployment verification fails after a new GitOps change, `deployment-poc` automatically restores the last known-good GitOps state and lets ArgoCD reconcile the rollback.

## 2. Complete System Flow (End-to-End)

The current implemented flow is:

1. **Developer commits code**
   - Developers commit application changes to the `dev` branch of `leninkart-frontend`, `leninkart-product-service`, or `leninkart-order-service`.
   - Those repos are intentionally where application change velocity happens for the dev environment.

2. **Service CI runs**
   - Each service repo has a GitHub Actions CI workflow triggered by `push` on `dev`, `staging`, and `main`, and by `workflow_dispatch`.
   - The current dev path is branch-aware; `dev` maps metadata publication to the `dev` environment.

3. **Docker image is built and pushed**
   - Frontend CI builds and pushes `leninfitfreak/frontend:<github.run_id>`.
   - Product-service CI builds and pushes `leninfitfreak/product-service:<github.run_id>`.
   - Order-service CI builds and pushes `leninfitfreak/order-service:<github.run_id>`.
   - The generated tag is deterministic per workflow run because it uses the GitHub run id.

4. **`latest_tags.yaml` is updated**
   - After image publish, the service CI workflow checks out `deployment-poc` on `main` using `secrets.PAT_TOKEN`.
   - It updates `deployment-poc/config/latest_tags.yaml` with:
     - service key
     - environment key
     - `latest`
     - image repository
     - `updated_at`
     - source repo
     - source branch
   - This is the shared metadata contract between CI and the deployment control plane.

5. **A Jira ticket is created**
   - A deployment request is raised in the `SCRUM` project in the LeninKart Platform workspace.
   - The current model is still explicit and operator-driven. Ticket creation alone does not auto-start deployment.

6. **`deployment-poc` is triggered**
   - The GitHub Actions workflow `deployment-poc/.github/workflows/deploy-from-jira.yml` is started via `workflow_dispatch`.
   - The ticket key is passed in as input.
   - The workflow runs on the Windows self-hosted runner with labels:
     - `self-hosted`
     - `Windows`
     - `X64`
     - `leninkart`
     - `local`
     - `dev`

7. **Version is resolved**
   - `src.orchestrator` fetches the Jira issue.
   - Ticket description fields are parsed through `config/jira_field_mapping.yaml`.
   - `src.target_resolver.resolve_target()` resolves:
     - app key
     - environment
     - values file path
     - ArgoCD app
     - namespace
     - ingress URL
   - Version resolution order is:
     1. `latest` / `latest-dev` -> `config/latest_tags.yaml`
     2. alias like `v1` / `v2` -> `config/app_mapping.yaml`
     3. any other value -> explicit tag

8. **GitOps update happens in `leninkart-infra`**
   - `src.gitops_repo.GitOpsRepoManager` clones `leninkart-infra` on the target branch.
   - For dev deployments, the target branch is `dev`.
   - The exact target `values-dev.yaml` is updated with the resolved image tag.
   - The control plane commits and pushes that change using `PAT_TOKEN`.

9. **ArgoCD syncs the GitOps state**
   - ArgoCD watches `leninkart-infra` and the root app `leninkart-root` points at `argocd/applications/dev` on branch `dev`.
   - `deployment-poc` waits until the target child app reaches `Synced` and `Healthy`.
   - If an explicit GitOps commit was pushed, the orchestrator verifies that ArgoCD is on that exact revision.

10. **Kubernetes deploys the runtime change**
   - The target Kubernetes app in the `dev` namespace rolls forward to the new image tag.
   - Supporting platform services such as ingress, Vault, External Secrets, Postgres, and observability remain under the same GitOps model.

11. **Validation runs**
   - `project-validation` can validate the deployment path and also the user-facing platform behavior.
   - It checks CI proof, latest-tag metadata, deployment workflow state, GitOps state, ArgoCD state, application user flow, and observability proof.

12. **Observability proof is captured**
   - Grafana, Prometheus, Loki, Tempo, and Kafka-related telemetry proof are captured where configured.
   - Observability is treated as platform evidence, not as optional decoration.

13. **Jira receives updates**
   - Jira gets stage-wise comments such as:
     - `workflow_triggered`
     - `jira_validated`
     - `target_resolved`
     - `lock_acquired`
     - `gitops_commit_pushed`
     - `argocd_sync_started`
     - `argocd_synced_healthy`
     - `post_checks_completed`
     - `completed`
     - failure and rollback stages when relevant
   - Final result feedback is added after the run.

14. **Success or rollback**
   - On success, state is recorded as successful and Jira receives success feedback.
   - On failure after a new deployment attempt, the control plane can automatically restore the previous known-good version by writing the old tag back into GitOps and waiting for ArgoCD to reconcile it.

## 3. Repository Responsibilities

### `deployment-poc` (`main`)
- role: deployment control plane
- responsibilities:
  - Jira ticket ingestion and parsing
  - target resolution
  - version resolution
  - GitOps updates to `leninkart-infra`
  - ArgoCD verification
  - deployment state tracking
  - lock management and stale-lock recovery
  - Jira progress comments and final result feedback
  - policy-driven automatic rollback
  - deployment reports and artifacts
- does **not**:
  - build service images
  - run service business logic
  - own runtime application manifests directly

### `leninkart-infra` (`dev`)
- role: GitOps source of truth for the dev environment
- responsibilities:
  - ArgoCD app-of-apps definitions
  - Helm values for deployable applications
  - platform support workloads
  - observability app values under GitOps
  - Vault / External Secrets / ingress / Postgres manifests
- does **not**:
  - resolve Jira intent
  - decide which version should be deployed
  - run CI image builds

### `leninkart-frontend` (`dev`)
- role: web UI service
- responsibilities:
  - frontend application code
  - frontend Docker image build and push
  - latest-tag metadata publication to `deployment-poc`
- does **not**:
  - update `leninkart-infra`
  - deploy directly to Kubernetes
  - own deployment orchestration

### `leninkart-product-service` (`dev`)
- role: product API service
- responsibilities:
  - product domain backend logic
  - service image build and push
  - latest-tag metadata publication
  - OpenTelemetry agent packaging in build context
- does **not**:
  - modify GitOps manifests directly
  - trigger ArgoCD deployment directly

### `leninkart-order-service` (`dev`)
- role: order API service
- responsibilities:
  - order domain backend logic
  - service image build and push
  - latest-tag metadata publication
  - OpenTelemetry agent packaging in build context
- does **not**:
  - update GitOps manifests directly
  - own deployment control-plane logic

### `kafka-platform` (`main`)
- role: external messaging runtime
- responsibilities:
  - single-node Kafka KRaft runtime via Docker Compose
  - Kafka listener on `9092`
  - JMX exporter on `7071`
  - topic bootstrapping helper script
  - network bridge into the observability network
- does **not**:
  - run inside the Kubernetes cluster
  - participate in GitOps delivery for app version rollout

### `observability-stack` (`main`)
- role: observability bootstrap and values generation workspace
- responsibilities:
  - generate Grafana, Prometheus, Loki, Tempo, and Promtail values
  - validate Prometheus and Loki queries before generating dashboards
  - generate Grafana alerting and contact points
  - ensure the Grafana admin secret path exists in Vault
  - write generated values back into `leninkart-infra/observability/*/values-dev.yaml`
- does **not**:
  - directly deploy runtime apps itself
  - own application business logic
- note:
  - in this workspace, the visible tracked content is `observability-stack/bootstrap`, which is the active observability authoring area

### `project-validation` (`main`)
- role: validation and evidence layer
- responsibilities:
  - run modular browser and infrastructure validation suites
  - verify deployment flow, GitOps state, ArgoCD state, Vault, messaging, application flow, and observability
  - capture screenshot evidence
  - generate MkDocs-ready reports and artifact bundles
- does **not**:
  - decide deployment versions
  - build application images
  - own cluster desired state

## 4. Deployment Flow (Detailed)

### Jira -> `deployment-poc`

The deployment request starts with a Jira issue whose description contains structured deployment metadata. `deployment-poc` fetches the issue through the Jira API and parses fields using aliases defined in `config/jira_field_mapping.yaml`.

Current required description fields are:
- `app`
- `env`
- `version`

Optional fields include:
- `component`
- `url`

### Version resolution logic

`src.target_resolver._resolve_version()` applies the real resolution order used today:

1. **Latest aliases**
   - `latest`
   - `latest-dev`
   - configured in `config/global.yaml`
   - resolved from `config/latest_tags.yaml`
2. **App-specific aliases**
   - for example `v1` and `v2`
   - defined per app and environment in `config/app_mapping.yaml`
3. **Explicit tag**
   - any other provided version string is treated as the image tag itself

The resolved target carries additional metadata such as:
- `version_source`
- `version_reference`
- `image_repository`
- `latest_tag_updated_at`
- `latest_tag_environment`

### GitOps commit

`src.gitops_repo.GitOpsRepoManager` clones the GitOps repo, updates the target values file, commits the change, rebases, and pushes. It requires `PAT_TOKEN` and refuses to proceed without it. The control plane remains the only writer of deployment version changes in `leninkart-infra`.

### ArgoCD behavior

ArgoCD is configured with:
- root app: `leninkart-root`
- repo URL: `https://github.com/Leninfitfreak/leninkart-infra.git`
- target revision: `dev`
- source path: `argocd/applications/dev`

For the target child app, the orchestrator waits for:
- `Sync = Synced`
- `Health = Healthy`
- expected revision match when a new commit was pushed

If the requested version is already present in the target values file, the orchestrator may run as:
- `already_deployed`
- `reconciled`
- `rollback_skipped`

That is an intentional idempotency feature, not a silent skip.

## 5. Rollback Flow (New Feature)

The current deployment control plane implements automatic rollback through GitOps state restoration. It does **not** depend on manual ArgoCD UI rollback.

### Failure detection

Failure is detected when critical verification fails after the deployment attempt, including:
- ArgoCD not reaching the expected healthy state
- post-deployment URL validation failing in `src.postchecks`
- other `PocError` conditions raised during the deployment attempt

### Previous stable version tracking

`src.state_manager.DeploymentStateManager` maintains `config/deployment_state.yaml` in `deployment-poc`. For each project/app/environment, it records:
- last deployed version
- last requested version
- last GitOps commit
- last Jira ticket
- last status
- last action
- sync and health summary
- previous successful version and commit
- rollback source version when relevant

This stored successful state is what the rollback path uses as the rollback target.

### Rollback execution path

When a deployment attempt fails, `src.orchestrator.attempt_automatic_rollback()`:
1. checks whether automatic rollback is enabled in `config/deployment_policy.yaml`
2. confirms this is not test mode and not manual rollback mode
3. loads the previous stable version from state
4. writes that previous version back into the same `values-dev.yaml`
5. commits and pushes a rollback GitOps commit
6. optionally forces ArgoCD sync
7. waits until ArgoCD reaches `Synced` and `Healthy` on the rollback commit

### Jira rollback lifecycle

Rollback-aware Jira stages in `config/global.yaml` are:
- `rollback_started`
- `rollback_completed`
- `rollback_failed`

Final Jira comments include:
- requested deployment version
- failed attempted version
- reverted stable version
- rollback trigger reason
- rollback GitOps commit
- final ArgoCD state

A rollback-successful deployment is still treated semantically as a deployment failure with recovery, not as a normal clean success. The feedback mode becomes `rolled_back`, and the ticket is moved to a failure/review-compatible state rather than a normal Done state.

## 6. Versioning System

### How tags are generated

Service CI uses the GitHub Actions run id as the image tag. This gives a deterministic, unique, sortable deployment identifier without requiring a separate release service.

Examples:
- frontend -> `23701721483`
- product-service -> `23701741505`
- order-service -> `23702948455`

### Friendly versions

Supported Jira-facing values include:
- `latest`
- `latest-dev`
- explicit tags such as `23701741505`
- aliases like `v1` and `v2`

### How metadata is used

`deployment-poc/config/latest_tags.yaml` stores the latest built tag per service and per environment. Each entry contains:
- `latest`
- `image`
- `updated_at`
- `source_repo`
- `source_branch`

The deployment control plane uses this metadata only for version resolution. It does not treat the metadata file as deployment state. Deployment state continues to live in GitOps and in the deployment state ledger.

## 7. Secrets Management

The current secrets path is Vault-centric and bridged into Kubernetes through External Secrets.

### Core components
- Vault runtime in the `vault` namespace
- External Secrets Operator in `external-secrets-system`
- `ClusterSecretStore` named `vault-backend`
- application `ExternalSecret` resources under `leninkart-infra/platform/external-secrets/applications`

### How apps consume secrets

Application values files enable Vault-backed secret consumption, for example:
- `product-service` values define:
  - `dbSecretName: product-service-db-secret`
  - `configSecretName: product-service-config-secret`
- `order-service` values define:
  - `dbSecretName: order-service-db-secret`
  - `configSecretName: order-service-config-secret`

The corresponding Helm templates mount these Kubernetes secrets into the deployment as environment sources. The application pods do not talk to Vault directly. Vault is the secret origin, External Secrets is the synchronization bridge, and Kubernetes Secret objects are the runtime consumption format.

### Security model

- secret values originate in Vault paths such as `secret/leninkart/...`
- a Kubernetes-authenticated `ClusterSecretStore` bridges Vault into the cluster
- applications consume only synchronized Kubernetes secrets
- validation captures safe path inventory and secret engine structure without exposing secret values

## 8. Observability

The platform currently uses a Grafana + Prometheus + Loki + Tempo + Promtail model, with Kafka metrics also exposed.

### Observability bootstrap

`observability-stack/bootstrap` generates values files and related configuration for:
- Grafana
- Prometheus
- Loki
- Tempo
- Promtail

It validates dashboards and alert expressions before writing values into `leninkart-infra/observability/*/values-dev.yaml`.

### Metrics
- Prometheus scrapes service metrics endpoints such as `/actuator/prometheus`
- Kafka exports metrics via JMX exporter on port `7071`
- service values include Prometheus scrape annotations

### Logs
- Promtail ships logs to Loki
- Grafana Explore is used as the main UI proof path for logs

### Traces
- Product-service and order-service include OTLP-related environment variables pointing to Tempo
- Grafana is configured with a Tempo datasource when enabled

### Kafka observability

Kafka runs outside the cluster in Docker Compose, but it is still part of the observability story:
- broker port `9092`
- JMX exporter port `7071`
- metrics are available for Prometheus/Grafana consumption
- the Kafka container joins the external `signoz-net` network

## 9. Validation System

`project-validation` is a modular validation and evidence framework rather than a single script.

### What it validates
- application user journey
- deployment workflow proof
- latest-tag metadata proof
- GitOps proof
- ArgoCD proof
- Vault proof
- messaging proof
- observability proof

### Application proof

The app validation flow uses Playwright to perform a real user-like path:
- open frontend
- sign up a fresh user
- log in
- verify the dashboard
- browse and create product state where required by the existing flow
- buy a product
- verify order ledger and user activity

### Deployment proof

The deployment validation flow verifies:
- the service CI run that published latest-tag metadata
- the GitHub Actions deployment run
- the deployment result artifact
- the GitOps commit page
- ArgoCD state
- Jira lifecycle through API-backed evidence

### Evidence model
- final screenshots are stored under `screenshots/`
- reports are written under `docs/`
- machine-readable summaries are stored under `artifacts/`
- validation-output packages bundle the latest run

## 10. CI/CD Model

The platform intentionally splits CI and CD responsibilities.

### Service repositories = CI only
Service repos own:
- application build
- quality checks
- Docker image push
- latest-tag metadata publication

Service repos do **not**:
- update `leninkart-infra`
- choose deployment targets
- trigger ArgoCD
- own Jira deployment orchestration

### `deployment-poc` = CD only
`deployment-poc` owns:
- Jira-driven deployment intent
- version resolution
- GitOps updates
- ArgoCD verification
- lock and state safety
- Jira lifecycle feedback
- rollback

This separation is the core architectural boundary of the system.

## 11. Design Principles

### Separation of concerns
Application repos stay application-focused. Deployment logic is centralized in the control plane.

### GitOps as the operating model
The live dev environment is driven by the Git state in `leninkart-infra/dev`, not by imperative deployment commands from service repos.

### Single source of truth
`leninkart-infra` is the desired-state source of truth for runtime deployment state. `latest_tags.yaml` is a version-resolution input, not a deployment truth source.

### Idempotency
If the requested version is already active and healthy, the deployment workflow exits cleanly without unnecessary churn.

### Safety before speed
The control plane tracks locks, previous state, stale lock recovery, final verification, and rollback. These protections exist specifically to keep the dev platform reproducible and debuggable.

## 12. Failure Scenarios

### Metadata publication failure
If a service CI run cannot push `latest_tags.yaml`, the workflow now fails instead of pretending metadata publication succeeded. This prevents stale-tag false positives in the deployment path.

### Deployment failure
If the deployment control plane pushes a new GitOps commit but the app never reaches a verified healthy state, the run fails. Depending on policy and available state, automatic rollback may restore the previous stable version.

### Rollback failure
If the deployment fails and rollback also fails, Jira receives rollback-failed feedback and manual intervention is required. This is treated as an escalated failure, not as partial success.

### Lock contention
If another deployment is already in progress for the same app/environment, the lock prevents overlapping writes. If the lock appears stale, the control plane checks the GitHub Actions run state before auto-releasing it.

### Post-check failure
Even if ArgoCD reports success, the platform can still fail the deployment if post-deployment URL validation fails. This prevents a purely control-plane-level success from masking application-level failure.

## 13. Current Limitations / Future Improvements

Current limitations visible in the real implementation:
- Jira ticket creation does not automatically trigger deployment; the current model still requires explicit `workflow_dispatch`.
- The environment model is primarily validated around `dev`; `staging` and `prod` metadata publication paths exist in CI, but the active documented GitOps runtime is dev-centric.
- Rollback currently restores the previous stable image tag in GitOps, but there is no advanced progressive-delivery mechanism such as canary or blue/green.
- Observability bootstrap is currently a separate authoring workspace rather than a fully integrated deployment pipeline.
- Jira browser MFA automation is intentionally not treated as the primary validation path; Jira lifecycle proof is API-backed.

Likely future improvements consistent with the current design:
- optional Jira webhook trigger for deployment workflow dispatch
- progressive delivery strategies
- richer automated smoke tests as deployment post-checks
- stronger staging/prod branch and policy separation
- automated release notes tied to Jira and GitOps commits

## 14. Quick Start / How to Use

### Trigger a deployment
1. Ensure the target service CI has published a fresh tag to `deployment-poc/config/latest_tags.yaml`.
2. Create a Jira ticket in project `SCRUM`.
3. Use a description like:

```text
app: product-service
env: dev
version: latest-dev
component: backend
reason: manual deployment request
```

4. Trigger `deployment-poc/.github/workflows/deploy-from-jira.yml` with the Jira ticket key.
5. Monitor Jira comments, GitHub Actions output, GitOps commit, and ArgoCD health.

### Create a Jira ticket
Use the `SCRUM` project in the LeninKart Platform workspace. Current normal examples are:
- frontend
- product-service
- order-service

### Validate the system
From `project-validation`:

```powershell
python run_validation.py
```

Focused runners are also available, for example:

```powershell
python -m validation.runners.run_app_validation
python -m validation.runners.run_infra_validation
python -m validation.runners.run_observability_validation
python -m validation.runners.run_vault_validation
```

### Access ArgoCD locally

```powershell
kubectl port-forward -n argocd svc/argocd-server 8085:443
```

Then open:
- `http://127.0.0.1:8085`

### Why branch separation exists

The current branch model is deliberate:
- `dev` branches for application repos and `leninkart-infra` hold mutable development-state work and the live dev desired state.
- `main` branches for `deployment-poc`, `kafka-platform`, and `project-validation` hold the more stable platform tooling, control-plane code, and validation framework.

This keeps the application delivery surface separated from the control-plane/tooling surface while still allowing the dev environment to move quickly.
