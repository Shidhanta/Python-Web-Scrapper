from urllib.request import urlopen
import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import itertools

def extract_url(i):
    url = 'http://www.freepatentsonline.com/result.html?p={}&edit_alert=&srch=xprtsrch&query_txt=Herbal+AND+%0D%0A%28ACN%2FUS+OR+ACN%2FCA+OR+ACN%2FIN+OR+ACN%2FCN+OR+ACN%2FKR+OR+ACN%2FDE+OR+ACN%2FGB+OR+ACN%2FJP%29&usapp=on&date_range=all&stemming=on&sort=relevance&search=Search'.format(i)
    with urlopen(url) as url_file:
        url_client = url_file.read().decode('utf-8')
    soup = bs(url_client)
    tag = soup.find_all(href = re.compile(r'/y\d*/\d*.html'))
    urls=list(map(lambda x: 'http://www.freepatentsonline.com'+x['href'], tag))
    return urls
addresses = list(map(extract_url, list(range(1, 183))))
addresses = list(itertools.chain(*addresses))
df = pd.DataFrame(data = {'urls':addresses})


def feature_extraction(link):
    with urlopen(link) as file:
        fp = file.read().decode('utf-8')
    soup = bs(fp)
    division = soup.find('form', {"action":"", "name":"biblio"})
    def extracter(string):
        abstract_list = soup.find_all('div', {'class':'disp_doc2'})
        for tag in abstract_list:
            try:
                abst = tag.find('div', class_='disp_elm_title').string
                if abst==None:
                    raise Exception('Hacked!')
            except Exception:
                abst = '---'
            if abst.startswith(string):
                abstract = tag.find('div', class_='disp_elm_text').text
                abstract = abstract.strip()
                return abstract
    abstract_list = soup.find_all('div', {'class':'disp_doc2'})
    patent_no = 'US'+division.find('input', {'name':'patent'})['value']
    patent_title = division.find('input', {'name':'title'})['value']
    author = division.find('input', {'name':'author'})['value']
    author_country = re.findall(r', ([A-Z]*)\)', author)
    if author_country == []:
        author_country = ''
    else:
        author_country = author_country[0]
    assignee = division.find('input', {'name':'assignee'})['value']
    assignee_country = re.findall(r'\(, ([A-Z]*)\)', assignee)
    if assignee_country == []:
        assignee_country = author_country
    else:
        assignee_country = assignee_country[0]
    abstract = extracter('Abstract:')
    publication_date = extracter('Publication Date:')
    description = extracter('Description:')
    sample_point = [patent_no, publication_date, patent_title, author, author_country, assignee, assignee_country, abstract, description]
    return sample_point



feature_mat = list(map(lambda x: feature_extraction(x), list(df.loc[0:0, 'urls'].values)))
df2 = pd.DataFrame(feature_mat, columns = ['Patent_number', 'Pub. Date', 'Patent_name', 'Inventor(s)', 'Inventor_Country', 'Assignee', 'Assignee_country', 'Abstract', 'Description'])





