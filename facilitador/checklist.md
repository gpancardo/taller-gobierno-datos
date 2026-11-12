# Checklist del facilitador

## Una semana antes

- [ ] Contratar **OpenCode Go Teams** (20 USD por persona al mes, cada miembro con su propio límite) y crear una llave o invitación por estudiante. La documentación no dice si se pueden poner topes por llave: **por confirmar** en la consola.
- [ ] En la consola, **Settings → Privacy → Regions**: elegir **Global**. Sin eso DeepSeek V4.1 Flash no está disponible.
- [ ] Modelo del taller: **DeepSeek V4.1 Flash** (`opencode-go/deepseek-v4.1-flash`, ya fijado en `opencode.json`).
- [ ] Probar una llave desde otra laptop, no solo desde la tuya.
- [ ] Mandar `SETUP-ESTUDIANTES.md` y la carpeta del taller (zip) 2 o 3 días antes.
- [ ] Abrir el laboratorio en Chrome, Edge y Safari.
- [ ] Probar las cinco pestañas y el modo `?facilitador=1`.

## El día anterior

- [ ] Correr los datos:

```bash
python generador/generar_datos.py
python -m pytest tests
```

- [ ] Revisar que `laboratorio/data/datos.js` sea el más reciente.
- [ ] Abrir `laboratorio/index.html` con doble clic y sin internet para confirmar que carga.
- [ ] Probar los prompts de las láminas 12, 13, 16, 17, 19 y 20 con el modelo barato y la carpeta real.
- [ ] Si un prompt falla o inventa, ajustarlo en la lámina y en `AGENTS.md`.

## Durante el taller

- [ ] Compartir pantalla con el laboratorio abierto.
- [ ] Tener a la mano `soluciones.sql`.
- [ ] Recordar: el estudiante le da tareas al agente, no conversa con un chat.
- [ ] A los 3 minutos de la parada 3, avisar que ya se puede ver la solución.
- [ ] En la parada 5, pedir un mensaje de menos de 120 palabras.

## Al terminar

- [ ] Cancelar la suscripción de Go Teams y desactivar todas las llaves.
- [ ] Confirmar que ninguna llave quedó activa.
- [ ] Guardar una copia de `laboratorio/data/` si se va a reutilizar el taller.
- [ ] Borrar las llaves del documento o hoja de cálculo donde se repartieron.

## Plan B

Si un estudiante no logra instalar OpenCode:

- [ ] Compartir pantalla con el laboratorio.
- [ ] Pedirle que haga las cinco paradas en el navegador.
- [ ] Darle los prompts en voz alta para que los siga.
- [ ] No detener el taller por una instalación.
