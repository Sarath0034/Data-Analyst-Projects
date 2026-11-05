# =============================================================================
# Database Consolidator — SOS Children's Villages Colombia
# =============================================================================

import os
import sys
import datetime
import threading
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1 — STYLES AND COLOR PALETTE
# Palette based on the visual identity of SOS Children's Villages Colombia
# ──────────────────────────────────────────────────────────────────────────────

# ── Corporate colors ──────────────────────────────────────────────────────
AZUL_PRIMARIO  = "#009FE3"   # Main SOS Children's Villages blue
AZUL_OSCURO    = "#007AB8"   # Blue for hover and active states
AZUL_CLARO     = "#EBF7FD"   # Soft blue background for sections
BLANCO         = "#FFFFFF"
GRIS_FONDO     = "#F4F6F9"   # General screen background
GRIS_CLARO     = "#E2E8EF"   # Borders, separators and inactive backgrounds
GRIS_MEDIO     = "#9CA3AF"   # Help and secondary text
GRIS_TEXTO     = "#6B7280"   # Low-priority text
NEGRO_SUAVE    = "#1F2937"   # Primary text
VERDE_EXITO    = "#10B981"   # Successfully completed state
VERDE_CLARO    = "#D1FAE5"   # Background for success messages
ROJO_ERROR     = "#EF4444"   # Critical errors
ROJO_CLARO     = "#FEE2E2"   # Background for error messages
NARANJA_AVISO  = "#F59E0B"   # Warnings and notices

# ── Typography ────────────────────────────────────────────────────────────────
FUENTE_TITULO       = ("Segoe UI", 15, "bold")
FUENTE_SUBTITULO    = ("Segoe UI", 12, "bold")
FUENTE_CUERPO       = ("Segoe UI", 10)
FUENTE_CUERPO_BOLD  = ("Segoe UI", 10, "bold")
FUENTE_PEQUEÑA      = ("Segoe UI", 9)
FUENTE_PEQUEÑA_BOLD = ("Segoe UI", 9, "bold")
FUENTE_MONO         = ("Consolas", 9)   # For the results log

# ── Spacing ─────────────────────────────────────────────────────────────────
PAD_S  = 6
PAD_M  = 12
PAD_L  = 20
PAD_XL = 30


def configurar_estilos(estilo):
    """
    Applies the theme and custom styles to all ttk widgets.
    Must be called once when the application starts.
    """
    estilo.theme_use('clam')

    # ── Primary button ────────────────────────────────────────────────────────
    estilo.configure(
        'Primario.TButton',
        background=AZUL_PRIMARIO, foreground=BLANCO,
        font=FUENTE_CUERPO_BOLD, padding=(20, 9),
        borderwidth=0, focusthickness=0, relief='flat',
    )
    estilo.map('Primario.TButton',
        background=[('active', AZUL_OSCURO), ('disabled', GRIS_CLARO)],
        foreground=[('disabled', GRIS_TEXTO)],
    )

    # ── Secondary button (blue outline) ──────────────────────────────────────
    estilo.configure(
        'Secundario.TButton',
        background=BLANCO, foreground=AZUL_PRIMARIO,
        font=FUENTE_CUERPO_BOLD, padding=(20, 9),
        borderwidth=1, focusthickness=0, relief='solid',
    )
    estilo.map('Secundario.TButton',
        background=[('active', AZUL_CLARO)],
    )

    # ── Danger / delete button ───────────────────────────────────────────
    estilo.configure(
        'Peligro.TButton',
        background=ROJO_CLARO, foreground=ROJO_ERROR,
        font=FUENTE_CUERPO, padding=(12, 7),
        borderwidth=0, focusthickness=0,
    )
    estilo.map('Peligro.TButton',
        background=[('active', '#FECACA')],
    )

    # ── Progress bar ─────────────────────────────────────────────────────
    estilo.configure(
        'SOS.Horizontal.TProgressbar',
        background=AZUL_PRIMARIO, troughcolor=GRIS_CLARO,
        thickness=14, borderwidth=0,
    )

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    estilo.configure(
        'TScrollbar',
        background=GRIS_CLARO, troughcolor=GRIS_FONDO,
        borderwidth=0, arrowsize=12,
    )
    estilo.map('TScrollbar', background=[('active', GRIS_MEDIO)])


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2 — PROCESSING LOGIC
# Reading, concatenation, filtering and export of Excel files
# ──────────────────────────────────────────────────────────────────────────────

# ── Mandatory minimum tabs ─────────────────────────────────────────────
# Each fixed tab has an associated ID column used to filter out empty rows.
# If the value is None (e.g. 'Listas'), it is imported without an ID filter.
PESTANAS_FIJAS = {
    'participantes':   'ID DEL PARTICIPANTE (PRIMARIA)',
    'servicios':       'ID DEL PARTICIPANTE',
    'familia_acogida': 'ID FAMILIA / CASA DE ACOGIDA',
    'familia_origen':  'ID FAMILIA DE ORIGEN EN DFE',
    'defensor':        'ID DEFENSORÍA',
    'Listas':          None,
}


def obtener_pestanas_disponibles(ruta_archivo):
    """
    Reads the sheet names of the first selected file.
    Returns the full list of sheet names.
    """
    try:
        excel = pd.ExcelFile(ruta_archivo, engine='openpyxl')
        return excel.sheet_names
    except Exception as e:
        raise RuntimeError(f"No se pudo leer el archivo: {e}")


def obtener_pestanas_opcionales(ruta_archivo):
    """
    Returns the sheets of the file that are NOT mandatory.
    These are the candidates for optional selection by the user.
    """
    todas = obtener_pestanas_disponibles(ruta_archivo)
    nombres_fijos = set(PESTANAS_FIJAS.keys())
    return [h for h in todas if h not in nombres_fijos]


