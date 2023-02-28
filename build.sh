if [[ ! -d bin ]] ; then
    mkdir bin
fi
gcc -fPIC -c simple_curl.c -o bin/simple_curl.o
gcc -shared -o bin/simple_curl.so bin/simple_curl.o