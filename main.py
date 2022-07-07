import nicehash, threading, sys, time, requests, logging, json
from threading import Timer
from datetime import datetime
from os import system, path, name

current_path = path.dirname(path.realpath(__file__))
logger_info = logging.getLogger('INFO')
logger_info.setLevel(logging.INFO)
handler_info = logging.FileHandler(path.join(current_path, 'info.log'), 'a' , encoding ='utf-8')
logger_info.addHandler(handler_info)

# logger_err = logging.getLogger('ERROR')
# logger_err.setLevel(logging.DEBUG)
# handler_err = logging.FileHandler(path.join(current_path, 'error.log'), 'w' , encoding ='utf-8')
# logger_err.addHandler(handler_err)

def cls():
    system('cls' if name=='nt' else 'clear')

def date_str():
    now = datetime.now()
    return now.strftime("%m/%d/%Y, %H:%M:%S")

def send_telegram(msg: str):
    try:
        requests.get(f'https://api.telegram.org/bot{token}/sendMessage', params=dict(
        chat_id=channel_id,
        text=msg))
    except:
        print(f'[E] Error send telegram.')

def alive_order(server, algo):
    json_my_order = private_api.get_my_active_orders(algo, 'true', server, 4)
    app_json = json.dumps(json_my_order, sort_keys=True, indent = 4)
    obj = json.loads(app_json)
    
    if len(obj['list']) == 0: 
        return None, None, None, None
    alive = obj['list'][0]['alive']
    id = obj['list'][0]['id']
    speed = obj['list'][0]['acceptedCurrentSpeed']
    return obj, alive, id, speed

def delete_order(id):
    logger_info.info(f'Удаление ордера {id}')
    send_telegram(f'Удаление ордера {id}')
    print(f'Удаление ордера {id}')
    return private_api.cancel_hashpower_order(id)

def pool_order(algo):
    json_my_pool = private_api.get_my_pools(0, 10, algo)
    app_json = json.dumps(json_my_pool, sort_keys=True, indent = 4)
    obj = json.loads(app_json)
    pool = obj['list'][0]['id']
    return pool
    
def info(algo):
    inf = public_api.buy_info()
    for item in inf['miningAlgorithms']:
        if item['name'].lower() == algo.lower():
            return item['min_price'],item['max_price'],item['min_amount']

def recomende_price(server,algo):
    res = public_api.get_hashpower_price(server,algo)
    return res['price']

def book_order(server):
    book = private_api.get_hashpower_orderbook(algo)
    price = book['stats'][server]['orders'][0]['price']
    totalSpeed = book['stats'][server]['totalSpeed']
    return price, totalSpeed

def calc_optimal_price(server,algo):
    optimal_price = 0
    book_price = 0
    tmp_price = 0
    tmp_amount = 0
    optimal_price = float(recomende_price(server, algo))
    book_price, totalSpeed = book_order(server)
    tmp_price = round(((optimal_price + float(book_price)) / 2),3)
    tmp_amount = round((tmp_price / 24 / 60 * minute * limit),3)
    tmp_server = ''
    for server_ in server_list:
        book_price, totalSpeed = book_order(server_)
        if float(totalSpeed) < limit: continue
        optimal_price = float(recomende_price(server_, algo))
        price = round(((optimal_price + float(book_price)) / 2),3)
        amount = round((price / 24 / 60 * minute * limit),3)
        if price < tmp_price:
            tmp_amount = amount
            tmp_price = price
            tmp_server = server_
    if tmp_server == '': tmp_server = server
    return tmp_server, tmp_price, tmp_amount