def procesar(archivos, pestanas_extra_sel, ruta_salida,
             callback_log=None, callback_progreso=None):
    """
    Main processing function.

    Parameters
    ----------
    archivos          : list[str]  — Paths of the .xlsx files to concatenate
    pestanas_extra_sel: list[str]  — Names of the additional sheets selected
    ruta_salida       : str        — Full path of the output file (.xlsx)
    callback_log      : callable   — Function(message, type) to log events
    callback_progreso : callable   — Function(value 0-100) for the progress bar
    """

    def log(msg, tipo='info'):
        if callback_log:
            callback_log(msg, tipo)

    def progreso(val):
        if callback_progreso:
            callback_progreso(val)

    # ── All tabs to process ─────────────────────────────────────────
    pestanas_a_procesar = list(PESTANAS_FIJAS.keys()) + pestanas_extra_sel
    total_pasos = len(archivos) * len(pestanas_a_procesar) + 1
    paso_actual = 0

    acumulados       = {h: [] for h in pestanas_a_procesar}
    archivos_fallidos  = []
    archivos_exitosos  = 0

    # ── File-by-file reading ───────────────────────────────────────────
    for archivo in archivos:
        nombre    = os.path.basename(archivo)
        archivo_ok = True
        log(f"\n📂 Procesando: {nombre}")

        for hoja in pestanas_a_procesar:
            try:
                df = pd.read_excel(archivo, sheet_name=hoja, engine='openpyxl')
                df['archivo_origen'] = nombre
                acumulados[hoja].append(df)
            except Exception as e:
                log(f"   ⚠ Pestaña '{hoja}' no encontrada o con error: {e}", 'aviso')
                archivo_ok = False

            paso_actual += 1
            progreso(int(paso_actual / total_pasos * 85))

        if archivo_ok:
            archivos_exitosos += 1
        else:
            archivos_fallidos.append(nombre)

    # ── Concatenation and cleanup per tab ──────────────────────────────────
    log("\n🔗 Concatenando y limpiando datos...")
    consolidados = {}

    for hoja, lista_df in acumulados.items():
        if not lista_df:
            log(f"   ⚠ Sin datos para '{hoja}', se omite.", 'aviso')
            continue

        combinado = pd.concat(lista_df, ignore_index=True)

        if hoja in PESTANAS_FIJAS:
            # Fixed tabs: filter by ID column
            col_id = PESTANAS_FIJAS[hoja]
            if col_id and col_id in combinado.columns:
                antes    = len(combinado)
                combinado = combinado.dropna(subset=[col_id])
                omitidas  = antes - len(combinado)
                if omitidas > 0:
                    log(f"   ↳ '{hoja}': {omitidas} filas sin ID eliminadas.")
        else:
            # Additional tabs: keep only rows with ≥ 4 filled-in fields
            antes    = len(combinado)
            combinado = combinado.dropna(thresh=4)
            omitidas  = antes - len(combinado)
            if omitidas > 0:
                log(f"   ↳ '{hoja}': {omitidas} filas con menos de 4 campos eliminadas.")

        consolidados[hoja] = combinado
        log(f"   ✔ '{hoja}': {len(combinado):,} filas consolidadas.")

    progreso(90)

    # ── Export to the output file ──────────────────────────────────────
    log(f"\n💾 Guardando archivo de salida...")
    try:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            for hoja, df in consolidados.items():
                df.to_excel(writer, sheet_name=hoja, index=False)

        progreso(100)
        log(f"\n✅ Archivo guardado exitosamente en:", 'exito')
        log(f"   {ruta_salida}", 'exito')

    except Exception as e:
        log(f"\n❌ Error al guardar el archivo: {e}", 'error')
        raise

    # ── Final summary ─────────────────────────────────────────────────────────
    log(f"\n{'─'*50}")
    log(f"📊 Resumen del proceso:")
    log(f"   • Archivos procesados: {archivos_exitosos} de {len(archivos)}")
    log(f"   • Pestañas exportadas: {len(consolidados)}")
    if archivos_fallidos:
        log(f"   • Archivos con errores parciales:", 'aviso')
        for f in archivos_fallidos:
            log(f"     - {f}", 'aviso')
    log(f"{'─'*50}")

    return {
        'exitosos': archivos_exitosos,
        'fallidos': archivos_fallidos,
        'pestanas': list(consolidados.keys()),
        'ruta':     ruta_salida,
    }


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3 — SCREEN 1: SOURCE FOLDER SELECTION
# ──────────────────────────────────────────────────────────────────────────────

