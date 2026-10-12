# Zeres Network Modpack

Modpacks que descarga el [Zeres Launcher](https://github.com/Zeres-Network/zeres-launcher).

- `manifest.json`: qué versión toca para cada instancia del launcher (`zeres` = Minecraft sin mods, `cobblemon` = Fabric + modpack) y la IP de la network.
- Los `.mrpack` (formato de Modrinth) van como archivos de cada **Release** (`cobblemon-<versión>`). Los mods públicos se bajan del CDN de Modrinth; dentro del pack solo van los propios (ZeresClient).

## Publicar una versión nueva del modpack de Cobblemon
1. `python tools/build_mrpack.py "<carpeta mods>" 0.1.1 cobblemon/zeres-cobblemon-0.1.1.mrpack --optional xaerominimap,xaeroworldmap --exclude axiom,flashback,litematica,malilib,worldedit`
2. `gh release create cobblemon-0.1.1 cobblemon/zeres-cobblemon-0.1.1.mrpack --title "Zeres Cobblemon 0.1.1"`
3. En `manifest.json`: subir `version`, cambiar `mrpack` (URL del release) y `sha1` (lo imprime el paso 1), y hacer push. Los jugadores lo verán como "Actualizar" al abrir el launcher.
