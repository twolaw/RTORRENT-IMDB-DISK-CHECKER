#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, datetime, smtplib, json, config as cfg

PY2 = sys.version_info[0] == 2  # True for Python 2

if PY2:
        from urllib2 import Request, urlopen
else:
        from urllib.request import Request, urlopen

lock = os.path.dirname(sys.argv[0]) + '/notif.txt'

if os.path.isfile(lock):
        file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getctime(lock))

        if file_age < datetime.timedelta(minutes=cfg.interval):
                sys.exit()

with open(lock, 'w+') as txt:
        txt.write('1')

def py2_encode(s, encoding='utf8'):
    if PY2:
        s = s.encode(encoding)
    return s

def py2_decode(s, encoding='utf8'):
    if PY2:
        s = s.decode(encoding)
    return s

def notif_email():
        server = False

        try:
                try:
                        server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
                        server.starttls()
                        server.login(cfg.account, cfg.password)
                except:
                        if server:
                                server.quit()

                        server = smtplib.SMTP_SSL(cfg.smtp_server, cfg.port, timeout=10)
                        server.login(cfg.account, cfg.password)
        except:
                if server:
                        server.quit()

                server = smtplib.SMTP(cfg.smtp_server, cfg.port, timeout=10)
                server.login(cfg.account, cfg.password)

        message = 'Subject: {}\n\n{}'.format(cfg.subject, cfg.message)
        server.sendmail(cfg.account, cfg.receiver, message)
        server.quit()

def notif_slack():
        slack_data = {
                'text': cfg.message,
                'username': cfg.slack_name,
                'icon_emoji': cfg.slack_icon
        }
        headers = {'content-type': 'application/json'}
        req = Request(cfg.slack_webhook_url, py2_decode(json.dumps(slack_data, ensure_ascii=False)).encode('utf8'), headers)
        response = urlopen(req).read()
        if response.decode('utf8') != 'ok':
                print('Failed to send slack notification, check slack_webhook_url.')

def notif_telegram():
        telegram_data = {
                'chat_id': cfg.telegram_chat_id,
                'text': cfg.message
        }
        headers = {'content-type': 'application/json'}
        req = Request("https://api.telegram.org/bot{token}/sendMessage".format(token=cfg.telegram_token), py2_decode(json.dumps(telegram_data, ensure_ascii=False)).encode('utf8'), headers)
        response = json.loads(urlopen(req).read())
        if response['ok'] != True:
                print('Failed to send telegram notification, check token and chat_id.')

if cfg.notification_email:
        notif_email()

if cfg.notification_slack:
        notif_slack()

if cfg.notification_telegram:
        notif_telegram()
