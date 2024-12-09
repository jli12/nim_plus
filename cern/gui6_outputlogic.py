import socket
import sys
import struct
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *

from PyQt5.QtCore import QSize, QTimer, QThread
from ctypes import *
import boolean  # pip install boolean.py
import re
import threading
from threading import Thread
import os
import signal
import time
import json
from multiprocessing import Manager, Process

# https://doc.bccnsoft.com/docs/PyQt5/signals_slots.html
# https://stackoverflow.com/questions/55641561/have-pyqt5-labels-dynamically-update-while-sending-http-requests

# ================================== GLOBAL VARS ==================================
userIP = None
PORT_main = 8080
PORT_cnt = 5050
workers = []
ch_vals = [-1] * 8
# pids = []
# localhost = 127.0.0.1

sock_main = None
# sock_cnt = None

# ================================== HELPER FUNCS =================================
# Function to convert Decimal number to Binary number  
def decimalToBinary(n):  
	return bin(n).replace("0b", "")

# ============================= DEFINE PAYLOAD STRUCT =============================
""" This class defines a C-like struct """
class Payload(Structure):
	_fields_ = [("dacData", c_uint32),
				("dacNum", c_uint32),
				("deadtime", c_float),
				("pulsewidth", c_float),
				# ("bool_vars", c_uint32),
				# ("bool_bits", c_uint32),
				# Output 1
				("truth_1_0", c_uint32),
				("truth_1_1", c_uint32),
				("truth_1_2", c_uint32),
				("truth_1_3", c_uint32),
				("truth_1_4", c_uint32),
				("truth_1_5", c_uint32),
				("truth_1_6", c_uint32),
				("truth_1_7", c_uint32),
				# Output 2
				("truth_2_0", c_uint32),
				("truth_2_1", c_uint32),
				("truth_2_2", c_uint32),
				("truth_2_3", c_uint32),
				("truth_2_4", c_uint32),
				("truth_2_5", c_uint32),
				("truth_2_6", c_uint32),
				("truth_2_7", c_uint32),
				# Output 3
				("truth_3_0", c_uint32),
				("truth_3_1", c_uint32),
				("truth_3_2", c_uint32),
				("truth_3_3", c_uint32),
				("truth_3_4", c_uint32),
				("truth_3_5", c_uint32),
				("truth_3_6", c_uint32),
				("truth_3_7", c_uint32),
				# Output 4
				("truth_4_0", c_uint32),
				("truth_4_1", c_uint32),
				("truth_4_2", c_uint32),
				("truth_4_3", c_uint32),
				("truth_4_4", c_uint32),
				("truth_4_5", c_uint32),
				("truth_4_6", c_uint32),
				("truth_4_7", c_uint32),
				("updateParams", c_uint32),
				("pauseCount", c_uint32),]
# =================================================================================

# ============================= DEFINE COUNTER THREAD =============================
class CounterThread(QtCore.QObject):
	count = QtCore.pyqtSignal(list)

	def __init__(self, parent=None):
		super(CounterThread, self).__init__(parent)
		self.connected = False
		self._count = 0
		self._sock = None
		self._conn = None
		self._run = True
		self._start_time = time.time()

	def counter(self):
		# update counter text via update_counter function that was connected 
		print("emitting", self._vals)
		
		# print(self._count)
		# print(time.time()-self._start_time)
		self._vals.append(time.time()-self._start_time)
		self.count.emit(self._vals) 
		#self.count.emit([1,2,3,4,5])
	
	def countConn(self):
		HOST = socket.gethostbyname('localhost')
		if userIP != None:
			HOST = userIP
		print(HOST)
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.bind(("", PORT_cnt))
		self._sock.listen(1)

		print(sys.stderr, 'waiting for a connection')
		self.connected=True
		self._run = True
		
	def startCounter(self):
		self.countConn()
		# Start clock
		self.runstart = time.time()

		#while self._run:
		# Wait for a connection
		self._conn, client_address = self._sock.accept()

		try:
			print(sys.stderr, 'connection from', client_address)

			# Receive the data in small chunks and retransmit it
			while True: # self._run:		
				app.processEvents()
				data = self._conn.recv(16)
				# print(sys.stderr, 'received "%s"' % data)

				if not data: # no more data
					break
				
				data_int = struct.unpack('<4I', data)
				# print(data_int)
				# current_time = time.time()-self.runstart
				# rate = [i/current_time for i in data_int]
				# print("Counter4 : ", data_int[3], "Counts : %.2f" % current_time, " (s) :", "%.2f" % rate[3], "(Hz)")

				self._vals = [data_int] # [data_int, rate]
				# print(self._vals)
				app.processEvents()

				self.counter()
				app.processEvents()
				
		except:
			pass

		# Clean up the connection
		self._conn.close()
		print("Count process complete")

	def terminate(self):
		print("Terminating Thread")
		self._run = False
		#self._conn.shutdown(socket.SHUT_RDWR)
		#self._conn.close()


