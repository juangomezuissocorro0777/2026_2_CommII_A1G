"""
Detector del mensaje conocido (recepcion con USRP).
Entrada: indices de simbolo 0..3 decididos con la tabla (1, j, -1, -j).
El receptor real tiene tres incognitas que el simulador no tenia:
  - ambiguedad de fase de 90 grados del lazo de Costas (indice + k mod 4),
  - en que simbolo empieza cada byte (4 posibilidades),
  - en que caracter del mensaje empieza la ventana.
Como el mensaje es conocido, se prueban las 16 combinaciones y se elige la que mas
caracteres acierta; con ella se muestran el texto recibido y la tasa de error de caracter.
"""
import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    def __init__(self, mensaje='UIS - Comunicaciones II - Grupo A1-GG - Enlace QPSK DCI. ', ventanas=2):
        gr.sync_block.__init__(self, name='Detector de mensaje', in_sig=[np.uint8], out_sig=None)
        self.ref = np.frombuffer(mensaje.encode('ascii'), dtype=np.uint8)
        self.L = len(self.ref)
        self.nsym = 4 * self.L * ventanas + 3          # simbolos por ventana de analisis
        self.buf = np.zeros(0, dtype=np.uint8)
        # tabla de referencia con todos los desplazamientos ciclicos del mensaje
        nb = self.L * ventanas
        idx = (np.arange(self.L)[:, None] + np.arange(nb)[None, :]) % self.L
        self.ref_shifts = self.ref[idx]                # (L, nb)
        self.ultimo = ''
        self.rot = 0
        self.n_car = 0
        self.n_err = 0
        self.cer_ventana = 1.0
        self.enganchado = False

    def _bytes(self, s):
        s = s[: (len(s) // 4) * 4].reshape(-1, 4).astype(np.uint16)
        return ((s[:, 0] << 6) | (s[:, 1] << 4) | (s[:, 2] << 2) | s[:, 3]).astype(np.uint8)

    def _analizar(self, s):
        nb = self.ref_shifts.shape[1]
        mejor = (-1, 0, 0, 0, None)
        for rot in range(4):
            sr = (s.astype(np.int16) - rot) % 4
            for off in range(4):
                b = self._bytes(sr[off:off + 4 * nb])
                aciertos = (self.ref_shifts == b[None, :]).sum(axis=1)
                k = int(np.argmax(aciertos))
                if aciertos[k] > mejor[0]:
                    mejor = (int(aciertos[k]), rot, off, k, b)
        acier, rot, off, k, b = mejor
        self.rot = rot
        self.cer_ventana = 1.0 - acier / nb
        # el conteo empieza cuando el receptor se engancha (primera ventana con menos de 25 % de error),
        # para que la adquisicion de la AGC, el FLL y el Costas no infle la tasa de error
        if not self.enganchado and self.cer_ventana < 0.25:
            self.enganchado = True
        if self.enganchado:
            self.n_car += nb
            self.n_err += nb - acier
        ini = (-k) % self.L                            # posicion donde empieza el mensaje
        linea = b[ini:ini + self.L]
        self.ultimo = ''.join(chr(c) if 32 <= c < 127 else '?' for c in linea)

    def work(self, input_items, output_items):
        x = input_items[0]
        self.buf = np.concatenate((self.buf, x))
        while len(self.buf) >= self.nsym:
            self._analizar(self.buf[:self.nsym])
            self.buf = self.buf[self.nsym:]
        return len(x)

    def texto(self):
        return self.ultimo

    def tasa_error_caracter(self):
        return self.n_err / self.n_car if self.n_car else 0.0

    def estado(self):
        if not self.enganchado:
            return 'Buscando el mensaje...'
        return 'Enganchado | ambiguedad de fase corregida: %d grados | error ultima ventana: %.1f %%' % (90 * self.rot, 100 * self.cer_ventana)

    def rotacion(self):
        return 90 * self.rot
