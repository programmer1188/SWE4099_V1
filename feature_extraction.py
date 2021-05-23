import ipaddress
import re
import urllib
import urllib.request
import os
import json
import base64
import datetime
import socket
import requests
import sys
from googlesearch import search
import whois
import favicon
import time
import xml.etree.ElementTree as ET 
import tldextract
from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parse
from urllib.parse import urlparse,urlencode
from subprocess import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

  

# Generate data set by extracting the features from the URL
def generate_data_set(url):

    data_set = []

    # Converts the given URL into standard format
    if not re.match(r"^https?", url):
        url = "http://" + url
        

    # Stores the response of the given URL
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
    except:
        response = ""
        soup = -999
    #print(response)
    #print(soup)    
    
    

    # Extracts domain from the given URL
    domain = re.findall(r"://([^/]+)/?", url)[0]
    if re.match(r"^www.",domain):
	       domain = domain.replace("www.","")
    #print(domain)       

    # Requests all the information about the domain
    whois_response = whois.whois(domain)
    #print(whois_response)


    # Extracts global rank of the website
    try:
        extract_res = tldextract.extract(url)
        url_ref = extract_res.domain + "." + extract_res.suffix
        html_content = requests.get("https://www.alexa.com/siteinfo/" + url_ref).text
        soup = BeautifulSoup(html_content, "lxml")
        global_rank = str(soup.find('div', {'class': "rankmini-rank"}))[42:].split("\n")[0].replace(",", "")
    except:
        global_rank = -1
    
    #print(global_rank)

    # 1.having_IP_Address
    try:
        import string
        index = url.find("://")
        split_url = url[index+3:]
        #print(split_url)
        index = split_url.find("/")
        split_url = split_url[:index]
        #print(split_url)
        split_urlh = split_url.replace(".", "")
        #print(split_urlh)
        counter_hex = 0
        for i in split_urlh:
            if i in string.hexdigits:
                counter_hex +=1

        total_len = len(split_urlh)

        having_IP_Address = 1
        
        if counter_hex >= total_len:
            having_IP_Address = -1
        
        try:
            ipaddress.ip_address(split_url)
            having_IP_Address = -1
        except:
            having_IP_Address = 1

        data_set.append(having_IP_Address) 
        
    except:
        data_set.append(-1)
        
        
    # 2.URL_Length
    try:
        if len(url) < 54:
            data_set.append(1)
        elif len(url) >= 54 and len(url) <= 75:
            data_set.append(0)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)    

    # 3.Shortining_Service
    try:    
        match=re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                        'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                        'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                        'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                        'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                        'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                        'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net', url)
        if match:
            data_set.append(-1)
        else:
            data_set.append(1) 
    except:
        data_set.append(-1) 
                

    # 4.having_At_Symbol
    try:
        if re.findall("@", url):
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1) 

    #5.double_slash_redirecting
    try:
        index = url.find("://")
        split_url = url[index+3:]
        #print(split_url)
        label = 1
        index = split_url.find("//")
        if index!=-1:
            label = -1
        data_set.append(label)
    except:
        data_set.append(-1) 

    # 6.Prefix_Suffix
    try:    
        if re.findall(r"https?://[^\-]+-[^\-]+/", url):
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1) 

    # 7.having_Sub_Domain
    try:
        if len(re.findall("\.", url)) == 2:
            data_set.append(1)
        elif len(re.findall("\.", url)) == 3:
            data_set.append(0)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1) 

    # 8.SSLfinal_State
    try:
        if response.text:
            data_set.append(1)
        else:
            data_set.append(0)
    except:
        data_set.append(-1)

    # 9.Domain_registeration_length
    
    try:
        expiration_date = whois_response.expiration_date
        creation_date = whois_response.creation_date
        registration_length = 0
        creation_date = min(creation_date)
        expiration_date = min(expiration_date)
        #today = time.strftime('%Y-%m-%d')
        #today = datetime.strptime(today, '%Y-%m-%d')
        registration_length = abs((expiration_date - creation_date).days)

        if registration_length / 365 <= 1:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)

    # 10.Favicon

    try:
        extract_res = tldextract.extract(url)
        url_ref = extract_res.domain
 
        favs = favicon.get(url)
 
        match = 0
        for favi in favs:
            url2 = favi.url
            extract_res = tldextract.extract(url2)
            url_ref2 = extract_res.domain
 
            if url_ref in url_ref2:
                match += 1
 
        if match >= 1:
            data_set.append(1) 
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
 

    #11. port
    import socket
    import time
    try:     
        extract_res = tldextract.extract(url)
        url_d = extract_res.domain+'.'+extract_res.suffix
        ip = url_d
        port = 443
        retry = 5
        delay = 10
        timeout = 3
    
        def isOpen(ip, port):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            try:
                s.connect((ip, int(port)))
                s.shutdown(socket.SHUT_RDWR)
                return True
            except:
                return False
            finally:
                s.close()
    
        def checkHost(ip, port):
            ipup = False
            for i in range(retry):
                if isOpen(ip, port):
                    ipup = True
                    break
                else:
                    time.sleep(delay)
            return ipup
    
        if checkHost(ip, port):
            data_set.append(1)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
        
    #12. HTTPS_token
    try:
        domain_part = urlparse(url).netloc
        if re.findall(r"^https://", domain_part):
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)

    #13. Request_URL
    try:  
        i=0
        for img in soup.find_all('img', src= True):
            dots= [x.start(0) for x in re.finditer('\.', img['src'])]
            if url in img['src'] or domain in img['src'] or len(dots)==1:
              success = success + 1
            i=i+1

        for audio in soup.find_all('audio', src= True):
            dots = [x.start(0) for x in re.finditer('\.', audio['src'])]
            if url in audio['src'] or domain in audio['src'] or len(dots)==1:
              success = success + 1
            i=i+1

        for embed in soup.find_all('embed', src= True):
            dots=[x.start(0) for x in re.finditer('\.',embed['src'])]
            if url in embed['src'] or domain in embed['src'] or len(dots)==1:
              success = success + 1
            i=i+1

        for iframe in soup.find_all('iframe', src= True):
            dots=[x.start(0) for x in re.finditer('\.',iframe['src'])]
            if url in iframe['src'] or domain in iframe['src'] or len(dots)==1:
              success = success + 1
            i=i+1

        percentage = success/float(i) * 100
        if percentage < 22.0 :
              data_set.append(1)
        elif((percentage >= 22.0) and (percentage < 61.0)) :
              data_set.append(0)
        else:
            data_set.append(-1)
    except:
        data_set.append(1)



    #14. URL_of_Anchor
    try:
        extract_res = tldextract.extract(url)
        url_ref = extract_res.domain
        html_content = requests.get(url).text
        soup = BeautifulSoup(html_content, "lxml")
        a_tags = soup.find_all('a')
    
        if len(a_tags) == 0:
            data_set.append(1)

        if a_tags:
            invalid = ['#', '#content', '#skip', 'JavaScript::void(0)']
            bad_count = 0
            for t in a_tags:
                try:
                    link = t['href']
                except KeyError:
                    continue
        
                if link in invalid:
                    bad_count += 1
        
                extract_res = tldextract.extract(link)
                url_ref2 = extract_res.domain
        
                if url_ref not in url_ref2:
                    bad_count += 1
        
            bad_count /= len(a_tags)
        
            if bad_count < 0.31:
                data_set.append(1) 
            elif bad_count <= 0.67:
                data_set.append(0)
            else:
                data_set.append(-1)
    except:
        data_set.append(-1)
    

    #15. Links_in_tags
    try:
        programhtml = requests.get(url).text
        s = BeautifulSoup(programhtml,"lxml")
        mtags = s.find_all('Meta')
        ud = tldextract.extract(url)
        upage = ud.domain
        mcount = 0
        for i in mtags:
            u1 = i['href']
            currpage = tldextract.extract(u1)
            u1page = currpage.domain
            if currpage not in ulpage:
                mcount+=1
        scount = 0
        stags = s.find_all('Script')
        for j in stags:
            u1 = j['href']
            currpage = tldextract.extract(u1)
            u1page = currpage.domain
            if currpage not in u1page:
                scount+=1
        lcount = 0
        ltags = s.find_all('Link')
        for k in ltags:
            u1 = k['href']
            currpage = tldextract.extract(u1)
            u1page = currpage.domain
            if currpage not in u1page:
                lcount+=1
        percmtag = 0
        percstag = 0
        percltag = 0
    
        if len(mtags) != 0:
            percmtag = (mcount*100)//len(mtags)
        if len(stags) != 0:
            percstag = (scount*100)//len(stags)
        if len(ltags) != 0:
            percltag = (lcount*100)//len(ltags)
          
        if(percmtag+percstag+percltag<17):
            data_set.append(1) 
        elif(percmtag+percstag+percltag<=81):
            data_set.append(0)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
    

    #16. SFH
    try:
        b=1
        for form in soup.find_all('form', action= True):
               if form['action'] =="" or form['action'] == "about:blank" :
                  b=-1
                  break
               elif url not in form['action'] and domain not in form['action']:
                   b=0
                   break
               else:
                     b=1
                     break
        data_set.append(b)
    except:
        data_set.append(-1)
        
    

    #17. Submitting_to_email
    try:    
        form_opt = str(soup.form)
        idx = form_opt.find("mail()")
        if idx == -1:
            idx = form_opt.find("mailto:")
    
        if idx == -1:
            data_set.append(1) 
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
            


    #18. Abnormal_URL
    try:
        # whois_response = whois.whois(url)
        host_name = whois_response.domain_name
          #print(host_name)
        if re.search(host_name[1], url):
            data_set.append(1)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
    
    #19. Redirect
    try:
        # r = requests.get(url)
        
        if len(response.history) <= 1:
            data_set.append(1)
        elif (len(response.history) >1 or len(response.history)<=4):
            data_set.append(0)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)


    #20. on_mouseover
    try:    
        if str(soup).lower().find('onmouseover="window.status') != -1:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)        

    #21. RightClick
    try:
        if str(soup).lower().find("event.button==2") != -1:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)


    #22. popUpWidnow
    try:    
        if re.findall(r"alert\(", response.text):
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)        


    #23. Iframe
    try:
        if str(soup.iframe).lower().find("frameborder") == -1:
            data_set.append(1) 
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
 
 
    #24. age_of_domain
    
    try:
        extract_res = tldextract.extract(url)
        url_ref = extract_res.domain + "." + extract_res.suffix
        whois_res = whois.whois(url)
        if datetime.now() > whois_res["creation_date"][0] + relativedelta(months=+6):
            data_set.append(1) 
        else:
            data_set.append(-1)
    except:
        data_set.append(-1) 

    #25. DNSRecord
    try:
        d = whois.whois(domain)
        if d:
            data_set.append(1)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)

    #26. web_traffic
    try:
        rank = BeautifulSoup(urllib.request.urlopen("http://data.alexa.com/data?cli=10&dat=s&url=" + url).read(), "xml").find("REACH")['RANK']
        rank= int(rank)
        if (rank<100000):
            data_set.append(1)
        else:
            data_set.append(0)
    except TypeError:
        data_set.append(-1)

    #27. Page_Rank
    try:
        extract_res = tldextract.extract(url)
        url_ref = extract_res.domain + "." + extract_res.suffix
        headers = {'API-OPR': 'ss8ssgsosog4ggsg8cw00o4gwokocwk8kosc4okk' }
        domain = url_ref
        req_url = 'https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D=' + domain
        request = requests.get(req_url, headers=headers)
        result = request.json()

        value = result['response'][0]['page_rank_decimal']
        #print(value)
        if value >=2:
            data_set.append(1)
        elif value<2:
            data_set.append(-1)
    except:
        data_set.append(-1)

    #28. Google_Index
    try:
        site=search(url)
        if site:
            data_set.append(1)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)

    #29. Links_pointing_to_page
    try:    
        number_of_links = len(re.findall(r"...href=", response.text))
        #print(number_of_links)
        if number_of_links == 0:
            data_set.append(-1)
        elif number_of_links <= 2:
            data_set.append(0)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)



    #30. Statistical_report
    try:
        url_match = re.search('at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweddy\.com|myjino\.ru|96\.lt|ow\.ly', url)
        ip_address = socket.gethostbyname(domain)
        ip_match = re.search('146\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|'
                            '107\.151\.148\.44|107\.151\.148\.107|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|52\.69\.166\.231|216\.58\.192\.225|'
                            '118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
                            '216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|'
                            '34\.196\.13\.28|103\.224\.212\.222|172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|'
                            '216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42', ip_address)
        if url_match:
            data_set.append(-1)
        elif ip_match:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)


    #print (data_set)
    return data_set

# data = generate_data_set('https://www.facebook.com/')
# print(data)


