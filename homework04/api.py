import requests
import time
import backoff
import config
import random


def get_req(url:str, params={}, timeout=5, max_retries=5, backoff_factor=0.3, MinDelay=0.1, Factor=2.7):
    """ Выполнить GET-запрос
    :param url: адрес, на который необходимо выполнить запрос
    :param params: параметры запроса
    :param timeout: максимальное время ожидания ответа от сервера
    :param max_retries: максимальное число повторных запросов
    :param backoff_factor: коэффициент экспоненциального нарастания задержки
    """

    delay = MinDelay # Начальное время 
    retrise=0 # счетчик выполнения запросов
    while True:
        try:
            if max_retries-retrise==0 and retrise!=0:
                return None
            quest=requests.get(url=url,params=params,timeout=timeout) # запрос
            quest.raise_for_status()
        # проверки ошибок 
        except requests.exceptions.RequestException as e:
            print(e)
            print(delay)
        except requests.exceptions.ReadTimeout as e:
            print(e)
            print(delay)
        except requests.exceptions.ConnectTimeout as e:
            print(e)
            print(delay)
        else:
            return quest.json()
        # вычисляет нормальное распределение
        finally:
            retrise+=1
            time.sleep(delay)
            delay = min(delay * Factor, timeout)
            delay = delay + random.normalvariate(delay,backoff_factor)


def get_friends(user_id:int, fields):
    """ Вернуть данных о друзьях пользователя
    :param user_id: идентификатор пользователя, список друзей которого нужно получить
    :param fields: список полей, которые нужно получить для каждого пользователя
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert isinstance(fields, str), "fields must be string"
    assert user_id > 0, "user_id must be positive integer"
    user_id=str(user_id)
    fields=str(fields)
    config.VK_CONFIG['user_id']=str(user_id)
    if fields!=' ':
        config.VK_CONFIG['fields']=fields
    url=config.VK_CONFIG['url']+'friends.get?'
    return get_req(url,params=config.VK_CONFIG)


def messages_get_history(user_id, offset=0, count=20):
    """ Получить историю переписки с указанным пользователем
    :param user_id: идентификатор пользователя, с которым нужно получить историю переписки
    :param offset: смещение в истории переписки
    :param count: число сообщений, которое нужно получить
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    assert isinstance(offset, int), "offset must be positive integer"
    assert offset >= 0, "user_id must be positive integer"
    assert count >= 0, "user_id must be positive integer"
    # PUT YOUR CODE HERE