#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>



int main(int argc, char *argv[]) {
	// time_t seconds;
	// seconds = time(NULL); 
	int delay = 1;
	while(1)
	{
		puts("Hi");
		sleep(delay);
	}
	// system("pause"); 
}  