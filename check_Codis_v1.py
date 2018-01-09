#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Auth Liangy
'''
import datetime
from email.Header import Header
from email.mime.text import MIMEText
import getopt
import json
import smtplib
import subprocess
import sys
import time
import urllib
import urllib2

from redis import StrictRedis


class check_Codis(object):

    def usage(self):
        print "Usage:python check_codis_demo.py [OPTIONS]"
        print u"-h,--host          required,dashboard ip, eg:127.0.0.1"
        print u"-p,--port          required,dashboard port, eg:18087"
        print u"-i,--path-install  required,codis installation path, eg:/opt/codis"
        print u"-c,--path-config   required,path of config.ini"
        print u"-n,--product_name  required,product_name of codis"
        print u"-e, --mail-to      required,mail_address seprated by comma"
        print u"--sms-to           optional,if set --report,then phone numbers must be needed"
        print u"--report           optional,if send sms or not"
        sys.exit(1)

    def errorAdd(self, p_name, msg):
        if p_name not in self.errorMsg:
            self.errorMsg[p_name] = []
        self.errorMsg[p_name].append(msg)

    def groupAdd(self, group_id, msg):
        if group_id not in self.groupMsg:
            self.groupMsg[group_id] = []
        self.groupMsg[group_id].append(msg)

    def getJobConfig(self):
        mail_config_dict = {"smtp_host": "127.0.0.1", "smtp_port": 25, "smtp_user": "xxx", "smtp_password": "xxx", "mail_from": "odisCheck@example.com", "smtp_ssl_enable": False, "mail_subject": u"Codis warning",
                            "mail_to": self.cmd_args["mail"]}  # 邮件发送目标，英文逗号分割
        sms_config_dict = {"sms_message": self.cmd_args["product"] + u":codis集群实例数发生变化，详细请检查邮件",
                           "proxy_server": "127.0.0.1", "proxy_port": "8080",  # 允许使用http代理发送短信
                           "sms_sendto": self.cmd_args["sms"]}  # 短信件发送目标，英文逗号分割
        self.contact_List = {"mail": mail_config_dict, "sms": sms_config_dict}
        return self.contact_List

    def jobReport(self, report_msg, report_config):
        smtp_host = report_config["mail"]["smtp_host"]
        smtp_port = report_config["mail"]["smtp_port"]
        smtp_user = report_config["mail"]["smtp_user"]
        smtp_pwd = report_config["mail"]["smtp_password"]
        try:
            # 发送邮件部分
            from_addr = report_config["mail"]["mail_from"]
            msg = MIMEText(report_msg, "plain", "utf-8")
            msg["Subject"] = Header(report_config["mail"][
                                    "mail_subject"] + "_" + self.op_date, "utf-8")
            msg["From"] = from_addr
            msg["To"] = report_config["mail"]["mail_to"]
            msg["Accept-Language"] = "zh-CN"
            msg["Accept-Charset"] = "ISO-8859-1,utf-8"
            if report_config["mail"]["smtp_ssl_enable"]:
                s = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                s = smtplib.SMTP(smtp_host, smtp_port)
            if smtp_user != "" and smtp_pwd != "":
                s.login(smtp_user, smtp_pwd)
                s.sendmail(from_addr, report_config["mail"][
                           "mail_to"].split(","), msg.as_string())
                s.close()
            if self.cmd_args["report"] is True:
                # 发送短信部分
                # proxy_server = report_config["sms"]["proxy_server"]
                # proxy_port = report_config["sms"]["proxy_port"]
                for st in report_config["sms"]["sms_sendto"].split(","):
                    sms_url = "http://message/sendSms.do"
                    params_dict = {
                        "userIp": "127.0.0.1"}
                    # if proxy_server != "" and proxy_port != "":
                    #    proxy = urllib2.ProxyHandler({"http": "http://" + proxy_server + ":" + proxy_port})
                    #    opener = urllib2.build_opener(proxy)
                    #    urllib2.install_opener(opener)
                    response = urllib2.urlopen(
                        sms_url + "?" + urllib.urlencode(params_dict)).read()
                    print "Send phone message to " + st + ",status is: " + response.strip()
        except Exception, e:
            print "Report job information to techs failed.Exception:%s" % str(e)

    def argsParse(self, sys_args):
        try:
            shortargs = "h:p:i:c:n:e:"
            longargs = ["host=", "port=", "path-install=",
                        "path-config=", "report", "product_name=", "mail-to=", "sms-to"]
            opts, args = getopt.getopt(sys_args[1:], shortargs, longargs)
            if len(opts) < 6:
                self.usage()
            for opt, val in opts:
                if opt in ("-h,--host") and val != "":
                    self.cmd_args["host"] = val
                if opt in ("-p,--port") and val != "":
                    self.cmd_args["port"] = val
                if opt in ("-i,--path-install") and val != "":
                    self.cmd_args["codis"] = val
                if opt in ("-c,--path-config") and val != "":
                    self.cmd_args["config"] = val
                if opt in ("-e,--mail-to") and val != "":
                    self.cmd_args["mail"] = val
                if opt == "--report":
                    self.cmd_args["report"] = True
                if opt == "--sms-to" and val != "":
                    self.cmd_args["sms"] = val
                if opt in ("-n,--product_name") and val != "":
                    self.cmd_args["product"] = val
            return self.cmd_args
        except Exception, e:
            print e
            self.usage()

    # 获取codis集群信息
    def getCodisGroups(self, host, port):
        codisGroupUrl = "http://" + host + ":" + port + "/api/server_groups"
        try:
            request = urllib2.Request(codisGroupUrl)
            response = urllib2.urlopen(url=request, timeout=5)
            groupList = json.loads(response.read())
            num_of_group = len(groupList)
            n = 0
            while n < num_of_group:
                num_of_server = len(groupList[n]["servers"])
                m = 0
                while m < num_of_server:
                    groupId = groupList[n]["servers"][m]["group_id"]
                    serverType = groupList[n]["servers"][m]["type"]
                    serverHost = groupList[n]["servers"][m]["addr"].split(":")[
                        0]
                    serverPort = groupList[n]["servers"][m]["addr"].split(":")[
                        1]
                    self.groupAdd(str(groupId) + ":" + serverType,
                                  serverHost + ":" + serverPort)
                    m = m + 1
                n = n + 1
        except Exception, e:
            self.errorAdd(host + ":" + port, "Your codis cluster %s must have some problems: %s" %
                          (self.cmd_args["product"], str(e)))
            self.jobReport(
                "\n".join(self.errorMsg[host + ":" + port]), self.getJobConfig())
            sys.exit()

    def check_codis(self, serverHost, serverPort):
        try:
            StrictRedis(serverHost, serverPort).ping()
            self.codisFlag = True
        except Exception, e:
            self.errorAdd(serverHost + ":" + serverPort, "Your Codis instance %s has some problems: %s" %
                          (serverHost + ":" + serverPort, str(e)))
            self.codisFlag = False
        finally:
            return self.codisFlag

    def save_codis(self, groupId, serverSlaveAddr):
        codisPath = self.cmd_args["codis"]
        configPath = self.cmd_args["config"]
        nullFile = open("/dev/null", "w")
        proCmd = codisPath + "/bin/codis-config -c " + configPath + \
            " server promote " + groupId + " " + serverSlaveAddr
        proRun = subprocess.Popen(
            proCmd, shell=True, stdout=nullFile, stderr=subprocess.PIPE, bufsize=100)
        proRun.wait()
        if proRun.returncode != 0:
            raise RuntimeError(u"promote codis instances.Exception:%s" % str(
                proRun.stderr.readlines()))

    def taskProcess(self):
        try:
            self.getCodisGroups(self.cmd_args["host"], self.cmd_args["port"])
            for i in self.groupMsg.iterkeys():
                group_id = i.split(":")[0]
                serverType = i.split(":")[1]
                if serverType == "master":
                    if not self.check_codis(self.groupMsg[i][0].split(":")[0], self.groupMsg[i][0].split(":")[1]):
                        self.jobReport("\n".join(self.errorMsg[self.groupMsg[i][0].split(
                            ":")[0] + ":" + self.groupMsg[i][0].split(":")[1]]), self.getJobConfig())
                        for j in self.groupMsg.iterkeys():
                            if j.split(":")[0] == group_id and j.split(":")[1] == "slave":
                                self.save_codis(group_id, self.groupMsg[j][0])
                                time.sleep(10)
        except Exception, e:
            print e

    def __init__(self, sys_args):
        '''
        Constructor
        '''
        self.cmd_args = {"host": None, "port": None, "codis": None,
                         "config": None, "report": False, "product": None,
                         "mail": None, "sms": None}
        self.argsParse(sys_args)
        self.errorMsg = {}
        self.groupMsg = {}
        self.op_date = (datetime.datetime.now() -
                        datetime.timedelta(days=1)).strftime("%Y%m%d")
        self.contact_List = {}


if __name__ == "__main__":
    while True:
        codis = check_Codis(sys.argv)
        codis.taskProcess()
        time.sleep(30)
