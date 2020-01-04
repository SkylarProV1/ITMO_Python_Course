import time
from statistics import median
from typing import Optional

from api import get_friends
from api_models import User


def age_predict(user_id: int) -> Optional[float]:
    """ Наивный прогноз возраста по возрасту друзей
    Возраст считается как медиана среди возраста всех друзей пользователя
    :param user_id: идентификатор пользователя
    :return: медианный возраст пользователя
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    now_year=time.localtime().tm_year
    friend_list=get_friends(user_id,fields='bdate') # получили список друзей для указанного пользователя
    # отсеиваем нужную информацию
    friend_list=friend_list.get('response')['items']
    born_frind=[date.get('bdate') for date in friend_list]
    count=0
    valueborn=0
    for date in born_frind:
    	if date!=None and len(date.split('.'))==3:
    		count+=1
    		valueborn+=int(now_year)-int(date.split('.')[2])
    if count!=0:
    	return valueborn/count
    else:
    	return None
if __name__=='__main__':
    try:
        age=int(input('Введите ваш id: '))
        print(age_predict(age))
    except ValueError:
        print('Введите корректное значение')
 




    



