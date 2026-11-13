# Web del proyecto EVEREST

Web del proyecto **EVEREST** (*Essential Variables for the rEmote characterisation and monitoRing of mountain EcosystemS along a biogeographical gradienT*).

- Referencia: PID2023-151939OB-I00.
- Financiación: MICIU/AEI/10.13039/501100011033 y FEDER, UE.
- Coordinación: Universidad de Granada.

Es una web estática con los mismos apartados que la de [PRESINMED](https://presinmed.eu). Se publica en Netlify, y cada cambio que llega a la rama `main` se publica automáticamente.

## Cómo cambiar un texto

Todo el contenido está en `_build/build.py`: proyecto, tareas, parques, equipo, noticias, publicaciones y MonitorEO.

Varias personas editan la web a la vez, así que **nunca se trabaja directamente en `main`**. Cada cambio va en su propia rama y entra en `main` mediante un *pull request*.

1. Parte de un `main` actualizado y crea una rama con un nombre corto que describa el cambio:

   ```
   git switch main
   git pull
   git switch -c nueva-noticia-taller
   ```

2. Edita `_build/build.py` y regenera las páginas:

   ```
   python _build/build.py
   ```

3. Guarda el cambio y sube la rama:

   ```
   git add -A
   git commit -m "Añade la noticia del taller nacional"
   git push -u origin nueva-noticia-taller
   ```

4. En GitHub, abre un *pull request* de tu rama hacia `main`. Cuando la otra persona lo revise, se fusiona y Netlify publica la nueva versión en un par de minutos.

Si dos ramas tocan la misma parte de `build.py`, GitHub avisará de un conflicto al fusionar la segunda. Las páginas `.html` se pueden resolver volviendo a ejecutar `python _build/build.py` sobre la rama actualizada.

No edites los `.html` a mano: el script los sobrescribe.

Por ejemplo, para añadir una noticia, inserta una línea al principio de la lista `NEWS`.

## Estructura

| Ruta | Contenido |
|---|---|
| `index.html` | Portada |
| `monitoreo.html` | MonitorEO |
| `proyecto/` | Resumen y objetivos, Variables esenciales, Tareas y T1–T5 |
| `parques/` | Mapa y resumen, y una ficha por parque |
| `equipo/` | Miembros e Instituciones |
| `noticias/` | Noticias |
| `resultados/` | Publicaciones, Datos abiertos, y Recursos y divulgación |
| `galeria.html` | Galería |
| `contacto.html` | Contacto |
| `assets/` | Estilos y comportamiento compartidos |
| `img/` | Logos de financiación, favicon y fotos |

## Publicidad de la AEI

Todas las páginas llevan los logos y el texto de financiación en la franja blanca bajo el menú y en el pie.
En la portada se ven sin desplazarse.
No los quites al cambiar el diseño.

## Fotos

Las fotos de `img/fotos/` proceden de Wikimedia Commons.
Cada una muestra su autoría y su licencia (CC BY, CC BY-SA o atribución Copernicus), como exigen esas licencias.
Para sustituir una por una foto propia del equipo, guárdala con el mismo nombre en `img/fotos/` y cambia la autoría en `PHOTOS` o `PARKS`, dentro de `build.py`.
