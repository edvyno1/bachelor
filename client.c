#include <stdio.h>
#include <curl/curl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void usage()
{
    printf("Possible options:\n login\n register\n");
}

void reg()
{
    char username[129];
    char *home = getenv("HOME");
    strcat(home, "/.2fa");
    printf(home);
    printf("\nEnter your desired username\nIt will be stored in %s for access when logging in\nUsername:", home);
    scanf("%128s", username);
    FILE *fp = NULL;
    fp = fopen(home, "rb");
    if(fp == NULL)
    {   
        fp = fopen(home, "wb");
        fprintf(fp, "%s", username);
        fclose(fp);
    } else {
        printf("\nFile %s already exists, edit it or delete it, exiting\n", home);
        exit(1);
    }
    char *password = getpass("Enter your password: "); // GETPASS ALLOWS FOR EMPTY INPUT, REDO LATER
    char *retype_pass = getpass("Retype your password: ");
    if (strcmp(password, retype_pass) != 0)
    {
        printf("\nPasswords do not match, exiting");
        exit(1);
    }
    printf(username);
    printf(password);
    
    

}

int main(int argc, char *argv[]){
    int opt;
    // printf(argv[1]);
    // int int_val = atoi(argv[1]);
    // printf(int_val);
    if (strcmp(argv[1], "login") == 0)
    {
        printf("logging in");
    }
    else if (strcmp(argv[1], "register") == 0)
    {
        printf("register\n");
        reg();
    }
    else {
        printf("Unrecognized option : %s\n", argv[1]);
        usage();
    }

    return 0;
    // while((opt = getopt(argc, argv, "login:register")) != -1) 
    // { 
    //     switch(opt) 
    //     { 
    //         case 'login':
    //             printf("logging in");
    //             break;
    //         case 'register':
    //             printf("registering");
    //             break;
    //         // case 'l': 
    //         // case 'r': 
    //         //     printf("option: %c\n", opt); 
    //         //     break; 
    //         // case 'f': 
    //         //     printf("filename: %s\n", optarg); 
    //         //     break; 
    //         // case ':': 
    //         //     printf("option needs a value\n"); 
    //         //     break; 
    //         case '?': 
    //             printf("unknown option: %c\n", optopt);
    //             break; 
    //     } 
    // } 
    
}