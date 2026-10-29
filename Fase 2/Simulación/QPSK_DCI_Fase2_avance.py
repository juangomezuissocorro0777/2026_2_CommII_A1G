#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: QPSK con RRC, AWGN e interferencia senoidal - Fase 2 (avance)
# Description: Abstraccion academica de un enlace optico coherente DCI: QPSK + RRC + AWGN + interferencia + receptor + BER
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
import numpy
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
import math
import sip
import threading



class QPSK_DCI_Fase2_avance(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "QPSK con RRC, AWGN e interferencia senoidal - Fase 2 (avance)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("QPSK con RRC, AWGN e interferencia senoidal - Fase 2 (avance)")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_DCI_Fase2_avance")

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
        self.span = span = 8
        self.Sps = Sps = 8
        self.Rs = Rs = 16000
        self.samp_rate = samp_rate = Rs*Sps
        self.ntaps = ntaps = span*Sps+1
        self.beta = beta = 0.35
        self.M = M = len(tabla_de_verdad_constelacion)
        self.rrc_raw = rrc_raw = firdes.root_raised_cosine(1.0, samp_rate, Rs, beta, ntaps)
        self.interf_amp = interf_amp = 0.1
        self.bps = bps = int(math.log(M,2))
        self.EsN0_dB = EsN0_dB = 10
        self.sym_delay = sym_delay = span
        self.rx_delay = rx_delay = Sps-1
        self.rrc_taps = rrc_taps = [t/math.sqrt(sum([x*x for x in rrc_raw])) for t in rrc_raw]
        self.noise_amp = noise_amp = (math.sqrt(10**(-EsN0_dB/10.0)))
        self.interf_freq = interf_freq = 6000
        self.constelacion_qpsk = constelacion_qpsk = digital.constellation_calcdist(tabla_de_verdad_constelacion, [0, 1, 2, 3],
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.constelacion_qpsk.set_npwr(1.0)
        self.SIR_dB = SIR_dB = round(10*math.log10((1.0/Sps)/(interf_amp**2)), 2) if interf_amp > 0 else 'sin interferencia'
        self.Rb = Rb = Rs*bps
        self.N_ber = N_ber = 100000
        self.EbN0_dB = EbN0_dB = (EsN0_dB - 10*math.log10(bps))

        ##################################################
        # Blocks
        ##################################################

        self._noise_amp_tool_bar = Qt.QToolBar(self)

        if None:
            self._noise_amp_formatter = None
        else:
            self._noise_amp_formatter = lambda x: eng_notation.num_to_str(x)

        self._noise_amp_tool_bar.addWidget(Qt.QLabel("noise_amp (desv. AWGN)"))
        self._noise_amp_label = Qt.QLabel(str(self._noise_amp_formatter(self.noise_amp)))
        self._noise_amp_tool_bar.addWidget(self._noise_amp_label)
        self.top_grid_layout.addWidget(self._noise_amp_tool_bar, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._interf_freq_range = qtgui.Range(0, 40000, 100, 6000, 200)
        self._interf_freq_win = qtgui.RangeWidget(self._interf_freq_range, self.set_interf_freq, "interf_freq [Hz]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._interf_freq_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._interf_amp_range = qtgui.Range(0, 0.5, 0.01, 0.1, 200)
        self._interf_amp_win = qtgui.RangeWidget(self._interf_amp_range, self.set_interf_amp, "interf_amp", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._interf_amp_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.throttle_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            512, #size
            samp_rate, #samp_rate
            "Envolvente compleja: Tx y salida del canal", #name
            2, #number of inputs
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


        labels = ['I Tx', 'Q Tx', 'I Rx', 'Q Rx', 'Signal 5',
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


        for i in range(4):
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
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 5, 0, 2, 3)
        for r in range(5, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.qtgui_number_sink_0.set_update_time(0.20)
        self.qtgui_number_sink_0.set_title("BER (ventana N_ber bits)")

        labels = ["BER", "", "", "", "",
            "", "", "", "", ""]
        units = ["", "", "", "", "",
            "", "", "", "", ""]
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0.set_min(i, 0)
            self.qtgui_number_sink_0.set_max(i, 0.5)
            self.qtgui_number_sink_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0.set_label(i, labels[i])
            self.qtgui_number_sink_0.set_unit(i, units[i])
            self.qtgui_number_sink_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0.enable_autoscale(False)
        self._qtgui_number_sink_0_win = sip.wrapinstance(self.qtgui_number_sink_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_win, 0, 2, 3, 1)
        for r in range(0, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "PSD: Tx vs AWGN vs interferencia vs Rx", #name
            4,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-120), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(0.1)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['Tx (QPSK-RRC)', 'AWGN', 'Interferencia', 'Rx (salida del canal)', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "dark green", "red", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(4):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 3, 1, 2, 2)
        for r in range(3, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "Constelacion: Tx ideal vs Rx (filtro acoplado + muestreo)", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(True)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ["Tx ideal", "Rx muestreado", "", "", "",
            "", "", "", "", ""]
        widths = [3, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["red", "blue", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, -1, -1, -1,
            -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
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
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win, 3, 0, 2, 1)
        for r in range(3, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_ccf(Sps, rrc_taps)
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_ccf(1, rrc_taps)
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(constelacion_qpsk)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc(tabla_de_verdad_constelacion, 1)
        self.blocks_xor_xx_0 = blocks.xor_bb()
        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(bps)
        self.blocks_packed_to_unpacked_xx_0 = blocks.packed_to_unpacked_bb(bps, gr.GR_MSB_FIRST)
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(8)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(N_ber, (1.0/N_ber), 4000, 1)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, Sps)
        self.blocks_delay_1 = blocks.delay(gr.sizeof_char*1, sym_delay)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, rx_delay)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, interf_freq, interf_amp, 0, 0)
        self.analog_random_source_x_0 = blocks.vector_source_b(list(map(int, numpy.random.randint(0, 2, 65536))), True)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amp, 0)
        self._SIR_dB_tool_bar = Qt.QToolBar(self)

        if None:
            self._SIR_dB_formatter = None
        else:
            self._SIR_dB_formatter = lambda x: repr(x)

        self._SIR_dB_tool_bar.addWidget(Qt.QLabel("SIR [dB]"))
        self._SIR_dB_label = Qt.QLabel(str(self._SIR_dB_formatter(self.SIR_dB)))
        self._SIR_dB_tool_bar.addWidget(self._SIR_dB_label)
        self.top_grid_layout.addWidget(self._SIR_dB_tool_bar, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._EsN0_dB_range = qtgui.Range(-5, 30, 0.5, 10, 200)
        self._EsN0_dB_win = qtgui.RangeWidget(self._EsN0_dB_range, self.set_EsN0_dB, "Es/N0 [dB]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._EsN0_dB_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._EbN0_dB_tool_bar = Qt.QToolBar(self)

        if None:
            self._EbN0_dB_formatter = None
        else:
            self._EbN0_dB_formatter = lambda x: eng_notation.num_to_str(x)

        self._EbN0_dB_tool_bar.addWidget(Qt.QLabel("Eb/N0 [dB]"))
        self._EbN0_dB_label = Qt.QLabel(str(self._EbN0_dB_formatter(self.EbN0_dB)))
        self._EbN0_dB_tool_bar.addWidget(self._EbN0_dB_label)
        self.top_grid_layout.addWidget(self._EbN0_dB_tool_bar, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_noise_source_x_0, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_pack_k_bits_bb_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.analog_sig_source_x_0, 0), (self.qtgui_freq_sink_x_0, 2))
        self.connect((self.blocks_add_xx_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_freq_sink_x_0, 3))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_delay_1, 0), (self.blocks_xor_xx_0, 1))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.qtgui_const_sink_x_0, 1))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.qtgui_number_sink_0, 0))
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.blocks_packed_to_unpacked_xx_0, 0))
        self.connect((self.blocks_packed_to_unpacked_xx_0, 0), (self.blocks_delay_1, 0))
        self.connect((self.blocks_packed_to_unpacked_xx_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.blocks_xor_xx_0, 0), (self.blocks_unpack_k_bits_bb_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.interp_fir_filter_xxx_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.blocks_xor_xx_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self.throttle_0, 0))
        self.connect((self.throttle_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.throttle_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.throttle_0, 0), (self.qtgui_time_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_DCI_Fase2_avance")
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
        self.set_sym_delay(self.span)

    def get_Sps(self):
        return self.Sps

    def set_Sps(self, Sps):
        self.Sps = Sps
        self.set_samp_rate(self.Rs*self.Sps)
        self.set_ntaps(self.span*self.Sps+1)
        self.set_rx_delay(self.Sps-1)
        self.set_SIR_dB(round(10*math.log10((1.0/self.Sps)/(self.interf_amp**2)), 2) if self.interf_amp > 0 else 'sin interferencia')
        self.blocks_keep_one_in_n_0.set_n(self.Sps)

    def get_Rs(self):
        return self.Rs

    def set_Rs(self, Rs):
        self.Rs = Rs
        self.set_Rb(self.Rs*self.bps)
        self.set_samp_rate(self.Rs*self.Sps)
        self.set_rrc_raw(firdes.root_raised_cosine(1.0, self.samp_rate, self.Rs, self.beta, self.ntaps))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_rrc_raw(firdes.root_raised_cosine(1.0, self.samp_rate, self.Rs, self.beta, self.ntaps))
        self.throttle_0.set_sample_rate(self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

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

    def get_rrc_raw(self):
        return self.rrc_raw

    def set_rrc_raw(self, rrc_raw):
        self.rrc_raw = rrc_raw
        self.set_rrc_taps([t/math.sqrt(sum([x*x for x in self.rrc_raw])) for t in self.rrc_raw])

    def get_interf_amp(self):
        return self.interf_amp

    def set_interf_amp(self, interf_amp):
        self.interf_amp = interf_amp
        self.set_SIR_dB(round(10*math.log10((1.0/self.Sps)/(self.interf_amp**2)), 2) if self.interf_amp > 0 else 'sin interferencia')
        self.analog_sig_source_x_0.set_amplitude(self.interf_amp)

    def get_bps(self):
        return self.bps

    def set_bps(self, bps):
        self.bps = bps
        self.set_Rb(self.Rs*self.bps)
        self.set_EbN0_dB((self.EsN0_dB - 10*math.log10(self.bps)))

    def get_EsN0_dB(self):
        return self.EsN0_dB

    def set_EsN0_dB(self, EsN0_dB):
        self.EsN0_dB = EsN0_dB
        self.set_noise_amp((math.sqrt(10**(-self.EsN0_dB/10.0))))
        self.set_EbN0_dB((self.EsN0_dB - 10*math.log10(self.bps)))

    def get_sym_delay(self):
        return self.sym_delay

    def set_sym_delay(self, sym_delay):
        self.sym_delay = sym_delay
        self.blocks_delay_1.set_dly(int(self.sym_delay))

    def get_rx_delay(self):
        return self.rx_delay

    def set_rx_delay(self, rx_delay):
        self.rx_delay = rx_delay
        self.blocks_delay_0.set_dly(int(self.rx_delay))

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.interp_fir_filter_xxx_0.set_taps(self.rrc_taps)
        self.fir_filter_xxx_0.set_taps(self.rrc_taps)

    def get_noise_amp(self):
        return self.noise_amp

    def set_noise_amp(self, noise_amp):
        self.noise_amp = noise_amp
        Qt.QMetaObject.invokeMethod(self._noise_amp_label, "setText", Qt.Q_ARG("QString", str(self._noise_amp_formatter(self.noise_amp))))
        self.analog_noise_source_x_0.set_amplitude(self.noise_amp)

    def get_interf_freq(self):
        return self.interf_freq

    def set_interf_freq(self, interf_freq):
        self.interf_freq = interf_freq
        self.analog_sig_source_x_0.set_frequency(self.interf_freq)

    def get_constelacion_qpsk(self):
        return self.constelacion_qpsk

    def set_constelacion_qpsk(self, constelacion_qpsk):
        self.constelacion_qpsk = constelacion_qpsk
        self.digital_constellation_decoder_cb_0.set_constellation(self.constelacion_qpsk)

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
        self.blocks_moving_average_xx_0.set_length_and_scale(self.N_ber, (1.0/self.N_ber))

    def get_EbN0_dB(self):
        return self.EbN0_dB

    def set_EbN0_dB(self, EbN0_dB):
        self.EbN0_dB = EbN0_dB
        Qt.QMetaObject.invokeMethod(self._EbN0_dB_label, "setText", Qt.Q_ARG("QString", str(self._EbN0_dB_formatter(self.EbN0_dB))))




def main(top_block_cls=QPSK_DCI_Fase2_avance, options=None):

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
