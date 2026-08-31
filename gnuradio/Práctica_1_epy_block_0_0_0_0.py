import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Differenciator',   # aparecerá en GRC
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
        self.last_sample = 0.0   # última muestra del bloque anterior

    def work(self, input_items, output_items):
        x = input_items[0]   # señal de entrada
        y0 = output_items[0] # señal de salida (diferenciada)

        # Calcular diferencias
        y0[0] = x[0] - self.last_sample   # primera diferencia usando la memoria
        y0[1:] = np.diff(x)               # diferencias dentro del bloque

        # Guardar la última muestra del bloque actual
        self.last_sample = x[-1]

        return len(y0)
