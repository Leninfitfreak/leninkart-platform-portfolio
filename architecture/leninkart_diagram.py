from pathlib import Path
import os

import requests
from cairosvg import svg2png
from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.generic.blank import Blank

ROOT = Path(__file__).resolve().parent
ICONS = ROOT / "icons"
MODERN_ASSETS = ROOT.parent / "leninkart-platform-portfolio" / "architecture" / "modern-assets"
GRAPHVIZ_BIN = Path(r"C:\Program Files\Graphviz\bin")

ICON_SOURCES = {
    "kubernetes": [
        "https://raw.githubusercontent.com/kubernetes/kubernetes/master/logo/logo.png",
        "https://cdn.simpleicons.org/kubernetes",
        str(MODERN_ASSETS / "kubernetes.svg"),
    ],
    "argocd": [
        "https://argo-cd.readthedocs.io/en/stable/assets/logo.png",
        "https://cdn.jsdelivr.net/gh/cncf/artwork/projects/argo/icon/color/argo-icon-color.svg",
        str(MODERN_ASSETS / "argo.svg"),
    ],
    "vault": [
        "https://cdn.simpleicons.org/vault",
        "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/vault.svg",
        str(MODERN_ASSETS / "vault.svg"),
    ],
    "kafka": [
        "https://cdn.simpleicons.org/apachekafka",
        "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/apachekafka.svg",
        str(MODERN_ASSETS / "apachekafka.svg"),
    ],
    "prometheus": [
        "https://cdn.simpleicons.org/prometheus",
        "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/prometheus.svg",
        str(MODERN_ASSETS / "prometheus.svg"),
    ],
    "grafana": [
        "https://cdn.simpleicons.org/grafana",
        "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/grafana.svg",
        str(MODERN_ASSETS / "grafana.svg"),
    ],
    "loki": [
        str(MODERN_ASSETS / "loki.png"),
    ],
    "tempo": [
        str(MODERN_ASSETS / "tempo.png"),
    ],
    "github": [
        "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        "https://cdn.simpleicons.org/github",
        str(MODERN_ASSETS / "github.svg"),
    ],
    "docker": [
        "https://cdn.simpleicons.org/docker",
        "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/docker.svg",
        str(MODERN_ASSETS / "docker.svg"),
    ],
    "postgres": [
        "https://cdn.simpleicons.org/postgresql",
        "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/postgresql.svg",
    ],
    "jira": [
        "https://cdn.simpleicons.org/jira",
        "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/jira.svg",
        str(MODERN_ASSETS / "jira.svg"),
    ],
}


def ensure_graphviz() -> None:
    current_path = os.environ.get("PATH", "")
    if GRAPHVIZ_BIN.exists() and str(GRAPHVIZ_BIN) not in current_path:
        os.environ["PATH"] = f"{GRAPHVIZ_BIN};{current_path}"


def fetch_bytes(source: str) -> bytes:
    if source.startswith("http://") or source.startswith("https://"):
        response = requests.get(source, timeout=60)
        response.raise_for_status()
        return response.content
    return Path(source).read_bytes()


def is_svg(source: str, content: bytes) -> bool:
    return source.lower().endswith(".svg") or b"<svg" in content[:512].lower()


def download_icons() -> dict[str, Path]:
    ICONS.mkdir(parents=True, exist_ok=True)
    downloaded: dict[str, Path] = {}

    for name, candidates in ICON_SOURCES.items():
        png_path = ICONS / f"{name}.png"
        if png_path.exists() and png_path.stat().st_size > 0:
            downloaded[name] = png_path
            continue

        last_error = None
        for source in candidates:
            try:
                content = fetch_bytes(source)
                if is_svg(source, content):
                    svg2png(bytestring=content, write_to=str(png_path), output_width=192, output_height=192)
                else:
                    png_path.write_bytes(content)
                downloaded[name] = png_path
                break
            except Exception as exc:
                last_error = exc
                if png_path.exists():
                    png_path.unlink(missing_ok=True)
        else:
            raise RuntimeError(f"Failed to prepare icon '{name}': {last_error}")

    return downloaded


def cicon(label: str, path: Path):
    return Custom(label, str(path))