if __name__ == "__main__":
    cls()
    #----------------- Telegram -------------------------------------------------------
    version = 'NaiceHash bot 1.9'
    token = '5303833410:AAHYtEsd_YgEJ7i09sPcHFHMM735JC4MwQ'
    channel_id = '@btcsearch'
    #---------- REAL ------------------------------------------------------------------
    # host = 'https://api2.nicehash.com'
    # organisation_id = 'e802e983-94d8-4c8f-b33c-7a1af64fd61e'
    # key = '8495bd76-c607-4165-9c81-d26a71d19957'
    # secret = '347345b7-cfdf-439a-b530-6a5995f344365381d47c-c56c-467a-b100-e743c926acc7'
    #--------- Test ---------------
    host = 'https://api-test.nicehash.com'
    organisation_id = '7e5deba0-46ed-4ed0-b0c4-1d606c472e3d'
    key = 'b334318e-6446-46db-a277-af2c1b42cd5b'
    secret = '2b6fe4ef-5f92-4b11-958b-c3a7a6fd57e0e4bfb401-9d89-44cc-bd16-58f1a250c1cb'
    #-----------------------------------------------------------------------------------
    server = 'EU' # server
    server_list = ["EU","USA","EU_N","USA_E"]
    algo = 'DAGGERHASHIMOTO' #'DAGGERHASHIMOTO'#'EQUIHASH'#'SCRYPT'#'GRINCUCKATOO31'
    type_order = 'STANDARD'
    limit = 2 # Сколько TH нужно
    minute = 10 # Сколько минут должен отработать
    check_order = True
    up_order = True
    order = True
    first = True
    print('-'*70)
    print(f'Старт программы: {date_str()}')
    print(f'Версия {version}')
    print(f'Разработчик @Noname400')
    print('-'*70)
    send_telegram(f'{date_str()} Bot NiceHash {version} RUN ...')
    logger_info.info(f'{date_str()} Bot NiceHash {version} RUN ...')
    
    private_api = nicehash.private_api(host, organisation_id, key, secret, True)
    public_api = nicehash.public_api(host, True)
    algorithms = public_api.get_algorithms()
    pool_id = pool_order(algo) # получаем id пула
    server, price, amount = calc_optimal_price(server,algo) # выбираем лучшую цену на серверах
    print(f'Сервер: {server}')
    print(f'Алгоритм: {algo}')
    print(f'Тип ордера: {type_order}')
    print(f'Pool ID: {pool_id}')
    print(f'Цена (BTC/TH/day {price}: {price}')
    print(f'Требуемая скорость: {limit}')
    print(f'Сумма BTC: {amount}')
    print('-'*70)
    print(f'Проверяем существующие ордера по алгоритму {algo}...')
    logger_info.info(f'Проверяем существующие ордера по алгоритму {algo}...')
    
    obj, alive, id, speed = alive_order(server, algo) #есть ордер или нет

    while True:
        check_order = alive
        while check_order != False:
            obj, alive, id, speed = alive_order(server, algo) #есть ордер или нет
            if alive == True: 
                print(f'Ордер {id} в работе.')
                time.sleep(10)
            else: 
                print(f'Ордер {id} закончил работу...')
                send_telegram(f'{date_str()} Ордер {id} закончил работу...')
                logger_info.info(f'{date_str()} Ордер {id} закончил работу...')
                check_order = False
                
        if first == False:
            server, price, amount = calc_optimal_price(server,algo)
            first = False
        print(f'{date_str()} Cоздаем ордер... {server} {type_order} {algo} {pool_id}')
        send_telegram(f'{date_str()} Cоздаем ордер... {server} {type_order} {algo} {pool_id}')
        logger_info.info(f'{date_str()} Cоздаем ордер... {server} {type_order} {algo} {pool_id}')
        new_order = private_api.create_hashpower_order(server, type_order, algo, price, limit, amount, pool_id, algorithms)
        
        while up_order != False: 
            time.sleep(10)
            obj, alive, id, speed = alive_order(server, algo)
            print(f'Текущая скорость: {speed}')
            if float(speed) < limit:
                price = round(price+0.01,3)
                private_api.set_price_hashpower_order(id, price, algo, algorithms)
                print(f'{date_str()} Скорость набрана {speed}. поднимаем цену на 0,01.')
                send_telegram(f'{date_str()} Скорость набрана {speed}. поднимаем цену на 0,01.')
                logger_info.info(f'{date_str()} Скорость набрана {speed}. поднимаем цену на 0,01.')
            else: up_order = False
            
        print(f'{date_str()} Ордер достиг скорости {speed}. Через 1 час перезапуск...')
        send_telegram(f'{date_str()} Ордер достиг скорости {speed}. Через 1 час перезапуск...')
        logger_info.info(f'{date_str()} Ордер достиг скорости {speed}. Через 1 час перезапуск...')
        time.sleep(3600)

