"""
An mitmproxy adblock script!
(Required python modules: re2 and adblockparser)

(c) 2015-2019 epitron
"""
import re

from mitmproxy.script import concurrent
from mitmproxy.http import HTTPResponse
from adblockparser import AdblockRules
from glob import glob
from mitmproxy.net.http.http1.assemble import assemble_request


from bs4 import BeautifulSoup
import whois
import sqlite3
# import response_file
from main import malacius
from mitmproxy.net.http.http1.assemble import assemble_request


IMAGE_MATCHER = re.compile(r"\.(png|jpe?g|gif)$")
SCRIPT_MATCHER = re.compile(r"\.(js)$")
STYLESHEET_MATCHER = re.compile(r"\.(css)$")


def db_insert(host):
    with sqlite3.connect('whois.db') as connect:
        connect.execute('''create table if not exists websites 
            (id INTEGER primary key autoincrement, domain char(100) unique, 
            registrar char(150), expiration_date timestamp, creation_date timestamp, last_updated timestamp)''')
        try:
            domain = whois.query(host)
        except whois.exceptions.WhoisCommandFailed:
            return 
        except:
            return
        try:
            connect.execute('''
                insert into websites (domain, registrar, expiration_date, creation_date, last_updated)
                values(?,?,?,?,?)
            ''', (domain.name, domain.registrar, domain.expiration_date, domain.creation_date, domain.last_updated))
            connect.commit()
        except sqlite3.IntegrityError:
            print('ignore this exception')
        except Exception as e:
            print('error occured in database funcition')
            print('v'*10)
            print('\n'*4)
            print(e)
            print('^'*10)


def log(msg):
    print(msg)


def combined(filenames):
    '''
    Open and combine many files into a single generator which returns all
    of their lines. (Like running "cat" on a bunch of files.)
    '''
    for filename in filenames:
        with open(filename) as file:
            for line in file:
                yield line


def load_rules(blocklists=None):
    rules = AdblockRules(
        combined(blocklists),
        use_re2=True,
        max_mem=512*1024*1024
    )

    return rules


blocklists = glob("blocklists/*")

if len(blocklists) == 0:
    log("Error, no blocklists found in 'blocklists/'. Please run the 'update-blocklists' script.")
    raise SystemExit

else:
    log("* Available blocklists:")
    for list in blocklists:
        log("  |_ %s" % list)

log("* Loading blocklists...")
rules = load_rules(blocklists)
log("")
log("* Done! Proxy server is ready to go!")


class response_modifyer:
    def load(self, loader):
        load


@concurrent
def response(flow):
    if "Content-Type" in flow.response.headers:
        req = flow.request
        options = {'domain': req.host}
        if not rules.should_block(flow.request.url, options):
            soup = BeautifulSoup(open('test.html'), features="html.parser")
            if ('text/html' in flow.response.headers["content-type"]):
                data = assemble_request(flow.request).decode('utf-8')
                try:
                    b_soup  = BeautifulSoup(flow.response.content.decode('utf-8'), 'html.parser')
                except:
                    return
                text = b_soup.text
                resp = malacius(text)
                if resp:
                    pass
                    # print('html-response', flow.response.content)
                else:
                    print(f'blocked-url {flow.request.url}')
                    flow.response.content = str(BeautifulSoup(
                    open('test.html'), 'html.parser')).encode('utf-8')
                    
        else:
            print(f'blocked-url {flow.request.url}')
            flow.response.content = str(BeautifulSoup(
            open('test.html'), 'html.parser')).encode('utf-8')


@concurrent
def request(flow):
    global rules

    req = flow.request

    options = {'domain': req.host}

    db_insert(req.host)
    with open('hostname.txt', 'a') as f:
        f.write(f"{req.host} ===> url {flow.request.url}\n \n\n\n\n")

    if IMAGE_MATCHER.search(req.path):
        options["image"] = True
    elif SCRIPT_MATCHER.search(req.path):
        options["script"] = True
    elif STYLESHEET_MATCHER.search(req.path):
        options["stylesheet"] = True

    if rules.should_block(req.url, options):
        log("vvvvvvvvvvvvvvvvvvvv BLOCKED vvvvvvvvvvvvvvvvvvvvvvvvvvv")
        with open('block_sites.txt', 'a') as file:
            file.write(
                f'{flow.request.url} ===> header: {flow.request.headers.get("Accept")}\n')
            file.write(f'options {options}\n\n\n\n\n')
        log("accept: %s" % flow.request.headers.get("Accept"))
        log("blocked-url: %s" % flow.request.url)
        log("^^^^^^^^^^^^^^^^^^^^ BLOCKED ^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        flow.response = HTTPResponse.make(404, b"OK",
                                          {"Content-Type": "text/html"})

        # HTTPResponse(http_version, status_code, reason, headers, content, timestamp_start=None, timestamp_end=None)

    else:
        log("url: %s" % flow.request.url)