class PantallaArchivos(tk.Frame):
    """
    First screen of the flow.
    The user selects a folder and the application automatically detects
    all the .xlsx files it contains. The resulting list is shown for
    review, with the option to exclude individual files before continuing.
    """

    def __init__(self, padre, app):
        super().__init__(padre, bg=BLANCO)
        self.app = app
        self._construir_ui()
        self._cargar_estado()

    def _construir_ui(self):
        """Builds all the visual elements of the screen."""

        # ── Title and description ──────────────────────────────────────────────
        tk.Label(
            self, text="Selección de carpeta fuente",
            font=FUENTE_TITULO, fg=NEGRO_SUAVE, bg=BLANCO
        ).pack(anchor='w', pady=(0, 4))

        tk.Label(
            self,
            text="Selecciona la carpeta que contiene las bases de datos. "
                 "Se detectarán automáticamente todos los archivos .xlsx.",
            font=FUENTE_CUERPO, fg=GRIS_TEXTO, bg=BLANCO,
            wraplength=680, justify='left'
        ).pack(anchor='w', pady=(0, PAD_M))

        # ── Navigation bar (packed first to guarantee space) ─────────────
        tk.Frame(self, bg=GRIS_CLARO, height=1).pack(
            side='bottom', fill='x', pady=(PAD_M, 0)
        )
        nav = tk.Frame(self, bg=BLANCO)
        nav.pack(side='bottom', fill='x', pady=(PAD_S, 0))

        self.lbl_estado = tk.Label(
            nav, text="", font=FUENTE_PEQUEÑA, fg=GRIS_TEXTO, bg=BLANCO
        )
        self.lbl_estado.pack(side='right', padx=PAD_M)

        self.btn_siguiente = ttk.Button(
            nav, text="Siguiente  →",
            style='Primario.TButton',
            command=self._ir_siguiente, state='disabled',
        )
        self.btn_siguiente.pack(side='right')

        # ── Folder selector ───────────────────────────────────────────────
        frame_carpeta = tk.Frame(self, bg=BLANCO)
        frame_carpeta.pack(fill='x', pady=(0, PAD_M))

        self.var_carpeta = tk.StringVar()
        self.entry_carpeta = tk.Entry(
            frame_carpeta, textvariable=self.var_carpeta,
            font=FUENTE_CUERPO, bg=GRIS_FONDO, fg=NEGRO_SUAVE,
            relief='flat', bd=0, highlightthickness=1,
            highlightbackground=GRIS_CLARO, highlightcolor=AZUL_PRIMARIO,
            state='readonly', readonlybackground=GRIS_FONDO,
        )
        self.entry_carpeta.pack(
            side='left', fill='x', expand=True, ipady=8, padx=(0, PAD_S)
        )

        ttk.Button(
            frame_carpeta, text="📂  Seleccionar carpeta",
            style='Primario.TButton',
            command=self._seleccionar_carpeta,
        ).pack(side='right')

        # ── List of files found ─────────────────────────────────────
        self.lbl_contador = tk.Label(
            self, text="Archivos encontrados  (0)",
            font=FUENTE_CUERPO_BOLD, fg=NEGRO_SUAVE, bg=BLANCO
        )
        self.lbl_contador.pack(anchor='w', pady=(0, 6))

        # Bordered frame for the list
        marco = tk.Frame(self, bg=GRIS_CLARO, padx=1, pady=1)
        marco.pack(fill='both', expand=True)

        frame_int = tk.Frame(marco, bg=BLANCO)
        frame_int.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(frame_int)
        scrollbar.pack(side='right', fill='y')

        self.listbox = tk.Listbox(
            frame_int, yscrollcommand=scrollbar.set,
            font=FUENTE_PEQUEÑA, bg=BLANCO, fg=NEGRO_SUAVE,
            selectbackground=AZUL_CLARO, selectforeground=AZUL_PRIMARIO,
            activestyle='none', borderwidth=0, highlightthickness=0,
            relief='flat', selectmode='extended',
        )
        self.listbox.pack(fill='both', expand=True, padx=8, pady=8)
        scrollbar.configure(command=self.listbox.yview)

        # Message shown when the list is empty
        self.lbl_vacio = tk.Label(
            self.listbox,
            text="Selecciona una carpeta para ver los archivos detectados.",
            font=FUENTE_PEQUEÑA, fg=GRIS_MEDIO, bg=BLANCO, justify='center'
        )
        self.lbl_vacio.place(relx=0.5, rely=0.45, anchor='center')

        # Button to exclude individual files
        frame_excluir = tk.Frame(self, bg=BLANCO, pady=PAD_S)
        frame_excluir.pack(fill='x')

        tk.Label(
            frame_excluir,
            text="Selecciona un archivo en la lista y pulsa el botón para excluirlo.",
            font=FUENTE_PEQUEÑA, fg=GRIS_TEXTO, bg=BLANCO
        ).pack(side='left')

        ttk.Button(
            frame_excluir, text="✕  Excluir seleccionado",
            style='Peligro.TButton',
            command=self._excluir_seleccionado,
        ).pack(side='right')

    # ── Folder and file handling ──────────────────────────────────────────

    def _seleccionar_carpeta(self):
        """
        Opens the folder selection dialog (lighter than the file one)
        and automatically scans all the .xlsx files it contains.
        """
        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta con bases de datos",
            initialdir=self.app.estado.get('carpeta_fuente', '') or None,
        )
        if not carpeta:
            return

        # Scan the folder for .xlsx files
        archivos = sorted([
            os.path.join(carpeta, f)
            for f in os.listdir(carpeta)
            if f.endswith('.xlsx') and not f.startswith('~$')  # exclude Excel temporary files
        ])

        if not archivos:
            messagebox.showwarning(
                "Sin archivos",
                f"No se encontraron archivos .xlsx en la carpeta seleccionada:\n{carpeta}"
            )
            return

        # Save the folder and file list in the state
        self.app.estado['carpeta_fuente'] = carpeta
        self.app.estado['archivos']       = archivos
        self.var_carpeta.set(carpeta)
        self._actualizar_lista()

    def _excluir_seleccionado(self):
        """Excludes the file selected in the list from the process."""
        seleccion = list(self.listbox.curselection())
        if not seleccion:
            messagebox.showinfo(
                "Sin selección", "Selecciona un archivo en la lista para excluirlo."
            )
            return
        for i in reversed(seleccion):
            del self.app.estado['archivos'][i]
        self._actualizar_lista()

    def _actualizar_lista(self):
        """Syncs the listbox with the current list of files in the state."""
        self.listbox.delete(0, 'end')
        archivos = self.app.estado['archivos']

        if archivos:
            self.lbl_vacio.place_forget()
            for ruta in archivos:
                self.listbox.insert('end', f"  {os.path.basename(ruta)}")
            self.btn_siguiente.configure(state='normal')
            self.lbl_estado.configure(
                text=f"{len(archivos)} archivo(s) detectado(s)", fg=VERDE_EXITO
            )
        else:
            self.lbl_vacio.place(relx=0.5, rely=0.45, anchor='center')
            self.btn_siguiente.configure(state='disabled')
            self.lbl_estado.configure(text="", fg=GRIS_TEXTO)

        self.lbl_contador.configure(
            text=f"Archivos encontrados  ({len(archivos)})"
        )

    def _cargar_estado(self):
        """Restores the folder and list if the user came back from a later screen."""
        if self.app.estado.get('carpeta_fuente'):
            self.var_carpeta.set(self.app.estado['carpeta_fuente'])
        if self.app.estado['archivos']:
            self._actualizar_lista()

    def _ir_siguiente(self):
        """Checks that there are files and moves on to the tabs screen."""
        if not self.app.estado['archivos']:
            messagebox.showwarning(
                "Sin archivos", "No hay archivos para procesar. Selecciona una carpeta."
            )
            return
        self.app.ir_a_pantalla(2)


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 4 — SCREEN 2: TAB SELECTION
# ──────────────────────────────────────────────────────────────────────────────

