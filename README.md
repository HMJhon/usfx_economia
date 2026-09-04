# Plataforma Web · Facultad de Ciencias Económicas y Administrativas (USFX)

Sistema desarrollado en **Python + Flask** con: publicaciones, cuentas de usuario con roles
(estudiante / administrativo / "El Rey"), actividades con código QR, sistema de puntos,
avatar 3D animado, canje de puntos y panel de administración.

---

## 1. Requisitos previos

Instala esto en tu computadora **antes** de abrir el proyecto:

1. **Python 3.11 o superior** → https://www.python.org/downloads/
   - Al instalar en Windows, marca la casilla **"Add Python to PATH"**.
2. **Visual Studio Code** → https://code.visualstudio.com/
3. En VS Code, instala la extensión **"Python"** de Microsoft (ícono de extensiones a la izquierda, buscar "Python", clic en Instalar).

---

## 2. Abrir el proyecto en Visual Studio Code

1. Descomprime la carpeta `usfx_economia` en tu computadora (por ejemplo en `Documentos`).
2. Abre **Visual Studio Code**.
3. Ve a **Archivo → Abrir carpeta...** y selecciona la carpeta `usfx_economia`.
4. Verás en el panel izquierdo esta estructura:

```
usfx_economia/
├── app.py                 → Backend: rutas y lógica del sistema
├── models.py               → Base de datos (usuarios, publicaciones, actividades, puntos)
├── requirements.txt        → Lista de librerías necesarias
├── templates/               → Todas las páginas HTML
├── static/
│   ├── css/style.css        → Estilos visuales
│   ├── js/avatar3d.js       → Avatar 3D animado (Three.js)
│   ├── uploads/              → Imágenes subidas por el administrador
│   └── qrcodes/               → Códigos QR generados automáticamente
```

---

## 3. Crear el entorno virtual (paso muy importante)

Abre la terminal integrada de VS Code: menú **Terminal → Nueva terminal** (o `Ctrl + ñ` / `Ctrl + Ñ`).

**En Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

**En macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Cuando esté activado, verás `(venv)` al inicio de la línea de la terminal.

> Si Windows te bloquea la activación con un error de "ejecución de scripts deshabilitada", ejecuta primero:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y vuelve a intentar.

En la esquina inferior derecha de VS Code, haz clic donde dice la versión de Python y selecciona el intérprete que dice `('venv': venv)` para que VS Code use ese entorno.

---

## 4. Instalar las librerías del proyecto

Con el entorno virtual activado (`(venv)` visible), ejecuta:

```bash
pip install -r requirements.txt
```

Esto instalará Flask, Flask-SQLAlchemy, Flask-Login, qrcode, Pillow, Werkzeug y gunicorn.

---

## 5. Ejecutar la página

En la misma terminal:

```bash
python app.py
```

Verás algo como:
```
 * Running on http://127.0.0.1:5000
```

Abre tu navegador (Chrome, Edge, Firefox) y entra a:

```
http://127.0.0.1:5000
```

¡Tu página ya está funcionando! La primera vez se crea automáticamente el archivo
`usfx_economia.db` (la base de datos) en la misma carpeta.

También puedes ejecutarlo presionando **F5** en VS Code (elige "Python File" si te lo pregunta).

Para **detener** el servidor: en la terminal presiona `Ctrl + C`.

---

## 6. Crear tu primer usuario ("El Rey")

1. En el navegador, clic en **Registrarse**.
2. Completa el formulario y envíalo.
3. **El primer usuario que se registre en todo el sistema queda automáticamente como
   "El Rey"** (superadministrador), con acceso total: crear publicaciones, actividades,
   generar QR, editar el avatar 3D, cambiar roles de otros usuarios y validar canjes de puntos.
4. Los siguientes usuarios que se registren serán "estudiante" por defecto. Desde el
   **Panel admin → cambiar rol**, "El Rey" puede convertir a cualquiera en "administrativo".

---

## 7. Cómo funciona cada módulo

### Publicaciones
- Menú **Publicaciones → Nueva publicación** (solo admin/El Rey).
- Puedes elegir si es del "Centro de Estudiantes" o de la "Facultad", agregar título,
  texto e imagen.

### Actividades y código QR
- Menú **Actividades → Nueva actividad** (solo admin/El Rey).
- Completa título, descripción, fecha, lugar, costo, beneficios, imagen y cuántos puntos
  otorga.
- Al guardar, el sistema **genera automáticamente un código QR único** y lo muestra en la
  página de detalle de la actividad (`static/qrcodes/`).
- Cualquier estudiante que escanee ese QR con su celular (estando registrado e iniciando
  sesión) gana los puntos automáticamente **una sola vez** y ve aparecer el **avatar 3D
  animado** felicitándolo.
- También pueden ganar puntos extra con el botón **"Compartir en redes"**.

### Sistema de puntos
- Cada acción (escanear QR, compartir) queda registrada en el historial de puntos del
  usuario (visible en **Mi perfil**).

