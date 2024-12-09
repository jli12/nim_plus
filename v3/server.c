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
    float_t deadtime;
    uint32_t top;
    uint32_t middle;
    uint32_t bottom;
    uint32_t bool_vars; // a 3 digit int, formated as xyz (e.g. if y and z are present -> 011)
    uint32_t bool_bits;  // the 8 digit truth table generated from the boolean string input
} payload;


void error(char *msg)
{
	perror(msg);
	exit(1);
}

void writeGPIO(unsigned address, int value, int fd){
	unsigned page_size=sysconf(_SC_PAGESIZE);
	unsigned page_addr = (address & (~(page_size-1)));
	unsigned page_offset = address - page_addr;
	void* ptr = mmap(NULL, page_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, page_addr);
	// write the bitvector to the corresponding GPIO slot
	*((unsigned *)(ptr + page_offset)) = value;
}


int main(int argc, char *argv[])
{
	// GPIO addresses
	int gpio_addr;
	int selection_addr;

	// // Open /dev/mem file
	// int fd = open("/dev/mem", O_RDWR);
	// if (fd<1){
	// 	perror(argv[0]);
	// 	return -1;
	// }

	// Instantiate Server Variables
	int sockfd, newsockfd, portno, clilen;
	char buffer[512];

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

	// Configure default input channels (T,M,B)
	int inputselection = 4*pow(2,8) + 6*pow(2,4) + 5*pow(2,0);

	// // Write the default input configuration (top : 4, middle : 6, bottom : 5)
	// selection_addr = 1092878336;
	// writeGPIO(selection_addr,inputselection,fd);

	while(1)
	{
		// Listen for clients
		clilen = sizeof(cli_addr);
		newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
		if (newsockfd < 0)
			error("ERROR on accept");

		// bzero(buffer,256);
		n = read(newsockfd,buffer,511);
		if (n < 0)
			error("ERROR reading from socket");


		printf("\nReceived %d bytes\n", n);
        payload* p = malloc(sizeof(payload));
        // p->bool_bits = malloc(8*sizeof(char));
        p = (payload*) buffer;
        // p-> bool_bits = "hi";
        printf("Received contents: dacData=%d, dacNum=%d, deadtime=%f, top=%d, middle=%d, bottom=%d\n", 
        	p->dacData, p->dacNum, p->deadtime, p->top, p->middle, p->bottom);

        printf("vars: %d\n", p->bool_vars); // 
        printf("bit: %d\n", p->bool_bits);



		//return 0;

		// // GPIO Address based on dacNum
		// // Start with base GPIO address 4120x0000
  //       gpio_addr = 1092616192;
		// // Move to desired GPIO module
		// gpio_addr += ((p->dacNum-1)/2)*65536;
		// // Check if even(second) channel in a module
		// gpio_addr += ((p->dacNum-1)%2)*8;
		// // Send dacData (dac# and threshold) to the correct GPIO Address
		// writeGPIO(gpio_addr,p->dacData,fd);

		// // Select which input channels to use
		// // Format the input configuration into the binary vector
		// inputselection = p->top*pow(2,8)+p->middle*pow(2,4)+p->bottom*pow(2,0);
		// printf("selection vector: %i\n", inputselection);
		// // Write the input configuration
		// writeGPIO(selection_addr,inputselection,fd);

		// // Write the deadtime (address is selection_addr + 8)
		// writeGPIO(1092878344, (int)p->deadtime, fd);
	}

	return 0;
}
