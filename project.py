#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import requests, re, datetime, time, codecs, sys, traceback
from bs4 import BeautifulSoup

start = time.time()

fi_links = open('links.txt', 'r')
links = fi_links.readlines()
fi_links.close()

expression_file = codecs.open('expression.txt', 'r', 'UTF-8')
expression = unicode(expression_file.read().rstrip())
expression_file.close()

filter_open = codecs.open('filter.txt', 'r', 'UTF-8')
filter_ = unicode(filter_open.read().rstrip())
filter_open.close()

NI_file = codecs.open('not_include.txt', 'r', 'UTF-8')
not_include = unicode(NI_file.read().rstrip())
NI_file.close()

TF_file = codecs.open('twitter_filter.txt', 'r', 'UTF-8')
twitter_filter = unicode(TF_file.read().rstrip())
TF_file.close()

update_total = 0
errors = 0
email = ''

for link in links:
        try:
                link = link.strip()
                filename =  re.sub("(http)(s)?(://)(www\.)?", '', link)
 filename = 'out/' + re.sub("/.*", '', filename) + '.html'

                try:

                        fo = open(filename,'r')
                        fo.close()
                except:

                        fo = open(filename,'w')
                        fo.write('<html lang="ja">\n<meta content="text/html; charset=UTF-8" http-equiv="Content-Type">')
                        fo.close()


                r = requests.get(link, timeout=10)
                html = BeautifulSoup(r.content)

                fo = codecs.open(filename, 'r', encoding='UTF-8')
                site = unicode(fo.read())
                fo.close()

                e = []
                e.extend(html.find_all( 'div'))
                e.extend(html.find_all( 'a'))
                e.extend(html.find_all( 'img'))
                e.extend(html.find_all( 'ul'))
                e.extend(html.find_all( 'link'))
                e.extend(html.find_all( 'p'))
                e.extend(html.find_all( 'h1'))
                e.extend(html.find_all( 'h2'))
                e.extend(html.find_all( 'h3'))
                e.extend(html.find_all( 'ol'))
                e.extend(html.find_all( 'dl'))
                e.extend(html.find_all( 'dl'))
                e.extend(html.find_all( 'text'))

                text = []
                out = []
                if re.search(u'twitter|baidu|ishuhui',  unicode(link), re.UNICODE | re.I) == None:
                        for input in e:
                                input_ = re.sub(unicode(filter_), u'', unicode(input), re.UNICODE | re.DOTALL)
                                if len(input_) < 2000 and \
                                re.search(expression, input_, re.UNICODE | re.I) != None:
                                                text.append(input_)

                        j = 0
                        if len(text) > 0:
                                text.append("stop")
                                while text[j] != "stop":
                                        steps = []
                                        for step in xrange(len(text)-1):
                                                steps.append((j+1+step)%len(text))

                                        for step in steps:
                                                if (text[j] in text[step]):
                                                        del text[j]
                                                        j = j - 1
                                                        break
                                        j = j + 1

                                text.pop()
                        for youtube in html.find_all('iframe'):
                                if unicode(youtube).find(u'youtube.com') > 0:
                                        youtube_ = re.sub('src="//www.youtube.com', 'src="http://www.youtube.com', unicode(youtube), re.UNICODE)
                                        text.append(youtube_)

                for twitter in html.find_all('div', {'class':'Grid', 'role':'presentation', 'data-component-term':'tweet'}):
                        tweet = unicode(twitter)
                        for filter_t in re.findall(twitter_filter, unicode(twitter), re.UNICODE | re.DOTALL):
                                tweet = tweet.replace(unicode(filter_t), '')
                        if not (tweet in site):
                                text.append(tweet)

                for baidu in html.find_all('a', {'class':'j_th_tit'}):
                        if (not (unicode(baidu) in site)) and re.search(expression, unicode(baidu), re.UNICODE | re.I) != None:
                                text.append(re.sub(filter_, u'', unicode(baidu), re.DOTALL | re.UNICODE))

                for baidu in html.find_all('div', {'class':'threadlist_abs threadlist_abs_onlyline'}):
                        if (not (unicode(baidu) in site)) and re.search(expression, unicode(baidu), re.UNICODE | re.I) != None:
                                text.append(re.sub(filter_, u'', unicode(baidu), re.DOTALL | re.UNICODE))

                if re.search(u'ishuhui',  unicode(link), re.UNICODE | re.I) != None:
                        for ishuhui in html.find_all('div', {'class':'thumbnail'}):
                                if not (unicode(ishuhui) in site):
                                        text.append(unicode(ishuhui))

                for mu in html.find_all('dl', {'class':'NA_articleLink'}):
                        mu_ = re.sub(unicode(filter_), u'', unicode(mu), re.UNICODE | re.DOTALL)
                        if (not (unicode(mu_) in site)) and re.search(expression, unicode(mu_), re.UNICODE | re.I) != None:
                                text.append(mu_)

                for anime in html.find_all('dl', {'class':'newslistItem-odd'}):
                        anime_ = unicode(anime)
                        if (not (unicode(anime_) in site)) and re.search(expression, unicode(anime_), re.UNICODE | re.I) != None:
                                text.append(anime_)

                for element in text:
                        link_b = link
                        if link[len(link)-1] != '/':
                                link_b = link_b + '/'
                        element = re.sub(u'src="/', u'src="' + re.findall('http://.*?/|https://.*?/',link_b)[0], element, re.UNICODE)
                        element = re.sub(u'href="/', u'href="' + re.findall('http://.*?/|https://.*?/',link_b)[0], element, re.UNICODE)
                        element = re.sub(u'url\("/', u'url\("' + re.findall('http://.*?/|https://.*?/',link_b)[0], element, re.UNICODE)
                        for img in re.findall(u'src="[a-gi-z]', element):
                                element = re.sub(u'src="[a-gi-z]', u'src="' + link_b + img[len(img)-1], element, re.UNICODE)

                        if (not (element in site)) and len(element) > 0:
                                out.append(element)

                fo = codecs.open(filename, 'a', encoding='UTF-8')
                update_count = len(out)
                if update_count >= 1:
                        fo.write('\n\n<br><br><br>\n\
                        <b>update: ' + str(datetime.datetime.now()) + '</b>' + \
                        '\n<br><font color=red size = 8>' + \
                        '<a href="' + link +'">' + link + '</a></font></b><br>\n')
                        print "writing to (" + filename + ")"

                        for k in xrange(update_count):
                                fo.write(out[k])
                                email = email + '<table border="1">\n\t<tr>\n\t\t<td>'\
                                + '<a href="' + link + '">' + link + '</a></td><td>' \
                                + '</tr>\n\t<tr>\n\t\t<td>' \
                                + out[k] + '</td>\n\t</tr>\n</table>\n<br><br>'

                fo.close()
                update_total = update_total + update_count
                print "A count of " + str(update_count) + " updates for " + link +  ' - ' + str(update_total) +  ' updates/' + str(errors)  + ' errors\n'

        except requests.Timeout:
                errors+=1
                error =  "--Timed out loading {}".format(link)
                print error
                email = email + error

        except:
                errors+=1
                error =  "--error with " + link + '\n' + str(traceback.format_exc())
                print error
                email = email + error


email = u'A count of ' + unicode(update_total) + u' updates  and ' + unicode(errors) + u' errors.\n\n' + email

if update_total > 0:

        print "sending email..."
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        # me == my email address
        # you == recipient's email address
        me = "senderemail@email.com"
        you = "receiveremail@email.com"
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Updates - ' + str(datetime.datetime.now())
        msg['From'] = me
        msg['To'] = you

        # Create the body of the message (a plain-text and an HTML version).
        #text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org"

        # Record the MIME types of both parts - text/plain and text/html.
        #part1 = MIMEText(text, 'plain')
        part2 = MIMEText(email, 'html', 'utf-8')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        #msg.attach(part1)
        msg.attach(part2)

        # Send the message via local SMTP server.
        #s = smtplib.SMTP('localhost')
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.

        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login("senderemail@email.com", "password")
        s.sendmail(me, you, msg.as_string())
        s.quit()
        print "--email sent."
	finish = time.time()

print "DONE : " +  str((finish - start)/60)
print u'A count of ' + unicode(update_total) + u' updates  and ' + unicode(errors) + u' errors.'
