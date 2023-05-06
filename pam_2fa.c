#include <curl/curl.h>
#include <openssl/sha.h>
#include <security/pam_appl.h>
#include <security/pam_misc.h>
#include <security/pam_modules.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define CODE_SIZE 8
#define CODE_TRIES 3
#define SHA512_SIZE 128
#define MAX_LINE_LENGTH 200

int converse(pam_handle_t *pamh, int nargs, struct pam_message **message,
             struct pam_response **response) {
    int retval;
    struct pam_conv *conv;

    retval = pam_get_item(pamh, PAM_CONV, (const void **)&conv);
    if (retval == PAM_SUCCESS) {
        retval = conv->conv(nargs, (const struct pam_message **)message,
                            response, conv->appdata_ptr);
    }

    return retval;
}

static struct pam_conv conv = {misc_conv, NULL};

static void conv_error(pam_handle_t *pamh, const char *text) {
    struct pam_message msg = {.msg_style = PAM_ERROR_MSG, .msg = text};
    struct pam_message *msgs = &msg;
    struct pam_response *resp = NULL;
    const int retval = converse(pamh, 1, &msgs, &resp);
    free(resp);
}

PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc,
                              const char **argv) {
    return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc,
                                const char **argv) {
    printf("Acct mgmt\n");
    return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc,
                                   const char **argv) {
    printf("START\n");
    int retval;

    unsigned char *input;
    struct pam_message msg[1], *pmsg[1];
    struct pam_response *resp;

    const char *username;
    if ((retval = pam_get_user(pamh, &username, "login: ")) != PAM_SUCCESS) {
        return retval;
    }
    printf(username);

    FILE *conffile;
    printf("checking user size\n");
    size_t usrsize = sizeof(username);
    // printf(usrsize);

    char path_to_file[11 + usrsize + 1];
    sprintf(path_to_file, "/home/%s/.2fa", username);
    path_to_file[11 + usrsize + 1] = 0;
    // printf(path_to_file);

    conffile = fopen(path_to_file, "r");
    if (conffile == NULL) {
        conv_error(pamh, "No file found in ~/.2fa");
        return PAM_AUTH_ERR;
    }
    char config_user[MAX_LINE_LENGTH];
    fgets(config_user, MAX_LINE_LENGTH, conffile);
    fclose(conffile);
    printf(config_user);

    char code[CODE_SIZE + 1];
    unsigned int random_number;
    FILE *urandom = fopen("/dev/urandom", "r");
    fread(&random_number, sizeof(random_number), 1, urandom);
    fclose(urandom);
    snprintf(code, CODE_SIZE + 1, "%u", random_number);
    code[CODE_SIZE] = 0;
    printf(code);
    CURL *curl;
    CURLcode res;

    curl_global_init(CURL_GLOBAL_ALL);

    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, "https://auth-api.com");
        char *post_data[4] = {"username=", config_user, "&code=", code};
        size_t leng = 0;
        for (int i = 0; i < 4; i++) {
            leng = leng + strlen(post_data[i]);
        }
        void *data = malloc(leng + 1);
        size_t offset = 0;
        for (int i = 0; i < 4; i++) {
            strcpy(data + offset, post_data[i]);
            offset = offset + strlen(post_data[i]);
        }

        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        printf(data);
        res = curl_easy_perform(curl);
        free(data);
        if (res != CURLE_OK)
            printf("curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        long code;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &code);
        if (code != 200) {
            conv_error(pamh, "Unable to send code to your phone number");
        }
        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();
    time_t start_t, end_t;
    double diff_t;
    time(&start_t);
    for (int i = 0; i < CODE_TRIES; i++) {

        pmsg[0] = &msg[0];
        msg[0].msg_style = PAM_PROMPT_ECHO_ON;
        msg[0].msg = "1-time code: ";
        resp = NULL;
        if ((retval = converse(pamh, 1, pmsg, &resp)) != PAM_SUCCESS) {
            // if this function fails, make sure that
            // ChallengeResponseAuthentication in sshd_config is set to yes
            return retval;
        }

        if (resp) {
            if ((flags & PAM_DISALLOW_NULL_AUTHTOK) && resp[0].resp == NULL) {
                free(resp);
                return PAM_AUTH_ERR;
            }
            input = resp[0].resp;
            resp[0].resp = NULL;
            time(&end_t);
        } else {
            return PAM_CONV_ERR;
        }

        if (strcmp(input, code) == 0) {
            /* good to go! */
            diff_t = difftime(end_t, start_t);
            if (diff_t < 60) {
                free(input);
                return PAM_SUCCESS;
            } else {
                conv_error(pamh, "Code has expired");
                return PAM_AUTH_ERR;
            }
        } else {
            conffile = fopen(path_to_file, "r");
            char emergency_code[SHA512_SIZE + 1];
            fgets(config_user, MAX_LINE_LENGTH, conffile);
            FILE *temp;
            temp = fopen("/tmp/delete.tmp", "w");
            fputs(config_user, temp);
            int code_found = 0;
            unsigned char obuf[SHA512_DIGEST_LENGTH];
            char code_sha[SHA512_SIZE + 1];
            printf("about to sha it up\n");
            SHA512(input, strlen(input), obuf);
            // obuf[strlen(obuf) +1] = 0;
            for (int j = 0; j < SHA512_DIGEST_LENGTH; j++) {
                sprintf(&code_sha[j * 2], "%02x", obuf[j]);
                // printf("%s", code_sha);
                // printf("%02x", obuf[j]);
            }
            code_sha[SHA512_SIZE + 1] = 0;
            // 24458215

            printf("\n");
            printf("%s \n", code_sha);
            while (fgets(emergency_code, SHA512_SIZE + 1, conffile)) {
                // printf(emergency_code);
                printf("input : %s, emergency code: %s \n", code_sha,
                       emergency_code);
                if (strcmp(code_sha, emergency_code) == 0) {
                    code_found = 1;
                    continue;
                }
                fputs(emergency_code, temp);
            }
            printf("after while loop\n");
            fclose(temp);
            fclose(conffile);
            if (code_found == 1) {
                remove(path_to_file);
                rename("/tmp/delete.tmp", path_to_file);
                printf("after remove and rename about to free\n");
                free(input);
                return PAM_SUCCESS;
            } else {
                remove("/tmp/delete.tmp");
            }
            printf("after code found\n");

            if (i != CODE_TRIES - 1) {
                conv_error(pamh, "Wrong code");
                continue;
            }
            /* wrong code */
            // free( input ) ;
        }
    }
    return PAM_AUTH_ERR;
}