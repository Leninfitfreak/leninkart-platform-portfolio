from __future__ import annotations

import base64
from pathlib import Path
import os
import re
import shutil

from PIL import Image
try:
    from cairosvg import svg2png
except Exception:
    svg2png = None
from graphviz import Digraph

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
ICONS_DIR = ROOT / "icons"
ICON_SOURCE_DIR = ROOT / "icon-sources"
MODERN_ASSETS = WORKSPACE / "leninkart-platform-portfolio" / "architecture" / "modern-assets"
PORTFOLIO_ICONS = WORKSPACE / "leninkart-platform-portfolio" / "icons"
PRODUCT_ICONS = ROOT / "icons"
GRAPHVIZ_BIN = Path(r"C:\Program Files\Graphviz\bin")

REMOTE_ICON_SOURCES = {}

LOCAL_ICON_SOURCES = {
    "jira": PORTFOLIO_ICONS / "jira.jpg",
    "github": PORTFOLIO_ICONS / "github.svg",
    "githubactions": PORTFOLIO_ICONS / "githubactions.svg",
    "docker": PORTFOLIO_ICONS / "docker.svg",
    "sonarqube": PORTFOLIO_ICONS / "sonarqube.svg",
    "gitleaks": PORTFOLIO_ICONS / "gitleaks.png",
    "trivy": PORTFOLIO_ICONS / "trivy.svg",
    "argocd": PORTFOLIO_ICONS / "argocd.svg",
    "kubernetes": PORTFOLIO_ICONS / "kubernetes.svg",
    "vault": PORTFOLIO_ICONS / "vault.svg",
    "kafka": PORTFOLIO_ICONS / "kafka.svg",
    "prometheus": PORTFOLIO_ICONS / "prometheus.svg",
    "grafana": PORTFOLIO_ICONS / "grafana.svg",
    "loki": PORTFOLIO_ICONS / "loki.png",
    "tempo": PORTFOLIO_ICONS / "tempo.jpg",
    "runner": PORTFOLIO_ICONS / "runner.png",
    "opentelemetry": PORTFOLIO_ICONS / "opentelemetry-qjp9r1tqogqgmxtl6tduv.webp",
    "orchestration": PORTFOLIO_ICONS / "orchestration.png",
    "rollback": PORTFOLIO_ICONS / "rollback.png",
    "validation": PORTFOLIO_ICONS / "validation.png",
    "lockopen": PORTFOLIO_ICONS / "lockopen.png",
    "nginx": PORTFOLIO_ICONS / "nginx.png",
    "postgres": PORTFOLIO_ICONS / "postgres.png",
    "k8s_deploy_official": PORTFOLIO_ICONS / "k8s_deploy_official.png",
    "k8s_pod_official": PORTFOLIO_ICONS / "k8s_pod_official.png",
    "k8s_svc_official": PORTFOLIO_ICONS / "k8s_svc_official.png",
}

