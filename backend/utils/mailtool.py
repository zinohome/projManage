#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import ssl
import traceback

# @Time    : 2025/04/11 09:46
# @Author  : ZhangJun
# @FileName: mailtool.py

from utils.log import log as log
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailTool(object):
    _smtp_server = 'smtp.163.com'
    _smtp_port = 25
    _sender_email = f'13583285152@163.com'
    _sender_password = 'BDbBazPnYasKrca7'

    def send_email(self,receiver_email, subject, body):
        '''
        # 创建邮件对象
        msg = MIMEMultipart()
        msg["From"] = self._sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        try:
            # 连接到SMTP服务器
            smtp = smtplib.SMTP(self._smtp_server, self._smtp_port, timeout=300)
            smtp.ehlo()
            smtp.starttls()  # 启用TLS加密
            smtp.ehlo()
            (code, resp) = smtp.login(self._sender_email, self._sender_password)
            smtp.send_message(msg)
            smtp.quit()
            log.debug("邮件发送成功！")
        except Exception as e:
            log.debug(f"邮件发送失败：{e}")
            traceback.print_exc()
        '''
        pass

    def send_outlook_email(self,receiver_email, subject, body):
        '''
        # 创建邮件对象
        msg = MIMEMultipart()
        msg["From"] = self._sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        try:
            # 连接到SMTP服务器
            smtp = smtplib.SMTP(self._smtp_server, self._smtp_port, timeout=300)
            smtp.ehlo()
            smtp.starttls()  # 启用TLS加密
            smtp.ehlo()
            (code, resp) = smtp.login(self._sender_email, self._sender_password)
            smtp.send_message(msg)
            smtp.quit()
            log.debug("邮件发送成功！")
        except Exception as e:
            log.debug(f"邮件发送失败：{e}")
            traceback.print_exc()
        '''
        pass


if __name__ == '__main__':
    mailtool = MailTool()
    mailtool.send_email("Jun.Zhang1@ibm.com","crtool测试邮件","这是一封测试邮件，发送自 Python。")