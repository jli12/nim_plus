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


typedef struct payload_t {
    uint32_t dacData;
    uint32_t dacNum;
    float deadtime;
    uint32_t top;
    uint32_t middle;
    uint32_t bottom;
} payload;


void error(char *msg)
{
	perror(msg);
	exit(1);
}

// Create the full bitvector to send to the FPGA
int createBitstream(char buffer[256], int *vector) {
	printf("received: %s\n",buffer);
	*vector = 0;
	// Ignore digits that select input channels
	int dacConfig = atoi(buffer)%100000;
	// extract channel and threshold from received message
	int dacNum = dacConfig / 10000;
	int dacData = dacConfig % 10000;
	printf("dacnum %d\n", dacNum);
	printf("dacData %d\n", dacData);

	// Put DAC address at 13,14,15th bits
	*vector += (dacNum-1)*pow(2,12);

	// Set vector databits
	*vector += dacData;

	// Start with base GPIO address 4120x0000
	int gpio_addr = 1092616192;
	// Move to desired GPIO module
	gpio_addr += ((dacNum-1)/2)*65536;
	// Check if even(second) channel in a module
	gpio_addr += ((dacNum-1)%2)*8;
	return gpio_addr;
}

void chooseInputs(int input, int *selection){
	*selection = 0;
	// Pick out the selected channels by digit
	int top = input/100;
	int middle = (input%100)/10;
	int bottom = input%10;

	*selection += top*pow(2,8) + middle*pow(2,4) + bottom*pow(2,0);
}


int main(int argc, char *argv[])
{
	//GPIO Variables
	unsigned page_addr, page_offset;
	void *ptr;
	unsigned page_size=sysconf(_SC_PAGESIZE);
	int gpio_addr;
	int selection_addr;
	int inputs;



	// // Open /dev/mem file
	// int fd = open("/dev/mem", O_RDWR);
	// if (fd<1){
	// 	perror(argv[0]);
	// 	return -1;
	// }

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
	// bzero((char *) &serv_addr, sizeof(serv_addr));
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
	// Configure default input channels (T,M,B)
	int inputselection = 4*pow(2,7) + 6*pow(2,3) + 5*pow(2,0);

	// // mmap the device into memory
	// selection_addr = 1092878336;
	// page_addr = (selection_addr & (~(page_size-1)));
	// page_offset = selection_addr - page_addr;
	// ptr = mmap(NULL, page_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, page_addr);
	// // write the bitvector to the corresponding GPIO slot
	// *((unsigned *)(ptr + page_offset)) = inputselection;

	while(1)
	{
		// Listen for clients
		clilen = sizeof(cli_addr);
		newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
		if (newsockfd < 0)
			error("ERROR on accept");

		// bzero(buffer,256);
		n = read(newsockfd,buffer,255);
		if (n < 0)
			error("ERROR reading from socket");


		printf("\nReceived %d bytes\n", n);
        payload *p = (payload*) buffer;
        printf("Received contents: dacData=%d, dacNum=%d, deadtime=%f, top=%d, middle=%d, bottom=%d\n", 
        	p->dacData, p->dacNum, p->deadtime, p->top, p->middle, p->bottom);
		return 0;

		printf("Sending: %s to ZedBoard\n",buffer);

		// create Bitstream and select GPIO Address based on dacNum
		gpio_addr = createBitstream(buffer, &bitvector);
		printf("Bitstream: %i\n", bitvector);

		// // mmap the device into memory
		// page_addr = (gpio_addr & (~(page_size-1)));
		// page_offset = gpio_addr - page_addr;
		// ptr = mmap(NULL, page_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, page_addr);
		// // write the bitvector to the corresponding GPIO slot
		// *((unsigned *)(ptr + page_offset)) = bitvector;

		// Select which input channels to use
		// Selected Input Channels
		inputs = atoi(buffer)/100000;
		chooseInputs(inputs, &inputselection);
		printf("selection vector: %i\n", inputselection);
		// // mmap the device into memory
		// selection_addr = 1092878336; //address for input selection data
		// page_addr = (selection_addr & (~(page_size-1)));
		// page_offset = selection_addr - page_addr;
		// ptr = mmap(NULL, page_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, page_addr);
		// // write the bitvector to the corresponding GPIO slot
		// *((unsigned *)(ptr + page_offset)) = inputselection;
	}


	return 0;
}


