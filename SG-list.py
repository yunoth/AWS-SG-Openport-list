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

#define the connection
ec2 = boto3.client('ec2')

def listsg(event, context):
    filters = [
        {
            'Name': 'vpc-id', 
            'Values': ['<VPCID>','<VPCID>']
        }
    ]
    #List Security group list
    instances = ec2.describe_security_groups(Filters=filters)
    sglist = instances['SecurityGroups']
    sg = []
    sg_out = []
    for i in sglist:
        report = []
        report_out = []
        print(i['IpPermissions'],i['GroupName'],i['GroupId'])
        print("calling parse function")
        report = parse(i['IpPermissions'],i['GroupName'],i['GroupId'],'inbound')
        report_out = parse(i['IpPermissionsEgress'],i['GroupName'],i['GroupId'],'outbound')
        if not report:
            continue
        for i in report:
            sg.append(i)
        for i in report_out:
            sg_out.append(i)
    html = table_formation(['Name','ID','Port','Description','Type'],sg)
    html_out = table_formation(['Name','ID','Port','Description','Type'],sg_out)
    mailer(html+"<br />"+html_out)
    print "Mail sent"
    
def parse(rules,name,sgid,type_):
    colomn = list()
    print rules
    for i in rules:
      if i.has_key('ToPort'):
          port = i['ToPort']
      else:
          continue
      for rule in i['IpRanges']:
          if rule['CidrIp'] == '0.0.0.0/0':
            col = (name,sgid,port,rule.get('Description','NA'),type_)
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
        msg['From'] = 'FROM_ADDRESS'
        msg['To'] = 'TO_ADDRESS'
        msg['Subject'] = 'AWS Public Open rules'
        message = "<h> Hi Team,<br><br> <h> Please find AWS Server SG rules opened to public (0.0.0.0/0) . <br> <br>"+html+"<h> <br> Best Regards, <br> Yuno"
        msg.attach(MIMEText(message,'html'))
        mailserver = smtplib.SMTP("email-smtp.us-east-1.amazonaws.com", 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login("SMTP_USERNAME,SMTP_PASSWORD")
        mailserver.sendmail('FROM_ADDRESS','TO_ADDRESS',msg.as_string())
        mailserver.quit()
