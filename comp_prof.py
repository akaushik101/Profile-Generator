from pptx import Presentation
import pandas as pd

import requests
import json
from datetime import datetime as dt

from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

from pptx.enum.chart import XL_TICK_MARK
from pptx.util import Pt

from pptx.enum.chart import XL_CATEGORY_TYPE


class Comp_prof():

	def __init__(self,company,file =  'sample_MA.pptx'):

		# company is the ticker  in string 
		self.presentation = Presentation(file)
		self.company = company

# prof =comp_prof('sample_MA.pptx')


	def run(self,slide_num =0):
		# returns presentation object 

		profile = self.presentation.slides[slide_num]
		company = self.company
		presentation = Comp_prof.insert_key_people(self.presentation, [('Aditya','student','hoping this works')])
		

		presentation = Comp_prof.set_company_name(presentation,company)
		presentation = Comp_prof.insert_business_description(presentation,['wwaaat'])
		presentation = Comp_prof.insert_recent_news(presentation,['this is the nws','things are working'])
		presentation = Comp_prof.add_stock_chart(presentation,company)
		return presentation	


	def find_placeholder_order(profile):
		#  useful for figuring out which placeholder corresponds to which  
		# profile is a comp_prof slide  object
		count =0

		for shapes in profile.shapes:
		    if not shapes.has_text_frame:
		        count += 1
		        continue
		    par = shapes.text_frame.paragraphs[0]
		    par.clear()
		    count += 1
		    par.text = str(count)
		return



    




	def set_company_name(ppt,Company_name):
	    # Company Name is a string which represents the company's name
	    # ppt is the Powerpoint object given. This particular method is build towards the template I've used 
	    # in general, it's imperative to figure out which placeholder indices you want to change
	    
	    
	    slides = ppt.slides[0]
	    title = slides.shapes[0]
	    comp_sub_title = slides.shapes[6]
	    try:
	        title.text = Company_name
	    except:
	        print('something went wrong with title')
	    try:
	        comp_sub_title.text = Company_name
	    except:
	        print('somethign went wrong with subtitle')
	    return ppt






	def insert_key_people(ppt, people):
	    # People is a list of tuples. each tuple contains the person's name, position, and then a description
	    
	    slides = ppt.slides[0]
	    people_box = slides.shapes[8].text_frame
	    
	    # we use 4 because that's the particular text frame we want to go to
	    
	    
	    
	    par = people_box.paragraphs[0]
	    
	    for peeps in people:
	        name = peeps[0]
	        position = peeps[1]
	        description = peeps[2]
	        
	        par.clear()
	        
	        run = par.add_run()
	        
	        run2 = par.add_run()
	        run2.text = position + ': '
	        
	        run3 = par.add_run()
	        run3.text = description 
	        
	        font = run.font
	        font.bold = True 
	        
	        font2 = run2.font
	        font2.underline =True
	        
	        run3 = par.add_run()
	        run.text = name + ' - '
	        par.add_line_break()
	        par = people_box.add_paragraph()
	        
	    return ppt
	        
	        
	    people_box.fit_frame()
	    






	def insert_business_description(ppt, description, slide_num =0):
	    # ppt is the powerpoint we're acting on
	    #slide is the index of the slide we're acting on
	    # description is a list of sentences that describe the business
	    
	    # business description is indexed by placehodler 5 
	    
	    slides = ppt.slides[slide_num]
	    
	    bus_descrip= slides.shapes[7].text_frame
	    
	    bus_descrip.clear()
	    
	    
	    par = bus_descrip.paragraphs[0]
	    

	    
	    for sentences in description:
	        run = par.add_run()
	        run.text = sentences
	        par = bus_descrip.add_paragraph()
	        
	        par.clear()
	        
	    return ppt
	    


	def insert_recent_news(ppt,news,slide_num =0):
	    #ppt is the powerpoint we are editing
	    # slide_num is the slide we want to target 
	    # news is a list of news items
	    slides = ppt.slides[slide_num]
	    
	    news_box= slides.shapes[4].text_frame
	    
	    news_box.clear()
	    
	    
	    par = news_box.paragraphs[0]
	    

	    
	    for sentences in news:
	        run = par.add_run()
	        run.text = sentences
	        par = news_box.add_paragraph()
	        
	        par.clear()
	    return ppt


	# In[384]:

	def get_historic_price(datatype = 'json',function = 'TIME_SERIES_DAILY', symbol = 'AAPL',outputsize = 'compact', apikey= 'IV0G9V6LPY0NIH1U'):
	    def retrieve_data():
	        api_url = 'https://www.alphavantage.co/query?function='+function+'&symbol='+ symbol+'&outputsize='+outputsize+'&apikey='+apikey+'&datatype='+datatype

	        response = requests.get(api_url)

	        if response.status_code == 200:
	            return json.loads(response.content.decode('utf-8'))
	        else:
	            return None
	    data = retrieve_data()
	    key = list(data.keys())[1]
	    stock_data = data[key]
	    
	    
	    
	    
	    def convert_datetime(x):
	        l = x.split('-')
	        return dt(int(l[0]),int(l[1]),int(l[2]))
	    
	    ## need to figure out how to get trailing 1 year financials from the 'FUll data set' or find a more efficient way
	    # to pull the data

	    stock_data = {convert_datetime(key): value for key, value in stock_data.items()}
	    
	    
	    return pd.DataFrame.from_dict(stock_data, orient = 'index')['4. close']
	   
	    






	def add_stock_chart(ppt, company, slide_num =0):
	    # data is a series indexed by date -- dates are all datetime objects! 
	    # company_name is a string of the company's ticker
	    
	    data = Comp_prof.get_historic_price(symbol = company)

	    slide = ppt.slides[slide_num]
	    
	    chart_data = CategoryChartData()

	    chart_data.categories = data.index.tolist()
	    chart_data.add_series(str(company),tuple(data.values.tolist()))
	    
	    
	    ## need to find a way to push the axis labels out -- ie delay the labels starting till a week after the first set of data
	    
	    

	    x, y, cx, cy = Inches(.403), Inches(5.33), Inches(2.22), Inches(1.3)
	    chart = slide.shapes.add_chart(
	        XL_CHART_TYPE.LINE, x, y, cx, cy, chart_data
	    ).chart
	    
	    chart.font.size = Pt(8)
	    chart.font.name = 'Arial'



	  #  chart.value_axis.minimum_scale = (min(data.values.tolist()))
	    
	    date_axis = chart.category_axis
	    date_axis.tick_labels.number_format = 'mmm-yy'
	    date_axis.major_unit = 90
	    chart.has_legend = False
	    chart.show_legend_key = False
	    
	    chart.has_title = False
	    chart.series[0].smooth = True
	    
	    return ppt

		# 3.33 cm by 5.72 cm length x width of desired chart

		#1.04 cm left 13.76 cm top desired location on slide








	
	    
	    
	    
	    def convert_datetime(x):
	        l = x.split('-')
	        return date(int(l[0]),int(l[1]),int(l[2]))
	    
	    ## need to figure out how to get trailing 1 year financials from the 'FUll data set' or find a more efficient way
	    # to pull the data

	    stock_data = {convert_datetime(key): value for key, value in stock_data.items()}
	    
	    
	    return pd.DataFrame.from_dict(stock_data, orient = 'index')['4. close']
	   

