import requests
import config
import telebot
from bs4 import BeautifulSoup
from typing import List,Tuple
from telebot import apihelper
from telebot import types
# доп файлы
import start
#время
from datetime import date
import calendar
import time

# access_token = put token
apihelper.proxy = {'https': 'https://45.77.24.239:3128'}
bot = telebot.TeleBot(access_token)

def get_page(group: str, week: str='') -> str:
    dom = 'http://www.ifmo.ru/ru/schedule'
    if week == '0':
        week=''
    if week:
        week = str(week) + '/'
    url = '{domain}/0/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(
        domain=dom,
        week=week,
        group=group)
    response = requests.get(url)
    web_page = response.text
    return web_page
 
def parse_schedule_for_a_monday(day:str,week:str,low_group:str,web_page: str) -> Tuple[List[str], List[str], List[str]]:

    day_dict={'monday': 1,'tuesday':2,'wednesday':3,'thursday':4,'friday':5,'saturday':6,'sunday':7}
    if week == '1':
        if start.Full_group.get(low_group)[day_dict.get(day)][3]!='':
            times_list = start.Full_group.get(low_group)[day_dict.get(day)][0]
            locations_list = start.Full_group.get(low_group)[day_dict.get(day)][1]
            lessons_list = start.Full_group.get(low_group)[day_dict.get(day)][2]
            aud_list = start.Full_group.get(low_group)[day_dict.get(day)][4]
            return times_list,aud_list, locations_list, lessons_list

    if week == '2':
        if start.Full_group.get(low_group)[day_dict.get(day)+7][3]!='':
            times_list = start.Full_group.get(low_group)[day_dict.get(day)+7][0]
            locations_list = start.Full_group.get(low_group)[day_dict.get(day)+7][1]
            lessons_list = start.Full_group.get(low_group)[day_dict.get(day)+7][2]
            aud_list = start.Full_group.get(low_group)[day_dict.get(day)+7][4]
            return times_list,aud_list, locations_list, lessons_list
    if week == '0': 
        if start.Full_group.get(low_group)[day_dict.get(day)+14][3]!='':
            times_list = start.Full_group.get(low_group)[day_dict.get(day)+14][0]
            locations_list = start.Full_group.get(low_group)[day_dict.get(day)+14][1]
            lessons_list = start.Full_group.get(low_group)[day_dict.get(day)+14][2]
            aud_list = start.Full_group.get(low_group)[day_dict.get(day)+14][4]
            return times_list,aud_list, locations_list, lessons_list

    soup = BeautifulSoup(web_page, "html5lib")
    # Получаем таблицу с расписанием на все дни недели
    if day == 'monday':
        schedule_table = soup.find("table", attrs=dict(id = "1day"))
    if day == 'tuesday':
        schedule_table = soup.find("table", attrs=dict(id = "2day"))
    if day == 'wednesday':
        schedule_table = soup.find("table", attrs=dict(id = "3day"))
    if day == 'thursday':
        schedule_table = soup.find("table", attrs=dict(id = "4day"))
    if day == 'friday':
        schedule_table = soup.find("table", attrs=dict(id = "5day"))
    if day == 'saturday':
        schedule_table = soup.find("table", attrs=dict(id = "6day"))
    if day == 'sunday':
        schedule_table = None

    if schedule_table == None or day == 'sunday':
        times_list=['']
        locations_list=['']
        lessons_list=['']
        aud_list=['']
        return times_list,aud_list, locations_list, lessons_list
    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [times.span.text for times in times_list]

    #кабинет проведения занятий
    audit = schedule_table.findAll("td", attrs={"class":"room"})
    k=len('<dd></dd>')
    aud_list=list()
    for room in audit:
        if room.dd!=None and len(room.dd)!=k:
            if room.dd.text=='':
                aud_list.append('Уточните ваш кабинет')
            else:
                aud_list.append(room.dd.text)

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
    lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

    # заполняем базу данных 
    if week == '1':
        start.Full_group.get(low_group)[day_dict.get(day)][0]=times_list
        start.Full_group.get(low_group)[day_dict.get(day)][1]=locations_list
        start.Full_group.get(low_group)[day_dict.get(day)][2]=lessons_list
        start.Full_group.get(low_group)[day_dict.get(day)][3]=1
        start.Full_group.get(low_group)[day_dict.get(day)][4]=aud_list
    if week == '2':
        start.Full_group.get(low_group)[day_dict.get(day)+7][0]=times_list
        start.Full_group.get(low_group)[day_dict.get(day)+7][1]=locations_list
        start.Full_group.get(low_group)[day_dict.get(day)+7][2]=lessons_list
        start.Full_group.get(low_group)[day_dict.get(day)+7][3]=1
        start.Full_group.get(low_group)[day_dict.get(day)+7][4]=aud_list
    if week =='0':
        start.Full_group.get(low_group)[day_dict.get(day)+14][0]=times_list
        start.Full_group.get(low_group)[day_dict.get(day)+14][1]=locations_list
        start.Full_group.get(low_group)[day_dict.get(day)+14][2]=lessons_list
        start.Full_group.get(low_group)[day_dict.get(day)+14][3]=1
        start.Full_group.get(low_group)[day_dict.get(day)+14][4]=aud_list

    return times_list,aud_list, locations_list, lessons_list

