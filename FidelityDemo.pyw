import pandas
from snaptrade_client import SnapTrade
import os
import sched
import time
import datetime

"""
A simple demo that gets active table for each account linked to UserID and saves them as xls.
Set up to run as a background process for real-time updates. Data through api is cached and updated daily by default.
User_id, user_secret can be found via other api call. API available on https://docs.snaptrade.com/docs/getting-started
API gets will fail by default! User_id and user secret to be entered manually.
For on demand updates, will need to use manual refresh for $0.05 per call: 
https://docs.snaptrade.com/reference/Connections/Connections_refreshBrokerageAuthorization
https://api.snaptrade.com/api/v1/accounts/{accountId}/recentOrders (realtime endpoint for last 24 hours orders)

"""
update = datetime.time(16, 0)

event_schedule = sched.scheduler(time.time, time.sleep)

def write_active_tables(user_id, user_secret, event_schedule):
    """
    Writes positions for all connected accounts to xls
    Params: 
        - user_id: unique id for account
        - user_secret: unique key generated as response when user_id generated
    Returns:
        - xls to current directory
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))

    snaptrade = SnapTrade(
        consumer_key=os.environ["SNAPTRADE_CONSUMER_KEY"],
        client_id=os.environ["SNAPTRADE_CLIENT_ID"],
    )

    accounts_response = snaptrade.account_information.list_user_accounts(
        userId=user_id,
        user_secret=user_secret)

    for account in accounts_response:
        positions_response = snaptrade.account_information.get_user_positions(
        account_id=accounts_response[account]['account_id'],
        user_id=user_id,
        user_secret=user_secret)
        sheet = pandas.read_json(positions_response)
        sheet.to_excel(f"{dir_path}/{accounts_response[account]['name']}active_table")
    event_schedule.enterabs(update, 1, write_active_tables) #schedules to run at 4pm


event_schedule.enterabs(update, 1, write_active_tables(user_id, user_secret, event_schedule)) #schedules to run at 4pm
#scheduling can be easily changed to update at interval, but this is redundant without manual refresh of account caching