class PantallaPestanas(tk.Frame):
    """
    Second screen of the flow.
    Shows the mandatory tabs (locked) and the optional ones
    detected in the first file, with free-choice checkboxes.
    """

    def __init__(self, padre, app):
        super().__init__(padre, bg=BLANCO)
        self.app = app
        self._vars_opcionales = {}   # {sheet_name: BooleanVar}
        self._anim_id = None         # after() ID for the loading animation
        self._construir_ui()
        # Short delay so the screen is painted before reading the file
        self.after(80, self._cargar_pestanas_async)

    def _construir_ui(self):
        """Builds all the visual elements of the screen."""

        # ── Title ────────────────────────────────────────────────────────────
        tk.Label(
            self, text="Selección de pestañas",
            font=FUENTE_TITULO, fg=NEGRO_SUAVE, bg=BLANCO
        ).pack(anchor='w', pady=(0, 4))

        tk.Label(
            self,
            text="Las pestañas obligatorias siempre se incluyen. "
                 "Selecciona las pestañas adicionales que deseas consolidar.",
            font=FUENTE_CUERPO, fg=GRIS_TEXTO, bg=BLANCO,
            wraplength=680, justify='left'
        ).pack(anchor='w', pady=(0, PAD_M))

        # ── Navigation (packed FIRST to guarantee space) ─────────
        tk.Frame(self, bg=GRIS_CLARO, height=1).pack(
            side='bottom', fill='x', pady=(PAD_M, 0)
        )
        nav = tk.Frame(self, bg=BLANCO)
        nav.pack(side='bottom', fill='x', pady=(PAD_S, 0))

        ttk.Button(
            nav, text="←  Atrás",
            style='Secundario.TButton',
            command=lambda: self.app.ir_a_pantalla(1)
        ).pack(side='left')

        ttk.Button(
            nav, text="Siguiente  →",
            style='Primario.TButton',
            command=self._ir_siguiente,
        ).pack(side='right')

        # ── Two columns (packed AFTER to fill the remaining space)
        columnas = tk.Frame(self, bg=BLANCO)
        columnas.pack(fill='both', expand=True)
        columnas.columnconfigure(0, weight=1)
        columnas.columnconfigure(2, weight=1)

        self._construir_seccion_fijas(columnas)

        tk.Frame(columnas, bg=GRIS_CLARO, width=1).grid(
            row=0, column=1, sticky='ns', padx=PAD_L, pady=4
        )

        self._construir_seccion_opcionales(columnas)

    def _construir_seccion_fijas(self, padre):
        """Builds the section for mandatory tabs (not editable)."""
        col = tk.Frame(padre, bg=BLANCO)
        col.grid(row=0, column=0, sticky='nsew', padx=(0, 0))

        enc = tk.Frame(col, bg=AZUL_CLARO, padx=PAD_M, pady=PAD_S)
        enc.pack(fill='x', pady=(0, PAD_S))

        tk.Label(
            enc, text="🔒  Pestañas obligatorias",
            font=FUENTE_CUERPO_BOLD, fg=AZUL_OSCURO, bg=AZUL_CLARO
        ).pack(side='left')

        tk.Label(
            enc, text=str(len(PESTANAS_FIJAS)),
            font=FUENTE_PEQUEÑA_BOLD, fg=BLANCO, bg=AZUL_PRIMARIO,
            padx=8, pady=2
        ).pack(side='right')

        tk.Label(
            col,
            text="Estas pestañas siempre se incluyen en el consolidado.",
            font=FUENTE_PEQUEÑA, fg=GRIS_TEXTO, bg=BLANCO
        ).pack(anchor='w', pady=(0, PAD_S))

        for nombre, col_id in PESTANAS_FIJAS.items():
            fila = tk.Frame(col, bg=BLANCO, pady=3)
            fila.pack(fill='x')

            tk.Label(
                fila, text="✔", font=FUENTE_CUERPO,
                fg=VERDE_EXITO, bg=BLANCO, width=2
            ).pack(side='left')

            tk.Label(
                fila, text=nombre, font=FUENTE_CUERPO,
                fg=NEGRO_SUAVE, bg=BLANCO
            ).pack(side='left', padx=(4, 0))

            if col_id:
                tk.Label(
                    fila,
                    text=f"ID: {col_id[:35]}{'…' if len(col_id) > 35 else ''}",
                    font=FUENTE_PEQUEÑA, fg=GRIS_TEXTO, bg=BLANCO
                ).pack(side='right')

            tk.Frame(col, bg=GRIS_CLARO, height=1).pack(fill='x', pady=(2, 0))

    def _construir_seccion_opcionales(self, padre):
        """Builds the section for additional tabs with checkboxes."""
        col = tk.Frame(padre, bg=BLANCO)
        col.grid(row=0, column=2, sticky='nsew')

        self.enc_opc = tk.Frame(col, bg=GRIS_FONDO, padx=PAD_M, pady=PAD_S)
        self.enc_opc.pack(fill='x', pady=(0, PAD_S))

        tk.Label(
            self.enc_opc, text="☑  Pestañas adicionales",
            font=FUENTE_CUERPO_BOLD, fg=NEGRO_SUAVE, bg=GRIS_FONDO
        ).pack(side='left')

        self.lbl_conteo_opc = tk.Label(
            self.enc_opc, text="0",
            font=FUENTE_PEQUEÑA_BOLD, fg=BLANCO, bg=GRIS_MEDIO,
            padx=8, pady=2
        )
        self.lbl_conteo_opc.pack(side='right')

        tk.Label(
            col,
            text="Selecciona las pestañas extra que quieres consolidar.\n"
                 "Se incluirán filas con al menos 4 campos diligenciados.",
            font=FUENTE_PEQUEÑA, fg=GRIS_TEXTO, bg=BLANCO, justify='left'
        ).pack(anchor='w', pady=(0, PAD_S))

        # Scrollable frame
        marco = tk.Frame(col, bg=GRIS_CLARO, padx=1, pady=1)
        marco.pack(fill='both', expand=True)

        interior = tk.Frame(marco, bg=BLANCO)
        interior.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(interior)
        scrollbar.pack(side='right', fill='y')

        self.canvas_opc = tk.Canvas(
            interior, bg=BLANCO,
            yscrollcommand=scrollbar.set,
            highlightthickness=0,
        )
        self.canvas_opc.pack(side='left', fill='both', expand=True)
        scrollbar.configure(command=self.canvas_opc.yview)

        self.frame_checks = tk.Frame(self.canvas_opc, bg=BLANCO)
        self.canvas_window = self.canvas_opc.create_window(
            (0, 0), window=self.frame_checks, anchor='nw'
        )

        self.frame_checks.bind('<Configure>', self._actualizar_scroll)
        self.canvas_opc.bind('<Configure>', self._ajustar_ancho)

        tk.Label(
            self.frame_checks,
            text="Leyendo pestañas del archivo...",
            font=FUENTE_PEQUEÑA, fg=GRIS_TEXTO, bg=BLANCO, pady=20
        ).pack()

        # Bulk selection buttons
        btns = tk.Frame(col, bg=BLANCO, pady=PAD_S)
        btns.pack(fill='x')

        ttk.Button(
            btns, text="Seleccionar todo",
            style='Secundario.TButton', command=self._seleccionar_todo,
        ).pack(side='left', padx=(0, PAD_S))

        ttk.Button(
            btns, text="Deseleccionar todo",
            style='Secundario.TButton', command=self._deseleccionar_todo,
        ).pack(side='left')

    def _cargar_pestanas_async(self):
        """
        Starts reading the tabs in a secondary thread so the interface is not
        blocked. Shows an animated loading indicator while it works.
        """
        self._iniciar_animacion_carga()
        threading.Thread(target=self._leer_pestanas_hilo, daemon=True).start()

    def _iniciar_animacion_carga(self):
        """Shows animated text with dots while the tabs are being read."""
        self._puntos = 0

        def animar():
            if not self.winfo_exists():
                return
            # Only animate while still in the loading state
            hijos = self.frame_checks.winfo_children()
            if hijos and isinstance(hijos[0], tk.Label):
                self._puntos = (self._puntos + 1) % 4
                hijos[0].configure(
                    text="Leyendo pestañas del archivo" + "." * self._puntos
                )
                self._anim_id = self.after(400, animar)

        self._anim_id = self.after(400, animar)

    def _leer_pestanas_hilo(self):
        """Function running in the secondary thread: reads the file and notifies the UI."""
        primer_archivo = self.app.estado['archivos'][0]
        try:
            opcionales = obtener_pestanas_opcionales(primer_archivo)
            # Always update the UI from the main thread
            self.after(0, lambda: self._poblar_checkboxes(opcionales))
        except Exception as e:
            self.after(0, lambda: self._mostrar_error_carga(str(e)))

    def _mostrar_error_carga(self, mensaje):
        """Shows the tab-reading error in the UI."""
        if self._anim_id:
            self.after_cancel(self._anim_id)
        messagebox.showerror("Error al leer pestañas",
                             f"No se pudieron leer las pestañas:\n{mensaje}")

    def _poblar_checkboxes(self, opcionales):
        """Creates the checkboxes for the detected additional tabs."""
        # Stop the loading animation before modifying the widgets
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None

        for w in self.frame_checks.winfo_children():
            w.destroy()
        self._vars_opcionales.clear()

        if not opcionales:
            tk.Label(
                self.frame_checks,
                text="No se encontraron pestañas adicionales.",
                font=FUENTE_PEQUEÑA, fg=GRIS_TEXTO, bg=BLANCO, pady=20
            ).pack()
            return

        seleccion_previa = set(self.app.estado.get('pestanas_extra', []))

        for nombre in opcionales:
            var = tk.BooleanVar(value=(nombre in seleccion_previa))
            self._vars_opcionales[nombre] = var

            fila = tk.Frame(self.frame_checks, bg=BLANCO, pady=3)
            fila.pack(fill='x', padx=PAD_S)

            tk.Checkbutton(
                fila, text=nombre, variable=var,
                font=FUENTE_CUERPO, fg=NEGRO_SUAVE, bg=BLANCO,
                activebackground=BLANCO, selectcolor=BLANCO,
                command=self._actualizar_conteo,
            ).pack(side='left')

            tk.Frame(self.frame_checks, bg=GRIS_CLARO, height=1).pack(
                fill='x', padx=PAD_S
            )

        self.lbl_conteo_opc.configure(text=str(len(opcionales)), bg=GRIS_MEDIO)
        self._actualizar_conteo()

    def _seleccionar_todo(self):
        for var in self._vars_opcionales.values():
            var.set(True)
        self._actualizar_conteo()

    def _deseleccionar_todo(self):
        for var in self._vars_opcionales.values():
            var.set(False)
        self._actualizar_conteo()

    def _actualizar_conteo(self):
        """Updates the badge with the number of extra tabs selected."""
        n = sum(1 for v in self._vars_opcionales.values() if v.get())
        self.lbl_conteo_opc.configure(
            text=str(n), bg=AZUL_PRIMARIO if n > 0 else GRIS_MEDIO
        )

    def _actualizar_scroll(self, event=None):
        self.canvas_opc.configure(scrollregion=self.canvas_opc.bbox('all'))

    def _ajustar_ancho(self, event):
        self.canvas_opc.itemconfig(self.canvas_window, width=event.width)

    def _ir_siguiente(self):
        """Saves the selection and moves on to the destination screen."""
        self.app.estado['pestanas_extra'] = [
            nombre for nombre, var in self._vars_opcionales.items() if var.get()
        ]
        self.app.ir_a_pantalla(3)


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 5 — SCREEN 3: DESTINATION AND FILE NAME
# ──────────────────────────────────────────────────────────────────────────────

