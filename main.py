import flet as ft
import os
import sys

# Directorio donde se guardará el archivo .desktop para el usuario actual
DESTINO_DIR = os.path.expanduser("~/.local/share/applications/")

# Asegurarse de que el directorio de destino exista
os.makedirs(DESTINO_DIR, exist_ok=True)


# --- Lógica de la Aplicación ---
def generate_desktop_file(
    page: ft.Page,
    name,
    exec_command,
    icon,
    comment,
    terminal_val,
    success_modal,
    modal_content_text,
    modal_path_text,
):
    """Construye y guarda el archivo .desktop."""

    # 1. Validación de campos obligatorios
    if not name or not exec_command:
        page.snack_bar = ft.SnackBar(
            ft.Text("❌ Error: Los campos 'Nombre' y 'Comando' son obligatorios."),
            bgcolor=ft.Colors.RED_700,
        )
        page.snack_bar.open = True
        page.update()
        return

    # 2. Construir el contenido y nombre del archivo
    # Nombre del archivo: Limpio, en minúsculas y reemplaza espacios por guiones bajos
    safe_file_name = (
        "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in name)
        .strip()
        .replace(" ", "_")
        .lower()
    )
    if not safe_file_name:
        safe_file_name = "custom-app"
    file_name = f"{safe_file_name}.desktop"
    ruta_completa = os.path.join(DESTINO_DIR, file_name)

    desktop_content = f"""[Desktop Entry]
Type=Application
Name={name}
Comment={comment if comment else name}
Exec={exec_command}
Icon={icon}
Terminal={terminal_val}
Categories=Utility;
StartupNotify=true
"""

    # 3. Guardar el archivo
    try:
        with open(ruta_completa, "w") as f:
            f.write(desktop_content)

        # 4. Dar permisos de ejecución
        os.chmod(ruta_completa, 0o755)

        # 5. Actualizar contenido del modal y notificar éxito
        modal_content_text.value = f"El lanzador '{name}' se ha creado correctamente."
        modal_path_text.value = f"📁 Ubicación: {ruta_completa}"
        return True

    except Exception as e:
        page.snack_bar = ft.SnackBar(
            ft.Text(f"❌ Error al guardar el archivo: {e}"), bgcolor=ft.Colors.RED_700
        )
        page.snack_bar.open = True
        page.update()
        return False


