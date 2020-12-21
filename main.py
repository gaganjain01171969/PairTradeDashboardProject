#!/usr/bin/env python
# added code to avoid Tkinter errors
import matplotlib
from flask import Flask, render_template, request, Markup

matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io, base64, os
import pandas as pd
# !sudo pip3 install wikipedia
import wikipedia
import requests
from requests.exceptions import HTTPError

from input import read_input_json, read_input_stocks, read_input_symbol, read_input_closeDates, read_input_name
# default traveler constants
DEFAULT_BUDGET = 10000
TRADING_DAYS_LOOP_BACK = 90
INDEX_SYMBOL = ['^DJI']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# global variables
stock_close_dates = []
stock_symbols = []
stock_names = []
stock_record_list = []
original_stock_names = []
original_stock_symbols = []
original_stock_close_dates = []
selIdx = 0
long_symbol = "None"
short_symbol = "None"
MAX_STOCKS = 12
app = Flask(__name__)

stock_close_dates = []
stock_symbols = []
stock_names = []
stock_record_list = []
original_stock_names = []
original_stock_symbols = []
original_stock_close_dates = []
selIdx = 0
long_symbol = "None"
short_symbol = "None"

def init_global_vars():
    global stock_close_dates, stock_symbols, stock_names, stock_record_list, original_stock_names, original_stock_symbols, original_stock_close_dates, selIdx, long_symbol, short_symbol

    stock_close_dates = []
    stock_symbols = []
    stock_names = []
    stock_record_list = []
    original_stock_names = []
    original_stock_symbols = []
    original_stock_close_dates = []
    selIdx = 0
    long_symbol = "None"
    short_symbol = "None"

def load_stocks(close_date):
    global stock_symbols, stock_record_list, stock_close_dates, symbols_close_dates, stock_names, original_stock_symbols, original_stock_close_dates, original_stock_names
    filtered_stock_symbols = []
    filtered_stock_names = []
    filtered_stock_close_dates = []
    stock_list_json = read_input_json('input.json')
    stock_record_list = read_input_stocks(stock_list_json)
    
    for symbol in original_stock_symbols:
        try:
            if (close_date not in ['None', 'All'] and original_stock_close_dates[original_stock_symbols.index(symbol)].index(close_date)):
                    filtered_stock_symbols.append(symbol)
                    close_dates = original_stock_close_dates[original_stock_symbols.index(symbol)]
                    filtered_stock_close_dates.append(close_dates)
                    name = original_stock_names[original_stock_symbols.index(symbol)]
                    filtered_stock_names.append(name)
            else:
                continue
            
        except ValueError as ve:
            continue

    if close_date == 'All':     
        x = range(MAX_STOCKS)
        stock_close_dates = []
        stock_symbols = []
        stock_names = []
        
        for i in x:    
            symbol = read_input_symbol(stock_record_list, i)      
            stock_symbols.append(symbol)
            close_dates = read_input_closeDates(stock_record_list, i)
            stock_close_dates.append(close_dates)
            name = read_input_name(stock_record_list, i)
            stock_names.append(name) 
            filtered_stock_symbols = None
            filtered_stock_names = None
            filtered_stock_close_dates = None

    if filtered_stock_symbols:
        stock_symbols = filtered_stock_symbols
        
    if filtered_stock_names:
        stock_names = filtered_stock_names

    if filtered_stock_close_dates:
        stock_close_dates = filtered_stock_close_dates
       
    if close_date == 'All':
        original_stock_close_dates = stock_close_dates
        original_stock_names = stock_names
        original_stock_symbols = stock_symbols
 
    if close_date == 'None':
        stock_close_dates = original_stock_close_dates
        stock_names = original_stock_names
        stock_symbols = original_stock_symbols

def prepare_pivot_market_data_frame(close_date):
    global stock_symbols
    load_stocks(close_date)
    # prep data
    # loop through each stock and load csv
    all_symbols = []
    stock_data_list = []
    
    try:
        if INDEX_SYMBOL in stock_symbols:
            all_symbols = stock_symbols
        else:
            all_symbols = INDEX_SYMBOL + stock_symbols
    except ValueError as vr:
        all_symbols = stock_symbols
    
    for stock in all_symbols:
        try:
            src = os.path.join(BASE_DIR, stock + '.csv')
            tmp = pd.read_csv(src)
            tmp['Symbol'] = stock
            tmp = tmp[['Symbol', 'Date', 'Adj Close']]
            stock_data_list.append(tmp)           
        except Exception as err:
            print(f'error occurred: {err}')
            print("Error: " + str(err) + " occurred!")
    stock_data = pd.concat(stock_data_list)
    stock_data = stock_data.pivot('Date','Symbol')
    stock_data.columns = stock_data.columns.droplevel()
    stock_data.index = pd.to_datetime(stock_data.index)
    stock_data = stock_data.tail(90)            

    return (stock_data)

