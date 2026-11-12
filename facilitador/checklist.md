# Checklist del facilitador

## Una semana antes

- [ ] Crear una llave de OpenCode Zen por estudiante.
- [ ] Poner tope de gasto a cada llave.
- [ ] Dejar habilitado un solo modelo: **DeepSeek V4.1 Flash** (`deepseek-v4.1-flash`).
- [ ] Probar una llave desde otra laptop, no solo desde la tuya.
- [ ] Mandar `SETUP-ESTUDIANTES.md` 2 o 3 días antes.
- [ ] Publicar el laboratorio en GitHub Pages.
- [ ] Abrir el laboratorio en Chrome, Edge y Safari.
- [ ] Probar las cinco pestañas y el modo `?facilitador=1`.

## El día anterior

- [ ] Correr los datos:

```bash
python generador/generar_datos.py
python -m pytest tests
```

- [ ] Revisar que `laboratorio/data/datos.js` sea el más reciente.
- [ ] Abrir el laboratorio sin internet para confirmar que carga.
- [ ] Probar los prompts de las láminas 12, 13, 16, 17, 19 y 20 con el modelo barato y la carpeta real.
- [ ] Si un prompt falla o inventa, ajustarlo en la lámina y en `AGENTS.md`.

## Durante el taller

- [ ] Compartir pantalla con el laboratorio abierto.
- [ ] Tener a la mano `soluciones.sql`.
- [ ] Recordar: el estudiante le da tareas al agente, no conversa con un chat.
- [ ] A los 3 minutos de la parada 3, avisar que ya se puede ver la solución.
- [ ] En la parada 5, pedir un mensaje de menos de 120 palabras.

## Al terminar

- [ ] Desactivar todas las llaves de OpenCode.
- [ ] Confirmar que ninguna llave quedó activa.
- [ ] Guardar una copia de `laboratorio/data/` si se va a reutilizar el taller.
- [ ] Borrar las llaves del documento o hoja de cálculo donde se repartieron.

## Plan B

Si un estudiante no logra instalar OpenCode:

- [ ] Compartir pantalla con el laboratorio.
- [ ] Pedirle que haga las cinco paradas en el navegador.
- [ ] Darle los prompts en voz alta para que los siga.
- [ ] No detener el taller por una instalación.