### Canje de puntos
- Menú **Panel admin → Canjear puntos de un estudiante**.
- Solo personal administrativo o "El Rey" pueden ingresar el usuario del estudiante y la
  cantidad de puntos a descontar (por ejemplo, por un descuento en fotocopiadora o
  cafetería).

### Avatar 3D
- Solo "El Rey" puede entrar a **Avatar 3D** en el menú y cambiar los colores y los
  mensajes de felicitación que se muestran al escanear el QR o compartir.

---

## 8. Cómo generar y usar los códigos QR en la vida real

1. Crea la actividad desde el Panel (paso 7). El QR se genera solo.
2. Ve a la página de detalle de la actividad y **descarga o imprime la imagen del QR**
   (clic derecho → Guardar imagen, o toma una captura).
3. Pega o proyecta ese QR físicamente en el evento (afiche, banner, mesa de registro).
4. Los estudiantes lo escanean con la cámara de su celular. El QR los llevará a una
   dirección web de tu sitio; deben iniciar sesión si no lo están, y automáticamente
   sumarán los puntos.

> ⚠️ Importante: el QR generado localmente en `http://127.0.0.1:5000` **solo funciona
> desde tu misma computadora**, porque "127.0.0.1" significa "esta máquina". Para que los
> celulares de los estudiantes puedan escanear el QR y abrir la página, tu sitio debe estar
> publicado en internet (ver el siguiente paso) o, para pruebas rápidas en la misma red
> Wi-Fi, tu computadora y los celulares deben estar conectados a la misma red y debes
> ejecutar la app así:
> ```bash
> python app.py
> ```
> y en `app.py`, en la última línea, cambiar temporalmente a:
> ```python
> app.run(debug=True, host="0.0.0.0", port=5000)
> ```
> Luego, en los celulares, entrar a `http://TU_IP_LOCAL:5000` (tu IP local la ves con
> `ipconfig` en Windows o `ifconfig`/`ip a` en Mac/Linux, algo como `192.168.1.15`).

---

## 9. Cómo subir (publicar) tu página a internet

Para que el QR y el sitio funcionen desde cualquier celular, necesitas subir el proyecto a
un servicio de hosting. La forma más simple y gratuita para empezar es **Render.com**:

### Paso a paso con Render (gratis)

1. Crea una cuenta en https://render.com (puedes entrar con GitHub).
2. Sube tu proyecto a GitHub:
   - Crea una cuenta en https://github.com si no tienes.
   - Crea un repositorio nuevo, por ejemplo `usfx-economia`.
   - En VS Code, abre la terminal dentro de la carpeta del proyecto y ejecuta:
     ```bash
     git init
     git add .
     git commit -m "Primera versión de la plataforma FCEA USFX"
     git branch -M main
     git remote add origin https://github.com/TU_USUARIO/usfx-economia.git
     git push -u origin main
     ```
3. En Render, clic en **New → Web Service** y conecta tu repositorio de GitHub.
4. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (ya incluido en el archivo `Procfile`)
   - **Environment Variable:** agrega `SECRET_KEY` con un valor secreto propio (una
     cadena larga y aleatoria).
5. Clic en **Create Web Service**. Render instalará todo y en unos minutos te dará una
   dirección pública, por ejemplo:
   ```
   https://usfx-economia.onrender.com
   ```
6. Comparte esa dirección o vuelve a generar tus actividades **ya desde el sitio en línea**
   (no desde tu computadora local) para que los códigos QR apunten a esa URL pública y
   funcionen al escanearlos desde cualquier celular.

> Nota sobre el plan gratuito de Render: el disco no es permanente entre reinicios del
> servicio gratuito, así que las imágenes subidas y la base de datos SQLite se pueden
> reiniciar. Para uso real y continuo de la Facultad, se recomienda:
> - Activar un **disco persistente** de Render (plan pagado, económico), o
> - Migrar la base de datos a **PostgreSQL** (Render ofrece una base gratuita) y las
>   imágenes a un servicio como Cloudinary. Si llegas a este punto, puedo ayudarte a
>   adaptar el código.

### Alternativas equivalentes
- **PythonAnywhere** (https://www.pythonanywhere.com) — fácil para principiantes, tiene
  plan gratuito con subdominio propio.
- **Railway** (https://railway.app) — similar a Render, muy simple de conectar con GitHub.

---

## 10. Resumen del flujo completo

1. Instalar Python + VS Code → abrir carpeta del proyecto.
2. Crear y activar entorno virtual → `pip install -r requirements.txt`.
3. `python app.py` → abrir `http://127.0.0.1:5000` para probar en tu computadora.
4. Registrarte primero para ser "El Rey".
5. Crear publicaciones y actividades (los QR se generan solos).
6. Subir el proyecto a GitHub y desplegarlo en Render (o similar) para tener una URL
   pública real.
7. Crear las actividades definitivas ya desde el sitio en línea, imprimir/mostrar sus QR,
   y dejar que los estudiantes escaneen y ganen puntos desde sus celulares.

Cualquier ajuste que necesites (colores institucionales exactos, logo de la Facultad,
más campos, integración con correo institucional, etc.) se puede seguir personalizando
sobre esta misma base.
