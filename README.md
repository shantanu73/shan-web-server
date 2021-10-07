## Flask app registration on Azure Web Portal
Refer to this [DOCUMENT](/Docs/Azure-app-registration.pdf)



## SHAN WEB Server Configuration
1)  Login as **root user** and perform all operations as **root user only**, run the command below and enter your password when prompted:-
    ```bash
    $ sudo su
    ```


2)  Install git and configure git to clone and use the source code repository in github via ssh keys:-
    ```bash
    $ yum update -y
    $ yum install -y git
    ```


3)  Connect to github account by creating a personal access token using following steps:-

    a) Login to your github account.

    b) Verify your email address (if it hasn't been verified yet) using following steps :

       I) In the upper-right corner of any page, click your profile photo, then click **Settings**.

       ![GitHub1](/Docs/images/git-1.png)

       II) In the left sidebar, click **Emails**.

       ![GitHub2](/Docs/images/git-2.png)

       III) Under your email address, click **Resend verification email**.

       ![GitHub3](/Docs/images/git-3.png)

       IV) GitHub will send you an email with a link in it. After you click that link, you'll be taken to your GitHub dashboard and see a confirmation banner.

       ![GitHub4](/Docs/images/git-4.png)

    c) In the upper-right corner of any page, click your profile photo, then click **Settings**.

    ![GitHub5](/Docs/images/git-5.png)

    d) In the left sidebar, click **Developer settings**.

    ![GitHub6](/Docs/images/git-6.png)

    e) In the left sidebar, click **Personal access tokens**.

    ![GitHub7](/Docs/images/git-7.png)

    f) Click **Generate new token**.

    ![GitHub8](/Docs/images/git-8.png)

    g) Give your token a descriptive name.

    ![GitHub9](/Docs/images/git-9.png)

    h) Select the scopes, or permissions, you'd like to grant this token. To use your token to access repositories from the command line, select **repo**.

    ![GitHub10](/Docs/images/git-10.png)

    i) Click **Generate token**.

    ![GitHub11](/Docs/images/git-11.png)

    j) Click paste icon to copy the token to your clipboard. For security reasons, after you navigate off the page, you will not be able to see the token again.

    ![GitHub12](/Docs/images/git-12.png)


4)  Clone the repo in **/opt** directory and go to the repo directory:-
    ```bash
    $ cd /opt
    $ git clone https://github.com/shantanu73/shan-web-server.git
    $ cd shan-web-server
    ```


5)  Open **app_config.py** file using command :-
    ```bash
    $ vi app_config.py
    ```
    And, edit the following variables in **app_config.py** as mentioned below :-

    ```python
    SHAN_SERVER_SECRET_KEY = "<your SHAN server secret key, should have same value as configured in SHAN API server>"
    CLIENT_ID = "<your client id>"
    CLIENT_SECRET = "<your client secret>"
    SERVER_2_URL = "<your server 2 url which is SHAN API server FQDN>/"
    TENANT_ID = "<your tenant id>"
    ELEVATION_TIMES_LIST = [
        "<specify your 1st time value in hours>",
        "<specify your 2nd time value in hours>",
        "<specify your 3rd time value in hours>",
    ]
    ADMIN_GROUPS_LIST = [
        "<specify your 1st admin group name>",
        "<specify your 2nd admin group name>",
        "<specify your 3rd admin group name>",
    ]
    ```


6)  Install **Python 3.6**, upgrade pip and install python requirements, using the following commands :-
    ```bash
    $ chmod +x -R /opt/shan-web-server
    $ /opt/shan-web-server/Scripts/install_python.sh
    $ /opt/shan-web-server/Scripts/pip_requirements.sh
    ```


7)  Open port **443** to run application in https, using the following commands:-
    ```bash
    $ /opt/shan-web-server/Scripts/open_https.sh
    ```


8)  Install and configure **authbind** for **443** port, using the following commands:-
    ```bash
    $ /opt/shan-web-server/Scripts/auth_bind.sh
    ```


9)  Create a new user and become owner of **authbind port 443** & **shan-web-server** directory, using the following commands:-
    ```bash
    $ /opt/shan-web-server/Scripts/new_user.sh
    ```


10) Now, create a new service file for our WEB server :-
    ```bash
    $ vi /lib/systemd/system/shan.service
    ```

    Add the following code to the file and edit the parameters as required and save the file:-

    ```python
    [Unit]
    Description=SHAN_WEB_SERVER
    Wants=network-online.target
    After=network-online.target syslog.target

    [Service]
    Type=simple
    User=shanuser
    WorkingDirectory=/opt/shan-web-server
    ExecStart=/usr/bin/authbind --deep /opt/rh/rh-python36/root/bin/python3.6 /opt/shan-web-server/app.py
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    ```



## Certificate creation and renewal using Cert-bot
1)  Become root user (if not already a root user):-
    ```bash
    $ sudo su
    ```


2)  To add the CentOS 7 EPEL repo, install certbot, install gatespeed repo & cloudFlare plugin(certbot) run the command:-
    ```bash
    $ /opt/shan-web-server/Scripts/install_certbot.sh
    ```


3)  Now, run the certbot command without any parameters to create the initial configuration file :-
    ```bash
    $ certbot
    ```


4)  Now, create a cf-api-token.ini in directory /etc/letsencrypt using command :-
    ```bash
    $ vi /etc/letsencrypt/cf-api-token.ini
    ```

    And paste the following content in it and save the file (e.g. your token : xxXX0XXX1XXxXXxXXX2XxXxx_3xxX4xxxx_5Xx):
    ```bash
    dns_cloudflare_api_token = <your api token>
    ```

    Change the permission of the api token file using command :-
    ```bash
    $ chmod 600 /etc/letsencrypt/cf-api-token.ini
    ```


5) Open the **create_certificate.sh** script using the following command:-
    ```bash
    $ vi /opt/shan-web-server/Scripts/create_certificate.sh
    ```

    Now, edit the variables **CERT_DOMAIN** & **CERT_EMAIL** in it, and save the file:
    ```bash
    export CERT_DOMAIN="<your domain>"
    export CERT_EMAIL="<your email address>"
    ```


6)  Run the following command to obtain the wildcard certificate for your domain and configure renewal:-
    ```bash
    $ /opt/shan-web-server/Scripts/create_certificate.sh
    ```


7)  Now your WEB server is up and running.
    Check your domain url in the browser.
    Refer to **/opt/shan-web-server/logs** folder to access log files.
