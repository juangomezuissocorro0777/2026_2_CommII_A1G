"""
Jeferson Uribe Correa
"""
import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Diferenciador', # Nombre del bloq
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
        self.last_sample = 0

    def work(self, input_items, output_items):
        x = input_items[0]   # Entrada
        y0 = output_items[0] # Salida

        y0[0] = x[0] - self.last_sample

        for i in range(1, len(x)):
            y0[i] = x[i] - x[i-1]

        self.last_sample = x[-1]

        return len(y0)