"""Ids de mod (Fabric) de una carpeta de mods, incluidos los jars anidados, para config/zeresserver/mods-permitidos.txt.
El servidor compara con esta lista los mods que reporta ZeresClient al entrar.

Uso:  python tools/mod_ids.py <carpeta_mods> [--exclude a,b] [--out archivo]
"""
import io, json, os, sys, zipfile

# los que pone Fabric Loader sin jar propio
BUILTIN = {"minecraft", "java", "fabricloader", "mixinextras"}


def ids_of(data, out):
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        meta = json.loads(z.read("fabric.mod.json").decode("utf-8-sig"), strict=False)
    except (KeyError, zipfile.BadZipFile, ValueError):
        return
    if meta.get("id"):
        out.add(meta["id"].lower())
    for j in meta.get("jars", []):
        try:
            ids_of(z.read(j["file"]), out)
        except KeyError:
            pass


def collect(mods, exclude=()):
    out = set(BUILTIN)
    for f in sorted(os.listdir(mods)):
        if not f.endswith(".jar") or any(e in f.lower() for e in exclude):
            continue
        with open(os.path.join(mods, f), "rb") as fh:
            ids_of(fh.read(), out)
    return sorted(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    opts = {args[i]: args[i + 1] for i in range(1, len(args) - 1) if args[i].startswith("--")}
    ids = collect(args[0], [s.lower() for s in opts.get("--exclude", "").split(",") if s])
    text = "# Mods del modpack oficial (generado por tools/mod_ids.py)\n" + "\n".join(ids) + "\n"
    if "--out" in opts:
        open(opts["--out"], "w", encoding="utf-8", newline="\n").write(text)
    else:
        sys.stdout.write(text)
    print(f"{len(ids)} ids", file=sys.stderr)
