# Antes del taller · instala OpenCode

Mándalo 2 o 3 días antes. Toma unos 15 minutos.

Vas a usar OpenCode Desktop. No necesitas terminal. Si algo falla, tienes un plan B al final.

## 1. Recibe tu llave

El facilitador te manda una llave de OpenCode Zen con tope de gasto.
No la compartas. Solo sirve para este taller.

## 2. Instala OpenCode

### Windows

1. Descarga el instalador:
   - Windows normal (Intel o AMD): https://opencode.ai/update/api/latest/desktop/opencode/opencode-desktop-win-x64.exe
   - Windows ARM: https://opencode.ai/update/api/latest/desktop/opencode/opencode-desktop-win-arm64.exe
2. Abre el archivo y sigue el instalador.
3. Abre **OpenCode** desde el menú de inicio.

### Mac

1. Descarga el instalador:
   - Mac con chip Apple (M1, M2, M3…): https://opencode.ai/update/api/latest/desktop/opencode/opencode-desktop-mac-arm64.dmg
   - Mac con Intel: https://opencode.ai/update/api/latest/desktop/opencode/opencode-desktop-mac-x64.dmg
2. Abre el `.dmg` y arrastra OpenCode a **Aplicaciones**.
3. Abre **OpenCode** desde Aplicaciones.
4. Si macOS dice que no puede abrir la app, haz clic derecho sobre el ícono y elige **Abrir**.

## 3. Conecta tu llave

1. Dentro de OpenCode, abre la paleta de comandos.
2. Escribe `/connect` y elige **OpenCode**.
3. Pega la llave que te mandó el facilitador.
4. Abre `/models` y elige **DeepSeek V4.1 Flash**.

Si no ves esa opción, cierra OpenCode, vuelve a abrirlo y revisa que la llave esté bien pegada, sin espacios.

## 4. Abre la carpeta

1. En OpenCode, elige **File → Open Folder**.
2. Busca la carpeta `carpeta-estudiante` que te mandó el facilitador.
3. Ábrela. Deben aparecer estos archivos:
   - `AGENTS.md`
   - `opencode.json`
   - `clientes.csv`
   - `pedidos.csv`
   - `reglas.csv`
   - `LEEME.md`

No abras la carpeta desde otro lado. El agente solo debe trabajar ahí.

## 5. Prueba

Escribe este mensaje en OpenCode:

> ¿Qué archivos hay aquí?

El agente debe contestar con la lista de archivos. Si contesta, ya estás listo.

Después pídele:

> Lee los tres CSV y escribe `diccionario.md`.

Si el agente intenta abrir archivos de otras carpetas, dile: “No salgas de esta carpeta”.

## Plan B

Si no logras instalar OpenCode, no te preocupes.
Sigue la pantalla del facilitador y usa solo el laboratorio web:

https://TU-USUARIO.github.io/taller-gobierno-datos/

El facilitador te pasa la dirección exacta el día del taller.
En el laboratorio haces las mismas cinco paradas, sin instalar nada.

## Si algo no funciona

- **La llave no funciona:** revisa que no tenga espacios al inicio o al final. Si sigue, avisa al facilitador.
- **No aparece DeepSeek V4.1 Flash:** abre `/models` otra vez. Si no sale, cierra sesión y vuelve a conectar la llave.
- **El agente quiere usar internet o salir de la carpeta:** dile “Trabaja solo con los archivos de esta carpeta”.
- **No abre el laboratorio:** usa Chrome, Edge o Safari actualizado. Si estás en el celular, mejor usa una laptop.