# --- Interfaz de Usuario (UI) de Flet ---
def main(page: ft.Page):
    page.title = "Generador de Lanzadores .desktop"
    page.vertical_alignment = ft.CrossAxisAlignment.START
    # Estableciendo tamaño fijo
    page.window_width = 500
    page.window_height = 600
    page.window_resizable = False  # Deshabilita el redimensionamiento
    # Centrar la ventana programáticamente no está disponible en esta versión

    page.theme_mode = ft.ThemeMode.SYSTEM  # Adapta el tema a Zorin OS (oscuro o claro)
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Configuraciones para reducir errores de Flutter
    page.padding = 0
    page.spacing = 0

    # Modal de confirmación
    def close_success_modal(e):
        success_modal.open = False
        page.update()

    def open_applications_folder(e):
        try:
            os.system(f"xdg-open {DESTINO_DIR}")
        except Exception as ex:
            print(f"Error al abrir la carpeta: {ex}")
        success_modal.open = False
        page.update()

    success_modal = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=30),
                ft.Text(
                    "¡Éxito!", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD, size=20
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        content=ft.Column(
            controls=[
                modal_content_text := ft.Text(
                    "El lanzador se ha creado correctamente.",
                    text_align=ft.TextAlign.CENTER,
                    size=16,
                ),
                modal_path_text := ft.Text(
                    "📁 Ubicación: ~/.local/share/applications/",
                    text_align=ft.TextAlign.CENTER,
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Text(
                    "Podrás encontrarlo en el menú de aplicaciones.",
                    text_align=ft.TextAlign.CENTER,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
        actions=[
            ft.TextButton(
                "Abrir Carpeta",
                on_click=open_applications_folder,
                style=ft.ButtonStyle(
                    color=ft.Colors.BLUE,
                    bgcolor=ft.Colors.BLUE_100,
                ),
            ),
            ft.TextButton(
                "¡Perfecto!",
                on_click=close_success_modal,
                style=ft.ButtonStyle(
                    color=ft.Colors.GREEN,
                    bgcolor=ft.Colors.GREEN_100,
                ),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    # Inicializar el diálogo de selección de archivos (picker)
    def handle_file_picker_result(e: ft.FilePickerResultEvent):
        if e.files and e.files[0].path:
            # Si se seleccionó un archivo, actualizar el campo de texto correcto
            if e.control.data == "exec":
                exec_input.value = e.files[0].path
            elif e.control.data == "icon":
                icon_input.value = e.files[0].path
            page.update()
        elif e.path:  # Caso para un directorio
            if e.control.data == "exec":
                exec_input.value = e.path
            page.update()

    file_picker_exec = ft.FilePicker(on_result=handle_file_picker_result, data="exec")
    file_picker_icon = ft.FilePicker(on_result=handle_file_picker_result, data="icon")
    page.overlay.extend([file_picker_exec, file_picker_icon, success_modal])

    # --- CAMPOS DE ENTRADA ---

    # 1. Nombre
    name_input = ft.TextField(
        label="Nombre de la Aplicación (Name=)",
        hint_text="Ej: Mi Juego Retro",
        icon=ft.Icons.APPS_OUTLINED,
    )

    # 2. Comando (Exec)
    exec_input = ft.TextField(
        label="Comando a Ejecutar (Exec=)",
        hint_text="/home/user/app/AppExecutable o 'firefox'",
        icon=ft.Icons.PLAY_ARROW,
    )

    # Botón de buscar ejecutable
    browse_exec_button = ft.ElevatedButton(
        "Buscar Ejecutable...",
        icon=ft.Icons.SEARCH,
        on_click=lambda e: file_picker_exec.pick_files(allow_multiple=False),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.all(12)
        ),
    )

    # 3. Icono (Icon)
    icon_input = ft.TextField(
        label="Icono (Icon=)",
        hint_text="Ej: firefox o /home/user/icons/mi-app.png",
        icon=ft.Icons.IMAGE_OUTLINED,
    )

    # Botón de buscar icono
    browse_icon_button = ft.ElevatedButton(
        "Buscar Archivo de Icono...",
        icon=ft.Icons.IMAGE,
        on_click=lambda e: file_picker_icon.pick_files(
            allow_multiple=False, allowed_extensions=["png", "svg", "jpg", "jpeg"]
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.all(12)
        ),
    )

    # 4. Comentario
    comment_input = ft.TextField(
        label="Comentario (Comment=) [Opcional]",
        hint_text="Una descripción breve de la aplicación.",
        icon=ft.Icons.COMMENT,
    )

    # 5. Tipo (Terminal)
    terminal_dropdown = ft.Dropdown(
        label="Tipo de Aplicación (Terminal=)",
        value="false",
        options=[
            ft.dropdown.Option("false", "Aplicación Gráfica (false)"),
            ft.dropdown.Option("true", "Aplicación de Terminal (true)"),
        ],
        icon=ft.Icons.SETTINGS_APPLICATIONS_OUTLINED,
    )

    # --- BOTÓN DE GENERAR ---
    def on_generate_click(e):
        success = generate_desktop_file(
            page,
            name_input.value.strip(),
            exec_input.value.strip(),
            icon_input.value.strip(),
            comment_input.value.strip(),
            terminal_dropdown.value,
            success_modal,
            modal_content_text,
            modal_path_text,
        )

        # Limpiar campos y mostrar modal al generar con éxito
        if success:
            name_input.value = ""
            exec_input.value = ""
            icon_input.value = ""
            comment_input.value = ""
            terminal_dropdown.value = "false"

            # Mostrar modal de confirmación
            success_modal.open = True
            page.update()

    # Se ajusta el width para que quede centrado si la ventana es más ancha que 460
    generate_button = ft.ElevatedButton(
        "✨ Generar y Guardar Lanzador .desktop",
        on_click=on_generate_click,
        icon=ft.Icons.SAVE,
        style=ft.ButtonStyle(
            # Corregido: Eliminado MaterialState y uso directo de ft.colors (minúsculas).
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.all(15),
        ),
        width=page.window_width - 30,  # Ajuste de ancho para centrar
    )

    # --- ESTRUCTURA DE LA PÁGINA ---
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Generador .desktop", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Crea lanzadores para tus aplicaciones que no aparecen en el menú.",
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    # Más espacio entre el encabezado y el contenido principal
                    ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
                    # Información Básica
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "🚀 Información Básica",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    name_input,
                                    # Espacio extra entre campos para evitar que se vean pegados
                                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                                    exec_input,
                                    ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                                    browse_exec_button,
                                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                                    icon_input,
                                    ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                                    browse_icon_button,
                                ],
                                spacing=8,  # Espaciado aumentado DENTRO del grupo
                            ),
                        ),
                        elevation=4,  # Aumento de elevación para mejor separación visual
                    ),
                    # Más espacio entre los dos grupos de tarjetas
                    ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
                    # Opciones Adicionales
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "⚙️ Opciones Adicionales",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    comment_input,
                                    ft.Divider(height=12, color=ft.Colors.TRANSPARENT),
                                    terminal_dropdown,
                                ],
                                spacing=8,
                            ),
                        ),
                        elevation=4,
                    ),
                    # Espacio final antes del botón
                    ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                    generate_button,
                ],
                spacing=8,  # Espaciado mejorado para el layout principal
            ),
            padding=ft.padding.all(15),
        )
    )


if __name__ == "__main__":
    try:
        # Configuraciones básicas para reducir errores
        os.environ.setdefault("FLET_WEB_RENDERER", "canvaskit")

        ft.app(target=main)
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)
