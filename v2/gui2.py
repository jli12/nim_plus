
import socket
import sys
import struct
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize    
from ctypes import *


global userIP
userIP = None

""" This class defines a C-like struct """
class Payload(Structure):
	_fields_ = [("dacData", c_uint32),
				("dacNum", c_uint32),
				("deadtime", c_float),
				("top", c_uint32),
				("middle", c_uint32),
				("bottom", c_uint32)]


class MainWindow(QMainWindow):


	def __init__(self):


		QMainWindow.__init__(self)

		self.setMinimumSize(QSize(640, 250))    
		self.setWindowTitle("Threshold Input") 

		# thresh = self.getDouble()
		# print("input:", thresh)
		# self.on_button_clicked
		# quit()
		self.threshold = 100.0
		self.dac_num = -1
		self.dacData = 0

		## DAC Signal Number
		self.cb_lbl = QLabel('DAC Signal Number:', self)
		self.cb = QComboBox(self)
		self.cb.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])

		self.cb.move(160, 40)
		self.cb.resize(60, 32)  # size of input box
		self.cb_lbl.move(30, 40)
		self.cb_lbl.resize(125, 32)  # size of input box


		## Threshold value
		self.thresh_lbl = QLabel('Threshold value:', self)
		# self.thresh_lbl.setText('Threshold value:')
		# self.line = QLineEdit(self)
		self.thresh_box = QLineEdit(self)
		self.thresh_box.setText("20")
		self.mv_lbl = QLabel('mV', self)

		# self.line.move(160, 80)  # location of input box (x,y)
		# self.line.resize(50, 32)  # size of input box
		self.thresh_lbl.move(50, 80)
		self.thresh_box.move(160, 80)
		self.thresh_box.resize(60, 32)  # size of input box
		self.mv_lbl.move(225, 80)



		## Deadtime
		self.dtime_lbl = QLabel('Deadtime:', self)
		# self.thresh_lbl.setText('Threshold value:')
		self.dtime_in = QLineEdit(self)
		self.dtime_in.setText("50")
		self.ms_lbl = QLabel('ms', self)

		self.dtime_lbl.move(85, 120)
		self.dtime_in.move(160, 120)  # location of input box (x,y)
		self.dtime_in.resize(60, 32)  # size of input box
		self.ms_lbl.move(225, 120)

		## Select Inputs
		self.top_lbl = QLabel('Top Channel:', self)
		self.top= QComboBox(self)
		self.top.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])
		self.top.setCurrentIndex(3)

		self.top.move(420, 40)
		self.top.resize(60, 32)  # size of input box
		self.top_lbl.move(330, 40)
		self.top_lbl.resize(125, 32)  # size of input box

		self.middle_lbl = QLabel('Middle Channel:', self)
		self.middle = QComboBox(self)
		self.middle.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])
		self.middle.setCurrentIndex(5)

		self.middle.move(420, 80)
		self.middle.resize(60, 32)  # size of input box
		self.middle_lbl.move(330, 80)
		self.middle_lbl.resize(125, 32)  # size of input box

		self.bottom_lbl = QLabel('Bottom Channel:', self)
		self.bottom = QComboBox(self)
		self.bottom.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])
		self.bottom.setCurrentIndex(4)

		self.bottom.move(420, 120)
		self.bottom.resize(60, 32)  # size of input box
		self.bottom_lbl.move(330, 120)
		self.bottom_lbl.resize(125, 32)  # size of input box


		## Submit  button
		pybutton = QPushButton('Set Configuration', self)
		pybutton.clicked.connect(self.on_button_clicked)
		# print(self.line.text())
		pybutton.resize(200,32)
		pybutton.move(220, 180)


	# Once "set threshold" button has been clicked
	def on_button_clicked(self):
		# if self.line.text():
		self.threshold = float(self.thresh_box.text())/1000
		self.dac_num = self.cb.currentIndex() + 1
		self.deadtime = int(self.dtime_in.text())

		print("DAC ", self.dac_num, " threshold set to: ", float(self.threshold), "V")

		#Convert threshold into DAC databits
		# Assumes threshold is put as positive for negative pulse heights
		DAC = 1.4-5*self.threshold 
		self.dacData = int(4096*DAC/3.3) # Convert into the 12-bit number for DAC
		# dacData is at most 4096, reserving 4 digits is safe
		
		# Read selected inputs
		self.inputs = (self.top.currentIndex()+1)*100 
		self.inputs += (self.middle.currentIndex()+1)*10
		self.inputs += self.bottom.currentIndex()+1
		print("Inputs:  ", self.inputs)
		print("dac_num:  ", self.dac_num)
		print("dacData:  ", self.dacData)
		self.send_bitstream()


		alert = QMessageBox()
		alert.setText('Input received')
		alert.exec()


	# send the bytestreamt to a port
	def send_bitstream(self):

		s = socket.socket()

		# HOST, PORT = "localhost", 22
		# HOST = socket.gethostname("") # essentially "localhost"

		HOST = socket.gethostbyname('localhost')
		if userIP != None:
			HOST = userIP

		PORT = 8080

		# Create a socket (SOCK_STREAM means a TCP socket)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect to server and send data
		s.connect((HOST, PORT))
		# s.sendall(ba)
		payload_out = Payload(self.dacData, self.dac_num, self.deadtime, 
			self.top.currentIndex()+1, self.middle.currentIndex()+1, self.bottom.currentIndex()+1)
		print("Sending dacData=%d, dacNum=%d, deadtime=%f, top=%d, middle=%d, bottom=%d" % 
			(self.dacData, self.dac_num, self.deadtime, self.top.currentIndex()+1, self.middle.currentIndex()+1, self.bottom.currentIndex()+1))
		nsent = s.send(payload_out)
		# return;

		# # Message format : TopMiddleBotomDAC#dacData
		# message = (self.inputs*100000)+(self.dac_num*10000)+self.dacData
		# # s.send((str(message)).encode('utf-8'))
		# # s.send((str(message)+"\n"+str(self.deadtime)).encode('utf-8'))
		# # s.send()


		# print("Dac # and threshold sent: ", message)
		# print("Deadtime: ", self.deadtime)
		# # print("Sent:	", struct.unpack('f', ba))
		# # print("Received: {}".format(received))


if __name__ == '__main__':

	try:
		userIP = sys.argv[1];
	except IndexError:
		print("No host IP specified. Default set to localhost.")
		# quit()

	app = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	sys.exit(app.exec_())

	