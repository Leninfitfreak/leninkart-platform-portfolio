from __future__ import annotations

import base64
import mimetypes
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent if ROOT.parent.name == 'leninkart-platform-portfolio' else ROOT.parent
PORTFOLIO_ARCH = WORKSPACE / 'leninkart-platform-portfolio' / 'architecture'
PORTFOLIO_ICONS = WORKSPACE / 'leninkart-platform-portfolio' / 'icons'
PRODUCT_ICONS = WORKSPACE / 'architecture' / 'icons'

OUT_NAME = 'leninkart-platform-final'
WIDTH = 2200
HEIGHT = 1720


def data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if not mime:
        mime = 'image/svg+xml' if path.suffix.lower() == '.svg' else 'application/octet-stream'
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode('ascii')


def card(x, y, w, h, title, subtitle=None, icon=None, icon_size=72, title_size=22, subtitle_size=16):
    parts = [
        f'<g>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#ffffff" stroke="#cfd8e3" stroke-width="2"/>'
    ]
    if icon:
        ix = x + (w - icon_size) / 2
        iy = y + 10
        parts.append(f'<image href="{data_uri(icon)}" x="{ix}" y="{iy}" width="{icon_size}" height="{icon_size}" preserveAspectRatio="xMidYMid meet"/>')
        ty = iy + icon_size + 22
    else:
        ty = y + h / 2 + 6
    parts.append(f'<text x="{x + w/2}" y="{ty}" text-anchor="middle" font-family="Segoe UI, Arial" font-size="{title_size}" fill="#111827">{title}</text>')
    if subtitle:
        for i, line in enumerate(str(subtitle).split('\n')):
            parts.append(f'<text x="{x + w/2}" y="{ty + 22 + i*18}" text-anchor="middle" font-family="Segoe UI, Arial" font-size="{subtitle_size}" fill="#374151">{line}</text>')
    parts.append('</g>')
    return '\n'.join(parts)


