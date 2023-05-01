sudo cat generated/auth.api.com.pem >> /etc/ssl/certs/ca-certificates.crt

# edit /etc/hosts
# 192.168.1.228 auth-api.com
# ^ is the url where the server is hosted
# ip a on the host and check inet of main interface