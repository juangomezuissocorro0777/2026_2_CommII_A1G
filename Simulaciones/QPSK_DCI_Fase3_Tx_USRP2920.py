#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Fase 3 - Transmisor QPSK (DCI) con USRP-2920 a 910 MHz
# Author: Grupo A1-GG
# Description: Solo transmision. Vector Source con mensaje conocido, QPSK (1, j, -1, -j), RRC de energia unitaria, adaptacion de tasa a 250 kS/s y osmocom Sink (UHD) a 910 MHz. Sin canal simulado ni receptor.
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import uhd
import time
import math
import threading



class QPSK_DCI_Fase3_Tx_USRP2920(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Fase 3 - Transmisor QPSK (DCI) con USRP-2920 a 910 MHz", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Fase 3 - Transmisor QPSK (DCI) con USRP-2920 a 910 MHz")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_DCI_Fase3_Tx_USRP2920")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.tabla_de_verdad_constelacion = tabla_de_verdad_constelacion = (1+0j, 0+1j, -1+0j, 0-1j)
        self.span = span = 11
        self.Sps = Sps = 8
        self.Rs = Rs = 16000
        self.samp_rate = samp_rate = Rs*Sps
        self.ntaps = ntaps = span*Sps+1
        self.beta = beta = 0.35
        self.M = M = len(tabla_de_verdad_constelacion)
        self.samp_rate_usrp = samp_rate_usrp = 6.25e6
        self.rrc_raw = rrc_raw = firdes.root_raised_cosine(1.0, samp_rate, Rs, beta, ntaps)
        self.mensaje = mensaje = "UIS - Comunicaciones II - Grupo A1-GG - Enlace QPSK DCI. "
        self.fc = fc = 905e6
        self.bps = bps = int(math.log(M,2))
        self.usrp_args = usrp_args = "uhd,addr=192.168.10.2"
        self.rrc_taps = rrc_taps = [t/math.sqrt(sum([x*x for x in rrc_raw])) for t in rrc_raw]
        self.lbl_mensaje_tx = lbl_mensaje_tx = mensaje
        self.lbl_fc = lbl_fc = (fc/1e6)
        self.interp_usrp = interp_usrp = int(samp_rate_usrp/math.gcd(int(samp_rate_usrp),int(samp_rate)))
        self.ganancia_tx = ganancia_tx = 0
        self.decim_usrp = decim_usrp = int(samp_rate/math.gcd(int(samp_rate_usrp),int(samp_rate)))
        self.amp_tx = amp_tx = 1.0
        self.Rb = Rb = Rs*bps

        ##################################################
        # Blocks
        ##################################################

        self._ganancia_tx_range = qtgui.Range(-10, 10, 0.5, 0, 200)
        self._ganancia_tx_win = qtgui.RangeWidget(self._ganancia_tx_range, self.set_ganancia_tx, "Ganancia Tx [dB]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._ganancia_tx_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._amp_tx_range = qtgui.Range(0, 1.8, 0.05, 1.0, 200)
        self._amp_tx_win = qtgui.RangeWidget(self._amp_tx_range, self.set_amp_tx, "Amplitud digital", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._amp_tx_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("addr=192.168.10.2", '')),
            uhd.stream_args(
                cpu_format="fc32",
                otw_format="sc16",
                args='',
                channels=list(range(0,1)),
            ),
            "",
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate_usrp)
        # No synchronization enforced.

        self.uhd_usrp_sink_0.set_center_freq(fc, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0.set_gain(ganancia_tx, 0)
        self.rrc_tx = filter.interp_fir_filter_ccf(Sps, rrc_taps)
        self.rrc_tx.declare_sample_delay(0)
        self._lbl_mensaje_tx_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_mensaje_tx_formatter = None
        else:
            self._lbl_mensaje_tx_formatter = lambda x: str(x)

        self._lbl_mensaje_tx_tool_bar.addWidget(Qt.QLabel("Mensaje transmitido"))
        self._lbl_mensaje_tx_label = Qt.QLabel(str(self._lbl_mensaje_tx_formatter(self.lbl_mensaje_tx)))
        self._lbl_mensaje_tx_tool_bar.addWidget(self._lbl_mensaje_tx_label)
        self.top_grid_layout.addWidget(self._lbl_mensaje_tx_tool_bar, 0, 0, 1, 3)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._lbl_fc_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_fc_formatter = None
        else:
            self._lbl_fc_formatter = lambda x: eng_notation.num_to_str(x)

        self._lbl_fc_tool_bar.addWidget(Qt.QLabel("Portadora [MHz]"))
        self._lbl_fc_label = Qt.QLabel(str(self._lbl_fc_formatter(self.lbl_fc)))
        self._lbl_fc_tool_bar.addWidget(self._lbl_fc_label)
        self.top_grid_layout.addWidget(self._lbl_fc_tool_bar, 1, 2, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.fuente_mensaje = blocks.vector_source_b(list(mensaje.encode("ascii")), True, 1, [])
        self.escala_tx = blocks.multiply_const_cc(amp_tx)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc(tabla_de_verdad_constelacion, 1)
        self.bits_to_symbols = blocks.repack_bits_bb(8, bps, "", False, gr.GR_MSB_FIRST)
        self.adaptacion_tasa = filter.rational_resampler_ccc(
                interpolation=interp_usrp,
                decimation=decim_usrp,
                taps=[],
                fractional_bw=0.4)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.adaptacion_tasa, 0), (self.escala_tx, 0))
        self.connect((self.bits_to_symbols, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.rrc_tx, 0))
        self.connect((self.escala_tx, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.fuente_mensaje, 0), (self.bits_to_symbols, 0))
        self.connect((self.rrc_tx, 0), (self.adaptacion_tasa, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_DCI_Fase3_Tx_USRP2920")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_tabla_de_verdad_constelacion(self):
        return self.tabla_de_verdad_constelacion

    def set_tabla_de_verdad_constelacion(self, tabla_de_verdad_constelacion):
        self.tabla_de_verdad_constelacion = tabla_de_verdad_constelacion
        self.set_M(len(self.tabla_de_verdad_constelacion))
        self.digital_chunks_to_symbols_xx_0.set_symbol_table(self.tabla_de_verdad_constelacion)

    def get_span(self):
        return self.span

    def set_span(self, span):
        self.span = span
        self.set_ntaps(self.span*self.Sps+1)

    def get_Sps(self):
        return self.Sps

    def set_Sps(self, Sps):
        self.Sps = Sps
        self.set_ntaps(self.span*self.Sps+1)
        self.set_samp_rate(self.Rs*self.Sps)

    def get_Rs(self):
        return self.Rs

    def set_Rs(self, Rs):
        self.Rs = Rs
        self.set_Rb(self.Rs*self.bps)
        self.set_rrc_raw(firdes.root_raised_cosine(1.0, self.samp_rate, self.Rs, self.beta, self.ntaps))
        self.set_samp_rate(self.Rs*self.Sps)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_decim_usrp(int(self.samp_rate/math.gcd(int(self.samp_rate_usrp),int(self.samp_rate))))
        self.set_interp_usrp(int(self.samp_rate_usrp/math.gcd(int(self.samp_rate_usrp),int(self.samp_rate))))
        self.set_rrc_raw(firdes.root_raised_cosine(1.0, self.samp_rate, self.Rs, self.beta, self.ntaps))

    def get_ntaps(self):
        return self.ntaps

    def set_ntaps(self, ntaps):
        self.ntaps = ntaps
        self.set_rrc_raw(firdes.root_raised_cosine(1.0, self.samp_rate, self.Rs, self.beta, self.ntaps))

    def get_beta(self):
        return self.beta

    def set_beta(self, beta):
        self.beta = beta
        self.set_rrc_raw(firdes.root_raised_cosine(1.0, self.samp_rate, self.Rs, self.beta, self.ntaps))

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.set_bps(int(math.log(self.M,2)))

    def get_samp_rate_usrp(self):
        return self.samp_rate_usrp

    def set_samp_rate_usrp(self, samp_rate_usrp):
        self.samp_rate_usrp = samp_rate_usrp
        self.set_decim_usrp(int(self.samp_rate/math.gcd(int(self.samp_rate_usrp),int(self.samp_rate))))
        self.set_interp_usrp(int(self.samp_rate_usrp/math.gcd(int(self.samp_rate_usrp),int(self.samp_rate))))
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate_usrp)

    def get_rrc_raw(self):
        return self.rrc_raw

    def set_rrc_raw(self, rrc_raw):
        self.rrc_raw = rrc_raw
        self.set_rrc_taps([t/math.sqrt(sum([x*x for x in self.rrc_raw])) for t in self.rrc_raw])

    def get_mensaje(self):
        return self.mensaje

    def set_mensaje(self, mensaje):
        self.mensaje = mensaje
        self.set_lbl_mensaje_tx(self.mensaje)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.set_lbl_fc((self.fc/1e6))
        self.uhd_usrp_sink_0.set_center_freq(self.fc, 0)

    def get_bps(self):
        return self.bps

    def set_bps(self, bps):
        self.bps = bps
        self.set_Rb(self.Rs*self.bps)
        self.bits_to_symbols.set_k_and_l(8,self.bps)

    def get_usrp_args(self):
        return self.usrp_args

    def set_usrp_args(self, usrp_args):
        self.usrp_args = usrp_args

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.rrc_tx.set_taps(self.rrc_taps)

    def get_lbl_mensaje_tx(self):
        return self.lbl_mensaje_tx

    def set_lbl_mensaje_tx(self, lbl_mensaje_tx):
        self.lbl_mensaje_tx = lbl_mensaje_tx
        Qt.QMetaObject.invokeMethod(self._lbl_mensaje_tx_label, "setText", Qt.Q_ARG("QString", str(self._lbl_mensaje_tx_formatter(self.lbl_mensaje_tx))))

    def get_lbl_fc(self):
        return self.lbl_fc

    def set_lbl_fc(self, lbl_fc):
        self.lbl_fc = lbl_fc
        Qt.QMetaObject.invokeMethod(self._lbl_fc_label, "setText", Qt.Q_ARG("QString", str(self._lbl_fc_formatter(self.lbl_fc))))

    def get_interp_usrp(self):
        return self.interp_usrp

    def set_interp_usrp(self, interp_usrp):
        self.interp_usrp = interp_usrp

    def get_ganancia_tx(self):
        return self.ganancia_tx

    def set_ganancia_tx(self, ganancia_tx):
        self.ganancia_tx = ganancia_tx
        self.uhd_usrp_sink_0.set_gain(self.ganancia_tx, 0)

    def get_decim_usrp(self):
        return self.decim_usrp

    def set_decim_usrp(self, decim_usrp):
        self.decim_usrp = decim_usrp

    def get_amp_tx(self):
        return self.amp_tx

    def set_amp_tx(self, amp_tx):
        self.amp_tx = amp_tx
        self.escala_tx.set_k(self.amp_tx)

    def get_Rb(self):
        return self.Rb

    def set_Rb(self, Rb):
        self.Rb = Rb




def main(top_block_cls=QPSK_DCI_Fase3_Tx_USRP2920, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
