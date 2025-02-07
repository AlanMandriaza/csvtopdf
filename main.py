import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import Counter
import re

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

# Función para extraer palabras clave de las URLs de búsqueda de Google
def extraer_palabras_google(url):
    match = re.search(r'q=([^&]*)', url)
    if match:
        query = match.group(1)
        palabras = query.split('+')
        return [palabra.lower() for palabra in palabras]
    return []

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
            color = colores[i]  # Obtener el color correspondiente del gráfico

            # Agregar fila a la tabla con el color correspondiente
            tabla.append([url_base, veces_bloqueado, porcentaje, color])

        # Mostrar la tabla debajo del gráfico con los colores correspondientes
        table_data = [[row[0], row[1], row[2]] for row in tabla]
        cell_colours = [[row[3]] * 3 for row in tabla]  # Repetir el color para las 3 columnas de cada fila

        table = ax.table(cellText=table_data,
                         colLabels=['Dominio', 'Veces Bloqueado', '%'],
                         loc='bottom', cellLoc='center', cellColours=cell_colours, bbox=[0, -0.6, 1, 0.4])

        table.auto_set_font_size(False)  # Desactivar ajuste automático del tamaño de la fuente
        table.set_fontsize(10)  # Establecer el tamaño de fuente deseado para la tabla
        table.auto_set_column_width([0, 1, 2])  # Ajustar automáticamente el ancho de las columnas

        # Ajustar el tamaño de fuente global de Matplotlib para la tabla
        plt.rcParams.update({'font.size': 10})

        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

        # Extraer palabras clave y calcular las top 10 más buscadas en Google
        palabras_google = []
        
        for index, row in df.iterrows():
            palabras = extraer_palabras_google(row['URL'])
            palabras_google.extend(palabras)
        
        top10_palabras_google = Counter(palabras_google).most_common(10)

        # Mostrar las top 10 palabras más buscadas en Google
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis('off')
        table_data = [['Palabra', 'Frecuencia']] + [[palabra, freq] for palabra, freq in top10_palabras_google]
        table = ax.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.auto_set_column_width([0, 1])

        ax.set_title('Top 10 Palabras Más Buscadas en Google', fontsize=14, weight='bold')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

        messagebox.showinfo("Éxito", f"Gráfico generado, cierre la ventana para continuar. '{pdf_file}'.")

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
