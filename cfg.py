import configparser

FROM_ACCOUNT = ""
PORT = 8088
SINGLE_GET_TOKEN_AMOUNT = 200
TOTAL_GET_TOKEN_AMOUNT_PER_IP_24H = 6000
TOTAL_GET_TOKEN_COUNT_PER_ACCOUNT_24H = 5


def load_cfg():
    global FROM_ACCOUNT
    global PORT
    global SINGLE_GET_TOKEN_AMOUNT
    global TOTAL_GET_TOKEN_AMOUNT_PER_IP_24H
    global TOTAL_GET_TOKEN_COUNT_PER_ACCOUNT_24H

    cf = configparser.ConfigParser()
    cf.read('./config.ini')
    FROM_ACCOUNT = cf.get('global', 'FROM_ACCOUNT')
    PORT = cf.getint('global', 'PORT')
    SINGLE_GET_TOKEN_AMOUNT = cf.getint('global', 'SINGLE_GET_TOKEN_AMOUNT')
    TOTAL_GET_TOKEN_AMOUNT_PER_IP_24H = cf.getint('global', 'TOTAL_GET_TOKEN_AMOUNT_PER_IP_24H')
    TOTAL_GET_TOKEN_COUNT_PER_ACCOUNT_24H = cf.getint('global', 'TOTAL_GET_TOKEN_COUNT_PER_ACCOUNT_24H')