import smtplib
import html5lib, lxml, lxml.cssselect
import requests
import time
import os

gmail_user = os.environ['GMAIL_USERNAME']
gmail_pass = os.environ['GMAIL_PASSWORD']
to_user = []
recipient = os.environ['TARGET_EMAIL']
to_user.append(recipient)


def scrape_registrar(course, url, css_query, max_capacity):
    try:
        r = requests.get(url)
    except:
        print("Connection reset. Retrying.")
        send_email('Connection reset', 'Retrying')
        return

    raw_html = r.text
    page = html5lib.parse(raw_html, treebuilder='lxml', namespaceHTMLElements=False)
    selector = lxml.cssselect.CSSSelector(css_query)
    match = selector(page)
    status = match[0].text
    print('current: %s, capcity: %s' % (status, max_capacity))

    if status != max_capacity:
        subj = '%s is availible, sign up now!\n' % course
        body = 'https://be.my.ucla.edu/ClassPlanner/ClassPlan.aspx'

        print(subj)
        send_email(subj, body)
        return True
    else:
        print('%s is still closed :(\n' % course)
        return False


def send_email(subject, text):
    message = 'Subject: %s\n\n%s' % (subject, text)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, to_user, message)
        print('Email sent successfully')
        server.quit()
    except smtplib.SMTPException:
        print('Error: sending email failed')


def run_checker(interval, status):
    stat100A_query = '#ctl00_BodyContentPlaceHolder_detselect_ctl02_ctl02_WaitListTotal span'
    math170A_query = '#ctl00_BodyContentPlaceHolder_detselect_ctl02_ctl02_EnrollTotal span'

    class1 = 'Stat 100A'
    class2 = 'Math 170A'

    stat100A_url = 'http://www.registrar.ucla.edu/schedule/detselect.aspx?termsel=16S&subareasel=STATS&idxcrs=0100A+++'
    math170A_url = 'http://www.registrar.ucla.edu/schedule/detselect.aspx?termsel=16S&subareasel=MATH&idxcrs=0170A+++'

    stat100A_capacity = '20'
    math170A_capacity = '40'

    class1_open = False
    class2_open = False
    start_time = time.time()
    initial_time = time.time()

    while not class1_open or not class2_open:
        curr_time = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())

        if not class1_open:
            print('At %s, checking for open spots for %s...' % (curr_time, class1))
            class1_open = scrape_registrar(class1, stat100A_url, stat100A_query, stat100A_capacity)

        if not class2_open:
            print('At %s, checking for open spots for %s...' % (curr_time, class2))
            class2_open = scrape_registrar(class2, math170A_url, math170A_query, math170A_capacity)

        time.sleep(interval)
        check_time = time.time()
        if check_time - start_time > status or check_time - initial_time < 15:
            start_time = check_time
            send_email('Checker status update', 'Still running fine!')

run_checker(10, 14400)