def check_week():
    week=time.strftime("%W", time.localtime())# номер недели в году начиная с понедельника
    if int(week)%2 == 0 :
        return 1
    else:
        return 2

@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
def get_schedule(message):
    """ Получить расписание на указанный день """
    # Находим день недели из сообщение 
    mess=message.text
    mess=mess[1:]
    mess=mess.split()
    day=str(mess[0])
    day=day.lower()
    days=['/monday', '/tuesday', '/wednesday', '/thursday', '/friday', '/saturday', '/sunday','/Monday', '/Tuesday', '/Wednesday', '/Thursday', '/Friday', '/Saturday', '/Sunday']
    m=message.text
    m=m.lower()

    for i in days:
        if m == i:
            return bot.send_message(message.chat.id,"Для начала работы введи номер своей группы.")

    if len(mess)==3:
            week=mess[2]
            week=str(week)
            group=mess[1]
    else:
        week=check_week()
        week=str(week)
        _,group = message.text.split()
    low_group=group.lower()

    if start.Full_group.get(low_group,'5')[0][0] == '5':
        return bot.send_message(message.chat.id,"Вы ввели некорректный номер группы.")
    else:
        keyboard(group,message,week)

    # В воскресенье не может бытьу учебы!
    if day == 'sunday':
        return bot.send_message(message.chat.id, 'Вы хорошо потрудились на этой недели, отдохните!', parse_mode='HTML')

    else :
        web_page=None
        if BigData_check(day,week,low_group):
            times_lst,aud_list, locations_lst, lessons_lst = \
                parse_schedule_for_a_monday(day,week,low_group,web_page)
        else:
            web_page = get_page(group,week)

            times_lst,aud_list, locations_lst, lessons_lst = \
                parse_schedule_for_a_monday(day,week,low_group,web_page)

        # Если в будень день нет пар
        if times_lst==[''] and locations_lst==[''] and lessons_lst==['']:
            
            return bot.send_message(message.chat.id, "Расслабься, у тебя сегодня нет пар)", parse_mode='HTML')
        else:
            resp = ''
            for time,aud, location, lession in zip(times_lst,aud_list, locations_lst, lessons_lst):
                resp += '<b>{}</b>,{}, <b>{}</b>{}'.format(time,location,aud, lession)
            return bot.send_message(message.chat.id, resp, parse_mode='HTML')   

def now_day():
    #День недели
    my_date = date.today()
    day=calendar.day_name[my_date.weekday()]
    day=day.lower()
    return day

def now_time():
    #Реальное время
    clock=list()
    clock.append(time.localtime().tm_hour)
    clock.append(time.localtime().tm_min)
    return clock

