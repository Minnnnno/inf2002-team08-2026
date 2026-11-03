"""Validate source HTML/CSS/SVG and saved fictional DOMs with the current Nu checker.

Download the official Windows runtime from https://github.com/validator/validator/releases/tag/latest
into the OS temp directory clarity-nu-checker, or pass --checker with its vnu.bat path.
Run accessibility_audit.py first to capture rendered DOMs.
"""
import argparse, json, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[1]
out = pathlib.Path(tempfile.gettempdir()) / 'clarity-accessibility'
parser = argparse.ArgumentParser()
parser.add_argument('--checker', default=str(pathlib.Path(tempfile.gettempdir())/'clarity-nu-checker/vnu-runtime-image/bin/vnu.bat'))
args = parser.parse_args()
folder = out / 'rendered'
folder.mkdir(exist_ok=True)
documents = json.loads((out / 'documents.json').read_text(encoding='utf-8'))
files = []
for name, content in documents.items():
    path = folder / name
    path.write_text(content, encoding='utf-8')
    files.append(str(path))
source = sorted(str(p) for p in (root/'dist').iterdir() if p.suffix in ['.html','.css','.svg'])
command = [args.checker, '--also-check-css', '--also-check-svg', '--format', 'json', '--stdout', *source, *files]
result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
messages = json.loads(result.stdout)
version = subprocess.run([args.checker, '--version'], capture_output=True, text=True, encoding='utf-8')
report = {'checker':version.stdout.strip() or version.stderr.strip(), 'sourceFiles':len(source), 'renderedDocuments':len(files), **messages}
(out / 'standards-local.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert result.returncode == 0, result.stderr
