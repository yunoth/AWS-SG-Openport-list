import boto3
import logging
import datetime
import email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def listsg(event,context):
    filters = [
        {
            'Name': 'vpc-id', 
            'Values': ['VPCID']
        }
    ]
    sg = []
    sg_out = []
    regions = { 'us-east-1':'N.Virginia','us-west-2':'Oregon','ap-southeast-1':'Singapore'}
    for region in regions.keys():
        ec2 = boto3.client('ec2',region_name=region)
        #List Security group list
        instances = ec2.describe_security_groups(Filters=filters)
        sglist = instances['SecurityGroups']
        for i in sglist:
            report = []
            report_out = []
            report = parse(i['IpPermissions'],i['GroupName'],i['GroupId'],'inbound',regions[region])
            report_out = parse(i['IpPermissionsEgress'],i['GroupName'],i['GroupId'],'outbound',regions[region])
            if not report:
                continue
            for i in report:
                sg.append(i)
            for i in report_out:
                sg_out.append(i)
    html = table_formation(['Name','ID','Port','Description','Type','Region'],sg)
    html_out = table_formation(['Name','ID','Port','Description','Type','Region'],sg_out)
    mailer(html+"<br />"+html_out)   

    
def parse(rules,name,sgid,type_,region):
    colomn = list()
    for i in rules:
      if i['IpRanges'] == []:
          for rule in i['UserIdGroupPairs']:
                port = rule['GroupId']
                col = (name,sgid,port,rule.get('Description','NA'),type_,region)
                colomn.append(col)
      else:
          if i['IpProtocol'] == '-1':
                port = 'All traffic'
          else:
                if i.has_key('ToPort'):
                        port = i['ToPort']
                else:
                    continue
      for rule in i['IpRanges']:
          if rule['CidrIp'] == '0.0.0.0/0':
            col = (name,sgid,port,rule.get('Description','NA'),type_,region)
            colomn.append(col)
    return colomn
    
def table_formation(header,data,opt="center"):
        html_str=''
        bg='white'
        if data:
                if header:
                        html_str+='<table border=1 cellspacing=0><tr bgcolor="009900">'
                        for value in header:
                                html_str+='<th align="'+opt+'">'+str(value)+'</th>'
                        html_str+='</tr>\n'

                for rows in data:
                        html_str+='\n<tr>'
                        for value in rows:
                           if value == '22' or value =='3360' :
                             bg="FF0000"
                           else:
                             bg='white'
                           html_str+='<td align="'+opt+'" bgcolor="'+bg+'">'+str(value)+'</td>'
                        html_str+='</tr>'
                html_str+='</table>'
        else:
                html_str=''
        return html_str

def mailer(html):
        today = datetime.date.today()
        msg = MIMEMultipart()
        msg['From'] = 'FROM ADDRESS'
        msg['To'] = 'TO ADDRESS'
        msg['Subject'] = 'AWS Public Open rules'
        message = "<h> Hi,<br><br> <h> Please find AWS Server SG rules opened to public (0.0.0.0/0) . <br> <br>"+html+"<h> <br> Best Regards, <br> YOUR NAME"
        msg.attach(MIMEText(message,'html'))
        mailserver = smtplib.SMTP("SERVERNAME", PORT)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login("<SMTP USERNAME>","<SMTP PASSWORD>")
        mailserver.sendmail('<FROM ADDRESS>','<TO ADDRESS>',msg.as_string())
        mailserver.quit()