stock_company_info_amex = None  
stock_company_info_nasdaq = None 
stock_company_info_nyse = None
def load_companylist_files():
    global stock_company_info_amex, stock_company_info_nasdaq, stock_company_info_nyse
    stock_company_info_amex = pd.read_csv(os.path.join(BASE_DIR, 'companylist_AMEX.csv'))
    stock_company_info_nasdaq = pd.read_csv(os.path.join(BASE_DIR, 'companylist_NASDAQ.csv'))
    stock_company_info_nyse = pd.read_csv(os.path.join(BASE_DIR, 'companylist_NYSE.csv'))

def GetCorollaryCompanyInfo(symbol):
    CompanyName = "No company name"
    Sector = "No sector"
    Industry = "No industry"
    MarketCap = "No market cap"

    if (symbol in list(stock_company_info_nasdaq['Symbol'])):
        data_row = stock_company_info_nasdaq[stock_company_info_nasdaq['Symbol'] == symbol]  
        CompanyName = data_row['Name'].values[0]
        Sector = data_row['Sector'].values[0]
        Industry = data_row['industry'].values[0]
        MarketCap = data_row['MarketCap'].values[0]
        
    elif (symbol in list(stock_company_info_amex['Symbol'])):
        data_row = stock_company_info_amex[stock_company_info_amex['Symbol'] == symbol]  
        CompanyName = data_row['Name'].values[0]
        Sector = data_row['Sector'].values[0]
        Industry = data_row['industry'].values[0]
        MarketCap = data_row['MarketCap'].values[0]
 
    elif (symbol in list(stock_company_info_nyse['Symbol'])):
        data_row = stock_company_info_nyse[stock_company_info_nyse['Symbol'] == symbol]  
        CompanyName = data_row['Name'].values[0]
        Sector = data_row['Sector'].values[0]
        Industry = data_row['industry'].values[0]
        MarketCap = data_row['MarketCap'].values[0]
 
    return (CompanyName, Sector, Industry, MarketCap)


def GetWikipediaIntro(company_name):
    description = ""
    try:
        description = wikipedia.page(company_name).content
    except wikipedia.exceptions.PageError as e:
        print(e)
    return(description.split('\n')[0])
 

def GetFinVizLink(symbol):
    return(r'http://finviz.com/quote.ashx?t={}'.format(symbol.lower()))

# period1=1507766400&period2=1539302400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true
def GetStockHistoryPrices(symbol, frequency):
    str_yahoo = fr'https://finance.yahoo.com/quote/{symbol.upper()}'
    str_history = r'/history?t={}&interval={}&frequency={}'.format(symbol.upper(), frequency, frequency)
    return str_yahoo + str_history

@app.before_first_request
def startup():
    #global stock_data_df
    # prepare pair trading data
    #stock_data_df = prepare_pivot_market_data_frame('All')
    load_stocks('All')
    load_companylist_files()

def generate_chart_plot(temp_series, market_data, sym, title):
    fig, ax = plt.subplots()
    ax.plot(temp_series.index, market_data)
    plt.suptitle(title + sym)

    # rotate dates
    myLocator = mticker.MultipleLocator(2)
    myLocator.MAXTICKS = 10000
    ax.xaxis.set_major_locator(myLocator)
    fig.autofmt_xdate()

    # fix label to only show first and last date
    labels = ['' for item in ax.get_xticklabels()]
    labels[1] = temp_series.index[0]

    labels[-2] = temp_series.index[-1]
    ax.set_xticklabels(labels)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    chart_plot = Markup(
        '<img style="padding:1px; border:1px solid #021a40; width: 80%; height: 300px" src="data:image/png;base64,{}">'.format(
            plot_url))

    return chart_plot

def generate_chart_diff_plot(temp_series2, diff, long_sym, short_sym):
    # DIFFERENCE PLOT
    fig, ax = plt.subplots()
    ax.plot(temp_series2.index, diff)
    # add zero line
    ax.axhline(y=0, color='green', linestyle='-')
    plt.suptitle(short_sym + " Minus " + long_sym + '\n(Overly Bullish Minus Overly Bearish)')

    # rotate dates
    myLocator = mticker.MultipleLocator(2)
    myLocator.MAXTICKS = 10000
    ax.xaxis.set_major_locator(myLocator)
    fig.autofmt_xdate()

    # fix label to only show first and last date
    labels = ['' for item in ax.get_xticklabels()]
    labels[1] = temp_series2.index[0]

    labels[-2] = temp_series2.index[-1]
    ax.set_xticklabels(labels)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    chart_diff_plot = Markup(
        '<img style="padding:1px; border:1px solid #021a40; width: 80%; height: 300px" src="data:image/png;base64,{}">'.format(
            plot_url))

    return chart_diff_plot

