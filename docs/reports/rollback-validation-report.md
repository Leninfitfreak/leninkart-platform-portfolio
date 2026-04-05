# Final Rollback Validation Report

## Scenario

A controlled failed deployment was triggered against the live LeninKart platform to validate the new automatic GitOps rollback path.

- Jira ticket: `SCRUM-37`
- Jira issue: `SCRUM-37` in project `SCRUM`
- Jira project: `SCRUM`
- Deployment workflow run: `23704346622`
- Workflow location: `deployment-poc / Deploy From Jira`
- Workflow conclusion: `failure`
- Target app: `product-service`
- Environment: `dev`
- Requested version: `rollback-bad-20260329b`
- Resolved attempted version: `rollback-bad-20260329b`

## Result

The requested deployment failed as expected, and the platform automatically restored the previous stable GitOps state.

- Deployment action: `auto_rolled_back`
- Overall workflow outcome: `failure`
- Failure trigger: `Timed out waiting for ArgoCD app 'dev-product-service' to reach revision 'f21562147ea3b4fe5cb8a7f7e43bad9021937899' with Sync=Synced and Health=Healthy`
- Attempted GitOps commit: `f21562147ea3b4fe5cb8a7f7e43bad9021937899`
- Target values file: `applications/product-service/helm/values-dev.yaml`
- Previous stable version: `23701741505`
- Effective live version after rollback: `23701741505`
- Rollback source version: `rollback-bad-20260329b`
- Rollback performed: `True`
- Rollback success: `True`
- Rollback commit: `805d23ac03d427d748552de499fc776f463b1786`

## ArgoCD Proof

- ArgoCD app: `dev-product-service`
- Final Sync: `Synced`
- Final Health: `Healthy`
- Final revision: `805d23ac03d427d748552de499fc776f463b1786`

This proves the platform recovered by writing the previous known-good version back into `leninkart-infra/dev` and waiting for ArgoCD to reconcile the reverted revision.

## Jira Rollback Lifecycle

The Jira issue reflected the failed deployment and rollback lifecycle.

- Final Jira status: `In Progress`
- Jira feedback mode: `rolled_back`
- Jira transition result: `success`
- Jira transition used: `In Progress`
- Jira comment added: `True`
- Posted progress stages: `workflow_triggered, jira_validated, target_resolved, lock_acquired, gitops_commit_pushed, argocd_sync_started, rollback_started, rollback_completed, failed`

Observed rollback-specific stages:

- `rollback_started`
- `rollback_completed`
- final `failed` stage with recovery detail

## Validation Verdict

`PASS`

The deployment request itself failed by design, but the automatic rollback feature worked correctly:

1. the bad tag was written to GitOps
2. ArgoCD timed out on the bad revision
3. deployment-poc pushed a rollback GitOps commit
4. ArgoCD reconciled the rollback commit to `Synced` and `Healthy`
5. Jira recorded failure plus rollback progression instead of a misleading success state

## Notes

- No new dedicated screenshot suite was generated for this rollback-specific feature pass because the live proof already came from the real Jira ticket, the real GitHub Actions run artifact, the GitOps commit history, and the final ArgoCD application state.
- The first rollback validation attempt (`SCRUM-36`) exposed a real issue in the rollback path: rollback sync was not being forced and the rollback commit was not retained on timeout. That gap was fixed before the successful proving run `SCRUM-37`.
