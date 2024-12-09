#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>
#include <fcntl.h>
#include <math.h>
// #define PORT 8888
void error(char *msg){
	perror(msg);exit(1);
}

// Create the full bitvector to send to the FPGA
int createBitstream(char buffer[256], int *vector) {
	printf("received: %s\n",buffer);
	*vector = 0;
	// extract channel and threshold from received message
	int dacNum = atoi(buffer) / 1000;
	int threshold = atoi(buffer) % 1000;printf("dacnum %d\n", dacNum);
	printf("threshold %d\n", threshold);
	// Put DAC address at 13,14,15th bits
	*vector += (dacNum-1)*pow(2,12);
	// Set vector databits
	*vector += 1613-31*((threshold-20)/5);
	// Start with base GPIO address 4120x0000
	int gpio_addr = 1092616192;
	// Move to desired GPIO module
	gpio_addr += ((dacNum-1)/2)*65536;
	// Check if even(second) channel in a module
	gpio_addr += ((dacNum-1)%2)*8;
	return gpio_addr;
}

int main(int argc, char *argv[]){
	//GPIO Variables
	unsigned page_addr, page_offset;
	void *ptr;
	unsigned page_size=sysconf(_SC_PAGESIZE);
	int gpio_addr;

	// Open /dev/mem file
	int fd = open("/dev/mem", O_RDWR);
	if (fd<1){
		perror(argv[0]);
		return -1;
	}
	// Instantiate Server Variables
	int sockfd, newsockfd, portno, clilen;
	char buffer[256];

	struct sockaddr_in serv_addr, cli_addr;
	int n;

	// Check for provided port
	if (argc < 2) {
		fprintf(stderr,"ERROR, no port provided\n");
		exit(1);
	}
	// Create Socket
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0)
		error("ERROR opening socket");

	// Bind socket to port
	portno = atoi(argv[1]);
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(portno);
	if (bind(sockfd, (struct sockaddr *) &serv_addr,
		sizeof(serv_addr)) < 0)
		error("ERROR on binding");
	puts("bind done");

	// Listen to port
	listen(sockfd,5);
	puts("Waiting for incoming connections...");
	// Accept incoming connection
	int bitvector = 0;
	while(1){
		// Listen for clients
		clilen = sizeof(cli_addr);
		newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
		if (newsockfd < 0)
			error("ERROR on accept");

		// bzero(buffer,256);
		n = read(newsockfd,buffer,255);
		if (n < 0)
			error("ERROR reading from socket");
		printf("Sending: %s to ZedBoard\n",buffer);

		// create Bitstream and select GPIO Address based on dacNum
		gpio_addr = createBitstream(buffer, &bitvector);
		printf("Bitstream: %i\n", bitvector);
		// // mmap the device into memory
		// page_addr = (gpio_addr & (~(page_size-1)));
		// page_offset = gpio_addr - page_addr;
		// // ptr = mmap(NULL, page_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, page_addr);
		// // write the bitvector to the corresponding GPIO slot
		// *((unsigned *)(ptr + page_offset)) = bitvector;
	}
	return 0;
}