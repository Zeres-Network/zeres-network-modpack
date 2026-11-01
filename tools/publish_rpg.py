"""Publica el modpack de la edición RPG test (Minecraft 26.3, canal dev del launcher): Fabric + Fabric API (desde
Modrinth) + ZeresRPG Client (dentro del pack). Crea el release rpg-<version>, actualiza la instancia "rpg" de
manifest.json (conserva server y local_server) y hace push.
Uso:  python tools/publish_rpg.py <version> <jar de ZeresRPG Client> "Novedad" ["Novedad"...]
"""
import hashlib, json, os, subprocess, sys, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "Zeres-Network/zeres-network-modpack"
MC = "26.3"
LOADER = "0.20.1"
FABRIC_API = "0.165.0+26.3"
UA = {"User-Agent": "ZeresNetwork/zeres-network-modpack (publish_rpg)"}


def modrinth_file(project, version_number):
    url = f"https://api.modrinth.com/v2/project/{project}/version?game_versions=%5B%22{MC}%22%5D&loaders=%5B%22fabric%22%5D"
    for v in json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)):
        if v["version_number"] == version_number:
            f = next(f for f in v["files"] if f["primary"]) if any(f["primary"] for f in v["files"]) else v["files"][0]
            return {"path": "mods/" + f["filename"], "hashes": {"sha1": f["hashes"]["sha1"], "sha512": f["hashes"]["sha512"]},
                    "env": {"client": "required", "server": "unsupported"}, "downloads": [f["url"]], "fileSize": f["size"]}
    sys.exit(f"Modrinth no tiene {project} {version_number}")


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    version, jar, notes = sys.argv[1], sys.argv[2], sys.argv[3:]
    os.makedirs(os.path.join(ROOT, "rpg"), exist_ok=True)
    out = os.path.join(ROOT, "rpg", f"zeres-rpg-{version}.mrpack")
    index = {"formatVersion": 1, "game": "minecraft", "versionId": version, "name": "Zeres RPG test",
             "summary": "Modalidad RPG de Zeres Network (pruebas)", "files": [modrinth_file("fabric-api", FABRIC_API)],
             "dependencies": {"minecraft": MC, "fabric-loader": LOADER}}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=2))
        z.write(jar, "overrides/mods/" + os.path.basename(jar))
    sha1 = hashlib.sha1(open(out, "rb").read()).hexdigest()
    print("mrpack:", out, "sha1:", sha1)
    tag = f"rpg-{version}"
    subprocess.run(["gh", "release", "create", tag, out, "--repo", REPO, "--prerelease", "--title", f"Zeres RPG test {version}",
                    "--notes", "\n".join("- " + n for n in notes)], check=True)
    mpath = os.path.join(ROOT, "manifest.json")
    m = json.load(open(mpath, encoding="utf-8"))
    r = m["instances"]["rpg"]
    r["version"] = version
    r["minecraft"] = MC
    r["mrpack"] = f"https://github.com/{REPO}/releases/download/{tag}/zeres-rpg-{version}.mrpack"
    r["sha1"] = sha1
    r["notes"] = notes
    open(mpath, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=2, ensure_ascii=False))
    subprocess.run(["git", "-C", ROOT, "add", "-A"], check=True)
    subprocess.run(["git", "-C", ROOT, "-c", "user.name=Days16", "-c", "user.email=btsamuel21@gmail.com", "commit", "-q", "-m",
                    f"Zeres RPG test {version}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], check=True)
    subprocess.run(["git", "-C", ROOT, "push", "-q", "origin", "main"], check=True)
    print("Publicado", tag)


main()
