import json
import logging
import os
import boto3

import ssl_expiry

sns = boto3.client("sns")
def lambda_handler(event, *args, **kwargs) -> list:
    # use the env var HOSTLIST to define a default list of hostnames
    HOST_LIST = os.environ['HOSTLIST'].split(',')
    EXPIRY_BUFFER = int(os.environ['EXPIRY_BUFFER'])

    # cleanup the host list
    HOST_LIST = filter(None, (x.strip() for x in HOST_LIST))

    response = [
        ssl_expiry.test_host(host + ".xyz.com", buffer_days=EXPIRY_BUFFER)
        for host in HOST_LIST
    ]
    resp = []
    for msg in response:
        tmp = {}
        if 'error' in msg or 'expire' in msg:
            tmp = {
                'message': 'Error',
                "result": msg
            }
            resp.append(tmp)

    if len(resp) > 0:
        res = sns.publish(
            TopicArn='',
            Message=json.dumps(resp),
            Subject='SSL Expiry Alert'
        )
    else:
        print("SSL not expiring for any (sub-)domain in next 30 days.")

    return resp
