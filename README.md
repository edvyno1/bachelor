`python3 -m venv .venv`

`source .venv/bin/activate`

`pip3 install -r requirements.txt`

# Flow for installation
Compile client.py using
`pyinstaller -F client.py`
Run the client binary and enter your registration details
Once your phone numbered is entered, you will receive a code to confirm your registration to your phone number
Once you confirm the registration a file located in your home directory will be created under `$HOME/.2fa`

Compile the PAM module using the build script `build.sh` or put the pre-compiled binary into `/lib/security`

Now edit the `/etc/pam.d/common-auth` configuration and add a line after the last `auth required` module that you can see and write
`auth   required    simple_curl.so`

Editing the `common-auth configuration` will make it ask for a 2fa code every time any authentication is required, if you would like to do this only in specific scenarios, you should add this `auth required` line in the appropriate configuration

Most common scenario would be to add it in `/etc/pam.d/gdm-password`
If you are using Ubuntu, this would make it that 2fa is only required on login via the Gnome Display Manager

Once that is done, try to login and observe the required 2fa code for authentication

# Hosting the api locally
Log into a root user as the GSM module requires elevated permissions to access the physical GSM device

Activate the virtual environment as root

Launch the api `python3 app.py`