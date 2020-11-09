## wilddash.cc dataset download helper ##

### General Note: ###
Download all files regularly using your browser via the wilddash.cc website. Only use these scripts if you run into troubles. The scripts use credentials/passwords placed in environment variables in plain-text format. This is not recommend and generally unsafe. Use all scripts with caution and be sure to cleanup your environment variables and bash history afterwards.

### Registration ###

Before downloading, you have to register here: https://wilddash.cc/accounts/login
Use a valid email address from your academic institution. Use your company email or private email if you have no accademic one. Remember: wilddash.cc benchmark and datasets are provided for non-commercial use only to improve machine learning for traffic-safety-relevant tasks (or low-level tasks which are used in this context).
Please refrain from registering using free webmail accounts (e.g. gmail, yahoo, 163.com, yandex.ru etc.) as we cannot attribute those to individuals.
Approval of your account may take a few days. Please read the FAQs for more information: https://wilddash.cc/submit

### License ###

By downloading a dataset wilddash.cc, you agree to the license terms associated with it. 
See https://wilddash.cc/download for more information.

### Usage ###

To use the automatic download script, define these environment variables using 

```
# Copy WildDash credentials here (note: username is a mail adress, use quotes to prevent problems with special characters)
# this prevents lines that start with a blank from showing up in your bash history:
HISTCONTROL=ignoreboth
 export WILDDASH_USERNAME="your_wd_username"
 export WILDDASH_PASSWORD="your_wd_passwd"
```

Now you can execute the download script ``` download_wilddash_file.sh ``` 

```
# Download specific file:
bash download_wilddash_file.sh name_of_wilddash_file.ext /path/to/target/dir/ 

# Download WildDash2:
cd /path/to/target/dir/
bash /path/to/wilddash_scripts/download_helper/download_wilddash2.sh

# Download RailSem19:
cd /path/to/target/dir/
bash /path/to/wilddash_scripts/download_helper/download_railsem19.sh


```

### Cleanup ###

When you are finished downloading your files, please remember to undefine your credentials and remove the cookie file:

```
# Copy WildDash credentials here
export WILDDASH_USERNAME=
export WILDDASH_PASSWORD=
rm /path/to/target/dir/wd_cookies_downl.txt
```

You should also check if your command line history is cleared of the lines which export the credentials/password.