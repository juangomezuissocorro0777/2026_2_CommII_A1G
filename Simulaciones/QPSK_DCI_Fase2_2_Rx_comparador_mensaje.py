"""
Receptor de texto: reconstruye el mensaje a partir de los bytes decididos
y lo compara con el mensaje transmitido (retardado) caracter a caracter.
"""
import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    def __init__(self, longitud=58, descartar=3):
        gr.sync_block.__init__(
            self,
            name='Comparador de mensaje',
            in_sig=[np.uint8, np.uint8],   # in0: bytes recibidos, in1: bytes transmitidos (retardados)
            out_sig=None
        )
        self.longitud = longitud
        self.descartar = descartar  # bytes previos al inicio del mensaje (retardo de los filtros)
        self.buf = bytearray()
        self.ultimo = ''
        self.n_car = 0
        self.n_err = 0

    def work(self, input_items, output_items):
        rx = input_items[0]
        tx = input_items[1]
        n = min(len(rx), len(tx))
        if self.descartar > 0:
            k = min(self.descartar, n)
            self.descartar -= k
            return k
        self.n_car += n
        self.n_err += int(np.count_nonzero(rx[:n] != tx[:n]))
        self.buf.extend(rx[:n].tobytes())
        while len(self.buf) >= self.longitud:
            linea = self.buf[:self.longitud]
            del self.buf[:self.longitud]
            self.ultimo = ''.join(chr(c) if 32 <= c < 127 else '?' for c in linea)
        return n

    def texto(self):
        return self.ultimo

    def tasa_error_caracter(self):
        return self.n_err / self.n_car if self.n_car else 0.0
