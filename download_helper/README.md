# wilddash.cc dataset download helper #

## Dataset Downloads ##

In general, download regularly using your browser via the website. Only use these scripts if you run into troubles. 

Before downloading, you have to register here: https://wilddash.cc/accounts/login
Use a valid email address from your academic institution. If you have none, than use one from your company. Please refrain from registering using free webmail accounts (e.g. gmail, yahoo, 163.com, yandex.ru etc.) as we cannot attribute those to individuals.
Approval of your account may take a few days. Please read the FAQs for more information: https://wilddash.cc/submit

By downloading a dataset wilddash.cc, you agree to the license terms associated with it. 
See https://wilddash.cc/download for more information.

To use the automatic download script, define these environment variables using 

```
# Copy WildDash credentials here
export WILDDASH_USERNAME="your_wd_username"
export WILDDASH_PASSWORD="your_wd_passwd"
```

Now you can execute the download script ``` download_wilddash2.sh ``` 

```
# Download files
bash download_wilddash2
```