def tnode(label: str):
    return Blank(label)


def build_diagram() -> None:
    ensure_graphviz()
    icons = download_icons()

    graph_attr = {
        "splines": "ortho",
        "nodesep": "0.45",
        "ranksep": "0.70",
        "pad": "0.40",
        "margin": "0.22",
        "fontsize": "20",
        "fontname": "Segoe UI",
        "labelloc": "t",
        "labeljust": "c",
        "compound": "true",
        "newrank": "true",
        "dpi": "220",
    }
    node_attr = {
        "shape": "box",
        "style": "rounded",
        "fontsize": "12",
        "fontname": "Segoe UI",
    }
    edge_attr = {
        "fontsize": "10",
        "fontname": "Segoe UI",
        "penwidth": "1.3",
    }

    with Diagram(
        "LeninKart Platform",
        direction="TB",
        filename=str(ROOT / "leninkart_devops_platform"),
        outformat=["png", "svg"],
        show=False,
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        with Cluster("Request Layer"):
            operator = tnode("Operator")
            jira = cicon("Jira", icons["jira"])
            operator >> jira

        with Cluster("CI / Control Plane"):
            github = cicon("GitHub", icons["github"])
            security = tnode("Security Gate\nSonarQube / Trivy")
            docker = cicon("Docker Images", icons["docker"])
            runner = tnode("Runner")
            deployment_poc = tnode("deployment-poc")
            lock_manager = tnode("Lock Manager")
            jira_lifecycle = tnode("Jira Lifecycle")

            github >> Edge(label="quality") >> security >> docker
            github >> runner >> deployment_poc >> lock_manager >> jira_lifecycle

        with Cluster("GitOps"):
            infra = cicon("leninkart-infra", icons["github"])
            desired_state = tnode("Desired State")
            argocd = cicon("ArgoCD", icons["argocd"])
            infra >> desired_state >> argocd

        with Cluster("Kubernetes Runtime"):
            k8s = cicon("Kubernetes", icons["kubernetes"])
            ingress = tnode("Ingress")
            frontend = tnode("Frontend")
            product_api = tnode("Product API")
            order_api = tnode("Order API")
            postgres = cicon("Postgres", icons["postgres"])
            vault = cicon("Vault", icons["vault"])
            secrets = tnode("Secrets Store")
            traffic_generator = tnode("Traffic Generator")

            k8s >> ingress >> frontend
            ingress >> product_api
            ingress >> order_api
            [product_api, order_api] >> postgres
            vault >> Edge(style="dotted", label="secrets") >> secrets
            secrets >> Edge(style="dotted") >> product_api
            secrets >> Edge(style="dotted") >> order_api
            traffic_generator >> frontend

        with Cluster("External Systems"):
            kafka = cicon("Kafka Runtime", icons["kafka"])

        with Cluster("Validation"):
            validation_engine = tnode("Validation Engine")
            proof_scope = tnode("Proof Scope")
            validation_reports = tnode("Validation Reports")
            validation_engine >> proof_scope
            validation_engine >> validation_reports

        with Cluster("Observability"):
            prometheus = cicon("Prometheus", icons["prometheus"])
            grafana = cicon("Grafana", icons["grafana"])
            loki = cicon("Loki", icons["loki"])
            tempo = cicon("Tempo", icons["tempo"])
            prometheus >> grafana
            loki >> grafana
            tempo >> grafana

        jira >> github
        deployment_poc >> Edge(label="GitOps") >> infra
        argocd >> Edge(label="sync") >> k8s
        [product_api, order_api] >> kafka
        [k8s, kafka] >> Edge(label="validate") >> validation_engine
        validation_engine >> Edge(label="metrics") >> prometheus
        validation_engine >> Edge(label="logs") >> loki
        validation_engine >> Edge(label="traces") >> tempo
        validation_engine >> Edge(label="failure", style="dashed", color="firebrick3") >> deployment_poc
        deployment_poc >> Edge(label="Git revert", style="dashed", color="firebrick3") >> infra
        infra >> Edge(label="restore", style="dashed", color="firebrick3") >> argocd


if __name__ == "__main__":
    build_diagram()
