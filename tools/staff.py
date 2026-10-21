"""Códigos de staff del launcher (canal dev). Cada miembro del staff tiene su propio código.

  python tools/staff.py lista
  python tools/staff.py dar <nombre> [--uuid <uuid de su cuenta premium>]   -> crea su código (sale UNA vez por pantalla)
  python tools/staff.py quitar <nombre>                                      -> le quita el acceso (los demás siguen igual)
  python tools/staff.py publicar                                             -> sube manifest.json a GitHub

En manifest.json solo se guarda la huella (sha256) del código, nunca el código. El launcher pide el código en
Ajustes > Launcher y lo compara con la lista "staff" para la cuenta activa (nombre y, si se puso, el uuid premium).
"""
import hashlib, json, os, secrets, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "manifest.json")
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O ni 1/I para no confundirse al copiarlo


def load():
    return json.load(open(MANIFEST, encoding="utf-8"))


def save(m):
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    m = load()
    staff = m.setdefault("staff", [])
    if a[0] == "lista":
        for e in staff:
            print(f"- {e['name']}" + (f" (premium {e['uuid']})" if e.get("uuid") else ""))
        print(f"{len(staff)} en el staff")
    elif a[0] == "dar":
        name = a[1]
        code = "ZERES-" + "-".join("".join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(3))
        entry = {"name": name, "code_sha256": hashlib.sha256(code.encode()).hexdigest()}
        if "--uuid" in a:
            entry["uuid"] = a[a.index("--uuid") + 1].replace("-", "")
        staff[:] = [e for e in staff if e["name"].lower() != name.lower()] + [entry]
        save(m)
        print(f"Código de {name}: {code}")
        print("Apúntalo y pásaselo por privado: no se guarda en ningún sitio. Luego: python tools/staff.py publicar")
    elif a[0] == "quitar":
        name = a[1]
        before = len(staff)
        staff[:] = [e for e in staff if e["name"].lower() != name.lower()]
        save(m)
        print(f"{name}: {'quitado' if len(staff) < before else 'no estaba'}. Luego: python tools/staff.py publicar")
    elif a[0] == "publicar":
        subprocess.run(["git", "add", "manifest.json"], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", "Staff del launcher: lista actualizada"], cwd=ROOT, check=True)
        subprocess.run(["git", "push"], cwd=ROOT, check=True)
        print("Publicado: el launcher lo verá en unos minutos.")
    else:
        sys.exit(__doc__)


main()