# ================================ DEFINE MAIN GUI ================================
class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		WIN_X = 1280
		WIN_Y = 800
		self.setMinimumSize(QSize(WIN_X, WIN_Y))	
		self.setWindowTitle("NIM+ HGCal Control Panel") 
		
		## Init some vars
		self.threshold = 100.0
		self.dacNum = 0
		self.dacData = 0
		self.pulsewidth = 0
		self.msgCnt = 0

		self.jsonCnt = 0
		self.childSock = None
		self.paused = False

		self.updateParams = 0
		self.pauseCount = 0
		self.total_pauseT = 0
		# self.resetCount = 0
		QThread.currentThread().setObjectName('main')

		#### ---- DAC # ---- ####
		self.cb_lbl = QLabel('Channel to Adjust Threshold:', self)
		self.cb = QComboBox(self)
		self.cb.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])
		self.cb.move(160, 40)
		self.cb.resize(60, 32)  # size of input box
		self.cb_lbl.move(30, 40)
		self.cb_lbl.resize(125, 32)  # size of input box

		#### ---- THRESHOLD ---- ####
		self.thresh_lbl = QLabel('Threshold value:', self)
		self.thresh_box = QLineEdit(self)
		self.thresh_box.setText("20")
		self.mv_lbl = QLabel('mV', self)
		self.thresh_lbl.move(40, 80)
		self.thresh_lbl.resize(200, 32)
		self.thresh_box.move(160, 80)
		self.thresh_box.resize(60, 32)  # size of input box
		self.mv_lbl.move(225, 80)

		#### ---- DEADTIME ---- ####
		self.dtime_lbl = QLabel('Deadtime:', self)
		self.dtime_in = QLineEdit(self)
		self.dtime_in.setText("50")
		self.ms_lbl = QLabel('ms', self)
		self.dtime_lbl.move(85, 120)
		self.dtime_in.move(160, 120)  # location of input box (x,y)
		self.dtime_in.resize(60, 32)  # size of input box
		self.ms_lbl.move(225, 120)

		#### ---- PulseWidth ---- ####
		self.pwidth_lbl = QLabel('Output Pulse Width:', self)
		self.pwidth_in = QLineEdit(self)
		self.pwidth_in.setText(".05")
		self.mus_lbl = QLabel('Î¼s', self)
		self.pwidth_lbl.move(20, 160)
		self.pwidth_lbl.resize(300,32)
		self.pwidth_in.move(160, 160)  # location of input box (x,y)
		self.pwidth_in.resize(60, 32)  # size of input box
		self.mus_lbl.move(225, 160)		

		#### ---- BOOLEAN INPUT ---- ####
		self.bool_lbl = QLabel(("Output Logic :\nBoolean Input (In Python Syntax):\n"
								"Inputs = I1, I2, ...\n"
								"Operations = and, or, not, ^ "), self)
		self.bool_lbl.move(int(WIN_X/2)+100, 25)
		self.bool_lbl.resize(400, 80)	

		#### ---- Output Channels Boolean ---- ####
		self.bool_lbl_1 = QLabel("Output 1: ", self)
		self.bool_lbl_1.move(int(WIN_X/2)+30, 100)
		self.bool_lbl_1.resize(100, 30)
		self.bool_box_1 = QLineEdit(self)
		self.bool_box_1.setText("I4 and I5")
		self.bool_box_1.move(int(WIN_X/2)+100, 100)
		self.bool_box_1.resize(240, 32)  # size of input box

		self.bool_lbl_2 = QLabel("Output 2: ", self)
		self.bool_lbl_2.move(int(WIN_X/2)+30, 140)
		self.bool_lbl_2.resize(100, 30)
		self.bool_box_2 = QLineEdit(self)
		self.bool_box_2.setText("I4 and I5 and I6")
		self.bool_box_2.move(int(WIN_X/2)+100, 140)
		self.bool_box_2.resize(240, 32)  # size of input box

		self.bool_lbl_3 = QLabel("Output 3: ", self)
		self.bool_lbl_3.move(int(WIN_X/2)+30, 180)
		self.bool_lbl_3.resize(100, 30)
		self.bool_box_3 = QLineEdit(self)
		self.bool_box_3.setText("I4 and I5 and not I6")
		self.bool_box_3.move(int(WIN_X/2)+100, 180)
		self.bool_box_3.resize(240, 32)  # size of input box

		self.bool_lbl_4 = QLabel("Output 4: ", self)
		self.bool_lbl_4.move(int(WIN_X/2)+30, 220)
		self.bool_lbl_4.resize(100, 30)
		self.bool_box_4 = QLineEdit(self)
		self.bool_box_4.setText("I4")
		self.bool_box_4.move(int(WIN_X/2)+100, 220)
		self.bool_box_4.resize(240, 32)  # size of input box

		#### ---- CHANNEL DISPLAYS ---- ####
		# self.ch_lbl = QLabel('Channel Values:', self)
		self.ch1_lbl = QLabel('Ch 1:', self)
		self.ch2_lbl = QLabel('Ch 2:', self)
		self.ch3_lbl = QLabel('Ch 3:', self)
		self.ch4_lbl = QLabel('Ch 4:', self)
		self.ch5_lbl = QLabel('Ch 5:', self)
		self.ch6_lbl = QLabel('Ch 6:', self)
		self.ch7_lbl = QLabel('Ch 7:', self)
		self.ch8_lbl = QLabel('Ch 8:', self)

		self.ch1 = QTextBrowser(self)
		self.ch2 = QTextBrowser(self)
		self.ch3 = QTextBrowser(self)
		self.ch4 = QTextBrowser(self)
		self.ch5 = QTextBrowser(self)
		self.ch6 = QTextBrowser(self)
		self.ch7 = QTextBrowser(self)
		self.ch8 = QTextBrowser(self)

		# split between 34
		# Channel 1
		ch_window_y = int(WIN_Y*6/22)
		ch_window_x_div = WIN_X/34
		self.ch1.move(int(1*ch_window_x_div)-10, ch_window_y)
		self.ch1.resize(int(ch_window_x_div)+10, int(ch_window_x_div))
		self.ch1.append("null")
		self.ch1_lbl.move(int(1*ch_window_x_div)-3, ch_window_y-25)
		# Channel 2
		self.ch2.move(int(3*ch_window_x_div)-10, ch_window_y)
		self.ch2.resize(int(ch_window_x_div)+10, int(ch_window_x_div))
		self.ch2.append("null")
		self.ch2_lbl.move(int(3*ch_window_x_div)-3, ch_window_y-25)
		# Channel 3
		self.ch3.move(int(5*ch_window_x_div)-10, ch_window_y)
		self.ch3.resize(int(ch_window_x_div)+10, int(ch_window_x_div))
		self.ch3.append("null")
		self.ch3_lbl.move(int(5*ch_window_x_div)-3, ch_window_y-25)
		# Channel 4
		self.ch4.move(int(7*ch_window_x_div)-10, ch_window_y)
		self.ch4.resize(int(ch_window_x_div)+10, int(ch_window_x_div))
		self.ch4.append("null")
		self.ch4_lbl.move(int(7*ch_window_x_div)-3, ch_window_y-25)
		# Channel 5
		self.ch5.move(int(9*ch_window_x_div)-10, ch_window_y)
		self.ch5.resize(int(ch_window_x_div)+10, int(ch_window_x_div))
		self.ch5.append("null")
		self.ch5_lbl.move(int(9*ch_window_x_div)-3, ch_window_y-25)
		# Channel 6
		self.ch6.move(int(11*ch_window_x_div)-10, ch_window_y)
		self.ch6.resize(int(ch_window_x_div)+10, int(ch_window_x_div))
		self.ch6.append("null")
		self.ch6_lbl.move(int(11*ch_window_x_div)-3, ch_window_y-25)
		# Channel 7
		self.ch7.move(int(13*ch_window_x_div)-10, ch_window_y)
		self.ch7.resize(int(ch_window_x_div)+10, int(ch_window_x_div))
		self.ch7.append("null")
		self.ch7_lbl.move(int(13*ch_window_x_div)-3, ch_window_y-25)
		# Channel 8
		self.ch8.move(int(15*ch_window_x_div)-10, ch_window_y)
		self.ch8.resize(int(ch_window_x_div)+10, int(ch_window_x_div))
		self.ch8.append("null")
		self.ch8_lbl.move(int(15*ch_window_x_div)-3, ch_window_y-25)

		#### ---- OUTPUT REDIRECTION BOX ---- ####
		self.output_lbl = QLabel('Output for user:', self)
		self.output_rd = QTextBrowser(self)
		self.output_rd.move(int(WIN_X/9), int(2*WIN_Y/3))
		self.output_rd.resize(int(WIN_X*7/9), int(WIN_Y/3)-10)
		self.output_lbl.move(int(WIN_X/9), int(2*WIN_Y/3)-25)

		#### ---- STOP button ---- ####
		self.pause_btn = QPushButton('Pause Counter', self)
		self.pause_btn.clicked.connect(self.pause_count)
		self.pause_btn.move(int(WIN_X/2-100), int(2*WIN_Y/3)-100)
		self.pause_btn.resize(200,32)
		self.pause_btn.setEnabled(False)

		#### ---- Counter displays ---- ####
		# self.cnt_disp = QTextBrowser(self)
		# Counter 1
		self.cnt_lbl_1 = QLabel('Counter 1:', self)
		self.cnt_lbl_1.move(int(WIN_X/2-360), int(2*WIN_Y/3)-130)

		self.cnt_disp_1 = QLabel("None", self)
		self.cnt_disp_1.move(int(WIN_X/2-300), int(2*WIN_Y/3)-130)
		# Counter 2
		self.cnt_lbl_2 = QLabel('Counter 2:', self)
		self.cnt_lbl_2.move(int(WIN_X/2-180), int(2*WIN_Y/3)-130)

		self.cnt_disp_2 = QLabel("None", self)
		self.cnt_disp_2.move(int(WIN_X/2-120), int(2*WIN_Y/3)-130)
		# Counter 3
		self.cnt_lbl_3 = QLabel('Counter 3:', self)
		self.cnt_lbl_3.move(int(WIN_X/2+120), int(2*WIN_Y/3)-130)

		self.cnt_disp_3 = QLabel("None", self)
		self.cnt_disp_3.move(int(WIN_X/2+180), int(2*WIN_Y/3)-130)
		# Counter 4
		self.cnt_lbl_4 = QLabel('Counter 4:', self)
		self.cnt_lbl_4.move(int(WIN_X/2+300), int(2*WIN_Y/3)-130)

		self.cnt_disp_4 = QLabel("None", self)
		self.cnt_disp_4.move(int(WIN_X/2+360), int(2*WIN_Y/3)-130)

		#### ---- Submit button ---- ####
		self.submit_btn = QPushButton('Set Configuration', self)
		# self.submit_btn.setToolTip("Pressing this button will set the NIM+ to the specified state, "
		# 	"and also start/restart the counter.")
		self.submit_btn.clicked.connect(self.on_button_clicked)
		self.submit_btn.move(int(WIN_X/2-100), int(2*WIN_Y/3)-70)
		self.submit_btn.resize(200,32)

		self.submit_info = QPushButton("", self) # QPushButton('SP_MessageBoxInformation')
		self.submit_info.clicked.connect(self.submit_info_msg)
		self.submit_info.move(int(WIN_X/2+90), int(2*WIN_Y/3)-70)
		self.submit_info.resize(40,32)
		self.submit_info.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))

		#### ---- Save button ---- ####
		self.save_btn = QPushButton('Save State', self)
		self.save_btn.clicked.connect(self.save_state)
		self.save_btn.move(int(WIN_X/2-100), int(2*WIN_Y/3)-40)
		self.save_btn.resize(200,32)
		self.save_btn.setEnabled(False)


	### --------------------------- SEND GUI DATA TO SERVER --------------------------- ### 
	def on_button_clicked(self):
		self.start_time = time.time()
		self.timestamps = []

		# convert to volts
		self.threshold = float(self.thresh_box.text())/1000 
		self.dacNum = self.cb.currentIndex() + 1
		# convert to multiples of 10ns
		self.deadtime = int(float(self.dtime_in.text())*10**5)
		self.pulsewidth = int(float(self.pwidth_in.text())*100)

		if self.threshold < 0.02:
			self.display_msg("ERROR: Input threshold below 20mV bound. Value overridden and set to 20mV.\n")
			self.threshold = 0.02
		elif self.threshold > 0.2:
			self.display_msg("ERROR: Input threshold above 200mV bound. Value overridden and set to 200mV.\n")
			self.threshold = 0.2

		#Convert threshold into DAC databits; assumes threshold is put as positive for negative pulse heights
		DAC = 1.4-5*self.threshold 
		self.dacData = int(4096*DAC/3.3) # Convert into the 12-bit number for DAC
		# DAC Address bits
		self.dacData += (self.dacNum-1)*2**12 # dacData is at most 4096, reserving 4 digits is safe
		
		print(self.dacData)

		## Handle booleans; loop over each bool_box
		self.all_truthtables = []
		for bool_box in [self.bool_box_1, self.bool_box_2, self.bool_box_3, self.bool_box_4]:
			bool_str = bool_box.text()
			# bool_str = bool_str.replace(" ", "")
			bool_err, truthtable = self.parse_boolean(bool_str)
			self.all_truthtables.append(truthtable)
			if (bool_err == -1):
				self.display_msg("ERROR: Invalid variable included.\n")
				return;
			elif (bool_err == -2): 
				self.display_msg("ERROR: Invalid boolean function. Please enter a valid function.\n")
				return;
			elif (bool_err == 0): 
				self.display_msg("NOTE: No boolean function inputed.\n")
				return;

		# Get Truth Tables:  Put most significant bits first
		# for i in range(len(self.all_truthtables)):
		# 	print(i, self.all_truthtables[i])
		# Output 1
		self.truth_1_0 = self.all_truthtables[0][7]
		self.truth_1_1 = self.all_truthtables[0][6]
		self.truth_1_2 = self.all_truthtables[0][5]
		self.truth_1_3 = self.all_truthtables[0][4]
		self.truth_1_4 = self.all_truthtables[0][3]
		self.truth_1_5 = self.all_truthtables[0][2]
		self.truth_1_6 = self.all_truthtables[0][1]
		self.truth_1_7 = self.all_truthtables[0][0]
		# Output 2
		self.truth_2_0 = self.all_truthtables[1][7]
		self.truth_2_1 = self.all_truthtables[1][6]
		self.truth_2_2 = self.all_truthtables[1][5]
		self.truth_2_3 = self.all_truthtables[1][4]
		self.truth_2_4 = self.all_truthtables[1][3]
		self.truth_2_5 = self.all_truthtables[1][2]
		self.truth_2_6 = self.all_truthtables[1][1]
		self.truth_2_7 = self.all_truthtables[1][0]
		# Output 3
		self.truth_3_0 = self.all_truthtables[2][7]
		self.truth_3_1 = self.all_truthtables[2][6]
		self.truth_3_2 = self.all_truthtables[2][5]
		self.truth_3_3 = self.all_truthtables[2][4]
		self.truth_3_4 = self.all_truthtables[2][3]
		self.truth_3_5 = self.all_truthtables[2][2]
		self.truth_3_6 = self.all_truthtables[2][1]
		self.truth_3_7 = self.all_truthtables[2][0]
		# Output 1
		self.truth_4_0 = self.all_truthtables[3][7]
		self.truth_4_1 = self.all_truthtables[3][6]
		self.truth_4_2 = self.all_truthtables[3][5]
		self.truth_4_3 = self.all_truthtables[3][4]
		self.truth_4_4 = self.all_truthtables[3][3]
		self.truth_4_5 = self.all_truthtables[3][2]
		self.truth_4_6 = self.all_truthtables[3][1]
		self.truth_4_7 = self.all_truthtables[3][0]

		self.updateParams = 1 # updating configuration also resets counter
		self.send_bitstream()
		self.update_text(self.dacNum, self.threshold)
		self.display_msg("DAC "+str(self.dacNum)+" threshold set to: "+str(float(self.threshold))+\
			"V with a deadtime of "+f'{self.deadtime/10**5:,}'+"ms")
		# self.display_msg("Boolean Function: " + str(decimalToBinary(self.truth_4_6)))
		# self.display_msg("Boolean Function: " + str(decimalToBinary(self.truth_4_7)))
		# self.display_msg(self.vars_present + "    " + str(self.bool_bits))

		# Change Button visibilities
		self.pause_btn.setText("Pause Counter")
		self.pause_btn.setEnabled(True)
		self.paused = False
		self.submit_btn.setEnabled(False)
		self.save_btn.setEnabled(False)
		
		# Create and manage counter process
		#print("json:", )
		thread_name = QThread.currentThread().objectName()
		print(thread_name)
		if not hasattr(self, "counterThread"):
			worker = CounterThread()
			#self.counterThread = 
			self.dispatch_counter(worker)
			self.jsonCnt += 1
			
		alert = QMessageBox()
		alert.setText('Input received')
		alert.exec()
		

	# send the bytestreamt to a port
	def send_bitstream(self):
		sock_main = socket.socket()

		HOST = socket.gethostbyname('localhost')
		if userIP != None:
			HOST = userIP
		self.host = HOST

		# Create a socket (SOCK_STREAM means a TCP socket)
		sock_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connect to server and send data
		sock_main.connect((HOST, PORT_main))
 
		payload_out = Payload(
			self.dacData, 
			self.dacNum, 
			self.deadtime, 
			self.pulsewidth,
			# Output 1
			self.truth_1_0,
			self.truth_1_1, 
			self.truth_1_2,
			self.truth_1_3,
			self.truth_1_4,
			self.truth_1_5,
			self.truth_1_6,
			self.truth_1_7,
			# Output 2
			self.truth_2_0,
			self.truth_2_1, 
			self.truth_2_2,
			self.truth_2_3,
			self.truth_2_4,
			self.truth_2_5,
			self.truth_2_6,
			self.truth_2_7,
			# Output 3
			self.truth_3_0,
			self.truth_3_1, 
			self.truth_3_2,
			self.truth_3_3,
			self.truth_3_4,
			self.truth_3_5,
			self.truth_3_6,
			self.truth_3_7,
			# Output 4
			self.truth_4_0,
			self.truth_4_1, 
			self.truth_4_2,
			self.truth_4_3,
			self.truth_4_4,
			self.truth_4_5,
			self.truth_4_6,
			self.truth_4_7,
			# Change Params or Pause/Unpause
			self.updateParams,
			self.pauseCount)

		# print("Sending dacData=%d, dacNum=%d, deadtime=%i, top=%d, middle=%d, bottom=%d" % \
		# 	(self.dacData, self.dacNum, self.deadtime, self.top.currentIndex()+1, \
		#    self.middle.currentIndex()+1, self.bottom.currentIndex()+1))
		nsent = sock_main.send(payload_out)

	### --------------------------- FUNCS TO HANDLE COUNTER --------------------------- ### 
	# cnt_val = pyqtSignal(int)
	def dispatch_counter(self, worker):
		# print("dispatched")
		self.cnt = -1
		self.paused = False
		self.update_counter([[0,0,0,0], [0,0,0,0], 0.0])
		
		## Create threading objects
		self.counterThread = QThread(self)
		self.counterThread.setObjectName('counterThread')
		#timer = QTimer(self)    
		
		#timer.timeout.connect(worker.counter)
		worker.count.connect(self.update_counter)

		worker.moveToThread(self.counterThread)
		#timer.moveToThread(thread)    
		#thread.timer = timer
		self.counterThread.worker = worker
		
		#timer.start(1000)
		
		
		## Connect signals and slots
		#self.thread.started.connect(self.worker.run)
		#self.worker.finished.connect(self.thread.quit)
		worker.startCounter()
		
		# self.worker.sock.connect(self.get_childSock)
		
		self.counterThread.start()
		# QtCore.QTimer.singleShot(5000, self.worker.countConn())
		# workers.append(thread)
		
		#return thread

	def stop_count(self):
		# self.childSock.shutdown(socket.SHUT_RDWR)
		# self.childSock.close()
		self.counterThread.worker.terminate()

		# self.submit_btn.setEnabled(True)
		self.pause_btn.setEnabled(False)
		self.display_msg("Counter stopped")

	def update_counter(self, vals):
		
		if not self.paused:
			counts = vals[0]
			rates = counts / (self.timestamps[-1] - self.total_pauseT) # vals[1]
			time = vals[1]
			# print("HIHI")
			self.cnt_disp_1.setText(str(counts[0])+" Rate: %.2f"% rates[0]+" (Hz)")
			self.cnt_disp_2.setText(str(counts[1])+" Rate: %.2f"% rates[1]+" (Hz)")
			self.cnt_disp_3.setText(str(counts[2])+" Rate: %.2f"% rates[2]+" (Hz)")
			self.cnt_disp_4.setText(str(counts[3])+" Rate: %.2f"% rates[3]+" (Hz)")
			self.timestamps.append(time)


	def pause_count(self):
		if self.paused: # unpause
			self.updateParams = 0
			self.pauseCount = 1
			self.total_pauseT += self.paused_time - time.time()

			print(self.pauseCount)
			self.send_bitstream() # Send unpause signal

			self.pause_btn.setText("Pause Counter")
			self.paused = False
			self.submit_btn.setEnabled(False)
			self.save_btn.setEnabled(False)
			self.display_msg("Counter continued")
		else: # pause
			self.updateParams = 0
			self.pauseCount = 0
			self.paused_time = time.time()

			print(self.pauseCount)
			self.send_bitstream() # Send pause signal

			self.pause_btn.setText("Continue Counter")
			self.paused = True
			self.submit_btn.setEnabled(True)
			self.save_btn.setEnabled(True)
			self.display_msg("Counter paused")


	def save_state(self):
		state = {}
		state['channel 1 threshold (V)'] = self.ch1.toPlainText()
		state['channel 2 threshold (V)'] = self.ch2.toPlainText()
		state['channel 3 threshold (V)'] = self.ch3.toPlainText()
		state['channel 4 threshold (V)'] = self.ch4.toPlainText()
		state['channel 5 threshold (V)'] = self.ch5.toPlainText()
		state['channel 6 threshold (V)'] = self.ch6.toPlainText()
		state['channel 7 threshold (V)'] = self.ch7.toPlainText()
		state['channel 8 threshold (V)'] = self.ch8.toPlainText()

		# state[''] = self.dacData
		state['dead time (10ns)'] = self.deadtime
		state['pulse width (10ns)'] = self.pulsewidth
			# self.top.currentIndex()+1,
			# self.middle.currentIndex()+1,
			# self.bottom.currentIndex()+1,
		state['Output1'] = self.bool_box_1.text()
		state['Output2'] = self.bool_box_2.text()
		state['Output3'] = self.bool_box_3.text()
		state['Output4'] = self.bool_box_4.text()
		times = self.timestamps[1:]
		state['event timestamps (s)'] = times
		state['number of events'] = len(times)
		state['rate (events/s)'] = len(times) / (times[-1] - self.total_pauseT)



		with open("saved_state"+str(self.jsonCnt)+".json", "w") as outfile:
			json.dump(state, outfile, indent = 4)



	### --------------------------- GENERAL HELPER FUNCS --------------------------- ### 
	def parse_boolean(self, bool_str):
		# init vars to pass to server
		truthtable = 0 # int corresponding to truth table
		
		if (len(bool_str) == 0):
			truthtable = 0
			return 0, truthtable

		tt_place = 0
		truthtables = []
		for I1 in range(2):
			for I2 in range(2):
				for I3 in range(2):
					for I4 in range(2):
						for I5 in range(2):
							for I6 in range(2):
								for I7 in range(2):
									for I8 in range(2):
										try: # Except valid Python Syntax
											truthtable += eval(bool_str)*2**(tt_place)
											tt_place += 1 
											# After 32 bits, save table and move to next unsigned 32-int
											if tt_place == 32:
												tt_place = 0
												truthtables.append(truthtable)	
												truthtable = 0
												# return 1, truthtables
										except:
											return -2, truthtables
										
		return 1, truthtables



	def update_text(self, chNum, text):
		if chNum == 1:
			self.ch1.clear()
			self.ch1.append(str(text))
		elif chNum == 2:
			self.ch2.clear()
			self.ch2.append(str(text))
		elif chNum == 3:
			self.ch3.clear()
			self.ch3.append(str(text))
		elif chNum == 4:
			self.ch4.clear()
			self.ch4.append(str(text))
		elif chNum == 5:
			self.ch5.clear()
			self.ch5.append(str(text))
		elif chNum == 6:
			self.ch6.clear()
			self.ch6.append(str(text))
		elif chNum == 7:
			self.ch7.clear()
			self.ch7.append(str(text))
		else:
			self.ch8.clear()
			self.ch8.append(str(text))


	def display_msg(self, error):
		self.msgCnt += 1
		self.output_rd.append(str(self.msgCnt) + ": " + str(error))

	def submit_info_msg(self):
		alert = QMessageBox()
		msg = ("Pressing this button will set the NIM+ to the specified state, and also start the counter. "
				"Subsequent presses will update the NIM+ state and restart the counter so make sure to save the state "
				"in between if necessary")
		alert.setText(msg)
		alert.exec()


# ==================================================================================

# ====================================== MAIN ======================================
def startGUI(args, app, ipArg):
	
	mainWin = MainWindow()
	mainWin.show()
	if not ipArg:
		mainWin.display_msg("NOTE: No host IP specified. Default set to localhost.\n")
	ret = app.exec_()

	for worker in workers:
		worker.terminate()
		worker.wait()

	sys.exit(ret)


if __name__ == '__main__':

	ipArg = 1

	try:
		userIP = sys.argv[1]
	except IndexError:
		ipArg = 0
		# print("No host IP specified. Default set to localhost.")

	app = QApplication(sys.argv)
	startGUI(sys.argv, app, ipArg)