import os
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pickle
from dateutil.parser import parse
import pandas as pd
import string
import json
from datetime import datetime
import time


def read_log_file():
    if os.path.exists('Visited_urls.txt'):
        with open('Visited_urls.txt', 'r', encoding='utf-8') as read_file:
            return read_file.read().split('\n')
    return []


def write_visited_log(url):
    with open('Visited_urls.txt', 'a', encoding='utf-8') as write_obj:
        write_obj.write(f"{url}\n")


def get_number_equivalent(letter):
    letters = list(string.ascii_lowercase)
    letter_number_dict = {letter: ord(letter) - ord('a') + 1 for letter in letters}
    return str(letter_number_dict.get(letter, ''))


def replace_with_num(value):
    alpha_numeric = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12,
                     'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19, 't': 20, 'u': 21, 'v': 22, 'w': 23,
                     'x': 24, 'y': 25, 'z': 26,'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10}
    try:
        sequence = alpha_numeric[value]
    except:
        sequence = value
    # print(sequence)
    return str(sequence)


def open_txt_file(file_name):
    '''Opens a html file and read it to return the soup of that page'''
    file_path = os.path.join(os.getcwd(), 'Html Txt Files')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(fr'Html Txt Files\{file_name}.txt', 'r', encoding='utf-8') as f:  # Folder name should be Html in the cwd
        # soup = get_soup_str(re.sub('\s+', ' ', str(BeautifulSoup(f.read(), 'html.parser'))))
        soup = BeautifulSoup(f.read(), 'html.parser')
        return soup


def get_abstract_page(url):
    """To get html of the page"""
    driver_obj.get(url)
    html = driver_obj.find_element(by=By.TAG_NAME, value='html')
    html.send_keys(Keys.END)
    driver_obj.implicitly_wait(5)
    html_file_name = url.split('/')[-1]
    # driver_obj.maximize_window()
    # driver_obj.implicitly_wait(10)
    while 'Loading...' in driver_obj.page_source:
        time.sleep(1)
    time.sleep(5)
    # html = BeautifulSoup(html, 'html.parser')
    return driver_obj.page_source


def get_author_page(url):
    """To get html of the page"""
    driver_obj.get(url)
    driver_obj.implicitly_wait(5)
    # driver_obj.maximize_window()
    # driver_obj.implicitly_wait(5)
    # time.sleep(10)
    html = BeautifulSoup(driver_obj.page_source, 'html.parser')
    return html


def strip_it(contents):
    striped_con = re.sub(r'\s+',' ',str(contents))
    return striped_con


def sup_sub_encode(html):
    """Encodes superscript and subscript tags"""
    encoded_html = html.replace('<sup>', 's#p').replace('</sup>', 'p#s').replace('<sub>', 's#b').replace('</sub>',
                                                                                                         'b#s') \
        .replace('<Sup>', 's#p').replace('</Sup>', 'p#s').replace('<Sub>', 's#b').replace('</Sub>', 'b#s')
    encoded_html = BeautifulSoup(encoded_html, 'html.parser').text.strip()
    return encoded_html


def sup_sub_decode(html):
    """Decodes superscript and subscript tags"""
    decoded_html = html.replace('s#p', '<sup>').replace('p#s', '</sup>').replace('s#b', '<sub>').replace('b#s',
                                                                                                         '</sub>')
    # decoded_html = BeautifulSoup(decoded_html, 'html.parser')
    return decoded_html


def abstract_cleaner(abstract):
    """Converts all the sup and sub script when passing the abstract block as html"""
    conversion_tags_sub = BeautifulSoup(str(abstract), 'lxml').find_all('sub')
    conversion_tags_sup = BeautifulSoup(str(abstract), 'lxml').find_all('sup')
    abstract_text = str(abstract).replace('<.', '< @@dot@@')
    for tag in conversion_tags_sub:
        original_tag = str(tag)
        key_list = [key for key in tag.attrs.keys()]
        for key in key_list:
            del tag[key]
        abstract_text = abstract_text.replace(original_tag, str(tag))
    for tag in conversion_tags_sup:
        original_tag = str(tag)
        key_list = [key for key in tag.attrs.keys()]
        for key in key_list:
            del tag[key]
        abstract_text = abstract_text.replace(original_tag, str(tag))
    abstract_text = sup_sub_encode(abstract_text)
    abstract_text = BeautifulSoup(abstract_text, 'lxml').text
    abstract_text = sup_sub_decode(abstract_text)
    abstract_text = re.sub('\s+', ' ', abstract_text)
    text = re.sub('([A-Za-z])(\s+)?(:|\,|\.)', r'\1\3', abstract_text)
    text = re.sub('(:|\,|\.)([A-Za-z])', r'\1 \2', text)
    text = re.sub('(<su(p|b)>)(\s+)(\w+)(</su(p|b)>)', r'\3\1\4\5', text)
    text = re.sub('(<su(p|b)>)(\w+)(\s+)(</su(p|b)>)', r'\1\3\5\4', text)
    text = re.sub('(<su(p|b)>)(\s+)(\w+)(\s+)(</su(p|b)>)', r'\3\1\4\6\5', text)
    abstract_text = re.sub('\s+', ' ', text)
    abstract_text = abstract_text.replace('< @@dot@@', '<.')
    return abstract_text.strip()


