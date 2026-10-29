#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Fase 2.2 - Enlace QPSK (DCI): Tx RRC, canal AWGN + tono y receptor digital
# Author: Grupo A1-GG
# Description: Construido sobre la base de la Guia 2. Tx RRC, canal AWGN calibrado en Es/N0 + interferencia senoidal, receptor: filtro acoplado RRC, diagrama de ojo, muestreo (Delay + Keep 1 in N), decision de minima distancia, comparacion Tx/Rx, SER y BER.
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
import QPSK_DCI_Fase2_2_Rx_comparador_mensaje as comparador_mensaje  # embedded python block
import math
import sip
import threading
import time



class QPSK_DCI_Fase2_2_Rx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Fase 2.2 - Enlace QPSK (DCI): Tx RRC, canal AWGN + tono y receptor digital", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Fase 2.2 - Enlace QPSK (DCI): Tx RRC, canal AWGN + tono y receptor digital")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_DCI_Fase2_2_Rx")

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
        self.M = M = len(tabla_de_verdad_constelacion)
        self.span = span = 11
        self.bps = bps = int(math.log(M,2))
        self.Sps = Sps = 8
        self.Rs = Rs = 16000
        self.sym_por_byte = sym_por_byte = 8//bps
        self.samp_rate = samp_rate = Rs*Sps
        self.ntaps = ntaps = span*Sps+1
        self.beta = beta = 0.35
        self.texto_rx = texto_rx = ""
        self.t_offset = t_offset = 0
        self.rrc_raw = rrc_raw = firdes.root_raised_cosine(1.0, samp_rate, Rs, beta, ntaps)
        self.mensaje = mensaje = "UIS - Comunicaciones II - Grupo A1-GG - Enlace QPSK DCI. "
        self.interf_amp = interf_amp = 0
        self.cer = cer = 0
        self.align = align = (-span) % sym_por_byte
        self.EsN0_dB = EsN0_dB = 30
        self.sym_delay = sym_delay = span
        self.rx_delay = rx_delay = Sps-1-t_offset
        self.rrc_taps = rrc_taps = [t/math.sqrt(sum([x*x for x in rrc_raw])) for t in rrc_raw]
        self.noise_amp = noise_amp = math.sqrt(10**(-EsN0_dB/10.0))
        self.lbl_mensaje_tx = lbl_mensaje_tx = mensaje
        self.lbl_mensaje_rx = lbl_mensaje_rx = texto_rx
        self.lbl_cer = lbl_cer = cer
        self.interf_freq = interf_freq = 6000
        self.constelacion_qpsk = constelacion_qpsk = digital.constellation_calcdist(tabla_de_verdad_constelacion, [0, 1, 2, 3],
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.constelacion_qpsk.set_npwr(1.0)
        self.byte_delay = byte_delay = (span+align)//sym_por_byte
        self.SIR_dB = SIR_dB = round(10*math.log10((1.0/Sps)/(interf_amp**2)), 2) if interf_amp > 0 else 'sin interferencia'
        self.Rb = Rb = Rs*bps
        self.N_ber = N_ber = 100000
        self.EbN0_dB = EbN0_dB = (EsN0_dB - 10*math.log10(bps))

        ##################################################
        # Blocks
        ##################################################

        self.pestanas = Qt.QTabWidget()
        self.pestanas_widget_0 = Qt.QWidget()
        self.pestanas_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.pestanas_widget_0)
        self.pestanas_grid_layout_0 = Qt.QGridLayout()
        self.pestanas_layout_0.addLayout(self.pestanas_grid_layout_0)
        self.pestanas.addTab(self.pestanas_widget_0, "Tx y canal")
        self.pestanas_widget_1 = Qt.QWidget()
        self.pestanas_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.pestanas_widget_1)
        self.pestanas_grid_layout_1 = Qt.QGridLayout()
        self.pestanas_layout_1.addLayout(self.pestanas_grid_layout_1)
        self.pestanas.addTab(self.pestanas_widget_1, "Receptor")
        self.pestanas_widget_2 = Qt.QWidget()
        self.pestanas_layout_2 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.pestanas_widget_2)
        self.pestanas_grid_layout_2 = Qt.QGridLayout()
        self.pestanas_layout_2.addLayout(self.pestanas_grid_layout_2)
        self.pestanas.addTab(self.pestanas_widget_2, "Validacion Tx vs Rx")
        self.top_grid_layout.addWidget(self.pestanas, 2, 0, 1, 4)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._interf_freq_range = qtgui.Range(0, 40000, 100, 6000, 200)
        self._interf_freq_win = qtgui.RangeWidget(self._interf_freq_range, self.set_interf_freq, "Frecuencia tono [Hz]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._interf_freq_win, 1, 2, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._interf_amp_range = qtgui.Range(0, 0.5, 0.01, 0, 200)
        self._interf_amp_win = qtgui.RangeWidget(self._interf_amp_range, self.set_interf_amp, "Amplitud tono interferente", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._interf_amp_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.comparador_mensaje = comparador_mensaje.blk(longitud=len(mensaje), descartar=byte_delay)
        self.tx_idx_f = blocks.char_to_float(1, 1)
        self.tono_interferente = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, interf_freq, interf_amp, 0, 0)
        self.throttle_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        def _texto_rx_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.comparador_mensaje.texto()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_texto_rx,val))
              except AttributeError:
                self.set_texto_rx(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (2))
        _texto_rx_thread = threading.Thread(target=_texto_rx_probe)
        _texto_rx_thread.daemon = True
        _texto_rx_thread.start()
        self.tasas_error = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_VERT,
            2,
            None # parent
        )
        self.tasas_error.set_update_time(0.20)
        self.tasas_error.set_title("Tasas de error (ventana deslizante)")

        labels = ["BER", "SER", '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(2):
            self.tasas_error.set_min(i, 0)
            self.tasas_error.set_max(i, 0.5)
            self.tasas_error.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.tasas_error.set_label(i, "Data {0}".format(i))
            else:
                self.tasas_error.set_label(i, labels[i])
            self.tasas_error.set_unit(i, units[i])
            self.tasas_error.set_factor(i, factor[i])

        self.tasas_error.enable_autoscale(False)
        self._tasas_error_win = sip.wrapinstance(self.tasas_error.qwidget(), Qt.QWidget)
        self.pestanas_grid_layout_2.addWidget(self._tasas_error_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.pestanas_grid_layout_2.setRowStretch(r, 1)
        for c in range(0, 2):
            self.pestanas_grid_layout_2.setColumnStretch(c, 1)
        self._t_offset_range = qtgui.Range((-3), 4, 1, 0, 200)
        self._t_offset_win = qtgui.RangeWidget(self._t_offset_range, self.set_t_offset, "Desfase de muestreo [muestras]", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._t_offset_win, 0, 3, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.sym_tx_rx = qtgui.time_sink_f(
            40, #size
            Rs, #samp_rate
            "Indice de simbolo: Tx (retardado) vs Rx decidido", #name
            2, #number of inputs
            None # parent
        )
        self.sym_tx_rx.set_update_time(0.10)
        self.sym_tx_rx.set_y_axis(-0.5, 3.5)

        self.sym_tx_rx.set_y_label("Indice", "")

        self.sym_tx_rx.enable_tags(True)
        self.sym_tx_rx.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.sym_tx_rx.enable_autoscale(False)
        self.sym_tx_rx.enable_grid(True)
        self.sym_tx_rx.enable_axis_labels(True)
        self.sym_tx_rx.enable_control_panel(False)
        self.sym_tx_rx.enable_stem_plot(True)


        labels = ["Tx", "Rx", 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [2, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [0, 2, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.sym_tx_rx.set_line_label(i, "Data {0}".format(i))
            else:
                self.sym_tx_rx.set_line_label(i, labels[i])
            self.sym_tx_rx.set_line_width(i, widths[i])
            self.sym_tx_rx.set_line_color(i, colors[i])
            self.sym_tx_rx.set_line_style(i, styles[i])
            self.sym_tx_rx.set_line_marker(i, markers[i])
            self.sym_tx_rx.set_line_alpha(i, alphas[i])

        self._sym_tx_rx_win = sip.wrapinstance(self.sym_tx_rx.qwidget(), Qt.QWidget)
        self.pestanas_grid_layout_2.addWidget(self._sym_tx_rx_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.pestanas_grid_layout_2.setRowStretch(r, 1)
        for c in range(0, 2):
            self.pestanas_grid_layout_2.setColumnStretch(c, 1)
        self.sym_error_f = blocks.char_to_float(1, 1)
        self.sym_error = blocks.threshold_ff(0.5, 0.5, 0)
        self.simbolos_a_bytes = blocks.repack_bits_bb(bps, 8, "", False, gr.GR_MSB_FIRST)
        self.ser_promedio = blocks.moving_average_ff((N_ber//bps), (1.0/(N_ber//bps)), 4000, 1)
        self.rx_idx_f = blocks.char_to_float(1, 1)
        self.rrc_tx = filter.interp_fir_filter_ccf(Sps, rrc_taps)
        self.rrc_tx.declare_sample_delay(0)
        self.rrc_rx = filter.fir_filter_ccf(1, rrc_taps)
        self.rrc_rx.declare_sample_delay(0)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            2048, #size
            samp_rate, #samp_rate
            "Envolvente compleja a la salida del canal", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['I', 'Q', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.pestanas_grid_layout_0.addWidget(self._qtgui_time_sink_x_0_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.pestanas_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 2):
            self.pestanas_grid_layout_0.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "PSD: Tx conformada vs salida del canal", #name
            3,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['Tx despues de RRC', 'Salida del canal + AWGN', "Salida filtro acoplado", '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(3):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.pestanas_grid_layout_0.addWidget(self._qtgui_freq_sink_x_0_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.pestanas_grid_layout_0.setRowStretch(r, 1)
        for c in range(1, 2):
            self.pestanas_grid_layout_0.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            2048, #size
            "Plano I-Q sobremuestreado a la salida del canal", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(True)
        self.qtgui_const_sink_x_0.enable_grid(True)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)

        self.qtgui_const_sink_x_0.disable_legend()

        labels = ["Salida del canal + AWGN", "", "", "", "",
            "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.pestanas_grid_layout_0.addWidget(self._qtgui_const_sink_x_0_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.pestanas_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.pestanas_grid_layout_0.setColumnStretch(c, 1)
        self.muestreo_simbolo = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, Sps)
        self._lbl_mensaje_tx_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_mensaje_tx_formatter = None
        else:
            self._lbl_mensaje_tx_formatter = lambda x: str(x)

        self._lbl_mensaje_tx_tool_bar.addWidget(Qt.QLabel("Mensaje transmitido"))
        self._lbl_mensaje_tx_label = Qt.QLabel(str(self._lbl_mensaje_tx_formatter(self.lbl_mensaje_tx)))
        self._lbl_mensaje_tx_tool_bar.addWidget(self._lbl_mensaje_tx_label)
        self.pestanas_grid_layout_2.addWidget(self._lbl_mensaje_tx_tool_bar, 2, 0, 1, 2)
        for r in range(2, 3):
            self.pestanas_grid_layout_2.setRowStretch(r, 1)
        for c in range(0, 2):
            self.pestanas_grid_layout_2.setColumnStretch(c, 1)
        self._lbl_mensaje_rx_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_mensaje_rx_formatter = None
        else:
            self._lbl_mensaje_rx_formatter = lambda x: str(x)

        self._lbl_mensaje_rx_tool_bar.addWidget(Qt.QLabel("Mensaje recuperado "))
        self._lbl_mensaje_rx_label = Qt.QLabel(str(self._lbl_mensaje_rx_formatter(self.lbl_mensaje_rx)))
        self._lbl_mensaje_rx_tool_bar.addWidget(self._lbl_mensaje_rx_label)
        self.pestanas_grid_layout_2.addWidget(self._lbl_mensaje_rx_tool_bar, 3, 0, 1, 2)
        for r in range(3, 4):
            self.pestanas_grid_layout_2.setRowStretch(r, 1)
        for c in range(0, 2):
            self.pestanas_grid_layout_2.setColumnStretch(c, 1)
        self._lbl_cer_tool_bar = Qt.QToolBar(self)

        if None:
            self._lbl_cer_formatter = None
        else:
            self._lbl_cer_formatter = lambda x: eng_notation.num_to_str(x)

        self._lbl_cer_tool_bar.addWidget(Qt.QLabel("Tasa de error de caracter"))
        self._lbl_cer_label = Qt.QLabel(str(self._lbl_cer_formatter(self.lbl_cer)))
        self._lbl_cer_tool_bar.addWidget(self._lbl_cer_label)
        self.pestanas_grid_layout_2.addWidget(self._lbl_cer_tool_bar, 4, 0, 1, 2)
        for r in range(4, 5):
            self.pestanas_grid_layout_2.setRowStretch(r, 1)
        for c in range(0, 2):
            self.pestanas_grid_layout_2.setColumnStretch(c, 1)
        self.fuente_mensaje = blocks.vector_source_b(list(mensaje.encode("ascii")), True, 1, [])
        self.eye_rx = qtgui.eye_sink_c(
            2048, #size
            samp_rate, #samp_rate
            1, #number of inputs
            None
        )
        self.eye_rx.set_update_time(0.10)
        self.eye_rx.set_samp_per_symbol(Sps)
        self.eye_rx.set_y_axis(-1.6, 1.6)

        self.eye_rx.set_y_label("Amplitud", "")

        self.eye_rx.enable_tags(True)
        self.eye_rx.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.eye_rx.enable_autoscale(False)
        self.eye_rx.enable_grid(True)
        self.eye_rx.enable_axis_labels(True)
        self.eye_rx.enable_control_panel(False)


        labels = ["I (filtro acoplado)", "Q (filtro acoplado)", 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'blue', 'blue', 'blue', 'blue',
            'blue', 'blue', 'blue', 'blue', 'blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.eye_rx.set_line_label(i, "Eye [Re{{Data {0}}}]".format(round(i/2)))
                else:
                    self.eye_rx.set_line_label(i, "Eye [Im{{Data {0}}}]".format(round((i-1)/2)))
            else:
                self.eye_rx.set_line_label(i, labels[i])
            self.eye_rx.set_line_width(i, widths[i])
            self.eye_rx.set_line_color(i, colors[i])
            self.eye_rx.set_line_style(i, styles[i])
            self.eye_rx.set_line_marker(i, markers[i])
            self.eye_rx.set_line_alpha(i, alphas[i])

        self._eye_rx_win = sip.wrapinstance(self.eye_rx.qwidget(), Qt.QWidget)
        self.pestanas_grid_layout_1.addWidget(self._eye_rx_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.pestanas_grid_layout_1.setRowStretch(r, 1)
        for c in range(0, 1):
            self.pestanas_grid_layout_1.setColumnStretch(c, 1)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc(tabla_de_verdad_constelacion, 1)
        self.delay_ref_tx = blocks.delay(gr.sizeof_char*1, sym_delay)
        self.delay_ref_bytes = blocks.delay(gr.sizeof_char*1, byte_delay)
        self.delay_muestreo = blocks.delay(gr.sizeof_gr_complex*1, rx_delay)
        self.delay_alineacion_byte = blocks.delay(gr.sizeof_char*1, align)
        self.decisor_qpsk = digital.constellation_decoder_cb(constelacion_qpsk)
        self.const_rx = qtgui.const_sink_c(
            1024, #size
            "Constelacion: Tx ideal vs Rx (1 muestra por simbolo)", #name
            2, #number of inputs
            None # parent
        )
        self.const_rx.set_update_time(0.10)
        self.const_rx.set_y_axis((-1.6), 1.6)
        self.const_rx.set_x_axis((-1.6), 1.6)
        self.const_rx.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.const_rx.enable_autoscale(False)
        self.const_rx.enable_grid(True)
        self.const_rx.enable_axis_labels(True)


        labels = ["Tx", "Rx muestreada", '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["red", "blue", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.const_rx.set_line_label(i, "Data {0}".format(i))
            else:
                self.const_rx.set_line_label(i, labels[i])
            self.const_rx.set_line_width(i, widths[i])
            self.const_rx.set_line_color(i, colors[i])
            self.const_rx.set_line_style(i, styles[i])
            self.const_rx.set_line_marker(i, markers[i])
            self.const_rx.set_line_alpha(i, alphas[i])

        self._const_rx_win = sip.wrapinstance(self.const_rx.qwidget(), Qt.QWidget)
        self.pestanas_grid_layout_1.addWidget(self._const_rx_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.pestanas_grid_layout_1.setRowStretch(r, 1)
        for c in range(1, 2):
            self.pestanas_grid_layout_1.setColumnStretch(c, 1)
        self.comparador = blocks.xor_bb()
        def _cer_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.comparador_mensaje.tasa_error_caracter()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_cer,val))
              except AttributeError:
                self.set_cer(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (2))
        _cer_thread = threading.Thread(target=_cer_probe)
        _cer_thread.daemon = True
        _cer_thread.start()
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.bits_to_symbols = blocks.repack_bits_bb(8, bps, "", False, gr.GR_MSB_FIRST)
        self.bits_error_f = blocks.char_to_float(1, 1)
        self.bits_error = blocks.unpack_k_bits_bb(bps)
        self._beta_range = qtgui.Range(0.10, 1.0, 0.05, 0.35, 200)
        self._beta_win = qtgui.RangeWidget(self._beta_range, self.set_beta, "beta (roll-off)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._beta_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.ber_promedio = blocks.moving_average_ff(N_ber, (1.0/N_ber), 4000, 1)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amp, 0)
        self._SIR_dB_tool_bar = Qt.QToolBar(self)

        if None:
            self._SIR_dB_formatter = None
        else:
            self._SIR_dB_formatter = lambda x: repr(x)

        self._SIR_dB_tool_bar.addWidget(Qt.QLabel("SIR [dB]"))
        self._SIR_dB_label = Qt.QLabel(str(self._SIR_dB_formatter(self.SIR_dB)))
        self._SIR_dB_tool_bar.addWidget(self._SIR_dB_label)
        self.top_grid_layout.addWidget(self._SIR_dB_tool_bar, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._EsN0_dB_range = qtgui.Range(-5, 30, 0.5, 30, 200)
        self._EsN0_dB_win = qtgui.RangeWidget(self._EsN0_dB_range, self.set_EsN0_dB, "Es/N0 [dB]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._EsN0_dB_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._EbN0_dB_tool_bar = Qt.QToolBar(self)

        if None:
            self._EbN0_dB_formatter = None
        else:
            self._EbN0_dB_formatter = lambda x: eng_notation.num_to_str(x)

        self._EbN0_dB_tool_bar.addWidget(Qt.QLabel("Eb/N0 [dB]"))
        self._EbN0_dB_label = Qt.QLabel(str(self._EbN0_dB_formatter(self.EbN0_dB)))
        self._EbN0_dB_tool_bar.addWidget(self._EbN0_dB_label)
        self.top_grid_layout.addWidget(self._EbN0_dB_tool_bar, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.ber_promedio, 0), (self.tasas_error, 0))
        self.connect((self.bits_error, 0), (self.bits_error_f, 0))
        self.connect((self.bits_error_f, 0), (self.ber_promedio, 0))
        self.connect((self.bits_to_symbols, 0), (self.delay_ref_tx, 0))
        self.connect((self.bits_to_symbols, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.rrc_rx, 0))
        self.connect((self.comparador, 0), (self.bits_error, 0))
        self.connect((self.comparador, 0), (self.sym_error_f, 0))
        self.connect((self.decisor_qpsk, 0), (self.comparador, 0))
        self.connect((self.decisor_qpsk, 0), (self.delay_alineacion_byte, 0))
        self.connect((self.decisor_qpsk, 0), (self.rx_idx_f, 0))
        self.connect((self.delay_alineacion_byte, 0), (self.simbolos_a_bytes, 0))
        self.connect((self.delay_muestreo, 0), (self.muestreo_simbolo, 0))
        self.connect((self.delay_ref_bytes, 0), (self.comparador_mensaje, 1))
        self.connect((self.delay_ref_tx, 0), (self.comparador, 1))
        self.connect((self.delay_ref_tx, 0), (self.tx_idx_f, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.const_rx, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.rrc_tx, 0))
        self.connect((self.fuente_mensaje, 0), (self.bits_to_symbols, 0))
        self.connect((self.fuente_mensaje, 0), (self.delay_ref_bytes, 0))
        self.connect((self.muestreo_simbolo, 0), (self.const_rx, 1))
        self.connect((self.muestreo_simbolo, 0), (self.decisor_qpsk, 0))
        self.connect((self.rrc_rx, 0), (self.delay_muestreo, 0))
        self.connect((self.rrc_rx, 0), (self.eye_rx, 0))
        self.connect((self.rrc_rx, 0), (self.qtgui_freq_sink_x_0, 2))
        self.connect((self.rrc_tx, 0), (self.throttle_0, 0))
        self.connect((self.rx_idx_f, 0), (self.sym_tx_rx, 1))
        self.connect((self.ser_promedio, 0), (self.tasas_error, 1))
        self.connect((self.simbolos_a_bytes, 0), (self.comparador_mensaje, 0))
        self.connect((self.sym_error, 0), (self.ser_promedio, 0))
        self.connect((self.sym_error_f, 0), (self.sym_error, 0))
        self.connect((self.throttle_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.throttle_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.tono_interferente, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.tx_idx_f, 0), (self.sym_tx_rx, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_DCI_Fase2_2_Rx")
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

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.set_bps(int(math.log(self.M,2)))

    def get_span(self):
        return self.span

    def set_span(self, span):
        self.span = span
        self.set_align((-self.span) % self.sym_por_byte)
        self.set_byte_delay((self.span+self.align)//self.sym_por_byte)
        self.set_ntaps(self.span*self.Sps+1)
        self.set_sym_delay(self.span)

    def get_bps(self):
        return self.bps

    def set_bps(self, bps):
        self.bps = bps
        self.set_EbN0_dB((self.EsN0_dB - 10*math.log10(self.bps)))
        self.set_Rb(self.Rs*self.bps)
        self.set_sym_por_byte(8//self.bps)
        self.bits_to_symbols.set_k_and_l(8,self.bps)
        self.ser_promedio.set_length_and_scale((self.N_ber//self.bps), (1.0/(self.N_ber//self.bps)))
        self.simbolos_a_bytes.set_k_and_l(self.bps,8)

    def get_Sps(self):
        return self.Sps

    def set_Sps(self, Sps):
        self.Sps = Sps
        self.set_SIR_dB(round(10*math.log10((1.0/self.Sps)/(self.interf_amp**2)), 2) if self.interf_amp > 0 else 'sin interferencia')
        self.set_ntaps(self.span*self.Sps+1)
        self.set_rx_delay(self.Sps-1-self.t_offset)
        self.set_samp_rate(self.Rs*self.Sps)
        self.eye_rx.set_samp_per_symbol(self.Sps)
        self.muestreo_simbolo.set_n(self.Sps)

    def get_Rs(self):
        return self.Rs

    def set_Rs(self, Rs):
        self.Rs = Rs
        self.set_Rb(self.Rs*self.bps)
        self.set_rrc_raw(firdes.root_raised_cosine(1.0, self.samp_rate, self.Rs, self.beta, self.ntaps))
        self.set_samp_rate(self.Rs*self.Sps)
        self.sym_tx_rx.set_samp_rate(self.Rs)

    def get_sym_por_byte(self):
        return self.sym_por_byte

    def set_sym_por_byte(self, sym_por_byte):
        self.sym_por_byte = sym_por_byte
        self.set_align((-self.span) % self.sym_por_byte)
        self.set_byte_delay((self.span+self.align)//self.sym_por_byte)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_rrc_raw(firdes.root_raised_cosine(1.0, self.samp_rate, self.Rs, self.beta, self.ntaps))
        self.eye_rx.set_samp_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.throttle_0.set_sample_rate(self.samp_rate)
        self.tono_interferente.set_sampling_freq(self.samp_rate)

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

    def get_texto_rx(self):
        return self.texto_rx

    def set_texto_rx(self, texto_rx):
        self.texto_rx = texto_rx
        self.set_lbl_mensaje_rx(self.texto_rx)

    def get_t_offset(self):
        return self.t_offset

    def set_t_offset(self, t_offset):
        self.t_offset = t_offset
        self.set_rx_delay(self.Sps-1-self.t_offset)

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
        self.comparador_mensaje.longitud = len(self.mensaje)

    def get_interf_amp(self):
        return self.interf_amp

    def set_interf_amp(self, interf_amp):
        self.interf_amp = interf_amp
        self.set_SIR_dB(round(10*math.log10((1.0/self.Sps)/(self.interf_amp**2)), 2) if self.interf_amp > 0 else 'sin interferencia')
        self.tono_interferente.set_amplitude(self.interf_amp)

    def get_cer(self):
        return self.cer

    def set_cer(self, cer):
        self.cer = cer
        self.set_lbl_cer(self.cer)

    def get_align(self):
        return self.align

    def set_align(self, align):
        self.align = align
        self.set_byte_delay((self.span+self.align)//self.sym_por_byte)
        self.delay_alineacion_byte.set_dly(int(self.align))

    def get_EsN0_dB(self):
        return self.EsN0_dB

    def set_EsN0_dB(self, EsN0_dB):
        self.EsN0_dB = EsN0_dB
        self.set_EbN0_dB((self.EsN0_dB - 10*math.log10(self.bps)))
        self.set_noise_amp(math.sqrt(10**(-self.EsN0_dB/10.0)))

    def get_sym_delay(self):
        return self.sym_delay

    def set_sym_delay(self, sym_delay):
        self.sym_delay = sym_delay
        self.delay_ref_tx.set_dly(int(self.sym_delay))

    def get_rx_delay(self):
        return self.rx_delay

    def set_rx_delay(self, rx_delay):
        self.rx_delay = rx_delay
        self.delay_muestreo.set_dly(int(self.rx_delay))

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.rrc_rx.set_taps(self.rrc_taps)
        self.rrc_tx.set_taps(self.rrc_taps)

    def get_noise_amp(self):
        return self.noise_amp

    def set_noise_amp(self, noise_amp):
        self.noise_amp = noise_amp
        self.analog_noise_source_x_0.set_amplitude(self.noise_amp)

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

    def get_lbl_cer(self):
        return self.lbl_cer

    def set_lbl_cer(self, lbl_cer):
        self.lbl_cer = lbl_cer
        Qt.QMetaObject.invokeMethod(self._lbl_cer_label, "setText", Qt.Q_ARG("QString", str(self._lbl_cer_formatter(self.lbl_cer))))

    def get_interf_freq(self):
        return self.interf_freq

    def set_interf_freq(self, interf_freq):
        self.interf_freq = interf_freq
        self.tono_interferente.set_frequency(self.interf_freq)

    def get_constelacion_qpsk(self):
        return self.constelacion_qpsk

    def set_constelacion_qpsk(self, constelacion_qpsk):
        self.constelacion_qpsk = constelacion_qpsk
        self.decisor_qpsk.set_constellation(self.constelacion_qpsk)

    def get_byte_delay(self):
        return self.byte_delay

    def set_byte_delay(self, byte_delay):
        self.byte_delay = byte_delay
        self.comparador_mensaje.descartar = self.byte_delay
        self.delay_ref_bytes.set_dly(int(self.byte_delay))

    def get_SIR_dB(self):
        return self.SIR_dB

    def set_SIR_dB(self, SIR_dB):
        self.SIR_dB = SIR_dB
        Qt.QMetaObject.invokeMethod(self._SIR_dB_label, "setText", Qt.Q_ARG("QString", str(self._SIR_dB_formatter(self.SIR_dB))))

    def get_Rb(self):
        return self.Rb

    def set_Rb(self, Rb):
        self.Rb = Rb

    def get_N_ber(self):
        return self.N_ber

    def set_N_ber(self, N_ber):
        self.N_ber = N_ber
        self.ber_promedio.set_length_and_scale(self.N_ber, (1.0/self.N_ber))
        self.ser_promedio.set_length_and_scale((self.N_ber//self.bps), (1.0/(self.N_ber//self.bps)))

    def get_EbN0_dB(self):
        return self.EbN0_dB

    def set_EbN0_dB(self, EbN0_dB):
        self.EbN0_dB = EbN0_dB
        Qt.QMetaObject.invokeMethod(self._EbN0_dB_label, "setText", Qt.Q_ARG("QString", str(self._EbN0_dB_formatter(self.EbN0_dB))))




def main(top_block_cls=QPSK_DCI_Fase2_2_Rx, options=None):

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
