# pyCodis-ha

* NOTICE: this script is only for codis-2.0, feel free to play with it and welcome suggestions and criticisms.

## How to use it

* get the code from git

* set your mail server configurations in the function **getJobConfig()**:

```python
mail_config_dict = {"smtp_host": "127.0.0.1", "smtp_port": 25, "smtp_user": "xxx", "smtp_password": "xxx", 
                    "mail_from": "odisCheck@example.com", "smtp_ssl_enable": False, 
                    "mail_subject": u"Codis warning",
```

* set your sms server configurations in the function **getJobConfig()** (if needed):

```python
sms_config_dict = {"sms_message": self.cmd_args["product"] + u":codis cluster has some problems.",
                   "proxy_server": "127.0.0.1", "proxy_port": "8080"}
```

* run it, get more details about options by directly run **python check_codis_v1.py**
```shell
python check_codis_v1.py -h 127.0.0.1 -p 18087 \
                         -i /opt/codis/ -c /opt/codis/config.ini \
                         -n example -e yourmail@example.com [--sms-to 10000000000 --report]
```
## Finally, Can I repost it?

Feel free to play with codes, fork it or send pull request, but, nope, you can not repost it, just direct them to here. Also, the use of the script is at your on risk and your own responsibility, and has nothing to do with me. :)
