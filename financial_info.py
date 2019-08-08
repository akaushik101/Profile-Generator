import ftplib
import io
import pandas as pd
import requests
import requests_html





from datetime import date, timedelta



# http://theautomatic.net/yahoo_fin-documentation/
# ^^ Yahoo fin documentation, what a beautiful person who created that

from yahoo_fin import stock_info as si

## To Do: find a way to get access to yahoo tickers - then i get access to all companies


def get_key_shareholders(ticker):
    # input is the yahoo ticker
    # returns the top 8 shareholders
    holders = si.get_holders(ticker)
    major_holders = holders['Direct Holders (Forms 3 and 4)'][['Holder','% Out']].iloc[[0,1,2,3,4,5,6]]
    inst_holders = holders['Top Institutional Holders'][['Holder','% Out']].iloc[[0,1,2,3,4,5,6]]
    tot_holders = pd.concat([major_holders,inst_holders],ignore_index= True)
    tot_holders['% Out']= tot_holders['% Out'].apply(lambda num: float(num.strip('%')))
    tot_holders.sort_values(by = '% Out', ascending = False,inplace = True)
    tot_holders['% Out'] = tot_holders['% Out'].apply(lambda num: str(num)+"%")
    return tot_holders.iloc[[0,1,2,3,4,5,6,7]]

get_key_shareholders('AAPL')




def get_quote_table(ticker):
    # this takes in the yahoo ticker and outputs a list of tuples with relevant info
    if not ticker == None:
        #try:
            quote_table = si.get_quote_table(ticker)
            ## this is the data of type float
            eps_ttm = replace_negative_financials(float_adjustment(quote_table['EPS (TTM)'])*1000)  # because float financial divides by 1000
            pe_ttm = str(quote_table['PE Ratio (TTM)'])
            previous_close = str(quote_table['Previous Close'])
            balance_sheet, key_bs_financials = get_balance_sheet(ticker)
            # this is the data of strings
            market_cap = quote_table['Market Cap']
            if market_cap[-1] == 'T':

                market_cap_value = float(market_cap.strip('T')) * (10** 6)
                EV_float = key_bs_financials['LT Debt'] - key_bs_financials['Cash and ST Investments'] + market_cap_value
                EV = str(round(EV_float/(10**6),2))+ 'T'


            elif market_cap[-1] == 'B':
                market_cap_value = float(market_cap.strip('B'))*(10**3)
                EV_float = key_bs_financials['LT Debt'] - key_bs_financials['Cash and ST Investments'] + market_cap_value
                EV = str(round(EV_float / (10 ** 3), 2)) + 'B'
            elif market_cap[-1] == 'M':
                market_cap_value = float(market_cap.strip('M'))
                EV_float = key_bs_financials['LT Debt'] - key_bs_financials['Cash and ST Investments'] + market_cap_value
                EV = str(round(EV_float, 2)) +'M'
            else:
                try:
                    market_cap_value = float(market_cap)
                    EV_float = key_bs_financials['LT Debt'] - key_bs_financials['Cash and ST Investments'] + market_cap_value
                    EV = str(round(EV_float, 2))
                except:
                    print('unable to retrieve float mrkt cap value - returned 0')
                    market_cap_value = 0




            return [("Market Cap",market_cap),('Enterprise Value',EV),('Previous Close',previous_close),('EPS (TTM)',eps_ttm),('PE Ratio (TTM)',pe_ttm)] + balance_sheet
        #except:
        #    print('invalid ticker, unable to retreive quote table')
        #    return []
    else:
        return []

def get_balance_sheet(ticker):
    # takes yahoo ticker and outputs balance sheet info
    if not ticker == None:
        #try:

            balance_sheet = si.get_balance_sheet(ticker)
            balance_sheet.set_index(keys = ['Period Ending'], inplace  = True, drop = True)
            last_year = balance_sheet.columns[0]
            balance_sheet = balance_sheet[last_year]
            ## remember all of this is currently string info -- will need to convert it
            cash_float = float_adjustment(balance_sheet['Cash And Cash Equivalents'])

            ltdebt_float = float_adjustment(balance_sheet['Long Term Debt'])
            ltdebt = replace_negative_financials(float_adjustment(balance_sheet['Long Term Debt'])).replace(' ','')

            st_investments_float = float_adjustment(balance_sheet['Short Term Investments'])

    #       minority_interest = balance_sheet['Minority Interest']
    #       preferred_stock = balance_sheet['Preferred Stock']
            return[('Cash and ST Investments', replace_negative_financials(cash_float +st_investments_float).replace(' ','')+'M'),('Long Term Debt',ltdebt+'M')],{'Cash and ST Investments':cash_float+st_investments_float,'LT Debt':ltdebt_float}
        #except ValueError:
        #    print('Have ticker but unable to return relevant balance sheet information')
    else:
        return []








def get_historic_price(ticker):
    # input should be reuters ticker for british and regular ticker for american
    # returns  series with datetime objects as dates and close price in the column
    # close prices returned
    # alternative input, if I have managed to find it, would equivalently be the yahoo ticker
    today = str(date.today())
    one_year_ago = date.today() - timedelta(days=365)
    data = si.get_data(ticker,start_date= one_year_ago, end_date = today)['close'].round(2)
    return data

