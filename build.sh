if [[ ! -d bin ]] ; then
    mkdir bin
fi
gcc -fPIC -c pam_2fa.c -o bin/pam_2fa.o
sudo ld -x --shared -o /lib/security/pam_2fa.so bin/pam_2fa.o -lcurl -lpam -lpam_misc -lssl

# pyinstaller client.py