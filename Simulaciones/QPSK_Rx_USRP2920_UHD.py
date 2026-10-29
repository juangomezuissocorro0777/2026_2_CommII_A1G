#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: QPSK Rx USRP-2920: recepcion del mensaje conocido
# Author: Grupo A1-GG
# Description: Recibe la senal de QPSK_Tx_USRP2920_UHD. AGC, FLL, sincronismo de simbolo (PFB), Costas, decision y deteccion del mensaje.
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
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
import QPSK_Rx_USRP2920_UHD_detector_mensaje as detector_mensaje  # embedded python block
import cmath
import math
import sip
import threading



class QPSK_Rx_USRP2920_UHD(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "QPSK Rx USRP-2920: recepcion del mensaje conocido", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("QPSK Rx USRP-2920: recepcion del mensaje conocido")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_Rx_USRP2920_UHD")

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
        self.Sps = Sps = 8
        self.Rs = Rs = 16000
        self.texto_rx = texto_rx = ""
        self.span = span = 11
        self.samp_rate_usrp = samp_rate_usrp = 6.25e6
        self.samp_rate = samp_rate = Rs*Sps
        self.nfilts = nfilts = 32
        self.mensaje = mensaje = "UIS - Comunicaciones II - Grupo A1-GG - Enlace QPSK DCI. "
        self.estado_rx = estado_rx = "Buscando el mensaje..."
        self.cer = cer = 0
        self.beta = beta = 0.35
        self.usrp_addr = usrp_addr = "addr=192.168.10.2"
        self.pfb_taps = pfb_taps = firdes.root_raised_cosine(nfilts, nfilts*Sps, 1.0, beta, span*Sps*nfilts)
        self.lbl_mensaje_tx = lbl_mensaje_tx = mensaje
        self.lbl_mensaje_rx = lbl_mensaje_rx = texto_rx
        self.lbl_estado = lbl_estado = estado_rx
        self.lbl_cer = lbl_cer = cer
        self.interp_rx = interp_rx = int(samp_rate/math.gcd(int(samp_rate_usrp),int(samp_rate)))
        self.ganancia_rx = ganancia_rx = 20
        self.fll_bw = fll_bw = 2*math.pi/100
        self.fc = fc = 900e6
        self.decim_rx = decim_rx = int(samp_rate_usrp/math.gcd(int(samp_rate_usrp),int(samp_rate)))
        self.costas_bw = costas_bw = 2*math.pi/200
        self.constelacion_qpsk = constelacion_qpsk = digital.constellation_calcdist([1, 1j, -1, -1j], [0, 1, 2, 3],
        4, 1, digital.constellation.AMPLITUDE_NORMALIZATION).base()
        self.constelacion_qpsk.set_npwr(1.0)
        self.clk_bw = clk_bw = 2*math.pi/100

        ##################################################
        # Blocks
        ##################################################

        self._ganancia_rx_range = qtgui.Range(0, 31.5, 0.5, 20, 200)
        self._ganancia_rx_win = qtgui.RangeWidget(self._ganancia_rx_range, self.set_ganancia_rx, "Ganancia Rx [dB]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._ganancia_rx_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.detector_mensaje = detector_mensaje.blk(mensaje=mensaje, ventanas=2)
        self.usrp_rx = uhd.usrp_source(
            ",".join((usrp_addr, "")),
            uhd.stream_args(
                cpu_format="fc32",
                otw_format="sc16",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.usrp_rx.set_samp_rate(samp_rate_usrp)
        # No synchronization enforced.

        self.usrp_rx.set_center_freq(fc, 0)
        self.usrp_rx.set_antenna("RX2", 0)
        self.usrp_rx.set_gain(ganancia_rx, 0)
        def _texto_rx_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.detector_mensaje.texto()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_texto_rx,val))
              except AttributeError:
                self.set_texto_rx(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (4))
        _texto_rx_thread = threading.Thread(target=_texto_rx_probe)
        _texto_rx_thread.daemon = True
        _texto_rx_thread.start()
        self.sincronismo_simbolo = digital.pfb_clock_sync_ccf(Sps, clk_bw, pfb_taps, nfilts, (nfilts/2), 1.5, 1)
        self.rot_menos45 = blocks.multiply_const_cc(cmath.exp(-1j*math.pi/4))
        self.rot_mas45 = blocks.multiply_const_cc(cmath.exp(1j*math.pi/4))
        self.rad_a_hz = blocks.multiply_const_ff((samp_rate/(2*math.pi)))
        self.nulo_fll = blocks.null_sink(gr.sizeof_float*1)
        self._lbl_mensaje_tx_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_mensaje_tx_formatter = None
        else:
            self._lbl_mensaje_tx_formatter = lambda x: str(x)

        self._lbl_mensaje_tx_tool_bar.addWidget(Qt.QLabel("Mensaje esperado "))
        self._lbl_mensaje_tx_label = Qt.QLabel(str(self._lbl_mensaje_tx_formatter(self.lbl_mensaje_tx)))
        self._lbl_mensaje_tx_tool_bar.addWidget(self._lbl_mensaje_tx_label)
        self.top_grid_layout.addWidget(self._lbl_mensaje_tx_tool_bar, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._lbl_mensaje_rx_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_mensaje_rx_formatter = None
        else:
            self._lbl_mensaje_rx_formatter = lambda x: str(x)

        self._lbl_mensaje_rx_tool_bar.addWidget(Qt.QLabel("Mensaje recibido "))
        self._lbl_mensaje_rx_label = Qt.QLabel(str(self._lbl_mensaje_rx_formatter(self.lbl_mensaje_rx)))
        self._lbl_mensaje_rx_tool_bar.addWidget(self._lbl_mensaje_rx_label)
        self.top_grid_layout.addWidget(self._lbl_mensaje_rx_tool_bar, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._lbl_estado_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_estado_formatter = None
        else:
            self._lbl_estado_formatter = lambda x: str(x)

        self._lbl_estado_tool_bar.addWidget(Qt.QLabel("Estado"))
        self._lbl_estado_label = Qt.QLabel(str(self._lbl_estado_formatter(self.lbl_estado)))
        self._lbl_estado_tool_bar.addWidget(self._lbl_estado_label)
        self.top_grid_layout.addWidget(self._lbl_estado_tool_bar, 4, 0, 1, 2)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._lbl_cer_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_cer_formatter = None
        else:
            self._lbl_cer_formatter = lambda x: eng_notation.num_to_str(x)

        self._lbl_cer_tool_bar.addWidget(Qt.QLabel("Tasa de error de caracter"))
        self._lbl_cer_label = Qt.QLabel(str(self._lbl_cer_formatter(self.lbl_cer)))
        self._lbl_cer_tool_bar.addWidget(self._lbl_cer_label)
        self.top_grid_layout.addWidget(self._lbl_cer_tool_bar, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.fll = digital.fll_band_edge_cc(Sps, beta, 44, fll_bw)
        def _estado_rx_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.detector_mensaje.estado()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_estado_rx,val))
              except AttributeError:
                self.set_estado_rx(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (4))
        _estado_rx_thread = threading.Thread(target=_estado_rx_probe)
        _estado_rx_thread.daemon = True
        _estado_rx_thread.start()
        self.espectro_rx = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            fc, #fc
            samp_rate_usrp, #bw
            "Espectro recibido (centrado en fc)", #name
            1,
            None # parent
        )
        self.espectro_rx.set_update_time(0.10)
        self.espectro_rx.set_y_axis((-120), 0)
        self.espectro_rx.set_y_label('Relative Gain', 'dB')
        self.espectro_rx.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.espectro_rx.enable_autoscale(False)
        self.espectro_rx.enable_grid(True)
        self.espectro_rx.set_fft_average(0.2)
        self.espectro_rx.enable_axis_labels(True)
        self.espectro_rx.enable_control_panel(False)
        self.espectro_rx.set_fft_window_normalized(False)

        self.espectro_rx.disable_legend()


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.espectro_rx.set_line_label(i, "Data {0}".format(i))
            else:
                self.espectro_rx.set_line_label(i, labels[i])
            self.espectro_rx.set_line_width(i, widths[i])
            self.espectro_rx.set_line_color(i, colors[i])
            self.espectro_rx.set_line_alpha(i, alphas[i])

        self._espectro_rx_win = sip.wrapinstance(self.espectro_rx.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._espectro_rx_win, 5, 0, 4, 1)
        for r in range(5, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.desvio_freq = qtgui.number_sink(
            gr.sizeof_float,
            0.1,
            qtgui.NUM_GRAPH_NONE,
            1,
            None # parent
        )
        self.desvio_freq.set_update_time(0.10)
        self.desvio_freq.set_title("Desvio de frecuencia corregido por el FLL [Hz]")

        labels = ["Hz", '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.desvio_freq.set_min(i, -10000)
            self.desvio_freq.set_max(i, 10000)
            self.desvio_freq.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.desvio_freq.set_label(i, "Data {0}".format(i))
            else:
                self.desvio_freq.set_label(i, labels[i])
            self.desvio_freq.set_unit(i, units[i])
            self.desvio_freq.set_factor(i, factor[i])

        self.desvio_freq.enable_autoscale(False)
        self._desvio_freq_win = sip.wrapinstance(self.desvio_freq.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._desvio_freq_win, 3, 1, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.decisor_qpsk = digital.constellation_decoder_cb(constelacion_qpsk)
        self.costas = digital.costas_loop_cc(costas_bw, 4, False)
        self.constelacion_rx = qtgui.const_sink_c(
            1024, #size
            "Constelacion recuperada", #name
            1, #number of inputs
            None # parent
        )
        self.constelacion_rx.set_update_time(0.10)
        self.constelacion_rx.set_y_axis((-1.5), 1.5)
        self.constelacion_rx.set_x_axis((-1.5), 1.5)
        self.constelacion_rx.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.constelacion_rx.enable_autoscale(False)
        self.constelacion_rx.enable_grid(True)
        self.constelacion_rx.enable_axis_labels(True)

        self.constelacion_rx.disable_legend()

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.constelacion_rx.set_line_label(i, "Data {0}".format(i))
            else:
                self.constelacion_rx.set_line_label(i, labels[i])
            self.constelacion_rx.set_line_width(i, widths[i])
            self.constelacion_rx.set_line_color(i, colors[i])
            self.constelacion_rx.set_line_style(i, styles[i])
            self.constelacion_rx.set_line_marker(i, markers[i])
            self.constelacion_rx.set_line_alpha(i, alphas[i])

        self._constelacion_rx_win = sip.wrapinstance(self.constelacion_rx.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._constelacion_rx_win, 5, 1, 4, 1)
        for r in range(5, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        def _cer_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.detector_mensaje.tasa_error_caracter()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_cer,val))
              except AttributeError:
                self.set_cer(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (4))
        _cer_thread = threading.Thread(target=_cer_probe)
        _cer_thread.daemon = True
        _cer_thread.start()
        self.agc = analog.agc2_cc((1e-1), (1e-1), 1.0, 1.0, 65536)
        self.adaptacion_tasa = filter.rational_resampler_ccc(
                interpolation=interp_rx,
                decimation=decim_rx,
                taps=[],
                fractional_bw=0.4)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.adaptacion_tasa, 0), (self.agc, 0))
        self.connect((self.agc, 0), (self.fll, 0))
        self.connect((self.costas, 0), (self.rot_menos45, 0))
        self.connect((self.decisor_qpsk, 0), (self.detector_mensaje, 0))
        self.connect((self.fll, 2), (self.nulo_fll, 0))
        self.connect((self.fll, 3), (self.nulo_fll, 1))
        self.connect((self.fll, 1), (self.rad_a_hz, 0))
        self.connect((self.fll, 0), (self.sincronismo_simbolo, 0))
        self.connect((self.rad_a_hz, 0), (self.desvio_freq, 0))
        self.connect((self.rot_mas45, 0), (self.costas, 0))
        self.connect((self.rot_menos45, 0), (self.constelacion_rx, 0))
        self.connect((self.rot_menos45, 0), (self.decisor_qpsk, 0))
        self.connect((self.sincronismo_simbolo, 0), (self.rot_mas45, 0))
        self.connect((self.usrp_rx, 0), (self.adaptacion_tasa, 0))
        self.connect((self.usrp_rx, 0), (self.espectro_rx, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_Rx_USRP2920_UHD")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_Sps(self):
        return self.Sps

    def set_Sps(self, Sps):
        self.Sps = Sps
        self.set_pfb_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.Sps, 1.0, self.beta, self.span*self.Sps*self.nfilts))
        self.set_samp_rate(self.Rs*self.Sps)

    def get_Rs(self):
        return self.Rs

    def set_Rs(self, Rs):
        self.Rs = Rs
        self.set_samp_rate(self.Rs*self.Sps)

    def get_texto_rx(self):
        return self.texto_rx

    def set_texto_rx(self, texto_rx):
        self.texto_rx = texto_rx
        self.set_lbl_mensaje_rx(self.texto_rx)

    def get_span(self):
        return self.span

    def set_span(self, span):
        self.span = span
        self.set_pfb_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.Sps, 1.0, self.beta, self.span*self.Sps*self.nfilts))

    def get_samp_rate_usrp(self):
        return self.samp_rate_usrp

    def set_samp_rate_usrp(self, samp_rate_usrp):
        self.samp_rate_usrp = samp_rate_usrp
        self.set_decim_rx(int(self.samp_rate_usrp/math.gcd(int(self.samp_rate_usrp),int(self.samp_rate))))
        self.set_interp_rx(int(self.samp_rate/math.gcd(int(self.samp_rate_usrp),int(self.samp_rate))))
        self.espectro_rx.set_frequency_range(self.fc, self.samp_rate_usrp)
        self.usrp_rx.set_samp_rate(self.samp_rate_usrp)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_decim_rx(int(self.samp_rate_usrp/math.gcd(int(self.samp_rate_usrp),int(self.samp_rate))))
        self.set_interp_rx(int(self.samp_rate/math.gcd(int(self.samp_rate_usrp),int(self.samp_rate))))
        self.rad_a_hz.set_k((self.samp_rate/(2*math.pi)))

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_pfb_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.Sps, 1.0, self.beta, self.span*self.Sps*self.nfilts))

    def get_mensaje(self):
        return self.mensaje

    def set_mensaje(self, mensaje):
        self.mensaje = mensaje
        self.set_lbl_mensaje_tx(self.mensaje)

    def get_estado_rx(self):
        return self.estado_rx

    def set_estado_rx(self, estado_rx):
        self.estado_rx = estado_rx
        self.set_lbl_estado(self.estado_rx)

    def get_cer(self):
        return self.cer

    def set_cer(self, cer):
        self.cer = cer
        self.set_lbl_cer(self.cer)

    def get_beta(self):
        return self.beta

    def set_beta(self, beta):
        self.beta = beta
        self.set_pfb_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.Sps, 1.0, self.beta, self.span*self.Sps*self.nfilts))

    def get_usrp_addr(self):
        return self.usrp_addr

    def set_usrp_addr(self, usrp_addr):
        self.usrp_addr = usrp_addr

    def get_pfb_taps(self):
        return self.pfb_taps

    def set_pfb_taps(self, pfb_taps):
        self.pfb_taps = pfb_taps
        self.sincronismo_simbolo.update_taps(self.pfb_taps)

    def get_lbl_mensaje_tx(self):
        return self.lbl_mensaje_tx

    def set_lbl_mensaje_tx(self, lbl_mensaje_tx):
        self.lbl_mensaje_tx = lbl_mensaje_tx
        Qt.QMetaObject.invokeMethod(self._lbl_mensaje_tx_label, "setText", Qt.Q_ARG("QString", str(self._lbl_mensaje_tx_formatter(self.lbl_mensaje_tx))))

    def get_lbl_mensaje_rx(self):
        return self.lbl_mensaje_rx

    def set_lbl_mensaje_rx(self, lbl_mensaje_rx):
        self.lbl_mensaje_rx = lbl_mensaje_rx
        Qt.QMetaObject.invokeMethod(self._lbl_mensaje_rx_label, "setText", Qt.Q_ARG("QString", str(self._lbl_mensaje_rx_formatter(self.lbl_mensaje_rx))))

    def get_lbl_estado(self):
        return self.lbl_estado

    def set_lbl_estado(self, lbl_estado):
        self.lbl_estado = lbl_estado
        Qt.QMetaObject.invokeMethod(self._lbl_estado_label, "setText", Qt.Q_ARG("QString", str(self._lbl_estado_formatter(self.lbl_estado))))

    def get_lbl_cer(self):
        return self.lbl_cer

    def set_lbl_cer(self, lbl_cer):
        self.lbl_cer = lbl_cer
        Qt.QMetaObject.invokeMethod(self._lbl_cer_label, "setText", Qt.Q_ARG("QString", str(self._lbl_cer_formatter(self.lbl_cer))))

    def get_interp_rx(self):
        return self.interp_rx

    def set_interp_rx(self, interp_rx):
        self.interp_rx = interp_rx

    def get_ganancia_rx(self):
        return self.ganancia_rx

    def set_ganancia_rx(self, ganancia_rx):
        self.ganancia_rx = ganancia_rx
        self.usrp_rx.set_gain(self.ganancia_rx, 0)

    def get_fll_bw(self):
        return self.fll_bw

    def set_fll_bw(self, fll_bw):
        self.fll_bw = fll_bw
        self.fll.set_loop_bandwidth(self.fll_bw)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.espectro_rx.set_frequency_range(self.fc, self.samp_rate_usrp)
        self.usrp_rx.set_center_freq(self.fc, 0)

    def get_decim_rx(self):
        return self.decim_rx

    def set_decim_rx(self, decim_rx):
        self.decim_rx = decim_rx

    def get_costas_bw(self):
        return self.costas_bw

    def set_costas_bw(self, costas_bw):
        self.costas_bw = costas_bw
        self.costas.set_loop_bandwidth(self.costas_bw)

    def get_constelacion_qpsk(self):
        return self.constelacion_qpsk

    def set_constelacion_qpsk(self, constelacion_qpsk):
        self.constelacion_qpsk = constelacion_qpsk
        self.decisor_qpsk.set_constellation(self.constelacion_qpsk)

    def get_clk_bw(self):
        return self.clk_bw

    def set_clk_bw(self, clk_bw):
        self.clk_bw = clk_bw
        self.sincronismo_simbolo.set_loop_bandwidth(self.clk_bw)




def main(top_block_cls=QPSK_Rx_USRP2920_UHD, options=None):

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
