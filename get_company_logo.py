import requests

def get_company_logo(company_name):
    # saves this file in the directory
    z = company_name
    if 'Inc' in company_name:
        company_name = company_name.replace('Inc','')
    elif 'inc' in company_name:
        company_name = company_name.replace('inc','')
    company_name = company_name.replace(' ','')
    url = 'https://logo.clearbit.com/' + company_name
    url_endings = ['.com','.co.uk','.de','.es','.fr','.in']
    for endings in url_endings:
        response = requests.get(url + endings, stream = True)
        print(response.status_code)
        if response.status_code == 200:
            with open(z+'.png', 'wb') as handle:
                for block in response.iter_content(1024):
                    handle.write(block)
            break