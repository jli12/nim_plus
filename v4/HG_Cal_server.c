#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <math.h>

#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
// #define PORT 8888


typedef struct payload_t {
    uint32_t dacData;
    uint32_t dacNum;
    float_t deadtime;
    float_t pulsewidth;
    uint32_t top;
    uint32_t middle;
    uint32_t bottom;
    uint32_t truth_1_2;
    uint32_t truth_3_4;
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
	// write the value to the corresponding GPIO slot
	*((unsigned *)(ptr + page_offset)) = value;
}

int readGPIO(unsigned address, int fd){
	unsigned page_size=sysconf(_SC_PAGESIZE);
	unsigned page_addr = (address & (~(page_size-1)));
	unsigned page_offset = address - page_addr;
	void* ptr = mmap(NULL, page_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, page_addr);
	// read value from GPIO slot
	int value = *((unsigned *)(ptr + page_offset));

	return value;
}

int cliConn (char *host, int port) {
 
	struct sockaddr_in name;
	struct hostent *hent;
	int sd;
 
	if ((sd = socket (AF_INET, SOCK_STREAM, 0)) < 0) {
		perror("(cliConn): socket() error");
		exit (-1);
	}
 
	if ((hent = gethostbyname (host)) == NULL)
		fprintf (stderr, "Host %s not found.\n", host);
	else
		bcopy (hent->h_addr, &name.sin_addr, hent->h_length);
 
	name.sin_family = AF_INET;
	name.sin_port = htons (port);
 
	/* connect port */
	if (connect (sd, (struct sockaddr *)&name, sizeof(name)) < 0) {
		perror("(cliConn): connect() error");
		exit (-1);
	}
 
	return (sd);
}

void handle_counter(unsigned address) { // , int fd) {

	char* serverIP = "127.0.0.1";
	int portno = 5050;

	int sd = cliConn(serverIP, portno);
	int count = 0;

	char buffer[256];
	int n;
	int flags = fcntl(sd, F_GETFL, 0); 

	fcntl(sd, F_SETFL, flags | O_NONBLOCK);
	while (1) {
	// --------------- UNCOMMENT BELOW TO TEST ON PC ---------------------//
		// count = readGPIO(address, fd)
		write (sd, &count, sizeof(count));
		count++; // comment this out when testing on PC
		sleep(5);

	}
}


int main(int argc, char *argv[])
{
	// --------------- COMMENT UNDER HERE TO TEST ON PC ---------------------//
	// // GPIO addresses
	// int gpio_addr;

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
	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0)
		error("ERROR on binding");
	puts("bind done");

	// Listen to port
	listen(sockfd,5);
	puts("Waiting for incoming connections...");

	// Configure default input channels (T,M,B)
	int inputselection = 4*pow(2,8) + 6*pow(2,4) + 5*pow(2,0);

	// Some GPIO addresses
	int truthaddr_1_2 = 1092878336;
	int truthaddr_3_4 = 1092878344;
	int deadtime_addr = 1092943872;
	int pulsewidth_addr = 1092943880;
	int counterreset_addr = 1093009408;
	int counterstop_addr = 1093009416;
	int selection_addr = 1093074944;
	int testcounter_addr = 1093140480;

	int forked = 0;

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


		// if (forked == 0) { // fork a child process to handle 
		// 	forked = 1;

		if (fork() == 0) {

			close(sockfd);
			puts("forked counter");
			sleep(1);
			handle_counter(testcounter_addr); // , fd);
			// while (1) {
			// 	int tempBuf = 101
			// 	write(newsockfd, tempBuf, sizeof(tempBuf));
			// 	sleep(1);
			// }
		}
		// else {
		// 	wait(sockfd)
		// }
		// }


		printf("\nReceived %d bytes\n", n);
        payload *p = (payload*) buffer;
        printf("Received contents: dacData=%d, dacNum=%d, deadtime=%f, pulsewidth=%f top=%d, middle=%d, bottom=%d\n",
        	p->dacData, p->dacNum, p->deadtime, p->pulsewidth, p->top, p->middle, p->bottom);

        // Check bool bits
        printf("truth_1_2: %d \n", p->truth_1_2);
        printf("truth_3_4: %d \n", p->truth_3_4);
		//return 0;
        // --------------- COMMENT UNDER HERE TO TEST ON PC ---------------------//
		// // GPIO Address based on dacNum
		// // Start with base GPIO address 4120x0000
  //       gpio_addr = 1092616192;
		// // Move to desired GPIO module
		// gpio_addr += ((p->dacNum-1)/2)*65536;
		// // Check if even(second) channel in a module
		// gpio_addr += ((p->dacNum-1)%2)*8;
		// // Send dacData (dac# and threshold) to the correct GPIO Address
		// writeGPIO(gpio_addr, p->dacData, fd);

		// // Select which input channels to use
		// // Format the input configuration into the binary vector
		// inputselection = p->top*pow(2,8)+p->middle*pow(2,4)+p->bottom*pow(2,0);
		// // Write the input configuration
		// writeGPIO(selection_addr, inputselection, fd);

		// // Write the output logic
		// writeGPIO(truthaddr_1_2, p->truth_1_2, fd);
		// writeGPIO(truthaddr_3_4, p->truth_3_4, fd);

		// // Write the deadtime
		// writeGPIO(deadtime_addr, (int)p->deadtime, fd);
		// // Write the output pulse width
		// writeGPIO(pulsewidth_addr, (int)p->pulsewidth, fd);
	}

	return 0;
}
