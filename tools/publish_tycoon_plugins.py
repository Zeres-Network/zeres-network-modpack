"""Publica la edición del Tycoon sin mods (Minecraft 26.3 normal): sin Fabric ni mods, solo el paquete de recursos con los modelos,
iconos y sonidos, que el launcher baja y deja activado. Crea el release tycoonp-<version>, actualiza la instancia «tycoonp» de
manifest.json y hace push. Los assets salen del mod (ZeresRPG-Client) para que no haya dos copias.
Uso:  python tools/publish_tycoon_plugins.py <version> "Novedad" ["Novedad"...]
"""
import hashlib, json, os, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(os.path.dirname(ROOT), "ZeresRPG-Client", "src", "main", "resources", "assets")
REPO = "Zeres-Network/zeres-network-modpack"
MC = "26.3"
PACK_FORMAT = 97  # pack_version.resource_major de version.json de 26.3
PUBLIC = "shrimp-montana.tun.ply.gg:56966"


def build_pack(path):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps({"pack": {"description": "Zeres Tycoon", "min_format": PACK_FORMAT, "max_format": PACK_FORMAT}}, indent=2))
        for base, _, files in os.walk(ASSETS):
            for f in files:
                full = os.path.join(base, f)
                z.write(full, os.path.join("assets", os.path.relpath(full, ASSETS)).replace("\\", "/"))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    version, notes = sys.argv[1], sys.argv[2:]
    os.makedirs(os.path.join(ROOT, "tycoon"), exist_ok=True)
    tag = f"tycoonp-{version}"
    pack = os.path.join(ROOT, "tycoon", "zeres-tycoon.zip")
    build_pack(pack)
    data = open(pack, "rb").read()
    entry = {"path": "resourcepacks/zeres-tycoon.zip", "hashes": {"sha1": hashlib.sha1(data).hexdigest(), "sha512": hashlib.sha512(data).hexdigest()},
             "env": {"client": "required", "server": "unsupported"}, "downloads": [f"https://github.com/{REPO}/releases/download/{tag}/zeres-tycoon.zip"], "fileSize": len(data)}
    out = os.path.join(ROOT, "tycoon", f"zeres-tycoon-plugins-{version}.mrpack")
    index = {"formatVersion": 1, "game": "minecraft", "versionId": version, "name": "Zeres Tycoon sin mods", "summary": "Modalidad Tycoon solo con plugins y paquete de recursos",
             "files": [entry], "dependencies": {"minecraft": MC}}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=2))
        # solo se copia si no existe: activa el paquete la primera vez sin pisar las opciones del jugador
        z.writestr("overrides/options.txt", 'resourcePacks:["vanilla","file/zeres-tycoon.zip"]\nonboardAccessibility:false\n')
    sha1 = hashlib.sha1(open(out, "rb").read()).hexdigest()
    subprocess.run(["gh", "release", "create", tag, out, pack, "--repo", REPO, "--prerelease", "--title", f"Zeres Tycoon sin mods {version}",
                    "--notes", "\n".join("- " + n for n in notes)], check=True)
    mpath = os.path.join(ROOT, "manifest.json")
    m = json.load(open(mpath, encoding="utf-8"))
    r = m["instances"].setdefault("tycoonp", {"name": "Zeres Tycoon sin mods", "server": {"host": "127.0.0.1", "port": 25568}, "local_server": "Desktop/dev/ZeresTycoon/servidor-plugins"})
    r["version"] = version
    r["minecraft"] = MC
    r["mrpack"] = f"https://github.com/{REPO}/releases/download/{tag}/zeres-tycoon-plugins-{version}.mrpack"
    r["sha1"] = sha1
    r["notes"] = notes
    open(mpath, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=2, ensure_ascii=False))
    subprocess.run(["git", "-C", ROOT, "add", "-A"], check=True)
    subprocess.run(["git", "-C", ROOT, "-c", "user.name=Days16", "-c", "user.email=btsamuel21@gmail.com", "commit", "-q", "-m",
                    f"Zeres Tycoon sin mods {version}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], check=True)
    subprocess.run(["git", "-C", ROOT, "push", "-q", "origin", "main"], check=True)
    print("Publicado", tag)


main()
