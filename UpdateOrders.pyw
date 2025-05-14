import pandas
from snaptrade_client import SnapTrade
import os
import sched
import time
import datetime

event_schedule = sched.scheduler(time.time, time.sleep)

def write_active_tables(user_id, user_secret, event_schedule):
    """
    Updates positions from orders in 24 hours
    TODO: define updates for 
    Params: 
        - user_id: unique id for account
        - user_secret: unique key generated as response when user_id generated
    Returns:
        - xls to current directory
    """
    sheets={}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    snaptrade = SnapTrade(
        consumer_key=os.environ["SNAPTRADE_CONSUMER_KEY"],
        client_id=os.environ["SNAPTRADE_CLIENT_ID"])
    
    for file in os.listdir(dir_path):
        filename = os.fsdecode(file)
        if filename.endswith(".xlsx"): 
            sheets[filename.rstrip("xlsx")] = (pandas.read_excel(os.path.join(dir_path, filename)))
    
    accounts_response = snaptrade.account_information.list_user_accounts(
        userId=user_id,
        user_secret=user_secret)
    for account in accounts_response:
        orders_response = snaptrade.account_information.get_user_account_recent_orders(
            account_id=accounts_response[account]['account_id'],
            user_id=user_id,
            user_secret=user_secret)['orders'] 
        orders: pandas.DataFrame = pandas.DataFrame.from_dict({[i][j][k]: orders_response[i][j][k] 
                                              for i in orders_response
                                              for j in orders_response[i].keys()
                                              for k in orders_response[i][j].keys()}, 
                                              orient='index') 
        contingencies: pandas.DataFrame = orders.loc[orders[slice(None)]['universal_symbol']['symbol'].str.contains('^CONTINGENCY', regex=True)]
        orders.drop(contingencies.get_level_values(0), inplace=True)
        contingencies.to_excel(f"{dir_path}/{accounts_response[account]['name']}_condition_table", index=False)
        
            

write_active_tables("", "", "")
    
