import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self):  # solo argumentos por defecto
        gr.sync_block.__init__(
            self,
            name='Averange time',   # Nombre que aparecerá en GRC
            in_sig=[np.float32],
            out_sig=[np.float32, np.float32, np.float32, np.float32, np.float32]
        )
        # Inicialización de acumuladores
        self.acum_anterior = 0.0
        self.acum_anterior1 = 0.0
        self.acum_anterior2 = 0.0
        self.Ntotales = 0

    def work(self, input_items, output_items):
        x = input_items[0]  # Señal de entrada
        y0 = output_items[0]  # Promedio acumulado
        y1 = output_items[1]  # Media (esperanza matemática)
        y2 = output_items[2]  # RMS
        y3 = output_items[3]  # Potencia promedio
        y4 = output_items[4]  # Desviación estándar
        # Número de muestras en este bloque
 

        # --- Cálculo del promedio ---
   
        y0[:] = np.mean(x)

        # --- Cálculo de la media cuadrática (para RMS) ---

        media_cuadratica = np.mean(x**2)

        # --- RMS ---
        y2[:] = np.sqrt(media_cuadratica)

        # --- Potencia promedio ---
        y3[:] = media_cuadratica

        # --- Media (simplemente el promedio) ---
        y1[:] = media_cuadratica

        # --- Desviación estándar ---

        y4[:] = np.std(x)

        return len(x)
