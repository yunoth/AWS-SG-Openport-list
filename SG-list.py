import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define the connection
ec2 = boto3.client('ec2')

def SG_handler(event, context):
    filters = [
        {
            'Name': 'vpc-id', 
            'Values': ['VPC ID']
        }
    ]
    #List Security group list
    instances = ec2.describe_security_groups(Filters=filters)
    sglist = instances['SecurityGroups']
    #print sglist
    sg = list()
    for i in sglist:
        report = list()
        report = parse(i['IpPermissions'],i['GroupName'],i['GroupId'])
        if not report:
          continue
        else:
          sg.append(report)
    return sg
    
def parse(rules,name,sgid):
    colomn = list()
    for i in rules:
      port = i['ToPort']
      for rule in i['IpRanges']:
          if rule['CidrIp'] == '0.0.0.0/0':
            col = (name,sgid,port)
            colomn.append(col)
    return colomn