class PantallaDestino(tk.Frame):
    """
    Third screen of the flow.
    The user chooses the destination folder and the output file name.
    Shows a preview of the full path before running.
    """

    def __init__(self, padre, app):
        super().__init__(padre, bg=BLANCO)
        self.app = app
        self._construir_ui()
        self._cargar_estado()

    def _construir_ui(self):
        """Builds all the visual elements of the screen."""

        tk.Label(
            self, text="Destino y nombre del archivo",
            font=FUENTE_TITULO, fg=NEGRO_SUAVE, bg=BLANCO
        ).pack(anchor='w', pady=(0, 4))

        tk.Label(
            self,
            text="Define dónde guardar el archivo consolidado y cómo nombrarlo.",
            font=FUENTE_CUERPO, fg=GRIS_TEXTO, bg=BLANCO,
        ).pack(anchor='w', pady=(0, PAD_L))

        # ── Navigation (first to guarantee space) ──────────────────────
        tk.Frame(self, bg=GRIS_CLARO, height=1).pack(
            side='bottom', fill='x', pady=(PAD_L, 0)
        )
        nav = tk.Frame(self, bg=BLANCO)
        nav.pack(side='bottom', fill='x', pady=(PAD_S, 0))

        ttk.Button(
            nav, text="←  Atrás",
            style='Secundario.TButton',
            command=lambda: self.app.ir_a_pantalla(2)
        ).pack(side='left')

        ttk.Button(
            nav, text="▶  Ejecutar consolidación",
            style='Primario.TButton', command=self._ejecutar,
        ).pack(side='right')

        # ── Configuration summary ──────────────────────────────────────────
        panel_resumen = tk.Frame(self, bg=AZUL_CLARO, padx=PAD_M, pady=PAD_S)
        panel_resumen.pack(fill='x', pady=(0, PAD_L))

        n_archivos = len(self.app.estado['archivos'])
        n_fijas    = len(PESTANAS_FIJAS)
        n_extra    = len(self.app.estado.get('pestanas_extra', []))

        tk.Label(
            panel_resumen,
            text=f"📁 {n_archivos} archivo(s)  •  📋 {n_fijas + n_extra} pestaña(s) "
                 f"({n_fijas} obligatorias + {n_extra} adicionales)",
            font=FUENTE_CUERPO, fg=AZUL_OSCURO, bg=AZUL_CLARO
        ).pack(anchor='w')

        # ── Destination folder ────────────────────────────────────────────────
        tk.Label(
            self, text="Carpeta de destino",
            font=FUENTE_CUERPO_BOLD, fg=NEGRO_SUAVE, bg=BLANCO
        ).pack(anchor='w', pady=(0, PAD_S))

        fila_carpeta = tk.Frame(self, bg=BLANCO)
        fila_carpeta.pack(fill='x', pady=(0, PAD_L))

        self.var_carpeta = tk.StringVar()
        tk.Entry(
            fila_carpeta, textvariable=self.var_carpeta,
            font=FUENTE_CUERPO, bg=GRIS_FONDO, fg=NEGRO_SUAVE,
            relief='flat', bd=0, highlightthickness=1,
            highlightbackground=GRIS_CLARO, highlightcolor=AZUL_PRIMARIO,
            state='readonly', readonlybackground=GRIS_FONDO,
        ).pack(side='left', fill='x', expand=True, ipady=8, padx=(0, PAD_S))

        ttk.Button(
            fila_carpeta, text="📂  Explorar",
            style='Secundario.TButton',
            command=self._seleccionar_carpeta,
        ).pack(side='right')

        # ── File name ────────────────────────────────────────────────
        tk.Label(
            self, text="Nombre del archivo  (.xlsx se agrega automáticamente)",
            font=FUENTE_CUERPO_BOLD, fg=NEGRO_SUAVE, bg=BLANCO
        ).pack(anchor='w', pady=(0, PAD_S))

        self.var_nombre = tk.StringVar()
        self.var_nombre.trace_add('write', self._actualizar_vista_previa)

        tk.Entry(
            self, textvariable=self.var_nombre,
            font=FUENTE_CUERPO, bg=BLANCO, fg=NEGRO_SUAVE,
            relief='flat', bd=0, highlightthickness=1,
            highlightbackground=GRIS_CLARO, highlightcolor=AZUL_PRIMARIO,
        ).pack(fill='x', ipady=8, pady=(0, PAD_S))

        # ── Path preview ───────────────────────────────────────────
        tk.Label(
            self, text="Archivo de salida:",
            font=FUENTE_PEQUEÑA_BOLD, fg=GRIS_TEXTO, bg=BLANCO
        ).pack(anchor='w', pady=(PAD_S, 2))

        self.lbl_preview = tk.Label(
            self, text="—",
            font=FUENTE_MONO, fg=NEGRO_SUAVE, bg=GRIS_FONDO,
            anchor='w', padx=PAD_S, pady=6,
            wraplength=660, justify='left',
        )
        self.lbl_preview.pack(fill='x')

    def _seleccionar_carpeta(self):
        """Opens the folder explorer and saves the selected path."""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if carpeta:
            self.var_carpeta.set(carpeta)
            self.app.estado['carpeta_destino'] = carpeta
            self._actualizar_vista_previa()

    def _actualizar_vista_previa(self, *_):
        """Updates the full-path preview label."""
        carpeta = self.var_carpeta.get()
        nombre  = self.var_nombre.get().strip()

        if carpeta and nombre:
            self.lbl_preview.configure(
                text=os.path.join(carpeta, nombre + '.xlsx'), fg=NEGRO_SUAVE
            )
        elif carpeta:
            self.lbl_preview.configure(
                text="Ingresa el nombre del archivo.", fg=GRIS_TEXTO
            )
        else:
            self.lbl_preview.configure(
                text="Selecciona una carpeta de destino.", fg=GRIS_TEXTO
            )

    def _cargar_estado(self):
        """Pre-fills the fields if there are already values saved in the state."""
        carpeta = self.app.estado.get('carpeta_destino', '')
        nombre  = self.app.estado.get('nombre_archivo', '')

        if carpeta:
            self.var_carpeta.set(carpeta)
        if nombre:
            self.var_nombre.set(nombre)
        else:
            fecha = datetime.datetime.now().strftime('%Y%m%d')
            self.var_nombre.set(f"consolidado_bases_datos_{fecha}")

        self._actualizar_vista_previa()

    def _ejecutar(self):
        """Validates the fields and launches the consolidation process."""
        carpeta = self.var_carpeta.get().strip()
        nombre  = self.var_nombre.get().strip()

        if not carpeta:
            messagebox.showwarning("Falta carpeta",
                                   "Debes seleccionar una carpeta de destino.")
            return
        if not nombre:
            messagebox.showwarning("Falta nombre",
                                   "Debes ingresar un nombre para el archivo.")
            return

        caracteres_invalidos = r'\/:*?"<>|'
        if any(c in nombre for c in caracteres_invalidos):
            messagebox.showwarning(
                "Nombre inválido",
                f"El nombre no puede contener los caracteres: {caracteres_invalidos}"
            )
            return

        ruta_final = os.path.join(carpeta, nombre + '.xlsx')

        if os.path.exists(ruta_final):
            if not messagebox.askyesno(
                "Archivo existente",
                f"Ya existe un archivo con ese nombre:\n{ruta_final}\n\n¿Deseas reemplazarlo?"
            ):
                return

        self.app.estado['carpeta_destino'] = carpeta
        self.app.estado['nombre_archivo']  = nombre
        self.app.estado['ruta_salida']     = ruta_final
        self.app.ir_a_pantalla(4)


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 6 — SCREEN 4: PROGRESS AND RESULTS
# ──────────────────────────────────────────────────────────────────────────────

