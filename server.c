#include <unistd.h> 
#include <stdio.h> 
#include <sys/types.h> 
#include <sys/socket.h>
#include <stdlib.h> 
#include <netinet/in.h>
#include <string.h> 
// #define PORT 8888 


void error(char *msg)
{
	perror(msg);
	exit(1);
}

// Set the XYZ bits of the bitstream
void setXYZ(int dacNum, int* stream) {

	if (dacNum == 2) { stream[5] = 1; }
	else if (dacNum == 3) { stream[4] = 1; }
	else if (dacNum == 4)
	{
		stream[4] = 1;
		stream[5] = 1;
	}
	else if (dacNum == 5) { stream[3] = 1; }
	else if (dacNum == 6)
	{
		stream[3] = 1;
		stream[5] = 1;
	}
	else if (dacNum == 7)
	{
		stream[3] = 1;
		stream[4] = 1;
	}
	else if (dacNum == 8)
	{
		stream[3] = 1;
		stream[4] = 1;
		stream[5] = 1;
	}
}

// set the DAC Value bits of the bitstream
void setDACVal(int dacVal, int* stream) {

	stream[7] = 1;

	if (dacVal < 35) {
		stream[8] = 1;
		stream[14] = 1;
		stream[15] = 1;
		if (dacVal == 20) { stream[11] = 1; stream[17] = 1;}
		else if (dacVal == 25) { stream[12] = 1; stream[16] = 1;}
		else if (dacVal == 30) { stream[16] = 1; stream[17] = 1;}
	}
	else {
		stream[9] = 1;
		stream[10] = 1;
		stream[13] = 1;
		if (dacVal == 35) { stream[11] = 1; stream[12] = 1;}
		else if (dacVal == 40) { stream[11] = 1; stream[17] = 1;}
		else if (dacVal == 45) { stream[12] = 1; stream[16] = 1;}
		else if (dacVal == 50) { stream[16] = 1; stream[17] = 1;}
	}
}


// Create the full bitstream to send to the FPGA
void createBitstream(char buffer[256], int* bitstream) {

	printf("received: %s\n",buffer);
	// int bitstream[18] = { 0 };
	int dacNum = atoi(buffer) / 1000;
	int dacVal = atoi(buffer) % 1000;
	printf("dacnum %d\n", dacNum);
	printf("dacval %d\n", dacVal);


	setXYZ(dacNum, bitstream);
	setDACVal(dacVal, bitstream);
	// int i;
	// for (i=0; i < 18; i++) {
	// 	printf("%d  ", bitstream[i]);  
	// }
}



int main(int argc, char *argv[])
{
	// Instantiate Variables
	int sockfd, newsockfd, portno, clilen;
	char buffer[256];
	char buffer2[256];
	struct sockaddr_in serv_addr, cli_addr;
	int n;
	int m;

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
	int bitstream[18] = { 0 };
	while(1) 
	{
		clilen = sizeof(cli_addr);
		newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
		if (newsockfd < 0) 
			error("ERROR on accept");

		// bzero(buffer,256);
		n = read(newsockfd,buffer,255);
		if (n < 0) 
			error("ERROR reading from socket");


		printf("%s\n", buffer);
		char* dacInput;
		int deadtime;
	    dacInput = strtok(buffer, "\n");
	    deadtime = atoi(strtok(NULL, "\n"));
	   	// printf("dacIn: %s\n", dacInput);
	   	// typeof(deadtime);
	    printf("dtime: %d\n", deadtime);
		printf("Sending %s to Zedboard with %d deadtime\n", dacInput, deadtime);


		createBitstream(dacInput, bitstream);
		int i;
		for (i=0; i < 18; i++) {
			printf("%d  ", bitstream[i]);  
		}
		printf("\n");
	}


	return 0; 
}







