"""Publica Open Front (Zeres Front) para Launcher Minecraft: Minecraft 26.3 normal, sin mods, con su paquete de recursos.
Crea el release front-<version>, actualiza la instancia «front» de manifest.json (conserva public_server) y hace push.
Uso:  python tools/publish_front.py <version> "Novedad" ["Novedad"...]
"""
import hashlib, json, os, shutil, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP = os.path.join(os.path.dirname(ROOT), "ZeresFront", "dist", "zeres-front.zip")
REPO = "Zeres-Network/zeres-network-modpack"
MC = "26.3"


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    version, notes = sys.argv[1], sys.argv[2:]
    folder = os.path.join(ROOT, "front")
    os.makedirs(folder, exist_ok=True)
    tag = f"front-{version}"
    pack = os.path.join(folder, "zeres-front.zip")
    shutil.copyfile(ZIP, pack)
    data = open(pack, "rb").read()
    entry = {"path": "resourcepacks/zeres-front.zip", "hashes": {"sha1": hashlib.sha1(data).hexdigest(), "sha512": hashlib.sha512(data).hexdigest()},
             "env": {"client": "required", "server": "unsupported"}, "downloads": [f"https://github.com/{REPO}/releases/download/{tag}/zeres-front.zip"],
             "fileSize": len(data)}
    out = os.path.join(folder, f"zeres-front-{version}.mrpack")
    index = {"formatVersion": 1, "game": "minecraft", "versionId": version, "name": "Open Front", "summary": "Guerra de territorios en un mapa gigante de bloques",
             "files": [entry], "dependencies": {"minecraft": MC}}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=2))
        # solo se copia si no existe: activa el paquete la primera vez sin pisar las opciones del jugador
        z.writestr("overrides/options.txt", 'resourcePacks:["vanilla","file/zeres-front.zip"]\nrenderDistance:32\nrenderClouds:"false"\nonboardAccessibility:false\n')
    sha1 = hashlib.sha1(open(out, "rb").read()).hexdigest()
    subprocess.run(["gh", "release", "create", tag, out, pack, "--repo", REPO, "--prerelease", "--title", f"Zeres Front {version}",
                    "--notes", "\n".join("- " + n for n in notes)], check=True)
    mpath = os.path.join(ROOT, "manifest.json")
    m = json.load(open(mpath, encoding="utf-8"))
    r = m["instances"].setdefault("front", {"name": "Open Front", "server": {"host": "127.0.0.1", "port": 25569}, "local_server": "Desktop/dev/ZeresFront/servidor"})
    r["version"] = version
    r["minecraft"] = MC
    r["mrpack"] = f"https://github.com/{REPO}/releases/download/{tag}/zeres-front-{version}.mrpack"
    r["sha1"] = sha1
    r["notes"] = notes
    open(mpath, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=2, ensure_ascii=False))
    subprocess.run(["git", "-C", ROOT, "add", "manifest.json", "tools/publish_front.py"], check=True)
    subprocess.run(["git", "-C", ROOT, "-c", "user.name=Days16", "-c", "user.email=btsamuel21@gmail.com", "commit", "-q", "-m",
                    f"Zeres Front {version}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], check=True)
    subprocess.run(["git", "-C", ROOT, "push", "-q", "origin", "main"], check=True)
    print("Publicado", tag)


main()
