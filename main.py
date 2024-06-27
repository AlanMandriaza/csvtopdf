import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Función para cargar el archivo CSV usando una ventana emergente
def cargar_datos_csv():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter

    archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if archivo:
        df = pd.read_csv(archivo)
        return df
    else:
        messagebox.showerror("Error", "No se seleccionó ningún archivo.")
        return None

# Función para limpiar y obtener la URL base completa
def obtener_url_base(url):
    return url.split('//')[0] + '//' + url.split('//')[1].split('/')[0]

# Función para calcular y graficar las top 10 URLs más bloqueadas
def graficar_top_urls_bloqueadas(df, pdf_file):
    if df is None:
        return
    
    # Filtrar y contar las URLs más bloqueadas
    urls_bloqueadas = df[df['Bloqueado/Permitido'] == 'block']['URL']
    top10_urls_bloqueadas = urls_bloqueadas.apply(obtener_url_base).value_counts().head(10)

    # Preparar los datos para el gráfico circular
    labels = top10_urls_bloqueadas.index
    sizes = top10_urls_bloqueadas.values

    # Definir colores para los segmentos del gráfico circular
    colores = plt.cm.Set3(range(len(labels)))

    # Crear el PDF y guardar el gráfico
    with PdfPages(pdf_file) as pdf:
        fig, ax = plt.subplots(figsize=(8, 8))  # Tamaño del gráfico circular
        
        wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', startangle=140, colors=colores, radius=0.7)

        ax.set_title('Top 10 URLs Más Bloqueadas', fontsize=14, weight='bold')
        
        # Añadir tabla con información detallada debajo del gráfico
        tabla = []
        for i, (label, size) in enumerate(zip(labels, sizes)):
            url_base = label
            veces_bloqueado = size
            porcentaje = autotexts[i].get_text()
            tabla.append([url_base, veces_bloqueado, porcentaje])

        # Mostrar la tabla debajo del gráfico con los colores correspondientes
        table = ax.table(cellText=[[str(item) for item in row] for row in tabla],
                         colLabels=['URL Base', 'Veces Bloqueado', 'Porcentaje'],
                         loc='bottom', cellLoc='center', colColours=['lightgray']*3, bbox=[0, -0.6, 1, 0.4])

        table.auto_set_font_size(False)  # Desactivar ajuste automático del tamaño de la fuente
        table.set_fontsize(10)  # Establecer el tamaño de fuente deseado para la tabla
        table.auto_set_column_width([0, 1, 2])  # Ajustar automáticamente el ancho de las columnas

        # Ajustar el tamaño de fuente global de Matplotlib para la tabla
        plt.rcParams.update({'font.size': 10})

        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

        messagebox.showinfo("Éxito", f"El gráfico de las URLs más bloqueadas se ha generado y guardado en '{pdf_file}'.")

# Función para crear la interfaz gráfica
def crear_interfaz():
    root = tk.Tk()
    root.title("Generador de Gráfico Circular de URLs Más Bloqueadas")

    # Función para manejar el botón de generar gráfico
    def generar_grafico():
        df = cargar_datos_csv()
        if df is not None:
            pdf_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if pdf_file:
                graficar_top_urls_bloqueadas(df, pdf_file)

    # Botón para cargar el archivo CSV y generar gráfico
    btn_cargar = tk.Button(root, text="Cargar Archivo CSV", command=generar_grafico)
    btn_cargar.pack(pady=20)

    root.mainloop()

# Ejecutar la interfaz
if __name__ == "__main__":
    crear_interfaz()
