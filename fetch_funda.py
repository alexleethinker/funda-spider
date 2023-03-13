# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup as bs
import re
import string

import smtplib
import email.utils
import time,sched,os

#########################################       crawler         ####################################

def iHouse_crawler():
    number_of_house = 0
    url = 'https://www.woonnet-haaglanden.nl/woningaanbod/totale-aanbod/zoekresultaat/?search=model:2,4|'
    #url of loting and direct te huur
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = bs(plain_text,"html.parser")
    email_content = ''
    link_list = []
    area_list = []
    #link_all_house = 'https://www.woonnet-haaglanden.nl/woningaanbod/totale-aanbod/zoekresultaat/?rentFrom=&rentTill=&buyFrom=&buyTill=&submit=resultaat+bijwerken&__id__=Portal_Form&__hash__=7010bcb2f93754394b9631f05d158aac'

    for link in soup.select('.dwelling-item-text h3 a'):
        href = 'https://www.woonnet-haaglanden.nl/' + link.get('href')
        link_list.append(href)
        #house_name = link.text

    for link in soup.select('.dwellingdetails li'):
        area_list.append(filter(lambda ch: ch in '0123456789,',link.text)[0:5].replace(',','.'))

    while '' in area_list:
        area_list.remove('')

    for i in area_list:
        if float(i) > 200:
            index = area_list.index(i)
            i = i[0:2]
            area_list[index] = i
            
      
    url_list = '\n'.join(link_list)
    #print url_list

    # read stored links and close the file
    stored_link = open('url_list.txt')
    try:
        stored_url = stored_link.read()
    finally:
        stored_link.close()

    #print stored_url



    # judge if there are new houses on the web site
    for link in link_list:
       
        if link not in stored_url:
            number_of_house = number_of_house + 1

            index = link_list.index(link)
            #print index
            s = requests.session()        
            login_data = dict(username='chulinxue', password='woshixchl')
            # post 数据实现登录
            s.post(link, login_data)
            #print s.post(link, login_data)
            headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding':'gzip, deflate, sdch',
                       'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-CA;q=0.2,zh-TW;q=0.2',
                       'Connection':'keep-alive',
                       'Cookie':'ASD2NWLB003=rd3o00000000000000000000ffff0a600413o80; nc_staticfilecache=fe_typo_user_logged_in; __utmt_UA-35890011-1=1; __utmt=1; __utma=148540593.1749037607.1447750961.1447758022.1447759837.3; __utmb=148540593.7.10.1447759837; __utmc=148540593; __utmz=148540593.1447750961.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=148540593.|1=age=25=1^2=huishouden=2=1^3=inschrijfduur=13=1; __utmli=submit; gatekeeper=1eba5968b8f8e03f90033a34e30eb224f7b23cd2; PHPSESSID=g7j2qmlqmkm3pvp7p4jfqknuo3',
                       'Host':'www.woonnet-haaglanden.nl',
                       'Referer':'https://www.woonnet-haaglanden.nl/woningaanbod/totale-aanbod/details/?dwellingID=155808',
                       'Upgrade-Insecure-Requests':'1',
                       'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
                       }
            house_source_code = s.get(link, headers = headers)
            #print link,'\n',house_source_code.url
            house_plain_text = house_source_code.text
            #print house_source_code.text
            isoup = bs(house_plain_text,"html.parser")

            for item in isoup.select('.dwelling-item-mainheader'):
                email_content=email_content + str(number_of_house) + '. \n'
                email_content=email_content + u'名称:\t\t'+ item.text + '\n'# house name
            
            for item in isoup.find('span',{'class':'price'}):
                email_content=email_content + u'原价:\t\t' + item.string + '\n'

            email_content=email_content + u'户型:\t\t'
            
            for item in isoup.select('.dwellingdetails li'):
                room = filter(lambda ch: ch in '0123456789',item.text)

            email_content=email_content + room + u'室\t' +str(area_list[index]) +u'平米\n'#room type

            for item in isoup.select('.dwelling-item-subheader'):

                address = item.text[:(item.text).index('-')]
                email_content=email_content + u'地址:\t\t' + address + '\n' # house address

            email_content=email_content + u'方式:\t\t'

            for item in isoup.select('.dwelling-item-toewijzing div span'):
                email_content=email_content + item.text.replace('Toewijzingsmodel ','').replace('Reageer voor: ','').replace('s',u'抽签').replace('d',u'先到先得').replace(', 20.00 uur','') +'\t'
                #rent information

            for item in isoup.findAll('div',{'class':'greenbox portalDwellingLeftSide'}):
                ss = u' '.join(item.text.split()) #criteria
                ss= ss.replace('Voorwaarden',u'要求: ')
                ss= ss.replace('Verhuurder','')
                ss= ss.replace('>','\n\t\t\t\t')
                #ss = '\n'.join(ss.split('>'))
                email_content=email_content + '\n' + ss

            email_content=email_content + u'网页:\t\t' + link + '\n\n'

    heads = u'亲爱的小小霖同学，\n\n\t 廉租房网站又更新房源啦！一共更新了' + str(number_of_house) + u'处，亲，请查收~！\n\n'
    email_content = heads + email_content 
    email_content = email_content.encode('utf-8')

    #print email_content
    # update local url list
    file("./url_list.txt",'w').writelines(url_list)

    if number_of_house > 0:

        GMAIL_USERNAME = 'alexleethinker@gmail.com'
        GMAIL_PASSWORD = '***********'
        email_subject = u'小小霖快来看，廉租房有更新啦'.encode('utf-8')
        recipient = 'chulinxue@gmail.com'
        message = 'Subject: %s\n\n%s' % (email_subject, email_content)
        # The below code never changes, though obviously those variables need values.
        session = smtplib.SMTP('smtp.gmail.com:587')
        #session.ehlo()
        session.starttls()
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        session.sendmail(GMAIL_USERNAME, recipient, message)
        session.quit()

        print 'Send successfully!!'
        
    else:
        print 'there is no updates'
#####################################   regular run     #########################################


s = sched.scheduler(time.time,time.sleep)

def perform(inc):
    s.enter(inc,0,perform,(inc,))
    iHouse_crawler()

def mymain(inc=900):
    s.enter(inc,0,perform,(inc,))
    s.run()

if __name__ == "__main__":
    mymain()

