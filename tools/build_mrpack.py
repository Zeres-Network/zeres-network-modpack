"""Genera el .mrpack de Zeres Cobblemon a partir de una carpeta de mods.

Los mods que estan en Modrinth se apuntan a su CDN (no se resuben); el resto (ZeresClient, mods privados...) van
dentro del pack en overrides/mods. Uso:
    python build_mrpack.py <carpeta_mods> <version> <salida.mrpack> [--optional nombre1,nombre2] [--exclude a,b]
"""
import hashlib, json, os, sys, urllib.request, zipfile

def main():
    mods_dir, version, out = sys.argv[1], sys.argv[2], sys.argv[3]
    opts = dict(zip(sys.argv[4::2], sys.argv[5::2]))
    optional = [s.lower() for s in opts.get("--optional", "").split(",") if s]
    exclude = [s.lower() for s in opts.get("--exclude", "").split(",") if s]
    jars = []
    for f in sorted(os.listdir(mods_dir)):
        if not f.endswith(".jar") or any(e in f.lower() for e in exclude):
            continue
        data = open(os.path.join(mods_dir, f), "rb").read()
        jars.append({"name": f, "data": data, "sha1": hashlib.sha1(data).hexdigest(), "sha512": hashlib.sha512(data).hexdigest()})
    req = urllib.request.Request("https://api.modrinth.com/v2/version_files", method="POST",
                                 data=json.dumps({"hashes": [j["sha1"] for j in jars], "algorithm": "sha1"}).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "ZeresNetwork/zeres-network-modpack (build script)"})
    found = json.load(urllib.request.urlopen(req, timeout=60))
    files, overrides = [], []
    for j in jars:
        v = found.get(j["sha1"])
        url = None
        if v:
            url = next((f["url"] for f in v["files"] if f["hashes"].get("sha1") == j["sha1"]), None)
        env = "optional" if any(o in j["name"].lower() for o in optional) else "required"
        if url:
            files.append({"path": "mods/" + j["name"], "hashes": {"sha1": j["sha1"], "sha512": j["sha512"]},
                          "env": {"client": env, "server": "unsupported"}, "downloads": [url], "fileSize": len(j["data"])})
        else:
            overrides.append(j)
    index = {"formatVersion": 1, "game": "minecraft", "versionId": version, "name": "Zeres Cobblemon",
             "summary": "Modpack oficial de Zeres Cobblemon", "files": files,
             "dependencies": {"minecraft": "1.21.1", "fabric-loader": "0.19.3"}}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=2))
        for j in overrides:
            z.writestr("overrides/mods/" + j["name"], j["data"])
        # configuracion por defecto (cobblemon/overrides/...): el launcher solo la copia si el jugador no la tiene
        extra = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cobblemon", "overrides")
        for root, _, names in os.walk(extra):
            for n in names:
                full = os.path.join(root, n)
                rel = os.path.relpath(full, extra).replace(os.sep, "/")
                z.write(full, "overrides/" + rel)
                print("   config:", rel)
    print("Modrinth:", len(files), "| dentro del pack:", len(overrides))
    for j in overrides:
        print("   pack:", j["name"])
    print("sha1:", hashlib.sha1(open(out, "rb").read()).hexdigest(), "size:", os.path.getsize(out))

main()
