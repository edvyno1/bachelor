import subprocess
import os

certs=["auth-api.com"]
IP="192.168.1.228"

# generate nginx and ssl conf files as well
os.makedirs("generated")

for cert in certs:
    with open(f"generated/{cert}.cnf", "w") as f:
        f.writelines(
            [
                "[ req ]\n",
                "prompt                 = no\n",
                "days                   = 365\n",
                "distinguished_name     = req_distinguished_name\n\n",

                "[ req_distinguished_name ]\n"
                "countryName            = AB\n"
                "stateOrProvinceName    = CD\n"
                "localityName           = EFG_HIJ\n"
                "organizationName       = MyOrg\n"
                "organizationalUnitName = MyOrgUnit\n"
                f"commonName             = {cert}\n"
                f"subjectAltName        = 2{cert}\n"
                "emailAddress           = emailaddress@myemail.com"
            ]
        )

    with open(f"generated/{cert}.nginx", "w") as f:
        f.writelines(
            [
                "server {\n\n",
                
                "   listen 443 ssl;\n",
                f"   ssl_certificate /server/generated/{cert}.pem;\n",
                f"   ssl_certificate_key /server/generated/{cert}.key;\n",
                f"   server_name {cert};\n\n",

                "  location / {\n",
                f"           proxy_pass http://{IP}:5000;\n",
                "           proxy_set_header X-Real_IP $remote_addr;\n",
                "       }\n",
                "}\n\n",

                "server {\n",
                "   listen 80;\n",
                f"   server_name {cert};\n",
                "return 302 https://$server_name$request_uri;\n",
                "}"
            ]
        )

    subprocess.check_call(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-keyout", f"generated/{cert}.key", "-out", f"generated/{cert}.pem", "-nodes", "-config", f"generated/{cert}.cnf"]
    )


#openssl req -x509 -newkey rsa:2048 -keyout /server/keylocalhost.pem -out /server/localhost.pem -nodes -config server.cnf