@bot.message_handler(commands=['near'])
def get_near_lesson(message):
    """ Получить ближайшее занятие """
    #Узнатем время, день,неделю,номер группы в данным момент

    clock=now_time()
    clock[0]=clock[0]+3
    day=now_day()
    mess=message.text
    if mess == '/near':
        
        return bot.send_message(message.chat.id,"Для начала работы введи номер группы.", parse_mode='HTML')
    mess=mess.split()
    if len(mess)==3:
        week=mess[2]
        week=str(week)
        group=mess[1]
    else:
        week=check_week()
        week=str(week)
        group=mess[1]
    low_group=group.lower()

    if start.Full_group.get(low_group,'5')[0][0] == '5':
        return bot.send_message(message.chat.id,"Вы ввели некорректный номер группы.")
    else:
        keyboard(group,message,week)

    days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    replay = True
    count=days.index(day)
    shoort_time=24,0 #Максимальная возможная разница во времени между занятиями.
    web_page = None
    if not BigData_check(days[count],week,low_group):
        web_page = get_page(group,week)

    while replay:
        times_lst,aud_list, locations_lst, lessons_lst = \
            parse_schedule_for_a_monday(days[count],week,low_group,web_page) # значения времени , локации, предмета для указанной группы

        if times_lst==[''] and locations_lst==[''] and lessons_lst==['']:
            if count<6:
                count+=1
                clock=0,0
            else:
                if week == '2':
                    week = '1'
                else:
                    week == '2'
                count = 0
                clock=0,0

            if not BigData_check(days[count],week,low_group):
                web_page = get_page(group,week) # обновляем в том случае если в БД  нет данных на следующий период


        else:
            count2=0
            block=0,0 # минимальная разница между парами 
            for i in range(len(times_lst)): # бежим по времени соответственно занятиям

                temp1=times_lst[i]
                value_time=int(temp1[6:8]),int(temp1[9:11]) # выбираем только окончания занятия , т.к пользователь может сделать запрос во время пары.
                helps=value_time[0]-clock[0],value_time[1]-clock[1]
                if shoort_time>=helps and helps>=block: 
                    replay = False
                    num=i
                    shoort_time=helps
                    count2+=1

            if count2 == 0 : # если таких пар не было (к примеру запрос прошел после пар)
                if count<6:
                    count+=1
                    clock=0,0
                else:
                    if week == 2:
                        week = 1
                    else:
                        week == 2
                    count = 0
                    clock=0,0

                if not BigData_check(days[count],week,low_group):
                    web_page = get_page(group,week)

    day_times=days[count]
    resp=''
    resp += '{}: <b>{}</b>,{}, <b>{}</b> {}\n'.format(day_times.title(),times_lst[num], locations_lst[num],aud_list[num], lessons_lst[num])
    return bot.send_message(message.chat.id, resp, parse_mode='HTML') 


@bot.message_handler(commands=['tommorow'])
def get_tommorow(message):
    """ Получить расписание на следующий день """
    day=now_day()
    mess=message.text
    if mess == '/tommorow':
        return bot.send_message(message.chat.id,"Для начала работы введи номер своей группы.")
    mess=mess.split()
    helps=check_week()
    if len(mess)==3 and str(helps)!=mess[2]:
        return bot.send_message(message.chat.id,"Расписание на завтра доступно только в настоящем времени. Уберите номер недели после ввода группы.")
    else:
        week=check_week()
        week=str(week)
        group = mess[1]
    low_group=group.lower()

    if start.Full_group.get(low_group,'5')[0][0] == '5':
        return bot.send_message(message.chat.id,"Вы ввели некорректный номер группы.")
    else:
        keyboard(group,message,week)

    days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    count=days.index(day)

    if count == 6 :
        count = 0
        if week == '2':
            week = '1'
        else:
            week = '2'
        web_page=None
        if not BigData_check(days[count],week,low_group):    
            web_page = get_page(group,week)

        times_lst,aud_list,locations_lst, lessons_lst = \
            parse_schedule_for_a_monday(days[count],week,low_group,web_page)

        day_times=days[count]
        resp=''
        for time,aud, location, lession in zip(times_lst,aud_list, locations_lst, lessons_lst):
            resp += '{}: <b>{}</b>, {}, <b>{}</b> {}\n'.format(day_times.title(),time, location,aud, lession)
        
        return bot.send_message(message.chat.id, resp, parse_mode='HTML')

    else:
        count+=1
        day_times=days[count]
        web_page=None
        if not BigData_check(days[count],week,low_group):
            web_page = get_page(group,week)

        times_lst,aud_list, locations_lst, lessons_lst = \
            parse_schedule_for_a_monday(days[count],week,low_group,web_page)

        if times_lst==['']:
            resp=''
            resp='{}: У тебя завтра нет занятий)'.format(day_times.title())
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
        else:
            resp = ''
            for time,aud, location, lession in zip(times_lst,aud_list, locations_lst, lessons_lst):
                resp += '{}: <b>{}</b>, {}, <b>{}</b> {}\n'.format(day_times.title(),time,location,aud, lession)
            
            return bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
    """ Получить расписание на всю неделю для указанной группы """
    mess=message.text
    if mess == '/all':
        
        return bot.send_message(message.chat.id,"Для начала работы введите номер группы.")
    mess=mess.split()
    if len(mess)==3:
        week=mess[2]
        week=str(week)
        group=mess[1]
    else:
        week=check_week()
        week=str(week)
        group =mess[1] 
    low_group=group.lower()
    web_page=None

    if start.Full_group.get(low_group,'5')[0][0] == '5':
        
        return bot.send_message(message.chat.id,"Вы ввели некорректный номер группы.")
    else:
        keyboard(group,message,week)

    days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    resp=''

    for i in range(len(days)):
        day_times=days[i]

        if not BigData_check(day_times,week,low_group):
            web_page = get_page(group,week)

        times_lst,aud_list, locations_lst, lessons_lst = \
            parse_schedule_for_a_monday(day_times,week,low_group,web_page)

        if times_lst!=[''] or locations_lst!=[''] or lessons_lst!=[''] :
            for time,aud, location, lession in zip(times_lst,aud_list, locations_lst, lessons_lst):
                resp += '{}: <b>{}</b>, {}, <b>{}</b> {}\n'.format(day_times.title(),time, location,aud, lession)
        else:
            resp+='{}: У тебя выходной намечается) \n'.format(day_times.title())
    
    return bot.send_message(message.chat.id, resp, parse_mode='HTML')

