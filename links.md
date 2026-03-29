# Source Repositories

| Repository | Branch Model | Purpose | Link |
| --- | --- | --- | --- |
| deployment-poc | `main` | Jira-driven deployment control plane, GitOps writes, rollback, Jira feedback | https://github.com/Leninfitfreak/deployment-poc |
| leninkart-infra | `dev` | GitOps source of truth for the dev environment | https://github.com/Leninfitfreak/leninkart-infra |
| leninkart-frontend | `dev` | Frontend application and CI image publication | https://github.com/Leninfitfreak/leninkart-frontend |
| leninkart-product-service | `dev` | Product API service and CI image publication | https://github.com/Leninfitfreak/leninkart-product-service |
| leninkart-order-service | `dev` | Order API service and CI image publication | https://github.com/Leninfitfreak/leninkart-order-service |
| kafka-platform | `main` | External Kafka runtime and Kafka metrics exposure | https://github.com/Leninfitfreak/kafka-platform |
| observability-stack | `main` | Observability bootstrap workspace for Grafana, Prometheus, Loki, Tempo, and Promtail values | https://github.com/Leninfitfreak/observability-stack |
| project-validation | `main` | End-to-end validation, browser proof, and reporting | https://github.com/Leninfitfreak/project-validation |

Manual confirmation note:
- `observability-stack` should be manually confirmed before public sharing because the local workspace used for this portfolio exposed the active `bootstrap/` content rather than a full repo-root remote configuration.
