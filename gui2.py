
import socket
import sys
import struct
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize    

class MainWindow(QMainWindow):

	# def __init__(self):
	# 	# super().__init__()
	# 	QMainWindow.__init__(self)

	# 	self.title = 'jeff input dialogs - pythonspot.com'
	# 	self.left = 10
	# 	self.top = 10
	# 	self.width = 640
	# 	self.height = 480
	# 	self.initUI()

	def __init__(self):


		# self.threshold = 100.0
		# self.send_bitsream()
		# quit()


		QMainWindow.__init__(self)

		self.setMinimumSize(QSize(320, 250))    
		self.setWindowTitle("Threshold Input") 

		# thresh = self.getDouble()
		# print("input:", thresh)
		# self.on_button_clicked
		# quit()
		self.threshold = 100.0
		self.dac_num = -1

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
		self.thresh_box = QComboBox(self)
		self.thresh_box.addItems(['25', '30', '35', '40', '45', '50'])	
		self.mv_lbl = QLabel('mV', self)

		# self.line.move(160, 80)  # location of input box (x,y)
		# self.line.resize(50, 32)  # size of input box
		self.thresh_lbl.move(50, 80)
		self.thresh_box.move(160, 80)
		self.thresh_box.resize(60, 32)  # size of input box
		self.mv_lbl.move(220, 80)



		## Deadtime
		self.dtime_lbl = QLabel('Deadtime:', self)
		# self.thresh_lbl.setText('Threshold value:')
		self.dtime_in = QLineEdit(self)
		self.ms_lbl = QLabel('ms', self)

		self.dtime_lbl.move(85, 120)
		self.dtime_in.move(160, 120)  # location of input box (x,y)
		self.dtime_in.resize(60, 32)  # size of input box
		self.ms_lbl.move(230, 120)


		## Submit  button
		pybutton = QPushButton('Set Threshold', self)
		pybutton.clicked.connect(self.on_button_clicked)
		# print(self.line.text())
		pybutton.resize(200,32)
		pybutton.move(70, 180)


	# Once "set threshold" button has been clicked
	def on_button_clicked(self):
		# if self.line.text():
		self.threshold = (self.thresh_box.currentIndex() * 5) + 25
		self.dac_num = self.cb.currentIndex() + 1
		self.deadtime = int(self.dtime_in.text())

		print("DAC ", self.dac_num, " threshold set to:", float(self.threshold))
		self.send_bitsream()

		alert = QMessageBox()
		alert.setText('Input received')
		alert.exec()


	# send the bytestreamt to a port
	def send_bitsream(self):

		# s = socket.socket()

		# HOST, PORT = "localhost", 22
		# HOST = socket.gethostname("") # essentially "localhost"
		HOST = socket.gethostbyname('localhost')
		PORT = 8080



		# thresh = bytes(struct.pack("f", self.threshold))  # byte array
		# print("Sending byte array:", ba)# struct.unpack('f', ba))
		# print("test".encode())
		# print(ba)


		# Create a socket (SOCK_STREAM means a TCP socket)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect to server and send data
		s.connect((HOST, PORT))
		# s.sendall(ba)

		message = (self.dac_num*1000)+self.threshold
		s.send((str(message)+"\n"+str(self.deadtime)).encode('utf-8'))
		# s.send(str(self.deadtime).encode('utf-8'))
			# Receive data from the server and shut down
			# received = str(sock.recv(1024), "utf-8")

		print("Dac # and threshold sent: ", message)
		print("Deadtime: ", self.deadtime)
		# print("Sent:	", struct.unpack('f', ba))
		# print("Received: {}".format(received))


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	sys.exit(app.exec_())

	