@bot.message_handler(commands=['Привет','привет','start'])
def get_all_schedule(message):
    resp='Привет, меня зовут Skylarr. Вы можете спросить у меня расписание университета ITMO.Что я умею делать: \n 1.Узнать расписание на определенный день(day week). \n 2. Узнать ближайшее занятие (near). \n 3. Получить рассписание на следующий день (tommorow). \n 4. Узнать все занятия на неделю (all).'
    bot.send_message(message.chat.id, resp, parse_mode='HTML')
    bot.send_message(message.chat.id,"Для начала работы введи номер своей группы и неделю на которую хотите посмотреть расписание \nДля всего рассписания 0, для четной 1, для нечетной 2. \nПолучить рассписание с этой недели. Просто введие номер группы.\n Пример: K3141 1 .")

@bot.message_handler(content_types=['text']) 
def dialogue(message:str):
    mess=message.text
    mess=mess.split()
    group = mess[0]

    if len(mess)!=1:
        week=mess[1]
        week=str(week)
    else:
        week=check_week()
        week=str(week)

    low_group=group.lower()
    if low_group !='/start':
        if start.Full_group.get(low_group,'5')[0][0] == '5':
            bot.send_message(message.chat.id,"Вы ввели некорректный номер группы.")
        elif week!='0' and week!='1' and week!='2':
            bot.send_message(message.chat.id,"Вы ввели некорректный номер недели, напишите мне /привет ,исходя из критериев недели, выполните ввод заново.")
        else:
            keyboard(group,message,week)

def keyboard(group:str,message:str,week:str): 
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    btn1 = types.KeyboardButton(text='/monday ' + group + ' ' + week)
    btn2 = types.KeyboardButton(text='/tuesday ' + group+ ' ' + week)
    btn3 = types.KeyboardButton(text='/wednesday '+ group+ ' ' + week)
    btn4 = types.KeyboardButton(text='/thursday ' + group+ ' ' + week)
    btn5 = types.KeyboardButton(text='/friday '+ group+ ' ' + week)
    btn6 = types.KeyboardButton(text='/saturday ' + group+ ' ' + week)
    btn7 = types.KeyboardButton(text='/sunday '+ group+ ' ' + week)
    btn8 = types.KeyboardButton(text="/near " + group+ ' ' + week)
    btn9 = types.KeyboardButton(text="/tommorow " + group+ ' ' + week)
    btn10 = types.KeyboardButton(text = "/all "+group + ' '+ week)
    markup.row(btn1,btn2,btn3)
    markup.row(btn4,btn5,btn6,btn7)
    markup.row(btn8,btn9)
    markup.add(btn10)
    group=''
    bot.send_message(message.chat.id,"Рад вам помочь &#10084  ".format(markup),reply_markup=markup,parse_mode='HTML')

def BigData_check(day:str,week:str,low_group:str):

    day_dict={'monday': 1,'tuesday':2,'wednesday':3,'thursday':4,'friday':5,'saturday':6,'sunday':7}
    if week == '1':
        if start.Full_group.get(low_group)[day_dict.get(day)][3]!='':
            return True
        else:
            return False

    if week == '2':
        if start.Full_group.get(low_group)[day_dict.get(day)+7][3]!='':
            return True
        else:
            return False
    if week =='0':
        if start.Full_group.get(low_group)[day_dict.get(day)+14][3]!='':
            return True
        else:
            return False

if __name__ == '__main__':
    bot.polling(none_stop=True)
