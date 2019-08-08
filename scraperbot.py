from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from bs4 import BeautifulSoup as bs
import requests
from sumy.nlp.tokenizers import Tokenizer





def search_company(company_name):
    # unfortuantely often times RTC codes will not be known. This function allows you to search Reuters and get the RTC code which can be used
    # then for further analysis.
    # this is the 'search' link: https://uk.reuters.com/business/quotes/lookup?searchType=any&comSortBy=marketcap&sortBy=&dateRange=&search=Bank+of+China
    # the end 'search =" + company name

    # if there is no company, just return the erorr. the end functions will catch it

    company_name = company_name.replace(" ","+").replace('&','%26')
    url = "https://uk.reuters.com/business/quotes/lookup?searchType=any&comSortBy=marketcap&sortBy=&dateRange=&search="+company_name

    search_return = requests.get(url)
    search_page = bs(search_return.text, 'html.parser')
    first_result = search_page.find_all('tr', class_ = 'stripe')
    rtc_code = first_result[0].get('onclick').split('=')[-1].split('\'')[0]
    return rtc_code
    #except ValueError:
    #   print('page not returned')



def get_officer_information(rtc):
    #rtc is a string that is the RTC code of the company
    # I need to find a way to convert company to a string that can be read by reuters
    # ie for british companies, there is a .L at the end of hte ticker -- a function that needs to be created)
    # if we can't find the company RTC code via reuters, then we return an empty tuple
    url = "https://www.reuters.com/finance/stocks/company-officers/"
    page = requests.get(url+rtc)
    html_tree = bs(page.text,'html.parser')
    officer_links = []
    for a in html_tree.find_all('a', href=True):
        if a.text and 'officer-profile' in a['href']:
            officer_links.append(a['href'])
    def information_summarizer(description, num_sentences = 1 ,LANGUAGE='english'):
        # this is going to get the key information by just taking the first three sentences of the description
        t = Tokenizer(LANGUAGE)
        sentences = t.to_sentences(description)

        try:
            return ' '.join(list(sentences)[0:num_sentences])
        except:
            # if there are less than 3 sentences
            return ' '.join(list(sentences))

    def retrieve_information(link):
        # this takes a list of links from reuters that go to an officers page
        # returns a list of tuples, each of which has the person's name then a description
        reuters_home = 'https://www.reuters.com'
        count = 0
        people = []

        def find_description(person_page):
            # this scrapes the reuters page and finds the relevant officer information
            # returns the descriptions???
            divs = person_page.find_all('div', class_='moduleBody')

            for dividers in divs:
                par = dividers.find_all('p')
                for paragraphs in par:
                    x = paragraphs.next


            try:
                return x.split("\n\t")[1]
            except:
                return 'No Information Found'



        # people should be a tuple of first name,last name and then a description
        for urls in link:
            if count == 3:
                return people
            req = requests.get(reuters_home+urls)
            person_page = bs(req.text, 'html.parser')
            name_response = person_page.find_all('h2',class_ = 'module-no-margin')[0].text
            names = name_response[2:-1].split(',')
            name = names[1] + "  " + names[0]
            description = find_description(person_page)
            description = information_summarizer(description, num_sentences= 2)
            count +=1
            people.append((name,description))

        return people




    return retrieve_information(officer_links)