class PantallaResumen(tk.Frame):
    """
    Fourth screen of the flow.
    Runs the process in a secondary thread so the UI is not blocked.
    Shows a progress bar and a real-time log.
    """

    def __init__(self, padre, app):
        super().__init__(padre, bg=BLANCO)
        self.app = app
        self._proceso_terminado = False
        self._construir_ui()
        self.after(150, self._lanzar_proceso)

    def _construir_ui(self):
        """Builds all the visual elements of the screen."""

        self.lbl_titulo = tk.Label(
            self, text="Consolidando datos...",
            font=FUENTE_TITULO, fg=NEGRO_SUAVE, bg=BLANCO
        )
        self.lbl_titulo.pack(anchor='w', pady=(0, 4))

        self.lbl_subtitulo = tk.Label(
            self, text="El proceso está en curso. Por favor espera.",
            font=FUENTE_CUERPO, fg=GRIS_TEXTO, bg=BLANCO
        )
        self.lbl_subtitulo.pack(anchor='w', pady=(0, PAD_M))

        # ── Progress bar ─────────────────────────────────────────────────
        frame_prog = tk.Frame(self, bg=BLANCO)
        frame_prog.pack(fill='x', pady=(0, PAD_S))

        self.barra = ttk.Progressbar(
            frame_prog, style='SOS.Horizontal.TProgressbar',
            mode='determinate', maximum=100,
        )
        self.barra.pack(fill='x', pady=(0, 4))

        self.lbl_porcentaje = tk.Label(
            frame_prog, text="0%",
            font=FUENTE_PEQUEÑA_BOLD, fg=AZUL_PRIMARIO, bg=BLANCO
        )
        self.lbl_porcentaje.pack(anchor='e')

        # ── Event log ────────────────────────────────────────────────────
        tk.Label(
            self, text="Registro del proceso:",
            font=FUENTE_CUERPO_BOLD, fg=NEGRO_SUAVE, bg=BLANCO
        ).pack(anchor='w', pady=(PAD_S, 4))

        marco_log = tk.Frame(self, bg=GRIS_CLARO, padx=1, pady=1)
        marco_log.pack(fill='both', expand=True)

        frame_log = tk.Frame(marco_log, bg=BLANCO)
        frame_log.pack(fill='both', expand=True)

        scroll_log = ttk.Scrollbar(frame_log)
        scroll_log.pack(side='right', fill='y')

        self.txt_log = tk.Text(
            frame_log, font=FUENTE_MONO, bg=BLANCO, fg=NEGRO_SUAVE,
            state='disabled', borderwidth=0, highlightthickness=0,
            relief='flat', yscrollcommand=scroll_log.set, wrap='word',
        )
        self.txt_log.pack(fill='both', expand=True, padx=8, pady=8)
        scroll_log.configure(command=self.txt_log.yview)

        self.txt_log.tag_configure('info',   foreground=NEGRO_SUAVE)
        self.txt_log.tag_configure('exito',  foreground=VERDE_EXITO)
        self.txt_log.tag_configure('error',  foreground=ROJO_ERROR)
        self.txt_log.tag_configure('aviso',  foreground=NARANJA_AVISO)

        # ── Navigation ────────────────────────────────────────────────────────
        tk.Frame(self, bg=GRIS_CLARO, height=1).pack(fill='x', pady=(PAD_M, 0))

        nav = tk.Frame(self, bg=BLANCO)
        nav.pack(fill='x', pady=(PAD_S, 0))

        self.btn_abrir = ttk.Button(
            nav, text="📂  Abrir carpeta de destino",
            style='Secundario.TButton',
            command=self._abrir_carpeta, state='disabled',
        )
        self.btn_abrir.pack(side='left', padx=(0, PAD_S))

        self.btn_nuevo = ttk.Button(
            nav, text="↺  Nuevo consolidado",
            style='Secundario.TButton',
            command=self._nuevo_proceso, state='disabled',
        )
        self.btn_nuevo.pack(side='left')

        self.btn_cerrar = ttk.Button(
            nav, text="✕  Cerrar",
            style='Primario.TButton',
            command=self.app.destroy, state='disabled',
        )
        self.btn_cerrar.pack(side='right')

    # ── Process in a secondary thread ────────────────────────────────────────────

    def _lanzar_proceso(self):
        """Starts the consolidation process in a secondary thread."""
        threading.Thread(target=self._ejecutar_proceso, daemon=True).start()

    def _ejecutar_proceso(self):
        """Calls the processor and updates the UI safely with .after()."""
        estado = self.app.estado
        try:
            procesar(
                archivos           = estado['archivos'],
                pestanas_extra_sel = estado.get('pestanas_extra', []),
                ruta_salida        = estado['ruta_salida'],
                callback_log       = self._cb_log,
                callback_progreso  = self._cb_progreso,
            )
            self.after(0, self._proceso_exitoso)
        except Exception as e:
            self.after(0, lambda: self._proceso_fallido(str(e)))

    def _cb_log(self, mensaje, tipo='info'):
        self.after(0, lambda m=mensaje, t=tipo: self._escribir_log(m, t))

    def _cb_progreso(self, valor):
        self.after(0, lambda v=valor: self._actualizar_barra(v))

    def _escribir_log(self, mensaje, tipo='info'):
        self.txt_log.configure(state='normal')
        self.txt_log.insert('end', mensaje + '\n', tipo)
        self.txt_log.see('end')
        self.txt_log.configure(state='disabled')

    def _actualizar_barra(self, valor):
        self.barra['value'] = valor
        self.lbl_porcentaje.configure(text=f"{valor}%")

    def _proceso_exitoso(self):
        self.lbl_titulo.configure(text="✅ Consolidación completada", fg=VERDE_EXITO)
        self.lbl_subtitulo.configure(
            text="El archivo fue generado exitosamente.", fg=VERDE_EXITO
        )
        self._actualizar_barra(100)
        self.btn_abrir.configure(state='normal')
        self.btn_nuevo.configure(state='normal')
        self.btn_cerrar.configure(state='normal')

    def _proceso_fallido(self, error):
        self.lbl_titulo.configure(text="❌ Error en el proceso", fg=ROJO_ERROR)
        self.lbl_subtitulo.configure(
            text="Ocurrió un error durante la consolidación. Revisa el log.",
            fg=ROJO_ERROR
        )
        self._escribir_log(f"\n❌ Error: {error}", 'error')
        self.btn_nuevo.configure(state='normal')
        self.btn_cerrar.configure(state='normal')

    def _abrir_carpeta(self):
        """Opens the destination folder in the operating system's file explorer."""
        carpeta = self.app.estado.get('carpeta_destino', '')
        if not carpeta or not os.path.exists(carpeta):
            return
        sistema = platform.system()
        if sistema == 'Windows':
            os.startfile(carpeta)
        elif sistema == 'Darwin':
            subprocess.Popen(['open', carpeta])
        else:
            subprocess.Popen(['xdg-open', carpeta])

    def _nuevo_proceso(self):
        """Restarts the application from screen 1 with a clean state."""
        self.app.estado = {
            'archivos': [], 'pestanas_extra': [],
            'carpeta_fuente': '', 'carpeta_destino': '',
            'nombre_archivo': '', 'ruta_salida': '',
        }
        self.app.ir_a_pantalla(1)


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 7 — MAIN WINDOW AND NAVIGATION
# ──────────────────────────────────────────────────────────────────────────────