def abstract_text(contents):
    li_replace = str(contents).replace('<li>','<li>• ').replace('</h2>', ': </h2>')
    abstract_clean = abstract_cleaner(li_replace)
    return abstract_clean


def get_content():
    count = 1
    while count <= 5:
        soup_ = get_author_page(url)
        volume_sessions = soup_.find_all('script', type='application/json')
        if volume_sessions:
            print('=' * 30)
            return volume_sessions
        else:
            count += 1
            time.sleep(10)


if __name__ == '__main__':
    JOURNAL_NAME = os.path.basename(__file__).rstrip('.py')
    journal_url = 'https://www.sciencedirect.com/journal/new-ideas-in-psychology/issues'
    base_url = r'https://www.sciencedirect.com'
    PATH = r'C:\Users\dell\PycharmProjects\pythonProject\hello\Scopus\Nov-2023\4th week\24-11-2023\psj_1001_sciencedirect_com_New Ideas in Psychology\chromedriver.exe'
    service = Service(PATH)
    option = webdriver.ChromeOptions()
    driver_obj = webdriver.Chrome(service=service, options=option)
    url = journal_url
    issn_number = '0732-118X'
    volume_sessions = get_content()
    if volume_sessions is not None:
        for sessions in volume_sessions:
            each_session = sessions.text
            each_session = json.loads(each_session)
            page_session = json.loads(each_session)['issuesArchive']['data']['noOfPages']
            for i in range(1, int(page_session) + 1):
                page_url = f'https://www.sciencedirect.com/journal/0732118X/years?page-size=20&page={i}&enrich=true'
                soup_ = get_author_page(page_url)
                # print(soup_)
                inner_session = soup_.find_all('pre')
                for sessions in inner_session:
                    inner_content = sessions.text
                    vol_session = json.loads(inner_content)['data']['results']
                    for url_session in vol_session:
                        volume_issue = url_session['issues']
                        for urls in volume_issue:
                            volume_issue_url = urls['uriLookup']
                            issue_url = f'https://www.sciencedirect.com/journal/new-ideas-in-psychology{volume_issue_url}'
                            volume_soup = get_author_page(issue_url)
                            abs_url_contents = volume_soup.find_all('a',
                                                                    class_='anchor article-content-title u-margin-xs-top u-margin-s-bottom anchor-default')
                            for abs_url_content in abs_url_contents:
                                abs_url = f'{base_url}{abs_url_content["href"]}'
                                file_id = abs_url.rsplit('/', 1)[1]
                                print(abs_url)
                                authors_url = fr"https://www.sciencedirect.com/sdfe/arp/pii/{file_id}/authors/"
                                if abs_url in read_log_file():
                                    continue
                                text_string = get_abstract_page(abs_url)
                                abs_soup = BeautifulSoup(text_string, 'html.parser')
                                author_soup = get_author_page(authors_url)
                                title_contents = abs_soup.find('h1', id='screen-reader-main-title')
                                try:
                                    if title_contents.find('span', class_='title-text'):
                                        article_title = abstract_cleaner(
                                            title_contents.find('span', class_='title-text').extract())
                                    else:
                                        article_title = abstract_cleaner(
                                            title_contents.find('span').extract())
                                except:
                                    article_title = ''
                                '''DOI'''
                                try:
                                    if abs_soup.find('a', class_='anchor doi anchor-default'):
                                        doi = abs_soup.find('a', class_='anchor doi anchor-default')['href'].strip()
                                    else:
                                        doi = abs_soup.find('a', class_='doi')['href'].strip()
                                except:
                                    doi = ''
                                '''KEYWORDS'''
                                try:
                                    if abs_soup.find('div', class_='Keywords u-font-gulliver text-s'):
                                        key = abs_soup.find('div', class_='Keywords u-font-gulliver text-s').find('div',
                                                                                                                  class_='keywords-section').find_all(
                                            'div', class_='keyword')
                                        key_list = [abstract_cleaner(single_key) for single_key in key]
                                        keywords = '; '.join(key_list).split('Keywords', 1)[-1].strip()
                                    elif abs_soup.find('div', class_='Keywords u-font-serif text-s'):
                                        key = abs_soup.find('div', class_='Keywords u-font-serif text-s').find('div',
                                                                                                               class_='keywords-section').find_all(
                                            'div', class_='keyword')
                                        key_list = [abstract_cleaner(single_key) for single_key in key]
                                        keywords = '; '.join(key_list).split('Keywords', 1)[-1].strip()
                                    else:
                                        keywords = ''
                                except:
                                    keywords = ''
                                '''JOURNAL NAME'''
                                try:
                                    journal_name = abs_soup.find('h2', class_='publication-title u-h3')
                                    journal_name = abstract_cleaner(journal_name)
                                except:
                                    journal_name = ''
                                '''VOLUME AND ISSUE'''
                                try:
                                    volume_issue = abs_soup.find('div', class_='text-xs').find('a',
                                                                                               class_='anchor anchor-default')
                                    volume_issue = abstract_cleaner(volume_issue)
                                    if 'Issue' in str(volume_issue):
                                        volume = volume_issue.split(',')[0].replace('Volume', '').strip()
                                        issue = volume_issue.split(',')[1].replace('Issue', '').strip()
                                    else:
                                        volume = volume_issue.split(',')[0].replace('Volume', '').strip()
                                        issue = ''
                                except:
                                    volume = ''
                                    issue = ''
                                '''PUBLISHED DATE AND YEAR'''
                                try:
                                    year = str(abs_soup.find('div', class_='text-xs')).split('<!-- -->')[1].strip()
                                    year = re.search('(\d{4})', str(year)).group()
                                    published_date = parse(year).strftime('%d/%m/%Y')
                                except:
                                    year = ''
                                    published_date = ''
                                '''PDF URL'''
                                try:
                                    PDF_URL = abs_soup.find('div', class_='accessbar').find('a')
                                    if '.pdf' in str(PDF_URL):
                                        pdf_url_ = PDF_URL['href']
                                        pdf_url = f'https://www.sciencedirect.com{pdf_url_}'
                                    else:
                                        pdf_url = ''
                                except:
                                    pdf_url = ''
                                '''REFERENCE'''
                                try:
                                    if abs_soup.find('div', id='preview-section-references'):
                                        reference = abs_soup.find('div', id='preview-section-references').extract()
                                        reference = abstract_cleaner(reference)
                                    elif abs_soup.find('ol', class_='references'):
                                        ref = abs_soup.find('ol', class_='references').extract()
                                        ref_list = [abstract_cleaner(single_ref) for single_ref in
                                                    ref.find_all('li')]
                                        reference = ' '.join(ref_list)
                                    else:
                                        reference = ''
                                except:
                                    reference = ''
                                '''CITATION'''
                                try:
                                    citation = abs_soup.find('div', id='preview-section-cited-by').extract()
                                    citation = abstract_cleaner(citation)
                                except:
                                    citation = ''
                                '''ACKNOWLEDGEMENT'''
                                try:
                                    if abs_soup.find('section', id='ack0005'):
                                        acknowledgment = abs_soup.find('section', id='ack0005').extract()
                                        acknowledgment = abstract_cleaner(acknowledgment).replace('Acknowledgment',
                                                                                                  'Acknowledgment ')
                                    elif abs_soup.find('section', id='ack0001'):
                                        acknowledgment = abs_soup.find('section', id='ack0001').extract()
                                        acknowledgment = abstract_cleaner(acknowledgment).replace('Acknowledgment',
                                                                                                  'Acknowledgment ')
                                    elif abs_soup.find('section', id='ack0010'):
                                        acknowledgment = abs_soup.find('section', id='ack0010').extract()
                                        acknowledgment = abstract_cleaner(acknowledgment).replace('Acknowledgment',
                                                                                                  'Acknowledgment ')
                                    else:
                                        acknowledgment = ''
                                except:
                                    acknowledgment = ''
                                '''CONFLICT OF INTEREST'''
                                try:
                                    if abs_soup.find('section', id='coi0001'):
                                        conflict_data = abs_soup.find('section', id='coi0001').extract()
                                        conflict = abstract_cleaner(conflict_data).replace(
                                            'Declaration of competing interest', '').strip()
                                    elif abs_soup.find('section', id='coi0005'):
                                        conflict_data = abs_soup.find('section', id='coi0005').extract()
                                        conflict = abstract_cleaner(conflict_data).replace(
                                            'Declaration of competing interest', '').strip()
                                    elif abs_soup.find('section', id='coi0010'):
                                        conflict_data = abs_soup.find('section', id='coi0010').extract()
                                        conflict = abstract_cleaner(conflict_data).replace(
                                            'Declaration of competing interest', '').strip()
                                    else:
                                        conflict = ''
                                except:
                                    conflict = ''
                                '''FULL TEXT'''
                                if abs_soup.find('div', id='preview-section-introduction'):
                                    text_block = abs_soup.find('div', id='preview-section-introduction')
                                    full_text_data = abstract_cleaner(text_block)
                                    session_snippets = abs_soup.find('div', id='preview-section-snippets')
                                    session_snippets = abstract_cleaner(session_snippets)
                                    if 'Funding' in str(session_snippets):
                                        text_split = session_snippets.split('Funding', 1)
                                        full_text = text_split[0].strip()
                                        funding = text_split[-1].strip()
                                        full_text_body = full_text_data + ' ' + full_text
                                    else:
                                        full_text = session_snippets
                                        funding = ''
                                        full_text_body = full_text_data + ' ' + full_text

                                elif abs_soup.find('div', class_='Body u-font-gulliver text-s'):
                                    text_block = abs_soup.find('div', class_='Body u-font-gulliver text-s')
                                    full_text_data = abstract_cleaner(text_block).replace('Introduction',
                                                                                          'Introduction ')
                                    session_snippets = abs_soup.find('div', id='preview-section-snippets')
                                    session_snippets = abstract_cleaner(session_snippets)
                                    if 'Funding' in str(session_snippets):
                                        text_split = session_snippets.split('Funding', 1)
                                        full_text = text_split[0].strip()
                                        funding = text_split[-1].strip()
                                        full_text_body = full_text_data + ' ' + full_text
                                    else:
                                        full_text = session_snippets
                                        funding = ''
                                        full_text_body = full_text_data + ' ' + full_text
                                elif abs_soup.find('div', class_='Body u-font-serif text-s'):
                                    text_block = abs_soup.find('div', class_='Body u-font-serif text-s')
                                    full_text_data = abstract_cleaner(text_block).replace('Introduction',
                                                                                          'Introduction ')
                                    session_snippets = abs_soup.find('div', id='preview-section-snippets')
                                    session_snippets = abstract_cleaner(session_snippets)
                                    if 'Funding' in str(session_snippets):
                                        text_split = session_snippets.split('Funding', 1)
                                        full_text = text_split[0].strip()
                                        funding = text_split[-1].strip()
                                        full_text_body = full_text_data + ' ' + full_text
                                    else:
                                        full_text = session_snippets
                                        funding = ''
                                        full_text_body = full_text_data + ' ' + full_text
                                else:
                                    full_text_body = ''
                                '''ABSTRACT BLOCK'''
                                if abs_soup.find('div', id='preview-section-abstract'):
                                    abstract_block = abs_soup.find('div', id='preview-section-abstract')
                                    abstract_join = abstract_cleaner(abstract_block).replace('Abstract', '').strip()
                                elif abs_soup.find('div', class_='Abstracts u-font-gulliver text-s'):
                                    abstract_block = abs_soup.find('div',
                                                                   class_='Abstracts u-font-gulliver text-s').find(
                                        'div', class_='abstract author')
                                    abstract_join = abstract_cleaner(abstract_block).replace('Abstract', '').strip()
                                elif abs_soup.find('div', class_='Abstracts u-font-serif text-s'):
                                    abstract_block = abs_soup.find('div',
                                                                   class_='Abstracts u-font-serif text-s').find(
                                        'div', class_='abstract author')
                                    abstract_join = abstract_cleaner(abstract_block).replace('Abstract', '').strip()
                                else:
                                    abstract_join = ''
                                '''auth, affiliation from json'''
                                try:
                                    load_data = json.loads(author_soup.text)
                                    author_list = []
                                    authors = load_data['content'][0]['$$']
                                    for author in authors:
                                        if author['#name'] != 'author':
                                            continue
                                        author_segments = []
                                        for segment in author['$$']:
                                            if segment['#name'].endswith('name'):
                                                author_segments.append(segment['_'])
                                        author_name = ' '.join(author_segments)
                                        author_seq = []
                                        for author_dict in author['$$']:
                                            if author_dict['#name'] == 'cross-ref' and author_dict.get('$$'):
                                                for sup_value in author_dict['$$']:
                                                    if sup_value['#name'] == 'sup':
                                                        if str(sup_value['_']).isdigit():
                                                            label = sup_value['_']
                                                        else:
                                                            label = get_number_equivalent(sup_value['_'])
                                                        author_seq.append(label)
                                        author_name = f"{author_name} {', '.join(author_seq)}"
                                        author_list.append(author_name)
                                    authors = '; '.join(author_list).replace(' ; ', '; ').strip(',').strip()

                                    affiliations_list = []
                                    affiliations = load_data['affiliations']
                                    allowed_values = ['__text__', 'textfn', 'label']
                                    aff_segments = []
                                    for affiliation in affiliations.values():
                                        if affiliation['#name'] == 'affiliation':
                                            aff_segments = []
                                        for segment in affiliation['$$']:
                                            if segment['#name'] == 'label':
                                                if str(segment['_']).isdigit():
                                                    label = segment['_']
                                                else:
                                                    label = get_number_equivalent(segment['_'])
                                                aff_segments.append(label)
                                            try:
                                                aff_list = []
                                                for single_value in segment['$$']:
                                                    if single_value['#name'] == '__text__':
                                                        content = single_value['_']
                                                        aff_list.append(content)
                                                aff_tag = ', '.join(aff_list).replace(', ,', '').strip()
                                                aff_segments.append(aff_tag)
                                            except:
                                                if segment['#name'] == 'textfn':
                                                    aff_segments.append(segment['_'])
                                        affiliation_name = ' '.join(aff_segments)
                                        affiliations_list.append(affiliation_name)
                                        affiliations = '; '.join(affiliations_list)
                                except Exception as e:
                                    print('EXCEPTION--->', e)
                                    authors = ''
                                    affiliations = ''
                                print('current datetime------>', datetime.now())
                                dictionary = {
                                    "journalname": journal_name,
                                    "journalabbreviation": "",
                                    "journalurl": journal_url,
                                    "year": year,
                                    "issn": issn_number,
                                    "volume": volume,
                                    "issue": issue,
                                    "articletitle": strip_it(article_title),
                                    "doiurl": doi,
                                    "author": strip_it(authors),
                                    "author_affiliation": strip_it(affiliations),
                                    "abstractbody": strip_it(abstract_join),
                                    "keywords": strip_it(keywords),
                                    "fulltext": full_text_body,
                                    "fulltexturl": abs_url,
                                    "publisheddate": published_date,
                                    "conflictofinterests": conflict,
                                    "otherurl": pdf_url,
                                    "articleurl": abs_url,
                                    "pubmedid": "",
                                    "pmcid": "",
                                    "sponsors": '',
                                    "manualid": "",
                                    "country": "",
                                    "chemicalcode": "",
                                    "meshdescriptioncode": "",
                                    "meshqualifiercode": "",
                                    "medlinepgn": "",
                                    "language": "",
                                    "nlmuniqueid": "",
                                    "datecompleted": "",
                                    "daterevised": '',
                                    "medlinedate": "",
                                    "studytype": "",
                                    "isboolean": "",
                                    "nativetitle": '',
                                    "nativeabstract": '',
                                    "citations": citation,
                                    "reference": reference,
                                    "disclosure": "",
                                    "acknowledgements": acknowledgment,
                                    "supplement_url": ""
                                }
                                articles_df = pd.DataFrame([dictionary])
                                if os.path.isfile(f'{JOURNAL_NAME}.csv'):
                                    articles_df.to_csv(f'{JOURNAL_NAME}.csv', index=False, header=False,
                                                       mode='a')
                                else:
                                    articles_df.to_csv(f'{JOURNAL_NAME}.csv', index=False)
                                write_visited_log(abs_url)
        driver_obj.close()