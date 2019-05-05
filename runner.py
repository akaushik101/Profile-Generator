from comp_prof import Comp_prof
import subprocess
from time import sleep
#ticker  = input('Give a ticker -- EXCHANGE:COMPANY_TICKER')
#company = input('Give the company name ')
def run(ticker = '', company=''):
    prof = Comp_prof(ticker = ticker,company = company)


    prof.presentation = prof.run()
    prof.presentation.save(str(company)+'.pptx')
    FileName = "/Users/adityakaushik/"+str(company)+".pptx"
    # figure out where the file is actually being saved with the exe -- this is the location where you want to open from!


    subprocess.call(['open',FileName])

    sleep(10)

    subprocess.call(['rm',FileName])


#if __name__ == 'main':
 #   run(ticker,company)