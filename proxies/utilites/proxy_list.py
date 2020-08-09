from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
from datetime import datetime
import re
import json
from multiprocessing import Pool


class ProxyListScrap(object):
    """Скрапит бесплатнные прокси на сайтах в данном списке"""
    
    def __init__(self, sites_list:list, headers:dict, port:int):
        self.sites_list = sites_list
        self.headers = headers
        self.port = port
        self.all_proxies = []
        self.to_json = None


    def get_html_text(self, url):
        """Получает файл html в текст формате"""
        r = requests.get(url=url, headers=self.headers)
        print('STATUS:', r.status_code)
        if r.status_code == 200:
            return r.text


    def get_proxy_iter(self,text_html):
        """Maked iterator for tuples of proxies"""
        soup = BeautifulSoup(text_html, 'html.parser')
        if soup == None:
            return
        table = soup.find('table', {'id': re.compile('.*proxy.*')})
        tr_s = table.find('tbody').findAll('tr')
        
        for tr in tr_s:
            td_s = tr.findAll('td')
            if len(td_s) > 2:
                ip = td_s[0].get_text().strip() if td_s[0].find('abbr') == None else re.search(r'\d+\.\d+\.\d+\.\d+',
                                                                                                td_s[0].find('script').string).group(0).strip()
                port = td_s[1].get_text().strip()
                yield ip + ':' + port


    def save_all_proxy(self, proxies_iters):

        for proxies_iter in proxies_iters:
            for proxy in proxies_iter:
                    if re.match(r'\d+\.\d+\.\d+\.\d+:\d+', proxy):
                        self.all_proxies.append(proxy)


    def check_proxy(self, proxy):
        """Проверяет корректность прокси"""
        proxy_http = {'http': 'http://{}'.format(proxy)}
        try:
            requests.get('https://www.translate.ru/', headers=self.headers, proxies=proxy_http)
            print('Proxy: {} \tADDED'.format(proxy))
            return proxy
        except ConnectionError:
            print('Proxy: {} \tNOT CONNECTED'.format(proxy))


    def save_json(self):
        with open('proxies.json', 'w') as f:
            json.dump(self.all_proxies, f)
    

    def save_only_check_json(self, processes=100):

        with Pool(processes=processes) as p:
            result = p.map(self.check_proxy, self.all_proxies)
            if result:
                self.to_json = result
        
        with open('proxies.json', 'w') as f:
            json.dump(self.to_json, f)


    def parse(self):
        iters = []
        for site in self.sites_list:
            html_text = self.get_html_text(site)
            proxy_iter = self.get_proxy_iter(html_text)
            if proxy_iter:
                iters.append(proxy_iter)
        
        self.save_all_proxy(iters)


def scrap_for_la_project():
    """For lastin project"""
    sites_list = ['https://www.proxynova.com/proxy-server-list/', 'https://free-proxy-list.net/']
    port = 443
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
        'Accept': 'text/css,*/*;q=0.1',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 
    }

    spider = ProxyListScrap(sites_list, headers, port)
    spider.parse()
    return spider.all_proxies


if __name__ == '__main__':
    # make list of sites with proxies and headers, port
    sites_list = ['https://www.proxynova.com/proxy-server-list/', 'https://free-proxy-list.net/']
    port = 443
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
        'Accept': 'text/css,*/*;q=0.1',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 
    }

    spider = ProxyListScrap(sites_list, headers, port)
    spider.parse()
    spider.save_only_check_json()