def plain_box(x, y, w, h, lines, title_size=22, line_size=16, fill='#ffffff'):
    parts = [f'<g>', f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="#cfd8e3" stroke-width="2"/>']
    if isinstance(lines, str):
        lines = lines.split('\n')
    total = len(lines)
    start_y = y + h/2 - ((total-1)*line_size*1.15)/2
    for i, line in enumerate(lines):
        size = title_size if i == 0 else line_size
        parts.append(f'<text x="{x + w/2}" y="{start_y + i*line_size*1.25}" text-anchor="middle" font-family="Segoe UI, Arial" font-size="{size}" fill="#111827">{line}</text>')
    parts.append('</g>')
    return '\n'.join(parts)


def cluster(x, y, w, h, title):
    return '\n'.join([
        '<g>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#f8fafc" stroke="#d8e0e8" stroke-width="2"/>',
        f'<text x="{x + w/2}" y="{y + 28}" text-anchor="middle" font-family="Segoe UI Semibold, Arial" font-size="24" fill="#111827">{title}</text>',
        '</g>'
    ])


def line(x1, y1, x2, y2, color='#57789a', width=3, dash=None, arrow=True):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    parts = [
        '<g>',
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{dash_attr}/>'
    ]
    if arrow:
        parts.append(f'<polygon points="{x2},{y2} {x2-10},{y2-5} {x2-10},{y2+5}" fill="{color}"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def poly(points, color='#57789a', width=3, dash=None, arrow_end=True):
    pts = ' '.join(f'{x},{y}' for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    parts = [
        '<g>',
        f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{dash_attr}/>'
    ]
    if arrow_end:
        x2, y2 = points[-1]
        x1, y1 = points[-2]
        if abs(x2 - x1) >= abs(y2 - y1):
            arrow = [(x2, y2), (x2 - 10 if x2 >= x1 else x2 + 10, y2 - 5), (x2 - 10 if x2 >= x1 else x2 + 10, y2 + 5)]
        else:
            arrow = [(x2, y2), (x2 - 5, y2 - 10 if y2 >= y1 else y2 + 10), (x2 + 5, y2 - 10 if y2 >= y1 else y2 + 10)]
        parts.append(f'<polygon points="{" ".join(f"{x},{y}" for x, y in arrow)}" fill="{color}"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def build_svg() -> str:
    A = PRODUCT_ICONS
    P = PORTFOLIO_ICONS
    icons = {
        'jira': P / 'jira.jpg',
        'gha': A / 'githubactions.png',
        'sonar': A / 'sonarqube.png',
        'gitleaks': P / 'gitleaks.png',
        'trivy': A / 'trivy.png',
        'docker': A / 'docker.png',
        'orch': P / 'orchestration.png',
        'runner': P / 'runner.png',
        'validation': P / 'validation.png',
        'rollback': P / 'rollback.png',
        'ticket': A / 'step_ticket.png',
        'lock': A / 'step_lock.png',
        'deploy': A / 'step_deploy.png',
        'sync': A / 'step_sync.png',
        'verify': A / 'step_verify.png',
        'done': A / 'step_done.png',
        'nginx': A / 'nginx.png',
        'svc': P / 'k8s_svc_official.png',
        'deploy_k8s': P / 'k8s_deploy_official.png',
        'pod': P / 'k8s_pod_official.png',
        'k8s': A / 'kubernetes.png',
        'docker_ext': A / 'docker.png',
        'kafka': A / 'kafka.png',
        'prometheus': A / 'prometheus.png',
        'loki': A / 'loki.png',
        'tempo': A / 'tempo.png',
        'grafana': A / 'grafana.png',
        'postgres': A / 'postgres.png',
        'yaml': A / 'yaml_custom.png',
    }

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    s.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    s.append('<text x="1100" y="26" text-anchor="middle" font-family="Segoe UI Semibold, Arial" font-size="20" fill="#111827">Leninkart Platform Architecture</text>')

    s.append(cluster(20, 40, 190, 110, 'Request / Entry'))
    s.append(cluster(110, 150, 820, 500, 'CI / Control Plane'))
    s.append(cluster(920, 510, 300, 140, 'GitOps / Reconciliation'))
    s.append(cluster(430, 670, 900, 760, 'Kubernetes Runtime - k3d-leninkart-dev'))
    s.append(cluster(1290, 800, 200, 130, 'External Runtime'))
    s.append(cluster(1340, 1030, 290, 220, 'Validation / Proof'))
    s.append(cluster(1590, 1030, 570, 120, 'Observability'))

    s.append(plain_box(36, 82, 56, 40, 'Open', title_size=12, line_size=12))
    s.append(card(110, 70, 84, 72, 'Jira', 'deploy issue', icons['jira'], icon_size=52, title_size=16, subtitle_size=11))
    s.append(poly([(92,102),(110,102)], color='#5c7694', width=3))

    x0, y0 = 120, 180
    step_w, step_h, gap = 135, 92, 20
    labels = [
        ('Source', None, icons['gha']),
        ('Build', None, icons['sonar']),
        ('Test', None, icons['gitleaks']),
        ('Security Scan', None, icons['trivy']),
        ('Dependency Scan', None, icons['docker']),
    ]
    for i, (t, sub, ico) in enumerate(labels):
        x = x0 + i * (step_w + gap)
        s.append(card(x, y0, step_w, step_h, t, sub, ico, icon_size=50, title_size=16, subtitle_size=11))
        if i:
            s.append(line(x - 20, y0 + 46, x, y0 + 46, color='#5c7694', width=2.5))
    s.append(plain_box(785, 198, 110, 52, 'LATEST TAGS and\nlatest dev metadata', title_size=11, line_size=9))
    s.append(line(795, y0 + 46, 785, y0 + 46, color='#5c7694', width=2.5))

    s.append(card(515, 310, 110, 90, 'Orchestration', None, icons['orch'], icon_size=50, title_size=14))
    s.append(card(640, 302, 120, 104, 'Validation Job', None, icons['gha'], icon_size=58, title_size=14))
    s.append(card(780, 312, 98, 84, 'Security Job', None, icons['validation'], icon_size=48, title_size=13))
    s.append(poly([(690,272),(690,302)], color='#5c7694', width=2.5))
    s.append(poly([(760,352),(780,352)], color='#5c7694', width=2.5))
    s.append(poly([(625,355),(640,355)], color='#5c7694', width=2.5))

    y1 = 440
    wf_w, wf_h, wf_gap, wf_start = 84, 70, 18, 112
    workflow = [
        ('rollback', icons['rollback']),
        ('ticket', icons['ticket']),
        ('lock open', icons['lock']),
        ('lock', icons['lock']),
        ('deploy', icons['deploy']),
        ('sync', icons['sync']),
        ('verify', icons['verify']),
        ('done / fail', icons['done']),
    ]
    for i, (t, ico) in enumerate(workflow):
        x = wf_start + i * (wf_w + wf_gap)
        s.append(card(x, y1, wf_w, wf_h, t, None, ico, icon_size=36, title_size=11, subtitle_size=10))
        if i:
            s.append(line(x - wf_gap, y1 + 35, x, y1 + 35, color='#9aa8b6', width=2))
    s.append(poly([(120,380),(120,580),(930,580)], color='#b5c1cc', width=2, dash='6 6', arrow_end=False))
    s.append(poly([(300,460),(300,360),(515,360)], color='#b5c1cc', width=2, dash='6 6', arrow_end=False))

    s.append(card(935, 550, 92, 80, 'GitHub', None, A / 'github.png', icon_size=44, title_size=13))
    s.append(plain_box(1038, 566, 92, 40, 'Git dev branch\nstate repo', title_size=12, line_size=10))
    s.append(card(1138, 548, 70, 84, 'ArgoCD', None, A / 'argocd.png', icon_size=44, title_size=12))
    s.append(line(1027,590,1038,590,width=2.5))
    s.append(line(1130,590,1138,590,width=2.5))

    s.append(card(860, 720, 90, 92, 'Nginx', None, icons['nginx'], icon_size=54, title_size=14))
    s.append(card(980, 720, 82, 92, 'LegacyCD', None, icons['yaml'], icon_size=50, title_size=13))
    s.append(card(1088, 710, 100, 104, 'Kubernetes', None, icons['k8s'], icon_size=60, title_size=14))
    s.append(poly([(1170,632),(1170,710)], color='#5c7694', width=3))
    s.append(poly([(905,814),(905,870),(900,870)], color='#5c7694', width=3, arrow_end=False))

    s.append(plain_box(810, 860, 180, 78, 'Service\nEndpoints', title_size=22, line_size=18))
    s.append(plain_box(650, 885, 100, 46, 'Traffic generator\n1 load pod', title_size=11, line_size=10))
    s.append(plain_box(1020, 885, 74, 46, 'Prom\nnode log', title_size=11, line_size=10))

    svc_y = 980
    svc_xs = [710, 870, 1030]
    svc_titles = ['frontend', 'product', 'order']
    dep_titles = ['Deployment', 'Deployment', 'order']
    pod_xs = [[650,740],[830,920],[1010,1100]]
    for x, t, dt, pods in zip(svc_xs, svc_titles, dep_titles, pod_xs):
        s.append(card(x, svc_y, 88, 96, t, None, icons['svc'], icon_size=48, title_size=14))
        s.append(poly([(x+44,938),(x+44,980)], color='#6a7f92', width=2.5))
        s.append(card(x-5, 1095, 98, 106, dt, None, icons['deploy_k8s'], icon_size=54, title_size=14))
        s.append(poly([(x+44,1076),(x+44,1095)], color='#6a7f92', width=2.5))
        for px in pods:
            s.append(card(px, 1225, 74, 96, 'Pod', None, icons['pod'], icon_size=42, title_size=13))
            s.append(poly([(x+44,1201),(x+44,1235),(px+37,1235),(px+37,1225)], color='#6a7f92', width=2.2))
    for x in svc_xs:
        s.append(poly([(900,938),(900,960),(x+44,960),(x+44,980)], color='#6a7f92', width=2.5))

    s.append(plain_box(900, 1338, 108, 44, 'Postgres', title_size=14, line_size=12))
    s.append(card(1015, 1318, 96, 108, 'DB', None, icons['postgres'], icon_size=58, title_size=14))
    s.append(plain_box(1128, 1338, 104, 44, 'Database', title_size=14, line_size=12))
    s.append(poly([(1075,1321),(1075,1352),(1008,1352)], color='#6a7f92', width=2.2))
    s.append(poly([(1111,1372),(1128,1360)], color='#6a7f92', width=2.2))

    s.append(card(1310, 840, 78, 86, 'Docker', None, icons['docker_ext'], icon_size=44, title_size=13))
    s.append(card(1400, 838, 70, 90, 'ExtSQL DB', None, icons['kafka'], icon_size=46, title_size=13))
    s.append(line(1388,883,1400,883,width=2.5))

    s.append(card(1360, 1080, 84, 100, 'Validation', None, icons['validation'], icon_size=54, title_size=13))
    s.append(plain_box(1452, 1104, 128, 48, 'pass / fail\nprove output', title_size=13, line_size=10))
    s.append(plain_box(1380, 1200, 150, 36, 'prove api flow + flux flow', title_size=11, line_size=10))
    s.append(line(1444,1128,1452,1128,width=2.5))
    s.append(poly([(1420,1180),(1420,1200)], color='#9aa8b6', width=2, dash='6 6'))

    obs_y = 1060
    obs_xs = [1610, 1730, 1850, 1970]
    obs = [('Probabilities', icons['prometheus']), ('Grafana loki', icons['loki']), ('GrafanaTempo', icons['tempo']), ('Grafkas', icons['grafana'])]
    for x, (title, ico) in zip(obs_xs, obs):
        s.append(card(x, obs_y, 96, 80, title, None, ico, icon_size=44, title_size=13))
    s.append(line(1706,1100,1730,1100,width=2.5,color='#f4a261'))
    s.append(line(1826,1100,1850,1100,width=2.5,color='#f4a261'))
    s.append(line(1946,1100,1970,1100,width=2.5,color='#f4a261'))

    s.append(poly([(194,106),(760,106),(760,340)], color='#57789a', width=3, arrow_end=False))
    s.append(poly([(760,340),(935,340),(935,590)], color='#57789a', width=3))
    s.append(poly([(1173,632),(1173,700),(1138,700)], color='#57789a', width=3, arrow_end=False))
    s.append(poly([(1188,760),(1500,760),(1500,1035)], color='#57789a', width=3))
    s.append(poly([(1188,760),(1500,760),(1500,840),(1310,840)], color='#57789a', width=3, arrow_end=False))
    s.append(poly([(1470,890),(1470,1035),(1610,1035)], color='#b5c1cc', width=2, dash='6 6'))

    s.append('</svg>')
    return '\n'.join(s)


def render_png(svg_path: Path, png_path: Path) -> None:
    edge = Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
    if not edge.exists():
        edge = Path(r'C:\Program Files\Microsoft\Edge\Application\msedge.exe')
    if not edge.exists():
        raise FileNotFoundError('Microsoft Edge not found for PNG export')
    subprocess.run([
        str(edge), '--headless', '--disable-gpu', f'--window-size={WIDTH},{HEIGHT}', f'--screenshot={png_path}', svg_path.as_uri()
    ], check=True)


def main() -> None:
    svg = build_svg()
    for base in [ROOT / OUT_NAME, PORTFOLIO_ARCH / OUT_NAME]:
        base.parent.mkdir(parents=True, exist_ok=True)
        svg_path = base.with_suffix('.svg')
        png_path = base.with_suffix('.png')
        svg_path.write_text(svg, encoding='utf-8')
        render_png(svg_path, png_path)


if __name__ == '__main__':
    main()
