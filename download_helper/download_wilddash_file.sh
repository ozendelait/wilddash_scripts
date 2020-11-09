#!/bin/bash

# Based on https://github.com/ozendelait/rvc_devkit/blob/master/segmentation/download_wilddash2.sh
# which is based on https://github.com/mseg-dataset/mseg-api/blob/master/download_scripts/mseg_download_wilddash.sh
# Downloads the WildDash2 dataset.

# By using this script, you agree to the
# WildDash license agreement:
# https://wilddash.cc/license/wilddash
# -------------------------------------------------------------------


WILDDASH_FILE_NAME=$1
WILDDASH_SERVER_URL="https://wilddash.cc"
WILDDASH_DOWNL_URL="${WILDDASH_SERVER_URL}/download/${WILDDASH_FILE_NAME}"
WILDDASH_ACCOUNT_URL="${WILDDASH_SERVER_URL}/accounts/login"
WILDDASH_DST_FOLDER=$2
WILDDASH_COOKIE_FILE="${WILDDASH_DST_FOLDER}/wd_cookies_downl.txt"

echo "Downloading WildDash2 to $WILDDASH_DST_FOLDER"
mkdir -p $WILDDASH_DST_FOLDER
cd $WILDDASH_DST_FOLDER

if [ -f "$WILDDASH_COOKIE_FILE" ]; then
  echo "Restarting download with existing session. If this fails, manually delete $WILDDASH_COOKIE_FILE and retry."
else
	#start session to get CSRF token
	wget --no-verbose --no-check-certificate --keep-session-cookies --save-cookies=wd_cookies_auth.txt -O wd_resp_auth_token.html ${WILDDASH_ACCOUNT_URL}
	#safe CSRF in variable
	WILDDASH_CSRF=$(grep csrfmiddlewaretoken wd_resp_auth_token.html | sed "s/.*value='\(.*\)'.*/\1/")
	rm wd_resp_auth_token.html
	#escape @,?,+,& symbol
	WILDDASH_USERNAME_ESC=$(echo "$WILDDASH_USERNAME" | sed "s/@/%40/g")
	WILDDASH_PASSWORD_ESC=$(echo "$WILDDASH_PASSWORD" | sed "s/@/%40/g" | sed "s/\\?/%3F/g" | sed "s/=/%3D/g" | sed "s/\\+/%2B/g" | sed "s/&/%26/g" | sed "s/\\$/%24/g")
	#login to the WildDash webpage
	WILDDASH_USERDATA="username=$WILDDASH_USERNAME_ESC&password=$WILDDASH_PASSWORD_ESC&csrfmiddlewaretoken=$WILDDASH_CSRF&submit=Login"
	wget --no-verbose --no-check-certificate --keep-session-cookies --load-cookies=wd_cookies_auth.txt --save-cookies=$WILDDASH_COOKIE_FILE -O wd_login_page.html --post-data $WILDDASH_USERDATA ${WILDDASH_ACCOUNT_URL}
	#cleanup env
	WILDDASH_USERDATA=
	WILDDASH_CSRF=
	WILDDASH_USERNAME_ESC=
	WILDDASH_PASSWORD_ESC=
	rm wd_cookies_auth.txt
	rm wd_login_page.html
fi

wget --no-check-certificate --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 0 --continue --load-cookies $WILDDASH_COOKIE_FILE --content-disposition $WILDDASH_DOWNL_URL

echo "Downloaded "