def get_financials(ticker):
    # input is yahoo ticker (or reuters ticker for American and British companies)
    # output is a dataframe with 4 trailing financials
    # out is in millions unconditionally at the moment
    income_statement = si.get_income_statement(ticker)
    income_statement.drop([23], inplace  = True)
    income_statement.set_index(keys = ['Revenue'],inplace = True,drop = True)
    income_statement.replace()
    cash_flows = si.get_cash_flow(ticker)
    cash_flows.set_index(keys = ['Period Ending'], inplace = True, drop = True)

    necessary_financials = income_statement.loc[['Total Revenue', 'Gross Profit',
                                       'Earnings Before Interest and Taxes',
                                        'Net Income',
                                       ]].applymap(float_adjustment)
    necessary_financials = necessary_financials.round(decimals = 1)
    necessary_financials.rename(index={
        'Earnings Before Interest and Taxes': 'EBIT',
        'Total Revenue': 'Revenue'
    }, inplace = True)

    ## to do -- enter the metrics

    depreciation = pd.DataFrame(cash_flows.loc[['Depreciation']]).applymap(float_adjustment)




    EBITDA = necessary_financials.loc['EBIT'] + depreciation.loc['Depreciation']
    EBITDA = EBITDA.apply(replace_negative_financials)
    EBITDA.name = 'EBITDA'
    EBIT_Margin = (necessary_financials.loc['EBIT']/ necessary_financials.loc['Revenue']*100)
    EBIT_Margin = EBIT_Margin.apply(replace_negative_percentiles)
    EBIT_Margin.name = 'EBIT Margin'

    Gross_Margin = (necessary_financials.loc['Gross Profit']/necessary_financials.loc['Revenue']*100)
    Gross_Margin = Gross_Margin.apply(replace_negative_percentiles)
    Gross_Margin.name = 'Gross Margin'

    Net_Margin = (necessary_financials.loc['Net Income'] / necessary_financials.loc['Revenue']*100)
    Net_Margin = Net_Margin.apply(replace_negative_percentiles)
    Net_Margin.name = 'Net Margin'

    necessary_financials = necessary_financials.applymap(replace_negative_financials)
    necessary_financials = necessary_financials.append([Gross_Margin,EBITDA,EBIT_Margin,Net_Margin] )
    necessary_financials = necessary_financials.reindex(['Revenue','Gross Profit','Gross Margin',
                                  'EBITDA','EBIT','EBIT Margin','Net Income','Net Margin'])
    return necessary_financials


def float_adjustment(financial):
    if financial == '-':
        return 0
    else:
        return float(financial)/1000

def replace_negative_financials(financial):
    # broader function that replaces negative financials and adds commas
    if financial >= 1000:
        number = (str(round(financial, 1))+" ").partition('.')
        first_number = list(number[0][::-1])
        # it is reversed ^^
        x = ''
        count = 0
        for char in first_number:
            count += 1
            if count == 4:
                x += ','
                count =0
            x += char

        x = x[::-1] + number[1] + number[2]

        return x

    elif financial < 1000 and financial > 0:
        return (str(round(financial, 1))+" ")
    elif financial == 0:
        return('- ')

    elif financial < 0 and financial > -1000:
        num = str(round(financial, 1)).split('-')[1]
        return "(" + num + ')'

    else:
        number = str(round(financial, 1)).split('-')[1].partition('.')
        first_number = list(number[0][::-1])
        x = ''
        count = 0
        for char in first_number:
            count += 1
            if count == 4:
                x += ','
                count =0
            x += char

        x = x[::-1] + number[1] + number[2]
        return "("+x+')'



def replace_negative_percentiles(percentile):
    if percentile >= 0:
        return str(round(percentile,1))+"% "
    else:
        num = str(round(percentile, 1)).split('-')[1]
        return "("+num+"%)"






## IS Items with respective index

"""                                  Revenue
0                            Total Revenue
1                          Cost of Revenue
2                             Gross Profit
3                       Operating Expenses
4                     Research Development
5       Selling General and Administrative
6                            Non Recurring
7                                   Others
8                 Total Operating Expenses
9                 Operating Income or Loss
10       Income from Continuing Operations
11         Total Other Income/Expenses Net
12      Earnings Before Interest and Taxes
13                        Interest Expense
14                       Income Before Tax
15                      Income Tax Expense
16                       Minority Interest
17          Net Income From Continuing Ops
18                    Non-recurring Events
19                 Discontinued Operations
20                     Extraordinary Items
21            Effect Of Accounting Changes
22                             Other Items
23                              Net Income
24                              Net Income
25   Preferred Stock And Other Adjustments
26  Net Income Applicable To Common Shares"""










### This is now deprecated. It pulls data from alphavantage -- use yahoo instead

"""
	def get_historic_price(datatype = 'json',function = 'TIME_SERIES_DAILY', symbol = 'AAPL',outputsize = 'compact', apikey= 'IV0G9V6LPY0NIH1U'):
		# so this works for American companies and for British companies
		# need to find another method for companeis that are from Hong Kong / Tokyo


		def retrieve_data():
			api_url = 'https://www.alphavantage.co/query?function='+function+'&symbol='+ symbol+'&outputsize='+outputsize+'&apikey='+apikey+'&datatype='+datatype

			response = requests.get(api_url)
			if response.status_code == 200:
				return json.loads(response.content.decode('utf-8'))
			else:
				return None
		def convert_datetime(x):

			l = x.split('-')
			return dt(int(l[0]), int(l[1]), int(l[2]))

		## need to figure out how to get trailing 1 year financials from the 'FUll data set' or find a more efficient way
		# to pull the data
		data = retrieve_data()
		key = list(data.keys())[1]
		stock_data = {convert_datetime(key): value for key, value in stock_data.items()}
		return pd.DataFrame.from_dict(stock_data, orient = 'index')['4. close']


"""