@app.route("/", methods=['POST', 'GET'])
def get_pair_trade():
    global selIdx, long_symbol, short_symbol
    selected_close_dt = stock_close_dates[0]
    if request.method == 'POST':
        selected_close_dt = request.form['selected_close_dt']
        if selected_close_dt == '':
            selected_close_dt = 'None'
        elif request.form['submit'] == 'restart':
            selected_close_dt = 'All'
            selIdx = 0
            init_global_vars()
        else:
            selIdx = stock_close_dates[0].index(selected_close_dt)            
       # prepare pair trading data
        stock_data_df = prepare_pivot_market_data_frame(selected_close_dt)
        load_companylist_files()

        selected_budget = request.form['selected_budget']
        # make sure the field isn't blank
        if selected_budget == '':
            selected_budget = 10000
            
        # calculate widest spread
        stock1 = '^DJI'
        last_distance_from_index = {}
        temp_series1 = stock_data_df[stock1].pct_change().cumsum()
        for stock2 in list(stock_data_df):
            # no need to process itself
            if (stock2 != stock1):
                temp_series2 = stock_data_df[stock2].pct_change().cumsum()
                # we are subtracting the stock minus the index, if stock is strong compared
                # to index, we assume a postive value
                diff = list(temp_series2 - temp_series1)
                last_distance_from_index[stock2] = diff[-1]

        weakest_symbol = min(last_distance_from_index.items(), key=lambda x: x[1])
        strongest_symbol = max(last_distance_from_index.items(), key=lambda x: x[1])

        # budget trade size
        short_symbol = stock_symbols[stock_symbols.index(strongest_symbol[0])]
        short_last_close = stock_data_df[strongest_symbol[0]][-1]
        short_market_data = stock_data_df[short_symbol].pct_change().cumsum()

        long_symbol = stock_symbols[stock_symbols.index(weakest_symbol[0])]
        long_last_close = stock_data_df[weakest_symbol[0]][-1]
        long_market_data = stock_data_df[long_symbol].pct_change().cumsum()

        if request.form['submit'] in ['calculate_trade', 'restart']:
            # get fundamental data from company list
            short_CompanyName, short_Sector, short_Industry, short_MarketCap = GetCorollaryCompanyInfo(short_symbol)
            long_CompanyName, long_Sector, long_Industry, long_MarketCap = GetCorollaryCompanyInfo(long_symbol)

            # get wikipedia intro
            short_intro = GetWikipediaIntro(short_CompanyName)
            long_intro = GetWikipediaIntro(long_CompanyName)

            # build finwiz jump link
            short_finviz = GetFinVizLink(short_symbol)
            long_finviz = GetFinVizLink(long_symbol)
            frequency = "1wk"
            short_history_prices = GetStockHistoryPrices(short_symbol, frequency)
            long_history_prices = GetStockHistoryPrices(long_symbol, frequency)

            # build three charts
            # WEAK SYMBOL - GO LONG
            title = 'Overly Bearish - Buy: '
            chart1_plot = generate_chart_plot(temp_series1, long_market_data, long_symbol, title)
            # STRONG SYMBOL - GO SHORT
            title = 'Overly Bullish - Sell: '
            chart2_plot = generate_chart_plot(temp_series2, short_market_data, short_symbol, title)
            chart_diff_plot = generate_chart_diff_plot(temp_series2, diff, long_symbol, short_symbol)


            return render_template('index.html',
                short_symbol = short_symbol,
                long_symbol = long_symbol,
                short_last_close = round(short_last_close,2),
                short_size = round((float(selected_budget) * 0.5) / short_last_close,2),
                long_last_close = round(long_last_close,2),
                long_size = round((float(selected_budget) * 0.5) / long_last_close,2),
                selected_budget = selected_budget, 
                selected_stock_names = stock_names,
                selected_stock_symbols = stock_symbols,
                selIdx = selIdx,
                selected_close_dt = stock_close_dates[0], 
                short_CompanyName = short_CompanyName, 
                short_Sector = short_Sector, 
                short_Industry = short_Industry, 
                short_MarketCap = short_MarketCap,
                short_intro = short_intro,
                short_finviz = short_finviz,
                short_history_prices=short_history_prices,
                long_CompanyName = long_CompanyName,
                long_Sector = long_Sector, 
                long_Industry = long_Industry, 
                long_MarketCap = long_MarketCap,
                long_intro = long_intro,
                long_finviz = long_finviz,
                long_history_prices=long_history_prices,
                chart1_plot=chart1_plot,
                chart2_plot=chart2_plot,
                chart_diff_plot=chart_diff_plot)
        elif request.form['submit'] == 'view_fundamentals':

            # get fundamental data from company list
            short_CompanyName, short_Sector, short_Industry, short_MarketCap = GetCorollaryCompanyInfo(short_symbol)
            long_CompanyName, long_Sector, long_Industry, long_MarketCap = GetCorollaryCompanyInfo(long_symbol)

            # get wikipedia intro
            short_intro = GetWikipediaIntro(short_CompanyName)
            long_intro = GetWikipediaIntro(long_CompanyName)

            # build finwiz jump link
            short_finviz = GetFinVizLink(short_symbol)
            long_finviz = GetFinVizLink(long_symbol)

            return render_template('fundamentals.html',
                short_symbol = short_symbol,
                short_CompanyName = short_CompanyName, 
                short_Sector = short_Sector, 
                short_Industry = short_Industry, 
                short_MarketCap = short_MarketCap,
                short_intro = short_intro,
                short_finviz = short_finviz,
                long_symbol = long_symbol,
                long_CompanyName = long_CompanyName, 
                long_Sector = long_Sector, 
                long_Industry = long_Industry, 
                long_MarketCap = long_MarketCap,
                long_intro = long_intro,
                long_finviz = long_finviz)
        elif request.form['submit'] == 'view_price_history':
            # get fundamental data from company list
            short_CompanyName, short_Sector, short_Industry, short_MarketCap = GetCorollaryCompanyInfo(short_symbol)
            long_CompanyName, long_Sector, long_Industry, long_MarketCap = GetCorollaryCompanyInfo(long_symbol)

            # get wikipedia intro
            short_intro = GetWikipediaIntro(short_CompanyName)
            long_intro = GetWikipediaIntro(long_CompanyName)

            # build finwiz jump link
            short_finviz = GetFinVizLink(short_symbol)
            long_finviz = GetFinVizLink(long_symbol)
            frequency = "1d"
            short_history_prices = GetStockHistoryPrices(short_symbol, frequency)
            long_history_prices = GetStockHistoryPrices(long_symbol, frequency)

            return render_template('fundamentals_prices.html',
                                   short_symbol=short_symbol,
                                   short_CompanyName=short_CompanyName,
                                   short_Sector=short_Sector,
                                   short_Industry=short_Industry,
                                   short_MarketCap=short_MarketCap,
                                   short_intro=short_intro,
                                   short_finviz=short_finviz,
                                   short_history_prices = short_history_prices,
                                   long_symbol=long_symbol,
                                   long_CompanyName=long_CompanyName,
                                   long_Sector=long_Sector,
                                   long_Industry=long_Industry,
                                   long_MarketCap=long_MarketCap,
                                   long_intro=long_intro,
                                   long_finviz=long_finviz,
                                   long_history_prices = long_history_prices)
        elif request.form['submit'] == 'view_charts':
            # build three charts
            # WEAK SYMBOL - GO LONG
            title = 'Overly Bearish - Buy: '
            chart1_plot = generate_chart_plot(temp_series1, long_market_data, long_symbol, title)
            # STRONG SYMBOL - GO SHORT
            title = 'Overly Bullish - Sell: '
            chart2_plot = generate_chart_plot(temp_series2, short_market_data, short_symbol, title)
            chart_diff_plot = generate_chart_diff_plot(temp_series2, diff, long_symbol, short_symbol)
            return render_template('charts.html',
                chart1_plot = chart1_plot,
                chart2_plot = chart2_plot,
                chart_diff_plot = chart_diff_plot,
                short_symbol = short_symbol,
                long_symbol = long_symbol,
                short_last_close = round(short_last_close,2),
                short_size = round((float(selected_budget) * 0.5) / short_last_close,2),
                long_last_close = round(long_last_close,2),
                long_size = round((float(selected_budget) * 0.5) / long_last_close,2),
                selected_budget = selected_budget)          
        else:
            selIdx = 0
            short_symbol = "None"
            long_symbol = "None"
            # set default settings
            return render_template('index.html',
                short_symbol = short_symbol,
                long_symbol = long_symbol,
                short_last_close = 0,
                short_size = 0,
                long_last_close = 0,
                long_size = 0,
                selected_budget = DEFAULT_BUDGET,
                selected_stock_names = stock_names,
                selected_stock_symbols = stock_symbols,
                selIdx = selIdx,
                selected_close_dt = stock_close_dates[0])
    else:
        # set default settings
        return render_template('index.html',
            short_symbol = short_symbol,
            long_symbol = long_symbol,
            short_last_close = 0,
            short_size = 0,
            long_last_close = 0,
            long_size = 0,
            selected_budget = DEFAULT_BUDGET,
            selected_stock_names = stock_names,
            selected_stock_symbols = stock_symbols,
            selIdx = selIdx,
            selected_close_dt = stock_close_dates[0])

if __name__=='__main__':
    app.run(debug=True)
