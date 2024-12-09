import socketimport sysimport structfrom PyQt5 import QtCore, QtWidgetsfrom PyQt5.QtWidgets import *from PyQt5.QtCore import QSize	from ctypes import *import boolean  # pip install boolean.pyimport reimport threadingfrom threading import Threadimport osimport signalimport timeimport jsonfrom multiprocessing import Manager, Process# https://doc.bccnsoft.com/docs/PyQt5/signals_slots.html# https://stackoverflow.com/questions/55641561/have-pyqt5-labels-dynamically-update-while-sending-http-requests# =================================================================================# ================================== GLOBAL VARS ==================================userIP = NonePORT_main = 8080PORT_cnt = 5050workers = []ch_vals = [-1] * 8# pids = []# localhost = 127.0.0.1sock_main = None# sock_cnt = None# =================================================================================# ================================== HELPER FUNCS =================================# Function to convert Decimal number to Binary number  def decimalToBinary(n):  	return bin(n).replace("0b", "")# =================================================================================# ============================= DEFINE PAYLOAD STRUCT =============================""" This class defines a C-like struct """class Payload(Structure):	_fields_ = [("dacData", c_uint32),				("dacNum", c_uint32),				("deadtime", c_float),				("pulsewidth", c_float),				("top", c_uint32),				("middle", c_uint32),				("bottom", c_uint32),				# ("bool_vars", c_uint32),				# ("bool_bits", c_uint32),				("truth_1_2", c_uint32),				("truth_3_4", c_uint32)]# =================================================================================# ============================= DEFINE COUNTER THREAD =============================class CounterThread(QtCore.QObject):	count = QtCore.pyqtSignal(list)	# sock = QtCore.pyqtSignal(int)	def __init__(self, parent=None):		super(CounterThread, self).__init__(parent)		self._count = 0		self._sock = None		self._conn = None		self._run = True		self._start_time = time.time()	def counter(self, val):		self._count = val		self.count.emit([self._count, time.time()-self._start_time]) 	def countConn(self):		# for i in range(5):		# 	self.counter(i)		# 	time.sleep(2)		HOST = socket.gethostbyname('localhost')		if userIP != None:			HOST = userIP		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)		self._sock.bind((HOST, PORT_cnt))		self._sock.listen(1)		print(sys.stderr, 'waiting for a connection')		while self._run:			# Wait for a connection			self._conn, client_address = self._sock.accept()			try:				print(sys.stderr, 'connection from', client_address)				# Receive the data in small chunks and retransmit it				while True:					data = self._conn.recv(16)					# print(sys.stderr, 'received "%s"' % data)					if not data: # no more data						break										data_int = struct.unpack('<L', data)					print("received: ", data_int[0])					self.counter(data_int[0])			except:				continue			# Clean up the connection			self._conn.close()			print("Count process complete")	def terminate(self):		print("Terminating Thread")		self._run = False		self._conn.shutdown(socket.SHUT_RDWR)		self._conn.close()	# def pause(self):# =================================================================================# ================================ DEFINE MAIN GUI ================================class MainWindow(QMainWindow):	def __init__(self):		QMainWindow.__init__(self)		WIN_X = 1280		WIN_Y = 800		self.setMinimumSize(QSize(WIN_X, WIN_Y))			self.setWindowTitle("NIM+ HGCal Control Panel") 				## Init some vars		self.threshold = 100.0		self.dacNum = 0		self.dacData = 0		self.pulsewidth = 0		self.msgCnt = 0		self.jsonCnt = 0		self.childSock = None		self.paused = False		#### ---- DAC # ---- ####		self.cb_lbl = QLabel('Channel to Adjust:', self)		self.cb = QComboBox(self)		self.cb.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])		# self.cb.move(160, 40)		self.cb.move(int(WIN_X/4-80), int(WIN_Y/25))		self.cb.resize(60, 32)  # size of input box		self.cb_lbl.move(30, 40)		self.cb_lbl.move(int(WIN_X/4-210), int(WIN_Y/25))		self.cb_lbl.resize(120, 32)  # size of input box		#### ---- THRESHOLD ---- ####		self.thresh_lbl = QLabel('Threshold value:', self)		# self.thresh_lbl.move(40, 80)		self.thresh_lbl.move(int(WIN_X/4-210), int(WIN_Y/25*2))		self.thresh_lbl.resize(200, 32)		self.thresh_box = QLineEdit(self)		self.thresh_box.setText("20.0")		# self.thresh_box.move(160, 80)		self.thresh_box.move(int(WIN_X/4-75), int(WIN_Y/25*2))		self.thresh_box.resize(40, 32)  # size of input box		self.mv_lbl = QLabel('mV', self)		# self.mv_lbl.move(225, 80)		self.mv_lbl.move(int(WIN_X/4-30), int(WIN_Y/25*2))		#### ---- DEADTIME ---- ####		self.dtime_lbl = QLabel('Deadtime:', self)		self.dtime_lbl.move(int(WIN_X/4-210), int(WIN_Y/25*3))		self.dtime_in = QLineEdit(self)		self.dtime_in.setText("50.0")		self.dtime_in.move(int(WIN_X/4-75), int(WIN_Y/25*3))  # location of input box (x,y)		self.dtime_in.resize(40, 32)  # size of input box		self.ms_lbl = QLabel('ms', self)		self.ms_lbl.move(225, 120)		self.ms_lbl.move(int(WIN_X/4-30), int(WIN_Y/25*3))		#### ---- PulseWidth ---- ####		self.pwidth_lbl = QLabel('Output Pulse Width:', self)		self.pwidth_lbl.move(20, 160)		self.pwidth_lbl.resize(300,32)		self.pwidth_lbl.move(int(WIN_X/4-210), int(WIN_Y/25*4))		self.pwidth_in = QLineEdit(self)		self.pwidth_in.setText(".050")		self.pwidth_in.move(int(WIN_X/4-75), int(WIN_Y/25*4))		self.pwidth_in.resize(40, 32)  # size of input box		self.mus_lbl = QLabel('μs', self)		self.mus_lbl.move(int(WIN_X/4-30), int(WIN_Y/25*4))		#### ---- Set top channel ---- ####		self.top_lbl = QLabel('Top Channel:', self)		self.top= QComboBox(self)		self.top.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])		self.top.setCurrentIndex(3)		self.top.move(460, 40) # Input box		self.top.resize(60, 32)  		# self.top_lbl.move(320, 40) # Input label		self.top_lbl.move(int(WIN_X/4+20), int(WIN_Y/20))		self.top_lbl.resize(125, 32) 		#### ---- Set middle channel ---- ####		self.middle_lbl = QLabel('Middle Channel:', self)		self.middle = QComboBox(self)		self.middle.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])		self.middle.setCurrentIndex(5)		self.middle.move(460, 80)		self.middle.resize(60, 32)  # size of input box		self.middle_lbl.move(320, 80)		self.middle_lbl.move(int(WIN_X/4+20), int(WIN_Y/20*2))		self.middle_lbl.resize(125, 32)  # size of input box		#### ---- Set bottom channel ---- ####		self.bottom_lbl = QLabel('Bottom Channel:', self)		self.bottom = QComboBox(self)		self.bottom.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])		self.bottom.setCurrentIndex(4)		self.bottom.move(460, 120)		self.bottom.resize(60, 32)  # size of input box		# self.bottom_lbl.move(320, 120)		self.bottom_lbl.move(int(WIN_X/4+20), int(WIN_Y/20*3))		self.bottom_lbl.resize(125, 32)  # size of input box				#### ---- BOOLEAN INPUT ---- ####		self.bool_lbl = QLabel(("Output Logic :\nBoolean Input (combination of vars and ops:\n"								"Variables = {\'T\',\'M\',\'B\'}\n"								"Operations = {\'&\', \'|\', \'~\', \'(\', \')\'}"), self)		self.bool_lbl.move(int(WIN_X*3/4)-200, 25)		self.bool_lbl.resize(400, 80)		#### ---- Output Channels Boolean ---- ####		b_lbl_x, b_lbl_y = (int(WIN_X*3/4)-200, 100)		self.bool_lbl_1 = QLabel("Output 1: ", self)		self.bool_lbl_1.move(b_lbl_x, b_lbl_y)		self.bool_lbl_1.resize(100, 30)		self.bool_box_1 = QLineEdit(self)		self.bool_box_1.setText("T & B")		self.bool_box_1.move(b_lbl_x+60, b_lbl_y)		self.bool_box_1.resize(240, 32)  # size of input box		self.bool_lbl_2 = QLabel("Output 2: ", self)		self.bool_lbl_2.move(b_lbl_x, b_lbl_y+40)		self.bool_lbl_2.resize(100, 30)		self.bool_box_2 = QLineEdit(self)		self.bool_box_2.setText("T & M & B")		self.bool_box_2.move(b_lbl_x+60, b_lbl_y+40)		self.bool_box_2.resize(240, 32)  # size of input box		self.bool_lbl_3 = QLabel("Output 3: ", self)		self.bool_lbl_3.move(b_lbl_x, b_lbl_y+80)		self.bool_lbl_3.resize(100, 30)		self.bool_box_3 = QLineEdit(self)		self.bool_box_3.setText("T & M & ~B")		self.bool_box_3.move(b_lbl_x+60, b_lbl_y+80)		self.bool_box_3.resize(240, 32)  # size of input box		self.bool_lbl_4 = QLabel("Output 4: ", self)		self.bool_lbl_4.move(b_lbl_x, b_lbl_y+120)		self.bool_lbl_4.resize(100, 30)		self.bool_box_4 = QLineEdit(self)		self.bool_box_4.setText("T")		self.bool_box_4.move(b_lbl_x+60, b_lbl_y+120)		self.bool_box_4.resize(240, 32)  # size of input box		#### ---- CHANNEL DISPLAYS ---- ####		# self.ch_lbl = QLabel('Channel Values:', self)		self.ch1_lbl = QLabel('Ch 1:', self)		self.ch2_lbl = QLabel('Ch 2:', self)		self.ch3_lbl = QLabel('Ch 3:', self)		self.ch4_lbl = QLabel('Ch 4:', self)		self.ch5_lbl = QLabel('Ch 5:', self)		self.ch6_lbl = QLabel('Ch 6:', self)		self.ch7_lbl = QLabel('Ch 7:', self)		self.ch8_lbl = QLabel('Ch 8:', self)		self.ch1 = QTextBrowser(self)		self.ch2 = QTextBrowser(self)		self.ch3 = QTextBrowser(self)		self.ch4 = QTextBrowser(self)		self.ch5 = QTextBrowser(self)		self.ch6 = QTextBrowser(self)		self.ch7 = QTextBrowser(self)		self.ch8 = QTextBrowser(self)		# split between 34		# Channel 1		ch_window_y = int(WIN_Y*6/22)		ch_window_x_div = WIN_X/34		self.ch1.move(int(1*ch_window_x_div)-10, ch_window_y)		self.ch1.resize(int(ch_window_x_div)+10, int(ch_window_x_div))		self.ch1.append("null")		self.ch1_lbl.move(int(1*ch_window_x_div)-3, ch_window_y-25)		# Channel 2		self.ch2.move(int(3*ch_window_x_div)-10, ch_window_y)		self.ch2.resize(int(ch_window_x_div)+10, int(ch_window_x_div))		self.ch2.append("null")		self.ch2_lbl.move(int(3*ch_window_x_div)-3, ch_window_y-25)		# Channel 3		self.ch3.move(int(5*ch_window_x_div)-10, ch_window_y)		self.ch3.resize(int(ch_window_x_div)+10, int(ch_window_x_div))		self.ch3.append("null")		self.ch3_lbl.move(int(5*ch_window_x_div)-3, ch_window_y-25)		# Channel 4		self.ch4.move(int(7*ch_window_x_div)-10, ch_window_y)		self.ch4.resize(int(ch_window_x_div)+10, int(ch_window_x_div))		self.ch4.append("null")		self.ch4_lbl.move(int(7*ch_window_x_div)-3, ch_window_y-25)		# Channel 5		self.ch5.move(int(9*ch_window_x_div)-10, ch_window_y)		self.ch5.resize(int(ch_window_x_div)+10, int(ch_window_x_div))		self.ch5.append("null")		self.ch5_lbl.move(int(9*ch_window_x_div)-3, ch_window_y-25)		# Channel 6		self.ch6.move(int(11*ch_window_x_div)-10, ch_window_y)		self.ch6.resize(int(ch_window_x_div)+10, int(ch_window_x_div))		self.ch6.append("null")		self.ch6_lbl.move(int(11*ch_window_x_div)-3, ch_window_y-25)		# Channel 7		self.ch7.move(int(13*ch_window_x_div)-10, ch_window_y)		self.ch7.resize(int(ch_window_x_div)+10, int(ch_window_x_div))		self.ch7.append("null")		self.ch7_lbl.move(int(13*ch_window_x_div)-3, ch_window_y-25)		# Channel 8		self.ch8.move(int(15*ch_window_x_div)-10, ch_window_y)		self.ch8.resize(int(ch_window_x_div)+10, int(ch_window_x_div))		self.ch8.append("null")		self.ch8_lbl.move(int(15*ch_window_x_div)-3, ch_window_y-25)		#### ---- OUTPUT REDIRECTION BOX ---- ####		self.output_lbl = QLabel('Output for user:', self)		self.output_rd = QTextBrowser(self)		self.output_rd.move(int(WIN_X/9), int(2*WIN_Y/3))		self.output_rd.resize(int(WIN_X*7/9), int(WIN_Y/3)-10)		# self.output_rd.append("hi")		self.output_lbl.move(int(WIN_X/9), int(2*WIN_Y/3)-25)		# self.output_lbl.resize(125, 32)  # size of input box		#### ---- STOP button ---- ####		self.pause_btn = QPushButton('Pause Counter', self)		self.pause_btn.clicked.connect(self.pause_count)		self.pause_btn.move(int(WIN_X/2-100), int(2*WIN_Y/3)-100)		self.pause_btn.resize(200,32)		self.pause_btn.setEnabled(False)		# self.pause_btn = QPushButton('Stop Count', self)		# self.pause_btn.clicked.connect(self.stop_count)		# self.pause_btn.move(int(WIN_X/2-100), int(2*WIN_Y/3)-100)		# self.pause_btn.resize(200,32)		# self.pause_btn.setEnabled(False)		#### ---- Counter display ---- ####		# self.cnt_disp = QTextBrowser(self)		self.cnt_lbl = QLabel('Counter:', self)		self.cnt_lbl.move(int(WIN_X/2-60), int(2*WIN_Y/3)-160)		self.cnt_disp = QLabel("None", self)		self.cnt_disp.move(int(WIN_X/2), int(2*WIN_Y/3)-160)		# self.cnt_disp.resize(200,32)		# self.cnt_disp.append(str(cnt_val))		#### ---- Counter rate ---- #### 		self.rate_lbl = QLabel('Rate:', self)		self.rate_lbl.move(int(WIN_X/2-60), int(2*WIN_Y/3)-140)		self.rate_disp = QLabel("None", self)		self.rate_disp.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)		self.rate_disp.resize(300, 32)		self.rate_disp.move(int(WIN_X/2), int(2*WIN_Y/3)-140)		#### ---- Submit button ---- ####		self.submit_btn = QPushButton('Set Configuration', self)		# self.submit_btn.setToolTip("Pressing this button will set the NIM+ to the specified state, "		# 	"and also start/restart the counter.")		self.submit_btn.clicked.connect(self.on_button_clicked)		self.submit_btn.move(int(WIN_X/2-100), int(2*WIN_Y/3)-70)		self.submit_btn.resize(200,32)		self.submit_info = QPushButton("", self) # QPushButton('SP_MessageBoxInformation')		self.submit_info.clicked.connect(self.submit_info_msg)		self.submit_info.move(int(WIN_X/2+90), int(2*WIN_Y/3)-70)		self.submit_info.resize(40,32)		self.submit_info.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))		#### ---- Save button ---- ####		self.save_btn = QPushButton('Save State', self)		self.save_btn.clicked.connect(self.save_state)		self.save_btn.move(int(WIN_X/2-100), int(2*WIN_Y/3)-40)		self.save_btn.resize(200,32)		self.save_btn.setEnabled(False)	### --------------------------- SEND GUI DATA TO SERVER --------------------------- ### 	def on_button_clicked(self):		self.start_time = time.time()		self.timestamps = []		# if self.paused:		try:			self.worker.terminate()			self.jsonCnt += 1			time.sleep(0.3)			print("stopped")			self.display_msg("Counter restarted\n")		except:			pass		# convert to volts		self.threshold = float(self.thresh_box.text())/1000 		self.dacNum = self.cb.currentIndex() + 1		# convert to multiples of 10ns		self.deadtime = int(float(self.dtime_in.text())*10**5)		self.pulsewidth = int(float(self.pwidth_in.text())*100)		if self.threshold < 0.02:			self.display_msg("ERROR: Input threshold below 20mV bound. Value overridden and set to 20mV.\n")			self.threshold = 0.02		elif self.threshold > 0.2:			self.display_msg("ERROR: Input threshold above 200mV bound. Value overridden and set to 200mV.\n")			self.threshold = 0.2		#Convert threshold into DAC databits; assumes threshold is put as positive for negative pulse heights		DAC = 1.4-5*self.threshold 		self.dacData = int(4096*DAC/3.3) # Convert into the 12-bit number for DAC		# DAC Address bits		self.dacData += (self.dacNum-1)*2**12 # dacData is at most 4096, reserving 4 digits is safe				## Handle booleans; loop over each bool_box		self.truthtables = []		for bool_box in [self.bool_box_1, self.bool_box_2, self.bool_box_3, self.bool_box_4]:			bool_str = bool_box.text()			bool_str = bool_str.replace(" ", "")			bool_err, truthtable = self.parse_boolean(bool_str)			self.truthtables.append(truthtable)			if (bool_err == -1):				self.display_msg("ERROR: Invalid variable included.\n")				return;			elif (bool_err == -2): 				self.display_msg("ERROR: Invalid boolean function. Please enter a valid function.\n")				return;			elif (bool_err == 0): 				self.display_msg("NOTE: No boolean function inputed.\n")				return;		# split truth tables into 2 16 bit packages for server		self.truth_1_2 = self.truthtables[0]*2**8 + self.truthtables[1]		self.truth_3_4 = self.truthtables[2]*2**8 + self.truthtables[3]		self.send_bitstream()		self.update_text(self.dacNum, self.threshold)		self.display_msg("DAC "+str(self.dacNum)+" threshold set to: "+str(float(self.threshold))+\			"V with a deadtime of "+f'{self.deadtime/10**5:,}'+"ms")		self.display_msg("Boolean Function: " + str(decimalToBinary(self.truth_1_2)))		self.display_msg("Boolean Function: " + str(decimalToBinary(self.truth_3_4)))		# self.display_msg(self.vars_present + "    " + str(self.bool_bits))		# create and manage counter process		self.pause_btn.setText("Pause Counter")		self.pause_btn.setEnabled(True)		self.submit_btn.setEnabled(False)		self.save_btn.setEnabled(False)		self.dispatch_counter()		alert = QMessageBox()		alert.setText('Input received')		alert.exec()	# send the bytestreamt to a port	def send_bitstream(self):		sock_main = socket.socket()		# HOST, PORT = "localhost", 22		# HOST = socket.gethostname("") # essentially "localhost"		HOST = socket.gethostbyname('localhost')		if userIP != None:			HOST = userIP		self.host = HOST		# Create a socket (SOCK_STREAM means a TCP socket)		sock_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		# Connect to server and send data		sock_main.connect((HOST, PORT_main))		# s.sendall(ba)		# print(self.bool_bits) 		payload_out = Payload(			self.dacData, 			self.dacNum, 			self.deadtime, 			self.pulsewidth,			self.top.currentIndex()+1,			self.middle.currentIndex()+1,			self.bottom.currentIndex()+1,			self.truth_1_2, 			self.truth_3_4)		# print("Sending dacData=%d, dacNum=%d, deadtime=%i, top=%d, middle=%d, bottom=%d" % \		# 	(self.dacData, self.dacNum, self.deadtime, self.top.currentIndex()+1, \		#    self.middle.currentIndex()+1, self.bottom.currentIndex()+1))		nsent = sock_main.send(payload_out)	### --------------------------- FUNCS TO HANDLE COUNTER --------------------------- ### 	def dispatch_counter(self):		# print("dispatched")		self.cnt = -1		self.paused = False		self.update_counter([0,0])		thread = QtCore.QThread(self)		thread.start()		# self.childSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		self.worker = CounterThread()		self.worker.moveToThread(thread)		self.worker.count.connect(self.update_counter)		# self.worker.sock.connect(self.get_childSock)		QtCore.QTimer.singleShot(0, self.worker.countConn)		workers.append(thread)	def stop_count(self):		# self.childSock.shutdown(socket.SHUT_RDWR)		# self.childSock.close()		self.worker.terminate()		# self.submit_btn.setEnabled(True)		self.pause_btn.setEnabled(False)		self.display_msg("Counter stopped")	def update_counter(self, vals):		if not self.paused:			self.cnt_disp.setText(str(vals[0]))			self.timestamps.append(vals[1])			times = self.timestamps[1:]			digitsToRound = 3			if len(times) == 0:				hz = 0			else:				hz = round(len(times) / times[-1], digitsToRound)			khz = hz * 1000			npm = hz * 60 # number per min			rate_txt = str(khz) + " kHz | " + str(hz) + " Hz | " + str(npm) + " events/min"			self.rate_disp.setText(rate_txt)	def pause_count(self):		if self.paused:			self.pause_btn.setText("Pause Counter")			self.paused = False			self.submit_btn.setEnabled(False)			self.save_btn.setEnabled(False)			self.display_msg("Counter continued")		else:			self.pause_btn.setText("Continue Counter")			self.paused = True			self.submit_btn.setEnabled(True)			self.save_btn.setEnabled(True)			self.display_msg("Counter paused")	def save_channel_thresh(self, state, qbutton, num):		try:			state['channel ' + str(num) + ' threshold (mV)'] = (float(qbutton) * 1000)		except:			state['channel ' + str(num) + ' threshold (mV)'] = "null"		return state	def save_state(self, digitsToRound=3):		digitsToRound = 3		state = {}		state = self.save_channel_thresh(state, self.ch1.toPlainText(), 1)		state = self.save_channel_thresh(state, self.ch2.toPlainText(), 2)		state = self.save_channel_thresh(state, self.ch3.toPlainText(), 3)		state = self.save_channel_thresh(state, self.ch4.toPlainText(), 4)		state = self.save_channel_thresh(state, self.ch5.toPlainText(), 5)		state = self.save_channel_thresh(state, self.ch6.toPlainText(), 6)		state = self.save_channel_thresh(state, self.ch7.toPlainText(), 7)		state = self.save_channel_thresh(state, self.ch8.toPlainText(), 8)		# state[''] = self.dacData		state['dead time (ms)'] = round(self.deadtime * 1e-5, digitsToRound)		state['pulse width (ns)'] = self.pulsewidth * 10			# self.top.currentIndex()+1,			# self.middle.currentIndex()+1,			# self.bottom.currentIndex()+1,		times = self.timestamps[1:]		state['event timestamps (s)'] = [round(val, digitsToRound) for val in times]		state['number of events'] = len(times)		state['rate (events/s)'] = round(len(times) / times[-1], digitsToRound)		state['rate (kHz)'] = state['rate (events/s)'] * 1000		state['truth 1-2'] = self.truth_1_2		state['truth 3-4'] = self.truth_3_4		with open("saved_state"+str(self.jsonCnt)+".json", "w") as outfile:			json.dump(state, outfile, indent = 4)		self.display_msg("State saved")	### --------------------------- GENERAL HELPER FUNCS --------------------------- ### 	def parse_boolean(self, bool_str):		# init vars to pass to server		truthtable = 0 # int corresponding to truth table		invalid_var = ['TM', 'MT', 'TB', 'BT', 'MB', 'BM', 'TMB', 'MTB', 'TBM', 'BTM', 'MBT', 'BMT'] 					# if inputed, throw an error		# check input variables for invalid variables		# if (re.search('[a-wA-W]', self.bool_str) != None):		# 	return -1; 		if (any(var in bool_str for var in invalid_var)):			return -1, truthtable;		algebra = boolean.BooleanAlgebra()		# use boolean package to determine if expression is valid		if (len(bool_str) > 1):			# print(algebra.parse(self.bool_str))			try:				bool_str = algebra.parse(bool_str)			except: 				return -2, truthtable; # invalid bool function		# function is left empty		elif (len(bool_str) == 0):			truthtable = 0			return 0, truthtable;		# replace logical ops for python to evaluate		# translate boolean string to python syntax		bool_str = str(bool_str).replace('&', ' and ').replace('|', ' or ').replace('~', ' not ')		# use python eval() to compute truth table		tt_place = 0		for T in range(2):			for M in range(2):				for B in range(2):					try : 						truthtable += eval(bool_str)*2**(tt_place)					except : # return invalid boolean function if cannot be evaluated						return -2, truthtable					tt_place += 1 # one binary digit at a time		return 1, truthtable;	def update_text(self, chNum, text):		if chNum == 1:			self.ch1.clear()			self.ch1.append(str(text))		elif chNum == 2:			self.ch2.clear()			self.ch2.append(str(text))		elif chNum == 3:			self.ch3.clear()			self.ch3.append(str(text))		elif chNum == 4:			self.ch4.clear()			self.ch4.append(str(text))		elif chNum == 5:			self.ch5.clear()			self.ch5.append(str(text))		elif chNum == 6:			self.ch6.clear()			self.ch6.append(str(text))		elif chNum == 7:			self.ch7.clear()			self.ch7.append(str(text))		else:			self.ch8.clear()			self.ch8.append(str(text))	def display_msg(self, error):		self.msgCnt += 1		self.output_rd.append(str(self.msgCnt) + ": " + str(error))	def submit_info_msg(self):		alert = QMessageBox()		msg = ("Pressing this button will set the NIM+ to the specified state, and also start the counter. "				"Subsequent presses will update the NIM+ state and restart the counter so make sure to save the state "				"in between if necessary")		alert.setText(msg)		alert.exec()# ==================================================================================# ====================================== MAIN ======================================def startGUI(args, ipArg):	app = QApplication(sys.argv)	mainWin = MainWindow()	mainWin.show()	if not ipArg:		mainWin.display_msg("NOTE: No host IP specified. Default set to localhost.\n")	ret = app.exec_()	# print("reaping: ", pids)	# for pid in pids:	# 	os.kill(pid, signal.SIGKILL)	# 	os.waitpid(pid, 0)	for worker in workers:		worker.terminate()		worker.wait()	sys.exit(ret)if __name__ == '__main__':	ipArg = 1	try:		userIP = sys.argv[1];	except IndexError:		ipArg = 0		# print("No host IP specified. Default set to localhost.")	startGUI(sys.argv, ipArg)	