# Definition of the flow steps
PASOS = [
    (1, "Archivos",  PantallaArchivos),
    (2, "Pestañas",  PantallaPestanas),
    (3, "Destino",   PantallaDestino),
    (4, "Resultado", PantallaResumen),
]


class AplicacionConcatenador(tk.Tk):
    """
    Main application window.
    Manages navigation between screens, the shared state
    and the common elements: header and step indicator.
    """

    def __init__(self):
        super().__init__()

        self.title("Consolidador de Bases de Datos — Aldeas Infantiles SOS")
        self.geometry("820x640")
        self.minsize(720, 560)
        self.configure(bg=BLANCO)
        self.resizable(True, True)
        self._centrar_ventana(820, 640)

        self._estilo = ttk.Style(self)
        configurar_estilos(self._estilo)

        # ── State shared across all screens ───────────────────────
        self.estado = {
            'archivos':        [],
            'pestanas_extra':  [],
            'carpeta_fuente':  '',    # Folder scanned in screen 1
            'carpeta_destino': '',
            'nombre_archivo':  '',
            'ruta_salida':     '',
        }

        self._construir_encabezado()
        self._construir_indicador_pasos()
        self._construir_contenido()

        self._pantalla_actual = None
        self.ir_a_pantalla(1)

    def _centrar_ventana(self, ancho, alto):
        """Positions the window in the center of the main monitor."""
        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto  // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _construir_encabezado(self):
        """Builds the top header with logo and title."""
        encabezado = tk.Frame(self, bg=AZUL_PRIMARIO, height=68)
        encabezado.pack(fill='x')
        encabezado.pack_propagate(False)

        logo_img = self._cargar_logo()
        if logo_img:
            self._logo_ref = logo_img
            tk.Label(
                encabezado, image=logo_img,
                bg=AZUL_PRIMARIO, padx=16
            ).pack(side='left', pady=8)
        else:
            tk.Label(
                encabezado, text="ALDEAS INFANTILES SOS",
                font=("Segoe UI", 11, "bold"),
                fg=BLANCO, bg=AZUL_PRIMARIO, padx=16
            ).pack(side='left', pady=8)

        tk.Frame(encabezado, bg='#4DC3EF', width=1).pack(
            side='left', fill='y', pady=14
        )
        tk.Label(
            encabezado, text="  Consolidador de Bases de Datos",
            font=("Segoe UI", 14, "bold"),
            fg=BLANCO, bg=AZUL_PRIMARIO
        ).pack(side='left', padx=PAD_M)

    def _cargar_logo(self):
        """
        Tries to load the logo from the 'assets' folder next to the script.
        Returns a PhotoImage, or None if it is not found or Pillow is not installed.
        """
        try:
            from PIL import Image, ImageTk
            ruta = self._ruta_recurso(os.path.join("assets", "logo.jpg"))
            img = Image.open(ruta)
            img.thumbnail((210, 50))
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _ruta_recurso(self, ruta_relativa):
        """
        Resolves resource paths compatible with PyInstaller.
        In executable mode it uses the _MEIPASS temporary directory.
        """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, ruta_relativa)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), ruta_relativa)

    def _construir_indicador_pasos(self):
        """Builds the visual progress indicator with circles and connectors."""
        self._frame_indicador = tk.Frame(self, bg=GRIS_FONDO)
        self._frame_indicador.pack(fill='x')

        self._canvas_pasos = tk.Canvas(
            self._frame_indicador,
            height=56, bg=GRIS_FONDO, highlightthickness=0
        )
        self._canvas_pasos.pack(fill='x')
        self._canvas_pasos.bind('<Configure>', lambda e: self._dibujar_pasos())
        self._paso_activo = 1

    def _dibujar_pasos(self):
        """Draws the circles, lines and labels of the step indicator."""
        c = self._canvas_pasos
        c.delete('all')

        ancho = c.winfo_width()
        if ancho < 10:
            return

        cy     = 28
        radio  = 14
        n      = len(PASOS)
        margen = 80
        paso_x = (ancho - 2 * margen) / (n - 1)
        posiciones = [margen + i * paso_x for i in range(n)]

        for i, (num, nombre, _) in enumerate(PASOS):
            x = posiciones[i]

            # Connector line
            if i < n - 1:
                color_linea = VERDE_EXITO if num < self._paso_activo else GRIS_CLARO
                c.create_line(
                    x + radio, cy, posiciones[i + 1] - radio, cy,
                    fill=color_linea, width=2
                )

            # Step state
            if num < self._paso_activo:
                estado = 'completado'
            elif num == self._paso_activo:
                estado = 'activo'
            else:
                estado = 'pendiente'

            # Step circle
            if estado == 'activo':
                c.create_oval(
                    x - radio, cy - radio, x + radio, cy + radio,
                    fill=AZUL_PRIMARIO, outline=AZUL_PRIMARIO
                )
                c.create_text(x, cy, text=str(num), fill=BLANCO,
                              font=("Segoe UI", 9, "bold"))
            elif estado == 'completado':
                c.create_oval(
                    x - radio, cy - radio, x + radio, cy + radio,
                    fill=VERDE_EXITO, outline=VERDE_EXITO
                )
                c.create_text(x, cy, text="✓", fill=BLANCO,
                              font=("Segoe UI", 9, "bold"))
            else:
                c.create_oval(
                    x - radio, cy - radio, x + radio, cy + radio,
                    fill=GRIS_FONDO, outline=GRIS_CLARO, width=2
                )
                c.create_text(x, cy, text=str(num), fill=GRIS_MEDIO,
                              font=("Segoe UI", 9))

            # Step label
            color_texto = (
                AZUL_PRIMARIO if estado == 'activo'
                else VERDE_EXITO if estado == 'completado'
                else GRIS_TEXTO
            )
            fuente_texto = (
                ("Segoe UI", 8, "bold") if estado == 'activo'
                else ("Segoe UI", 8)
            )
            c.create_text(x, cy + radio + 10,
                          text=nombre, fill=color_texto, font=fuente_texto)

    def _construir_contenido(self):
        """Creates the container frame for the flow screens."""
        self._frame_contenido = tk.Frame(self, bg=BLANCO)
        self._frame_contenido.pack(fill='both', expand=True,
                                   padx=PAD_M * 2, pady=PAD_M)

    def ir_a_pantalla(self, numero):
        """
        Destroys the current screen, creates the new one and
        updates the step indicator.
        """
        if self._pantalla_actual:
            self._pantalla_actual.destroy()

        self._paso_activo = numero
        self.after(10, self._dibujar_pasos)

        mapa = {num: clase for num, _, clase in PASOS}
        clase = mapa.get(numero)
        if clase:
            self._pantalla_actual = clase(self._frame_contenido, self)
            self._pantalla_actual.pack(fill='both', expand=True)


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AplicacionConcatenador()
    app.mainloop()
