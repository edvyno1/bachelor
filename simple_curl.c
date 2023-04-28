#include <stdio.h>
#include <curl/curl.h>
#include <security/pam_modules.h>
#include <security/pam_misc.h>
#include <security/pam_appl.h>
#include <stdlib.h>
#include <string.h>
 
#define CODE_SIZE 6
#define CODE_TRIES 3
// define url endpoints here for easier access

int converse( pam_handle_t *pamh, int nargs, struct pam_message **message, struct pam_response **response ) {
	int retval ;
	struct pam_conv *conv ;

	retval = pam_get_item( pamh, PAM_CONV, (const void **) &conv ) ; 
	if( retval==PAM_SUCCESS ) {
		retval = conv->conv( nargs, (const struct pam_message **) message, response, conv->appdata_ptr ) ;
	}

	return retval ;
}

static struct pam_conv conv = {
    misc_conv,
    NULL
};

PAM_EXTERN int pam_sm_setcred( pam_handle_t *pamh, int flags, int argc, const char **argv ) {
	return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	printf("Acct mgmt\n");
	return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags,int argc, const char **argv)
{
    printf( "START\n");
    int retval;

    char *input ;
    struct pam_message msg[1],*pmsg[1];
	struct pam_response *resp;
	

    const char *username ;
    	if( (retval = pam_get_user(pamh,&username,"login: "))!=PAM_SUCCESS ) {
		return retval ;
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
    
    curl_global_init(CURL_GLOBAL_ALL);
    
    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, "http://192.168.1.228:5000");
        char *post_data[4] = {"username=", username, "&code=", code};
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
        
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        printf(data);
        
        res = curl_easy_perform(curl);
        free(data);
        if(res != CURLE_OK)
        printf("curl_easy_perform() failed: %s\n",
                curl_easy_strerror(res));
        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();

    for( int i = 0; i < CODE_TRIES; i++)
    {
        pmsg[0] = &msg[0] ;
        msg[0].msg_style = PAM_PROMPT_ECHO_ON ;
        msg[0].msg = "1-time code: " ;
        resp = NULL ;
        if( (retval = converse(pamh, 1 , pmsg, &resp))!=PAM_SUCCESS ) {
            // if this function fails, make sure that ChallengeResponseAuthentication in sshd_config is set to yes
            return retval ;
        }

        if( resp ) {
            if( (flags & PAM_DISALLOW_NULL_AUTHTOK) && resp[0].resp == NULL ) {
                    free( resp );
                    return PAM_AUTH_ERR;
            }
            input = resp[ 0 ].resp;
            resp[ 0 ].resp = NULL; 		  				  
        } else {
            return PAM_CONV_ERR;
        }

        if( strcmp(input, code)==0 ) {
            /* good to go! */
            free( input ) ;
            return PAM_SUCCESS ;
        } else {
            if (i != CODE_TRIES-1){
                continue;
            }
            /* wrong code */
            free( input ) ;
            // REIMPLEMENT ERROR MSG
            // return PAM_AUTH_ERR ;
        }
        // }
    }
    return PAM_AUTH_ERR;
}