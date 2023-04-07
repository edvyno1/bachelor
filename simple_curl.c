#include <stdio.h>
#include <curl/curl.h>
#include <security/pam_modules.h>
#include <security/pam_misc.h>
#include <security/pam_appl.h>
#include <stdlib.h>
#include <string.h>
 
#define CODE_SIZE 6

int generate_mfa_code()
{

}
static struct pam_conv conv = {
    misc_conv,
    NULL
};
/* expected hook */
PAM_EXTERN int pam_sm_setcred( pam_handle_t *pamh, int flags, int argc, const char **argv ) {
	return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	printf("Acct mgmt\n");
	return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags,int argc, const char **argv)
{
    int retval;
    const char* pUsername;

    pam_get_user(pamh, &pUsername, "Username: ");

    printf("Welcome %s\n", pUsername);

	retval = pam_start("check", pUsername, &conv, &pamh);
    printf("start moment\n");

    // if (retval == PAM_SUCCESS)
    //     printf("pam auth\n");
    //     retval = pam_authenticate(pamh, 0);    /* is user really user? */

    if (retval == PAM_SUCCESS)
        printf("pam acct mgmt\n");
        retval = pam_acct_mgmt(pamh, 0);       /* permitted access? */

    /* This is where we have been authorized or not. */

    if (retval == PAM_SUCCESS) {
	printf("Authenticated\n");
    } else {
	printf("Not Authenticated\n");
    return retval;
    }

    if (pam_end(pamh,retval) != PAM_SUCCESS) {     /* close Linux-PAM */
	pamh = NULL;
	printf("check_user: failed to release authenticator\n");
	exit(1);
    }

    char code[CODE_SIZE+1] ;
  	unsigned int random_number ;
	FILE *urandom = fopen( "/dev/urandom", "r" ) ;
	fread( &random_number, sizeof(random_number), 1, urandom ) ;
	fclose( urandom ) ;
	snprintf( code, CODE_SIZE+1,"%u", random_number ) ;
	code[CODE_SIZE] = 0 ;
    printf(code);


    CURL *curl;
    CURLcode res;
    
    /* In windows, this will init the winsock stuff */
    curl_global_init(CURL_GLOBAL_ALL);
    
    /* get a curl handle */
    curl = curl_easy_init();
    if(curl) {
        /* First set the URL that is about to receive our POST. This URL can
        just as well be an https:// URL if that is what should receive the
        data. */
        curl_easy_setopt(curl, CURLOPT_URL, "http://127.0.0.1:5000");
        /* Now specify the POST data */
        char *post_data[4] = {"username=", pUsername, "&code=", code};
        // strcpy(data, *post_data);
        size_t leng = 0;
        for (int i = 0; i < 4; i++){
            leng = leng + strlen(post_data[i]);
        }
        void *data = malloc(leng+1);
        size_t offset = 0;
        for (int i = 0; i < 4; i++){
            strcpy(data+offset, post_data[i]);
            offset = offset + strlen(post_data[i]);
        }
        
        
        // vasprintf(&post_data, "username=%C&code=%C", &pUsername, &code);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        printf(data);
    
        /* Perform the request, res will get the return code */
        res = curl_easy_perform(curl);
        /* Check for errors */
        if(res != CURLE_OK)
        printf("curl_easy_perform() failed: %s\n",
                curl_easy_strerror(res));
    
        /* always cleanup */
        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();
    return PAM_SUCCESS;
}