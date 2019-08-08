from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from scraperbot import search_company

import wikipedia
import requests
from datetime import date
from newsapi import NewsApiClient

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from bs4 import BeautifulSoup as bs
from sumy.utils import get_stop_words


# using  https://newsapi.org

# API Key: 9a2b70eaea5b465ca6f09ee30784eb1f

common_abbreviations = {
    'Inc.' : 'Inc',
    'Co.' : 'Co'

}


def summarize_text(text, num_sentences, LANGUAGE='english'):
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)

    final_output = []
    for sents in summarizer(parser.document, num_sentences):
        final_output.append(sents._text)
    return final_output

def news_summary_generator(company_name,rtc_code = None,num_articles=8, from_paramter='2019-04-05' ,LANGUAGE = 'english'):
    # takes in company name as only necessary parameter
    # if rtc code known, enter that
    # num_articles denotes number of sentences to return
    # from denotes start date of news search
    # returns a string which is all the sentences -- should change this to a list tbh
    try:
        if rtc_code == None:
            rtc_code = search_company(company_name)
        url = requests.get('https://www.reuters.com/finance/stocks/company-news/'+rtc_code)
        reuters_newsPage = bs(url.text,'html.parser')

        articles = reuters_newsPage.find_all('div',class_ = 'feature')
        headlines = []
        sentences = []

        for arts in articles:
            headlines.append(arts.find_all('h2')[0].text)

            sentences.append(arts.find_all('p')[0].text)
        headlines = '. '.join(headlines)
        sentences = '  '.join(sentences)

        sent_par =  sentences + headlines

        return summarize_text(text = sent_par, num_sentences= 4)




    except IndexError:
        # this will occur more often for private copmanies for which there is no rtc code
        # i'm really using reuters a lot...
        print('We have an Index Error achieved')
        url = requests.get('https://www.reuters.com/search/news?sortBy=&dateRange=&blob='+company_name.replace(' ','+').replace('&','%26'))
        reuters_newsPage = bs(url.text, 'html.parser')
        results = reuters_newsPage.find_all('h3',class_ = 'search-result-title')
        reuters_url = 'https://www.reuters.com'
        final_output = []
        count = 0

        for res in results:

            if count == 3:
                break
            else:
                count += 1
            arts = res.find_all('a', href=True)[0]
            text = ''
            link = reuters_url+arts['href']
            response = requests.get(link)
            website = bs(response.text, 'html.parser')
            article_pars = website.find_all('div',class_ = 'StandardArticleBody_body')[0].find_all('p')
            for pars in article_pars:
                text += pars.text
            z = summarize_text(text = text, num_sentences= 2)
            final_output += summarize_text(text = text, num_sentences= 2)

        return final_output


    except:
        try:
            print('We were unable to get any ouptput from searching the company name')
            newsapi = NewsApiClient('9a2b70eaea5b465ca6f09ee30784eb1f')

            #domains = 'ft.com, bbc.co.uk, cnn.com, msnbc.com, wsj.com,washingtonpost.com, economist.com'
            articles = newsapi.get_everything(q=str(company), page_size=100, language='en',from_param= from_paramter)['articles']
            headlines = []
            description = []

            for arts in articles:
                try:

                    headlines.append(arts['title'])
                    sentences = arts['description'].split('. ')
                    if '..' in sentences[0] or '…' in sentences[0]:
                        continue
                    description.append(sentences[0])
                except:
                    continue
            sentences = '. '.join(description)

            parser = PlaintextParser.from_string(sentences,Tokenizer(LANGUAGE))
            stemmer = Stemmer(LANGUAGE)
            summarizer = Summarizer(stemmer)
            recent_news = []
            for sentence in summarizer(parser.document, 5):
                recent_news.append(sentence._text)
            return recent_news
        except:
            print('unable to retreieve any news - errors reached the entire way')
            return ''



def business_description_generator(company,rtc_code = None, number_sentences=2, LANGUAGE = 'english'):
    # input company name and then get list of relevant business description sentences

    def wikipedia_info_generator(company, number_sentences):
        try:

            # want num sentences ==5 ratio = num sentences / total sentences
            first_sentences = wikipedia.summary(str(company), sentences = 2)
            rest_of_sentences = wikipedia.summary(str(company)).replace(first_sentences,'')
            end_descript = [first_sentences]
            return end_descript + summarize_text(rest_of_sentences, num_sentences =number_sentences )

        except:
            print("Wikipedia doesn't have an article on the company")
            return []

    def reuters_info_generator(rtc_code, number_sentences):
        url = 'https://uk.reuters.com/business/stocks/company-profile/' + rtc_code
        req = requests.get(url)
        description_page = bs(req.text, 'html.parser')
        full_description = description_page.find_all('div',class_ = 'moduleBody')[1]
        if full_description.find('p'):
            paragraph1 = full_description.find_all('p')[0].text
            try:
                paragraph2 = full_description.find_all('p')[2].text
                total_text = paragraph1 + paragraph2
            except:
                total_text = paragraph1
        else:
            total_text = full_description.text

        return summarize_text(total_text, num_sentences= number_sentences+1)
    if rtc_code == 'Private':
        return wikipedia_info_generator(company, number_sentences = 2)
    else:
        try:
            wiki_summary = [wikipedia.summary(str(company), sentences = 2)]
            return wiki_summary + reuters_info_generator(rtc_code = rtc_code, number_sentences= number_sentences)
        except wikipedia.exceptions.PageError:
            return reuters_info_generator(rtc_code = rtc_code, number_sentences= number_sentences + 2)
        except:
            print('unable to get information from Reuters')
            return wikipedia_info_generator(company =company,number_sentences= number_sentences)



