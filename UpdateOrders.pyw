import pandas
from snaptrade_client import SnapTrade
import os
import sched
import time
import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
snaptrade = SnapTrade(
consumer_key=os.environ["SNAPTRADE_CONSUMER_KEY"],
client_id=os.environ["SNAPTRADE_CLIENT_ID"])
event_schedule = sched.scheduler(time.time, time.sleep)

    
def main():

def write_active_tables(user_id, user_secret):
    """
    Updates positions from orders in 24 hours
    TODO: fine tune columns updates in active table for analytics & effective trading 
    Params: 
        - user_id: unique id for account
        - user_secret: unique key generated as response when user_id generated
    Returns:
        - xls to current directory
    """
    sheets={}
    for file in os.listdir(dir_path):
        filename = os.fsdecode(file)
        if filename.endswith(".xlsx"): 
            sheets[filename.rstrip("xlsx")] = (pandas.read_excel(os.path.join(dir_path, filename)))
    accounts_response = snaptrade.account_information.list_user_accounts(
        userId=user_id,
        user_secret=user_secret)
    for account in accounts_response:
        orders_response = snaptrade.account_information.get_user_account_recent_orders(
                account_id=account['account_id'],
                user_id=user_id,
                user_secret=user_secret)['orders'] 
        orders = get_account_changes(account, accounts_response, orders_response)
        name = account['name']
        for action in ["BUY", "BUY_SHORT", "SELL"]: 
            sheets[name].loc[sheets['symbol'].isin(orders[slice(None)]['universal_symbol']['symbol'])]['units'] += \
            orders.loc[orders[slice(None)]['universal_symbol']['symbol'].isin(sheets[name]['symbol'])& orders.get_level(1)['action'] == action] \
            .get_level(1)['total_quantity'] * (action == "BUY" or "BUY_SHORT")[-1, 1]  #add or substract order quantity from active table
        sheets[name].drop(sheets[name].loc[sheets[name]['units'] == 0], inplace=True)
        sheets[name].to_excel(f"{dir_path}/{name}active_table{datetime.datetime.now()}")

def get_account_changes(account, accounts_response, orders_response) -> pandas.DataFrame:
    
        orders: pandas.DataFrame = pandas.DataFrame.from_dict({[i][j][k]: orders_response[i][j][k] 
                                                            for i in orders_response
                                                            for j in orders_response[i].keys()
                                                             for k in orders_response[i][j].keys()}, 
                                                            orient='index') 
        contingencies: pandas.DataFrame = orders.loc[orders[slice(None)]['universal_symbol']['symbol'].str.contains('^CONTINGENCY', regex=True)]
        orders.drop(contingencies.get_level_values(0), inplace=True)
        contingencies.to_excel(f"{dir_path}/{accounts_response[account]['name']}_condition_table", index=False)
        return orders

def trigger_account_update():
    """TODO possible to configure script locally to check for changes in fidelity and run?"""

event_schedule.enter(5, 1, write_active_tables(user_id, user_secret)) # run on change of orders table in background