CUSTOM_SVGS = {
    "runner_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="32" y="20" width="96" height="120" rx="18" fill="#f8fbff" stroke="#2563eb" stroke-width="6"/><rect x="48" y="40" width="64" height="18" rx="8" fill="#dbeafe"/><rect x="48" y="68" width="64" height="10" rx="5" fill="#bfdbfe"/><rect x="48" y="88" width="64" height="10" rx="5" fill="#bfdbfe"/><circle cx="80" cy="116" r="13" fill="#22c55e"/><path d="M74 116l4 4 9-10" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "orchestrator_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="24" y="24" width="112" height="112" rx="22" fill="#fffaf5" stroke="#f97316" stroke-width="6"/><circle cx="80" cy="80" r="18" fill="#ffedd5" stroke="#ea580c" stroke-width="5"/><path d="M80 70v20M70 80h20" stroke="#ea580c" stroke-width="5" stroke-linecap="round"/><circle cx="52" cy="52" r="8" fill="#fdba74"/><circle cx="108" cy="52" r="8" fill="#fdba74"/><circle cx="52" cy="108" r="8" fill="#fdba74"/><circle cx="108" cy="108" r="8" fill="#fdba74"/><path d="M60 52h16M84 52h16M52 60v40M108 60v40M60 108h16M84 108h16" stroke="#fb923c" stroke-width="4" stroke-linecap="round"/></svg>''',
    "lock_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="30" y="70" width="100" height="68" rx="18" fill="#faf5ff" stroke="#8b5cf6" stroke-width="8"/><path d="M52 70V52a28 28 0 0 1 56 0v18" fill="none" stroke="#8b5cf6" stroke-width="8" stroke-linecap="round"/><circle cx="80" cy="98" r="10" fill="#7c3aed"/><path d="M80 108v12" stroke="#7c3aed" stroke-width="8" stroke-linecap="round"/><path d="M58 34l8 8M102 34l-8 8" stroke="#c4b5fd" stroke-width="6" stroke-linecap="round"/></svg>''',
    "rollback_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><circle cx="80" cy="80" r="50" fill="#fff7f7" stroke="#dc2626" stroke-width="5"/><path d="M108 66c-8-11-22-17-36-16-18 2-33 15-38 32" fill="none" stroke="#dc2626" stroke-width="7" stroke-linecap="round"/><path d="M98 52l18 0-1 18" fill="none" stroke="#dc2626" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "step_ticket": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="26" y="36" width="108" height="88" rx="16" fill="#eff6ff" stroke="#2563eb" stroke-width="8"/><path d="M52 64h56M52 82h56M52 100h36" stroke="#2563eb" stroke-width="8" stroke-linecap="round"/></svg>''',
    "step_lock": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="34" y="72" width="92" height="58" rx="14" fill="#f5f3ff" stroke="#7c3aed" stroke-width="8"/><path d="M52 72V56a28 28 0 0 1 56 0v16" fill="none" stroke="#7c3aed" stroke-width="8" stroke-linecap="round"/></svg>''',
    "step_deploy": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 24l52 28v56l-52 28-52-28V52z" fill="#ecfccb" stroke="#65a30d" stroke-width="8"/><path d="M80 46v68M54 60l26 14 26-14" fill="none" stroke="#65a30d" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "step_sync": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><circle cx="80" cy="80" r="42" fill="#ecfeff" stroke="#0891b2" stroke-width="8"/><path d="M80 36a44 44 0 0 1 36 18" fill="none" stroke="#0891b2" stroke-width="8" stroke-linecap="round"/><path d="M112 48l8 6-6 8" fill="none" stroke="#0891b2" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/><path d="M80 124a44 44 0 0 1-36-18" fill="none" stroke="#0891b2" stroke-width="8" stroke-linecap="round"/><path d="M48 112l-8-6 6-8" fill="none" stroke="#0891b2" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "step_verify": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><circle cx="80" cy="80" r="48" fill="#ecfdf5" stroke="#16a34a" stroke-width="8"/><path d="M56 82l16 16 34-38" fill="none" stroke="#16a34a" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "step_done": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><circle cx="58" cy="80" r="30" fill="#ecfdf5" stroke="#16a34a" stroke-width="8"/><path d="M44 82l10 10 18-20" fill="none" stroke="#16a34a" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="108" cy="80" r="30" fill="#fef2f2" stroke="#dc2626" stroke-width="8"/><path d="M96 68l24 24M120 68L96 92" stroke="#dc2626" stroke-width="8" stroke-linecap="round"/></svg>''',
    "pod_frontend": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 18l50 29v58l-50 29-50-29V47z" fill="#f8fbff" stroke="#2563eb" stroke-width="8"/><rect x="50" y="54" width="60" height="42" rx="12" fill="#dbeafe" stroke="#60a5fa" stroke-width="4"/><rect x="58" y="64" width="18" height="14" rx="4" fill="#2563eb"/><rect x="84" y="64" width="18" height="14" rx="4" fill="#60a5fa"/><path d="M56 108h48" stroke="#2563eb" stroke-width="8" stroke-linecap="round"/></svg>''',
    "pod_product": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 18l50 29v58l-50 29-50-29V47z" fill="#f7fff9" stroke="#16a34a" stroke-width="8"/><rect x="50" y="54" width="60" height="42" rx="12" fill="#dcfce7" stroke="#4ade80" stroke-width="4"/><circle cx="68" cy="75" r="8" fill="#16a34a"/><circle cx="92" cy="75" r="8" fill="#22c55e"/><path d="M56 108h48" stroke="#16a34a" stroke-width="8" stroke-linecap="round"/></svg>''',
    "pod_order": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 18l50 29v58l-50 29-50-29V47z" fill="#f8faff" stroke="#4f46e5" stroke-width="8"/><rect x="50" y="54" width="60" height="42" rx="12" fill="#e0e7ff" stroke="#818cf8" stroke-width="4"/><path d="M62 72h36M62 86h22" stroke="#4f46e5" stroke-width="8" stroke-linecap="round"/><path d="M56 108h48" stroke="#4f46e5" stroke-width="8" stroke-linecap="round"/></svg>''',
    "validation_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="32" y="24" width="96" height="112" rx="18" fill="#eff6ff" stroke="#0284c7" stroke-width="8"/><rect x="50" y="18" width="60" height="20" rx="10" fill="#bae6fd" stroke="#0284c7" stroke-width="6"/><path d="M52 66h56M52 86h34" stroke="#0284c7" stroke-width="8" stroke-linecap="round"/><path d="M92 100l10 10 18-22" fill="none" stroke="#16a34a" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "report_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M44 24h58l22 22v90H44z" fill="#fffaf0" stroke="#f97316" stroke-width="6" stroke-linejoin="round"/><path d="M102 24v22h22" fill="#ffedd5" stroke="#f97316" stroke-width="6" stroke-linejoin="round"/><path d="M60 68h44M60 88h44M60 108h26" stroke="#f97316" stroke-width="6" stroke-linecap="round"/><circle cx="104" cy="110" r="14" fill="#14b8a6"/><path d="M98 110l5 5 9-11" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>''',

    "service_frontend": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 22l44 25v50l-44 25-44-25V47z" fill="#eff6ff" stroke="#2563eb" stroke-width="8"/><rect x="54" y="58" width="52" height="14" rx="7" fill="#93c5fd"/><rect x="54" y="82" width="52" height="14" rx="7" fill="#bfdbfe"/></svg>''',
    "service_product": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 22l44 25v50l-44 25-44-25V47z" fill="#f0fdf4" stroke="#16a34a" stroke-width="8"/><rect x="54" y="58" width="52" height="14" rx="7" fill="#86efac"/><rect x="54" y="82" width="52" height="14" rx="7" fill="#bbf7d0"/></svg>''',
    "service_order": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 22l44 25v50l-44 25-44-25V47z" fill="#eef2ff" stroke="#4f46e5" stroke-width="8"/><rect x="54" y="58" width="52" height="14" rx="7" fill="#a5b4fc"/><rect x="54" y="82" width="52" height="14" rx="7" fill="#c7d2fe"/></svg>''',
    "playwright_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="34" y="24" width="92" height="112" rx="18" fill="#f0fdfa" stroke="#0f766e" stroke-width="6"/><rect x="52" y="42" width="56" height="14" rx="7" fill="#ccfbf1"/><path d="M56 72h48M56 90h28" stroke="#14b8a6" stroke-width="6" stroke-linecap="round"/><circle cx="100" cy="106" r="14" fill="#14b8a6"/><path d="M94 106l5 5 8-10" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "tempo_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><circle cx="80" cy="80" r="48" fill="#fff7ed" stroke="#f97316" stroke-width="8"/><path d="M80 52v30l22 12" fill="none" stroke="#f97316" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/><path d="M44 44l14 10M116 44l-14 10" fill="none" stroke="#fb923c" stroke-width="8" stroke-linecap="round"/></svg>''',
    "yaml_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M44 24h58l22 22v90H44z" fill="#f8fafc" stroke="#64748b" stroke-width="8" stroke-linejoin="round"/><path d="M102 24v22h22" fill="#e2e8f0" stroke="#64748b" stroke-width="8" stroke-linejoin="round"/><path d="M60 70h44M60 90h44M60 110h26" stroke="#64748b" stroke-width="8" stroke-linecap="round"/></svg>''',
    "route_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="26" y="26" width="108" height="108" rx="18" fill="#f8fafc" stroke="#64748b" stroke-width="8"/><path d="M46 56h68M46 80h44M98 80h16M46 104h24M80 104h34" stroke="#64748b" stroke-width="8" stroke-linecap="round"/><circle cx="118" cy="80" r="7" fill="#2563eb"/><circle cx="70" cy="104" r="7" fill="#16a34a"/></svg>''',
    "secretstore_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="34" y="42" width="92" height="78" rx="14" fill="#f8fafc" stroke="#475569" stroke-width="8"/><path d="M54 72h52M54 94h34" stroke="#64748b" stroke-width="8" stroke-linecap="round"/><circle cx="108" cy="98" r="12" fill="#0f172a"/><path d="M108 88v20M98 98h20" stroke="#fff" stroke-width="5" stroke-linecap="round"/></svg>''',
    "externalsecrets_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="28" y="34" width="104" height="92" rx="18" fill="#f5f3ff" stroke="#7c3aed" stroke-width="8"/><path d="M48 62h44M48 84h44" stroke="#8b5cf6" stroke-width="8" stroke-linecap="round"/><path d="M104 58l12 12-12 12" fill="none" stroke="#7c3aed" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>''',
    "promtail_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="30" y="30" width="100" height="100" rx="18" fill="#f8fafc" stroke="#64748b" stroke-width="8"/><path d="M52 54v52" stroke="#64748b" stroke-width="8" stroke-linecap="round"/><path d="M76 60h36M76 82h28M76 104h20" stroke="#94a3b8" stroke-width="8" stroke-linecap="round"/></svg>''',
    "traffic_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><circle cx="54" cy="60" r="16" fill="#94a3b8"/><circle cx="108" cy="60" r="16" fill="#94a3b8"/><circle cx="81" cy="102" r="16" fill="#94a3b8"/><path d="M66 66l16 24M96 66l-12 18" stroke="#64748b" stroke-width="8" stroke-linecap="round"/></svg>''',
    "scope_custom": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="26" y="26" width="108" height="108" rx="18" fill="#fffaf0" stroke="#f59e0b" stroke-width="8"/><circle cx="62" cy="62" r="10" fill="#f59e0b"/><circle cx="98" cy="62" r="10" fill="#f59e0b"/><circle cx="62" cy="98" r="10" fill="#f59e0b"/><circle cx="98" cy="98" r="10" fill="#f59e0b"/><path d="M72 62h16M62 72v16M88 98H72M98 88V72" stroke="#f59e0b" stroke-width="7" stroke-linecap="round"/></svg>''',
    "deploy_frontend": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="30" y="34" width="84" height="62" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="8"/><rect x="46" y="52" width="84" height="62" rx="12" fill="#dbeafe" stroke="#60a5fa" stroke-width="8"/><path d="M62 70h36M62 88h26" stroke="#2563eb" stroke-width="8" stroke-linecap="round"/></svg>''',
    "deploy_product": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="30" y="34" width="84" height="62" rx="12" fill="#f0fdf4" stroke="#16a34a" stroke-width="8"/><rect x="46" y="52" width="84" height="62" rx="12" fill="#dcfce7" stroke="#4ade80" stroke-width="8"/><path d="M62 70h36M62 88h26" stroke="#16a34a" stroke-width="8" stroke-linecap="round"/></svg>''',
    "deploy_order": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><rect x="30" y="34" width="84" height="62" rx="12" fill="#eef2ff" stroke="#4f46e5" stroke-width="8"/><rect x="46" y="52" width="84" height="62" rx="12" fill="#e0e7ff" stroke="#818cf8" stroke-width="8"/><path d="M62 70h36M62 88h26" stroke="#4f46e5" stroke-width="8" stroke-linecap="round"/></svg>''',
    "pod_small_frontend": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 26l44 25v52l-44 25-44-25V51z" fill="#f8fbff" stroke="#2563eb" stroke-width="8"/><rect x="56" y="64" width="48" height="26" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="4"/></svg>''',
    "pod_small_product": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 26l44 25v52l-44 25-44-25V51z" fill="#f7fff9" stroke="#16a34a" stroke-width="8"/><rect x="56" y="64" width="48" height="26" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="4"/></svg>''',
    "pod_small_order": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><path d="M80 26l44 25v52l-44 25-44-25V51z" fill="#f8faff" stroke="#4f46e5" stroke-width="8"/><rect x="56" y="64" width="48" height="26" rx="8" fill="#e0e7ff" stroke="#818cf8" stroke-width="4"/></svg>''',
    "tempo_minimal": '''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><circle cx="80" cy="80" r="46" fill="#fff7ed" stroke="#f97316" stroke-width="6"/><circle cx="80" cy="80" r="10" fill="#fb923c"/><path d="M80 34v18M80 108v18M34 80h18M108 80h18" stroke="#f97316" stroke-width="6" stroke-linecap="round"/><path d="M80 80l18-16" stroke="#111827" stroke-width="6" stroke-linecap="round"/></svg>''',
}


def ensure_graphviz() -> None:
    current_path = os.environ.get("PATH", "")
    if GRAPHVIZ_BIN.exists() and str(GRAPHVIZ_BIN) not in current_path:
        os.environ["PATH"] = f"{GRAPHVIZ_BIN};{current_path}"


def write_custom_icons() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for name, svg in CUSTOM_SVGS.items():
        svg_path = ICONS_DIR / f"{name}.svg"
        png_path = ICONS_DIR / f"{name}.png"
        svg_path.write_text(svg, encoding="utf-8")
        if svg2png is not None:
            svg2png(bytestring=svg.encode("utf-8"), write_to=str(png_path), output_width=160, output_height=160)
            out[name] = png_path
        elif png_path.exists():
            out[name] = png_path
        else:
            out[name] = svg_path
    return out


def normalize_raster_icon(source: Path, target: Path, *, size: tuple[int, int] = (160, 160)) -> None:
    img = Image.open(source).convert("RGBA")
    # Trim near-white or transparent margins so wide local logos like Tempo remain legible.
    bg = Image.new("RGBA", img.size, (255, 255, 255, 0))
    diff = Image.new("RGBA", img.size)
    px_src = img.load()
    px_diff = diff.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px_src[x, y]
            if a == 0 or (r > 245 and g > 245 and b > 245):
                px_diff[x, y] = (0, 0, 0, 0)
            else:
                px_diff[x, y] = (255, 255, 255, 255)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)
    canvas = Image.new("RGBA", size, (255, 255, 255, 0))
    ratio = min((size[0] - 12) / img.size[0], (size[1] - 12) / img.size[1])
    new_size = (max(1, int(img.size[0] * ratio)), max(1, int(img.size[1] * ratio)))
    img = img.resize(new_size)
    pos = ((size[0] - new_size[0]) // 2, (size[1] - new_size[1]) // 2)
    canvas.alpha_composite(img, dest=pos)
    canvas.save(target, "PNG")


def ensure_icons() -> dict[str, Path]:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    icons: dict[str, Path] = {}

    for name, source in LOCAL_ICON_SOURCES.items():
        target = ICONS_DIR / f"{name}.png"
        if target.exists() and target.stat().st_size > 0:
            icons[name] = target
            continue

        suffix = source.suffix.lower()
        if suffix == ".png":
            shutil.copy2(source, target)
        elif suffix in {".jpg", ".jpeg", ".webp"}:
            normalize_raster_icon(source, target)
        elif suffix == ".svg":
            if svg2png is None:
                raise RuntimeError(f"cairosvg required for local SVG icon: {source}")
            svg2png(url=str(source), write_to=str(target), output_width=160, output_height=160)
        else:
            raise RuntimeError(f"Unsupported local icon format: {source}")
        icons[name] = target

    return icons


def embed_images_in_svg(svg_path: Path) -> None:
    if not svg_path.exists():
        return

    svg_text = svg_path.read_text(encoding='utf-8')
    pattern = re.compile(r'xlink:href="([^"]+)"')

    def replace(match: re.Match[str]) -> str:
        raw_path = match.group(1)
        if raw_path.startswith('data:'):
            return match.group(0)

        image_path = Path(raw_path)
        if not image_path.exists():
            return match.group(0)

        mime = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml',
        }.get(image_path.suffix.lower())
        if not mime:
            return match.group(0)

        encoded = base64.b64encode(image_path.read_bytes()).decode('ascii')
        return f'xlink:href="data:{mime};base64,{encoded}"'

    svg_path.write_text(pattern.sub(replace, svg_text), encoding='utf-8')


def add_icon_node(dot: Digraph, name: str, label: str, image: Path, *, subtitle: str | None = None,
                  width: str = "1.70", height: str = "1.62", fontsize: str = "12") -> None:
    full_label = label if not subtitle else f"{label}\n{subtitle}"
    dot.node(
        name,
        label=full_label,
        image=str(image),
        shape="box",
        style="rounded,filled",
        fillcolor="white",
        color="#b8c2cc",
        fontname="Segoe UI",
        fontsize=fontsize,
        labelloc="b",
        imagescale="true",
        fixedsize="true",
        width=width,
        height=height,
        margin="0.24,0.24",
        imagepos="tc",
    )


def add_box_node(dot: Digraph, name: str, label: str, *, width: str = "1.55", height: str = "0.82",
                 fontsize: str = "12", fill: str = "white") -> None:
    dot.node(
        name,
        label=label,
        shape="box",
        style="rounded,filled",
        fillcolor=fill,
        color="#b8c2cc",
        fontname="Segoe UI",
        fontsize=fontsize,
        width=width,
        height=height,
        margin="0.20,0.20",
    )


def edge(dot: Digraph, a: str, b: str, *, label: str = "", color: str = "#4b5b6b",
         style: str = "solid", penwidth: str = "1.4") -> None:
    dot.edge(a, b, label=label, color=color, style=style, penwidth=penwidth)


def add_step_badge(dot: Digraph, name: str, label: str) -> None:
    dot.node(name, label=label, shape="box", width="0.92", height="0.42", fixedsize="false", style="rounded,filled", fillcolor="#e8f1ff", color="#2f5b8a", fontname="Segoe UI Semibold", fontsize="10", margin="0.08,0.04")


def build() -> None:
    ensure_graphviz()
    icons = ensure_icons()

    dot = Digraph("LeninKartPlatformFinal")
    dot.attr(
        rankdir="TB",
        splines="ortho",
        compound="true",
        nodesep="0.80",
        ranksep="1.10",
        pad="0.45",
        bgcolor="white",
        dpi="190",
    )
    dot.attr(label="LeninKart Platform Architecture", labelloc="t", labeljust="c", fontname="Segoe UI Semibold", fontsize="30")
    dot.attr("node", fontname="Segoe UI", fontsize="12")
    dot.attr("edge", fontname="Segoe UI", fontsize="12", color="#4b5b6b", arrowsize="0.9", penwidth="1.6")

    with dot.subgraph(name="cluster_request") as c:
        c.attr(label="Request / Entry", color="#d5dce3", style="rounded", bgcolor="#f7f9fb")
        add_box_node(c, "operator", "Operator", width="1.10", height="0.75")
        add_icon_node(c, "jira", "Jira Ticket", icons["jira"], subtitle="deploy request", width="1.60", height="1.60")
        edge(c, "operator", "jira")
        with c.subgraph() as row:
            row.attr(rank="same")
            row.node("operator")
            row.node("jira")

    with dot.subgraph(name="cluster_control") as c:
        c.attr(label="CI / Control Plane", color="#d5dce3", style="rounded", bgcolor="#f7f9fb")
        add_icon_node(c, "service_ci", "Service CI", icons["githubactions"], subtitle="app pipelines", width="2.48", height="1.92")
        add_icon_node(c, "sonar", "SonarQube", icons["sonarqube"], subtitle="quality", width="1.48", height="1.60")
        add_icon_node(c, "gitleaks", "Secrets Gate", icons["gitleaks"], subtitle="GitLeaks", width="2.18", height="1.70")
        add_icon_node(c, "trivy", "Trivy", icons["trivy"], subtitle="fs + image", width="1.52", height="1.60")
        add_icon_node(c, "dockerhub", "Docker Images", icons["docker"], subtitle="image tags", width="1.88", height="1.60")
        add_box_node(c, "latest_tags", "latest_tags.yaml\nlatest-dev metadata", width="1.90", height="0.90")

        add_icon_node(c, "deploy_workflow", "Deploy Workflow", icons["githubactions"], subtitle="deploy trigger", width="1.92", height="1.68")
        add_icon_node(c, "runner", "Self-hosted Runner", icons["runner"], subtitle="Windows runner", width="1.75", height="1.52")
        add_icon_node(c, "deployment_poc", "deployment-poc", icons["orchestration"], subtitle="orchestration", width="2.05", height="1.68")

        add_icon_node(c, "lock_mgr", "Lock Released", icons["lockopen"], subtitle="unlock state", width="1.84", height="1.58")
        add_icon_node(c, "rollback_logic", "Rollback Logic", icons["rollback"], subtitle="previous stable", width="1.85", height="1.55")

        add_box_node(c, "wf_code", "Code", width="0.94", height="0.78", fontsize="11")
        add_icon_node(c, "wf_scan", "Scan", icons["gitleaks"], subtitle="gate", width="0.98", height="1.02", fontsize="10")
        add_icon_node(c, "wf_build", "Build", icons["docker"], subtitle="image", width="0.94", height="1.02", fontsize="10")
        add_icon_node(c, "wf_push", "Push", icons["githubactions"], subtitle="tag", width="0.94", height="1.02", fontsize="10")
        add_icon_node(c, "wf_deploy", "Deploy", PRODUCT_ICONS / "step_deploy.png", subtitle="release", width="0.94", height="1.02", fontsize="10")
        add_icon_node(c, "wf_validate", "Validate", icons["validation"], subtitle="checks", width="1.02", height="1.06", fontsize="10")
        add_icon_node(c, "wf_result", "Result", PRODUCT_ICONS / "step_done.png", subtitle="pass/fail", width="1.02", height="1.02", fontsize="10")

        edge(c, "service_ci", "sonar")
        edge(c, "sonar", "gitleaks")
        edge(c, "gitleaks", "trivy")
        edge(c, "trivy", "dockerhub")
        edge(c, "dockerhub", "latest_tags")
        edge(c, "deploy_workflow", "runner")
        edge(c, "runner", "deployment_poc")
        edge(c, "deployment_poc", "lock_mgr", style="dashed", color="#7a8794")
        edge(c, "deployment_poc", "rollback_logic", style="dashed", color="#7a8794")
        edge(c, "wf_code", "wf_scan")
        edge(c, "wf_scan", "wf_build")
        edge(c, "wf_build", "wf_push")
        edge(c, "wf_push", "wf_deploy")
        edge(c, "wf_deploy", "wf_validate")
        edge(c, "wf_validate", "wf_result")
        edge(c, "deployment_poc", "wf_code", style="dashed", color="#7a8794")

        with c.subgraph() as row1:
            row1.attr(rank="same")
            row1.node("service_ci")
            row1.node("sonar")
            row1.node("gitleaks")
            row1.node("trivy")
            row1.node("dockerhub")
            row1.node("latest_tags")
        with c.subgraph() as row2:
            row2.attr(rank="same")
            row2.node("deploy_workflow")
            row2.node("runner")
            row2.node("deployment_poc")
        with c.subgraph() as row3:
            row3.attr(rank="same")
            row3.node("lock_mgr")
            row3.node("rollback_logic")
        with c.subgraph() as row4:
            row4.attr(rank="same")
            row4.node("wf_code")
            row4.node("wf_scan")
            row4.node("wf_build")
            row4.node("wf_push")
            row4.node("wf_deploy")
            row4.node("wf_validate")
            row4.node("wf_result")

    with dot.subgraph(name="cluster_gitops") as c:
        c.attr(label="GitOps / Reconciliation", color="#d5dce3", style="rounded", bgcolor="#f7f9fb")
        add_icon_node(c, "infra_repo", "leninkart-infra", icons["github"], subtitle="dev branch", width="1.55", height="1.52")
        add_box_node(c, "desired_state", "Desired State\nvalues-dev.yaml", width="1.90", height="0.90")
        add_icon_node(c, "argocd", "ArgoCD", icons["argocd"], subtitle="sync + health", width="1.74", height="1.62")
        edge(c, "infra_repo", "desired_state")
        edge(c, "desired_state", "argocd")
        with c.subgraph() as row:
            row.attr(rank="same")
            row.node("infra_repo")
            row.node("desired_state")
            row.node("argocd")

    with dot.subgraph(name="cluster_runtime") as c:
        c.attr(label="Kubernetes Runtime - k3d-leninkart-dev", color="#d5dce3", style="rounded", bgcolor="#f7f9fb")
        add_icon_node(c, "k8s", "Kubernetes", icons["kubernetes"], subtitle="k3d-leninkart-dev", width="2.00", height="1.78")
        add_icon_node(c, "ingress_nginx", "NGINX Ingress", icons["nginx"], subtitle="80 / 443", width="2.05", height="1.76")
        add_box_node(c, "ingress_routes", "Ingress Routes\n/ -> frontend\n/api/products -> product\n/api/orders -> order", width="3.05", height="1.28", fontsize="13")

        add_icon_node(c, "frontend_svc", "Frontend Service", icons["k8s_svc_official"], subtitle="Service (ClusterIP :80)", width="1.95", height="1.64", fontsize="11")
        add_icon_node(c, "product_svc", "Product Service", icons["k8s_svc_official"], subtitle="Service (ClusterIP :8081)", width="2.05", height="1.64", fontsize="11")
        add_icon_node(c, "order_svc", "Order Service", icons["k8s_svc_official"], subtitle="Service (ClusterIP :8080)", width="2.05", height="1.64", fontsize="11")

        add_icon_node(c, "frontend_deploy", "Frontend Deploy", icons["k8s_deploy_official"], subtitle="Deployment", width="1.88", height="1.68", fontsize="11")
        add_icon_node(c, "product_deploy", "Product Deploy", icons["k8s_deploy_official"], subtitle="Deployment", width="1.96", height="1.68", fontsize="11")
        add_icon_node(c, "order_deploy", "Order Deploy", icons["k8s_deploy_official"], subtitle="Deployment", width="1.96", height="1.68", fontsize="11")

        add_icon_node(c, "frontend_pod_1", "frontend-pod-1", icons["k8s_pod_official"], subtitle="Replica", width="1.42", height="1.48", fontsize="10")
        add_icon_node(c, "product_pod_1", "product-pod-1", icons["k8s_pod_official"], subtitle="Replica", width="1.48", height="1.48", fontsize="10")
        add_icon_node(c, "order_pod_1", "order-pod-1", icons["k8s_pod_official"], subtitle="Replica", width="1.48", height="1.48", fontsize="10")
        add_icon_node(c, "frontend_pod_2", "frontend-pod-2", icons["k8s_pod_official"], subtitle="Replica", width="1.42", height="1.48", fontsize="10")
        add_icon_node(c, "product_pod_2", "product-pod-2", icons["k8s_pod_official"], subtitle="Replica", width="1.48", height="1.48", fontsize="10")
        add_icon_node(c, "order_pod_2", "order-pod-2", icons["k8s_pod_official"], subtitle="Replica", width="1.48", height="1.48", fontsize="10")

        add_icon_node(c, "postgres", "Postgres", icons["postgres"], subtitle="DB :5432", width="1.50", height="1.54")
        add_icon_node(c, "vault", "Vault", icons["vault"], subtitle="Vault :8200", width="1.56", height="1.54")
        add_box_node(c, "secretstore", "Secrets Store\nvault-backend", width="1.75", height="0.90")
        add_box_node(c, "externalsecrets", "External Secrets\noperator + sync", width="1.90", height="0.90")
        add_box_node(c, "promtail", "Promtail\nnode logs", width="1.35", height="0.85")
        add_box_node(c, "traffic_generator", "Traffic Generator\n3 load pods", width="1.55", height="0.85")

        edge(c, "k8s", "ingress_nginx")
        edge(c, "ingress_nginx", "ingress_routes")
        edge(c, "ingress_routes", "frontend_svc")
        edge(c, "ingress_routes", "product_svc")
        edge(c, "ingress_routes", "order_svc")
        edge(c, "frontend_svc", "frontend_deploy")
        edge(c, "product_svc", "product_deploy")
        edge(c, "order_svc", "order_deploy")
        edge(c, "frontend_deploy", "frontend_pod_1")
        edge(c, "frontend_deploy", "frontend_pod_2")
        edge(c, "product_deploy", "product_pod_1")
        edge(c, "product_deploy", "product_pod_2")
        edge(c, "product_pod_1", "postgres")
        edge(c, "order_deploy", "order_pod_1")
        edge(c, "order_deploy", "order_pod_2")
        edge(c, "order_pod_1", "postgres")
        edge(c, "vault", "secretstore", style="dashed", color="#7f8c8d")
        edge(c, "secretstore", "externalsecrets", style="dashed", color="#7f8c8d")
        edge(c, "externalsecrets", "product_deploy", style="dashed", color="#7f8c8d")
        edge(c, "externalsecrets", "order_deploy", style="dashed", color="#7f8c8d")
        edge(c, "traffic_generator", "frontend_svc", style="dashed", color="#7f8c8d")

        with c.subgraph() as row1:
            row1.attr(rank="same")
            row1.node("k8s")
            row1.node("ingress_nginx")
            row1.node("vault")
        with c.subgraph() as row2:
            row2.attr(rank="same")
            row2.node("ingress_routes")
        with c.subgraph() as row3:
            row3.attr(rank="same")
            row3.node("frontend_svc")
            row3.node("product_svc")
            row3.node("order_svc")
        with c.subgraph() as row4:
            row4.attr(rank="same")
            row4.node("frontend_deploy")
            row4.node("product_deploy")
            row4.node("order_deploy")
        with c.subgraph() as row5:
            row5.attr(rank="same")
            row5.node("frontend_pod_1")
            row5.node("product_pod_1")
            row5.node("order_pod_1")
        with c.subgraph() as row6:
            row6.attr(rank="same")
            row6.node("frontend_pod_2")
            row6.node("product_pod_2")
            row6.node("order_pod_2")
        with c.subgraph() as row7:
            row7.attr(rank="same")
            row7.node("postgres")
            row7.node("secretstore")
            row7.node("externalsecrets")
        with c.subgraph() as row8:
            row8.attr(rank="same")
            row8.node("promtail")
            row8.node("traffic_generator")
        edge(c, "frontend_svc", "product_svc", style="invis")
        edge(c, "product_svc", "order_svc", style="invis")
        edge(c, "frontend_deploy", "product_deploy", style="invis")
        edge(c, "product_deploy", "order_deploy", style="invis")
        edge(c, "frontend_pod_1", "product_pod_1", style="invis")
        edge(c, "product_pod_1", "order_pod_1", style="invis")
        edge(c, "frontend_pod_2", "product_pod_2", style="invis")
        edge(c, "product_pod_2", "order_pod_2", style="invis")


    with dot.subgraph(name="cluster_external") as c:
        c.attr(label="External Runtime", color="#d5dce3", style="rounded", bgcolor="#f7f9fb")
        add_icon_node(c, "docker_compose", "Docker Compose", icons["docker"], subtitle="host runtime", width="1.82", height="1.58")
        add_icon_node(c, "kafka", "Kafka Runtime", icons["kafka"], subtitle="kafka :9092\njmx :7071", width="1.55", height="1.50")
        edge(c, "docker_compose", "kafka")
        with c.subgraph() as row:
            row.attr(rank="same")
            row.node("docker_compose")
            row.node("kafka")

    with dot.subgraph(name="cluster_validation") as c:
        c.attr(label="Validation / Proof", color="#d5dce3", style="rounded", bgcolor="#f7f9fb")
        add_icon_node(c, "validation", "Validation Engine", icons["validation"], subtitle="project-validation", width="2.12", height="1.90", fontsize="12")
        add_box_node(c, "validation_report", "Validation Result\npass + proof", width="2.12", height="1.06", fontsize="11")
        add_box_node(c, "proof_scope", "GitHub | GitOps | UI | Vault | Kafka | Obs", width="2.08", height="0.94", fontsize="10")
        edge(c, "validation", "validation_report")
        edge(c, "validation", "proof_scope", style="dashed", color="#7a8794")
        with c.subgraph() as row:
            row.attr(rank="same")
            row.node("validation")
            row.node("validation_report")

    with dot.subgraph(name="cluster_observability") as c:
        c.attr(label="Observability", color="#d5dce3", style="rounded", bgcolor="#f7f9fb")
        add_icon_node(c, "prometheus", "Prometheus", icons["prometheus"], subtitle="metrics", width="1.82", height="1.82", fontsize="12")
        add_icon_node(c, "grafana", "Grafana", icons["grafana"], subtitle="dashboards", width="1.82", height="1.82", fontsize="12")
        add_icon_node(c, "loki", "Loki", icons["loki"], subtitle="logs", width="1.82", height="1.82", fontsize="12")
        add_icon_node(c, "tempo", "Tempo", icons["tempo"], subtitle="traces", width="1.82", height="1.82", fontsize="12")
        edge(c, "prometheus", "grafana")
        edge(c, "loki", "grafana", color="#7f8c8d")
        edge(c, "tempo", "grafana", color="#7f8c8d")
        with c.subgraph() as row:
            row.attr(rank="same")
            row.node("prometheus")
            row.node("grafana")
            row.node("loki")
            row.node("tempo")

    dot.node("ci_gitops_anchor", "", shape="point", width="0.01", height="0.01", style="invis")
    dot.node("gitops_runtime_anchor", "", shape="point", width="0.01", height="0.01", style="invis")
    dot.node("runtime_split_anchor", "", shape="point", width="0.01", height="0.01", style="invis")
    dot.node("validation_anchor", "", shape="point", width="0.01", height="0.01", style="invis")
    dot.node("observability_anchor", "", shape="point", width="0.01", height="0.01", style="invis")

    dot.edge("jira", "service_ci", style="invis", weight="120")
    dot.edge("deployment_poc", "ci_gitops_anchor", style="invis", weight="120")
    dot.edge("ci_gitops_anchor", "infra_repo", style="invis", weight="120")
    dot.edge("argocd", "gitops_runtime_anchor", style="invis", weight="120")
    dot.edge("gitops_runtime_anchor", "k8s", style="invis", weight="120")
    dot.edge("k8s", "runtime_split_anchor", style="invis", weight="120")
    dot.edge("runtime_split_anchor", "validation_anchor", style="invis", weight="100")
    dot.edge("validation_anchor", "validation", style="invis", weight="100")
    dot.edge("runtime_split_anchor", "observability_anchor", style="invis", weight="100")
    dot.edge("observability_anchor", "prometheus", style="invis", weight="100")

    edge(dot, "jira", "deploy_workflow", color="#2f5b8a", penwidth="2.1")
    edge(dot, "latest_tags", "deployment_poc", color="#2f5b8a", penwidth="2.1")
    dot.edge("deployment_poc", "ci_gitops_anchor", color="#2f5b8a", penwidth="2.1", arrowhead="none")
    edge(dot, "ci_gitops_anchor", "infra_repo", color="#2f5b8a", penwidth="2.1")
    dot.edge("argocd", "gitops_runtime_anchor", color="#2f5b8a", penwidth="2.1", arrowhead="none")
    edge(dot, "gitops_runtime_anchor", "k8s", color="#2f5b8a", penwidth="2.1")
    dot.edge("k8s", "runtime_split_anchor", color="#2f5b8a", penwidth="1.8", arrowhead="none")
    edge(dot, "runtime_split_anchor", "validation_anchor", color="#2f5b8a", penwidth="1.6")
    edge(dot, "validation_anchor", "validation", color="#2f5b8a", penwidth="1.8")
    edge(dot, "runtime_split_anchor", "observability_anchor", style="dashed", color="#7f8c8d", penwidth="1.3")
    edge(dot, "observability_anchor", "prometheus", style="dashed", color="#7f8c8d", penwidth="1.3")

    edge(dot, "k8s", "kafka", style="dashed", color="#7f8c8d", penwidth="1.2")
    edge(dot, "rollback_logic", "infra_repo", style="dashed", color="#c0392b", penwidth="1.4")

    output_base = ROOT / "leninkart-platform-final"
    dot.render(filename=output_base.name, directory=str(ROOT), format="png", cleanup=True)
    dot.render(filename=output_base.name, directory=str(ROOT), format="svg", cleanup=True)
    embed_images_in_svg(output_base.with_suffix('.svg'))


if __name__ == "__main__":
    build()
