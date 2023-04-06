#include <stdio.h>
#include <string.h>

char* commandfix(const char* character1, const char* character2)
{
	char* apotelesma = malloc(strlen(character1) + strlen(character2) + 1); 
	strcpy(apotelesma, character1);
	strcat(apotelesma, character2);
	return apotelesma;
}

int main(int argc, char* argv[]) {


	if (argc == 2) {
		char* command = commandfix("python starlet.py ", argv[1]);
		system(command);
	}
	else if (argc > 2) {
		printf("error parapanw apo metablites apo oti prepei\n");
	}
	else {
		printf("leipei mia metabliti \n");
	}
		
	
}
	