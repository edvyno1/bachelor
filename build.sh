if [[ ! -d bin ]] ; then
    mkdir bin
fi
gcc -fPIC -c simple_curl.c -o bin/simple_curl.o
sudo ld -x --shared -o /lib/security/simple_curl.so bin/simple_curl.o -lcurl -lpam -lpam_misc

pyinstaller client.py