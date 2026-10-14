"""Publica una version nueva del modpack de Zeres Cobblemon en un solo paso:
genera el .mrpack desde la instancia de Prism, crea el release en GitHub, actualiza manifest.json y hace push.

Uso:  python tools/publish_cobblemon.py 0.1.4 "Novedad 1" "Novedad 2" ...
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "Zeres-Network/zeres-network-modpack"
MODS = r"C:/Users/Administrator/AppData/Roaming/PrismLauncher/instances/server prueba fabric v2/minecraft/mods"
# Con el juego abierto se puede publicar desde una copia de la carpeta: ZERES_MODS_DIR=<carpeta>
MODS = os.environ.get("ZERES_MODS_DIR", MODS)
OPTIONAL = "xaerominimap,xaeroworldmap"
EXCLUDE = "axiom,flashback,litematica,malilib,worldedit,fabric-api-0.116.13,.bak"


def main():
    if len(sys.argv) < 3:
        sys.exit("uso: publish_cobblemon.py <version> <novedad> [<novedad>...]")
    version, notes = sys.argv[1], sys.argv[2:]
    out = os.path.join(ROOT, "cobblemon", f"zeres-cobblemon-{version}.mrpack")
    res = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_mrpack.py"), MODS, version, out,
                          "--optional", OPTIONAL, "--exclude", EXCLUDE], capture_output=True, text=True, check=True)
    print(res.stdout)
    sha1 = next(l.split()[1] for l in res.stdout.splitlines() if l.startswith("sha1:"))
    tag = f"cobblemon-{version}"
    subprocess.run(["gh", "release", "create", tag, out, "--repo", REPO, "--title", f"Zeres Cobblemon {version}",
                    "--notes", "\n".join("- " + n for n in notes)], check=True)
    mpath = os.path.join(ROOT, "manifest.json")
    m = json.load(open(mpath, encoding="utf-8"))
    c = m["instances"]["cobblemon"]
    c["version"] = version
    c["mrpack"] = f"https://github.com/{REPO}/releases/download/{tag}/zeres-cobblemon-{version}.mrpack"
    c["sha1"] = sha1
    c["notes"] = notes
    m["news"] = [{"tag": "COBBLEMON", "title": f"Modpack {version}", "text": notes[0]}]
    json.dump(m, open(mpath, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    subprocess.run(["git", "-C", ROOT, "add", "-A"], check=True)
    subprocess.run(["git", "-C", ROOT, "-c", "user.name=Days16", "-c", "user.email=btsamuel21@gmail.com", "commit", "-q", "-m",
                    f"Zeres Cobblemon {version}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], check=True)
    subprocess.run(["git", "-C", ROOT, "push", "-q", "origin", "main"], check=True)
    print("Publicado", tag, "sha1", sha1)


main()
