import secrets
import threading
import random
import time as ti
import telebot
import datetime
from classdb import *

bot=telebot.TeleBot('6375736731:AAHpz64Bxk5H52vUk66tKk03TNslmMcCStg')
bot_name = "Raffle_Kept_Bot"
channel_name = "lot_ch_1"
channel_id = -1001935698867
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, "Привет, и добро пожаловать в бот для создания розыгрышей! \n"
                                           "/start - перезапуск бота \n"
                                           "/raffle - создание розыгрыша")
    if bot.get_chat_member("@lot_ch_1", message.from_user.id).status == 'left':
        markup = telebot.types.InlineKeyboardMarkup()
        btn= telebot.types.InlineKeyboardButton(text='ПОДПИСАТЬСЯ', url="https://t.me/" + channel_name)
        markup.add(btn)
        bot.send_message(message.from_user.id, "Подпишись на канал!", reply_markup=markup)
    sp = message.text.split(' ')
    if len(sp) > 1:
        r = db.execute(raffles.select().where(raffles.c.id == int(sp[1]))).one()
        if bot.get_chat_member("@lot_ch_1", message.from_user.id).status == 'left':
            bot.send_message(message.from_user.id, str(r.name) + "\n\n" + str(r.text))
            markup = telebot.types.InlineKeyboardMarkup()
            btn= telebot.types.InlineKeyboardButton(text='ПОДПИСАТЬСЯ', url="https://t.me/" + channel_name)
            markup.add(btn)
            bot.send_message(message.from_user.id, "Для участия в этом розыгрыше тебе надо подписаться на этот канал:", reply_markup=markup)
        else:
            markup = telebot.types.InlineKeyboardMarkup()
            btn= telebot.types.InlineKeyboardButton(text='УЧАСТВОВАТЬ', callback_data="useradd " + str(r.id))
            markup.add(btn)
            showraff(message.from_user.id, r)
            bot.send_message(message.from_user.id, "Участвуй:", reply_markup=markup)

@bot.message_handler(commands=['raffle'])
def raf_message(message):
    if bot.get_chat_member("@" + channel_name, message.from_user.id).status != 'administrator' and bot.get_chat_member("@" + channel_name, message.from_user.id).status != 'creator':
        bot.send_message(message.from_user.id, "Ты не админ!")
        return
    ra = db.execute(raffles.select()).all()
    markup = telebot.types.InlineKeyboardMarkup()
    for i in ra:
        btn= telebot.types.InlineKeyboardButton(text=str(i.name), callback_data=str(i.id))
        markup.add(btn)
    btn= telebot.types.InlineKeyboardButton(text="+", callback_data="add")
    markup.add(btn)
    bot.send_message(message.from_user.id, "Запущено " + str(len(ra)) + " розыгрышей", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback(callback):
    if callback.data == 'add':
        db.execute(raffles.insert().values(fromm = callback.from_user.id, time = "10 00 10 10 2126"))
        db.commit()
        raf = db.execute(raffles.select()).all()[-1].id
        m = bot.send_message(callback.from_user.id, "Введите название:")
        bot.register_next_step_handler(m, name, id = raf)
        return
    sp = callback.data.split(' ')
    if sp[0] == 'useradd':
        if len(db.execute(usersraf.select().where(usersraf.c.idtele == callback.from_user.id, usersraf.c.idraf == sp[1])).all()) == 0:
            db.execute(usersraf.insert().values(idtele = callback.from_user.id, idraf = sp[1], nicktele=callback.from_user.username, textid=gentextid()))
            db.commit()
            bot.send_message(callback.from_user.id, "ОТЛИЧНО! ТЕПЕРЬ ТЫ УЧАСТВУЕШЬ В РОЗЫГРЫШЕ!!!!")
        else:
            bot.send_message(callback.from_user.id, "Ты не можешь участвовать в розыгрыше дважды!")
        return
    elif sp[0] == 'post':
        r = db.execute(raffles.select().where(raffles.c.id == int(sp[1]))).one()
        markup = telebot.types.InlineKeyboardMarkup()
        btn= telebot.types.InlineKeyboardButton(text='УЧАСТВОВАТЬ', url="t.me/" + bot_name + "?start=" + str(r.id))
        markup.add(btn)
        time = (r.time).split(" ")
        bot.send_message(channel_id, str(r.name) + "\n\n" + str(r.text) + "\n\nДо " + str(time[0]) + ":" + str(time[1]) + " " + str(time[2]) + "числа " + str(time[3]) + "месяца " + str(time[4]) + "г. ", reply_markup=markup)
    elif sp[0] == 'raffle':
        if sp[1] == 'edt':
            if sp[2] == 'name':
                m = bot.send_message(callback.from_user.id, "Введите название:")
                bot.register_next_step_handler(m, nameend, id = sp[3])
            if sp[2] == 'text':
                m = bot.send_message(callback.from_user.id, "Введите описание:")
                bot.register_next_step_handler(m, descrend, id = sp[3])
            if sp[2] == 'wintext':
                m = bot.send_message(callback.from_user.id, "Введите текст для сообщения о выигрыше:")
                bot.register_next_step_handler(m, wintextend, id = sp[3])
            if sp[2] == 'time':
                m = bot.send_message(callback.from_user.id, "Введите время выигрыша в формате ЧЧ ММ ДД ММ ГГГГ!:")
                bot.register_next_step_handler(m, timeend, id = sp[3])
            if sp[2] == 'ucount':
                m = bot.send_message(callback.from_user.id, "Введите количество участников:")
                bot.register_next_step_handler(m, ucountend, id = sp[3])
        elif sp[1] == 'inwin':
            inwin(callback.from_user.id, sp[2])
        return
    r = db.execute(raffles.select().where(raffles.c.id == callback.data)).one()
    showraff(callback.from_user.id, r)
    markup = telebot.types.InlineKeyboardMarkup()
    btn= telebot.types.InlineKeyboardButton(text='Изменить название', callback_data="raffle edt name " + str(r.id))
    markup.add(btn)
    btn= telebot.types.InlineKeyboardButton(text='Изменить описание', callback_data="raffle edt text " + str(r.id))
    markup.add(btn)
    btn= telebot.types.InlineKeyboardButton(text='Изменить сообщение для победителя', callback_data="raffle edt wintext " + str(r.id))
    markup.add(btn)
    btn= telebot.types.InlineKeyboardButton(text='Изменить время', callback_data="raffle edt time " + str(r.id))
    markup.add(btn)
    btn= telebot.types.InlineKeyboardButton(text='Изменить количество победителей', callback_data="raffle edt ucount " + str(r.id))
    markup.add(btn)
    btn= telebot.types.InlineKeyboardButton(text='Завершить розыгрыш и определить победителя сейчас', callback_data="raffle inwin " + str(r.id))
    markup.add(btn)
    bot.send_message(callback.from_user.id, "Выберите, что вы хотите сделать с этим розыгрышем:", reply_markup=markup)
    
def gentextid():
    token = secrets.token_urlsafe(4)
    for i in db.execute(usersraf.select()).all():
        if i.textid == token:
            return gentextid()
    return token

def showraff(msgto : int, r):
    time = (r.time).split(" ")
    bot.send_message(msgto, str(r.name) + "\n\n" + str(r.text) + "\n\nДо " + str(time[0]) + ":" + str(time[1]) + " " + str(time[2]) + "числа " + str(time[3]) + "месяца " + str(time[4]) + "г. ")


def parsmark(text):
    text = str(text)
    return (text).replace("_", "\_").replace("*", "\*").replace("~", "\~")

def inwin(mesfrom, refid):
    ref = db.execute(raffles.select().where(raffles.c.id == refid)).one()
    lc = 0
    wc = 0
    me = bot.send_message(mesfrom, "Подсчитываю резyльтаты...")
    w = db.execute(usersraf.select().where(usersraf.c.idraf == refid)).all()
    if len(w) == 0:
        bot.send_message(mesfrom, "У этого розыгрыша 0 участинков. Розыгрыш закончен и удален.")
        delref(ref)
        return
    ucount = ref.ucount
    if len(w) < ucount:
        ucount = len(w)
    ch = random.choices(w, k=ucount)
    m = ""
    for i in ch:
        showraff(i.idtele, ref)
        bot.send_message(i.idtele, "ВЫ ВЫИГРАЛИ!!! с токеном `" + parsmark(i.textid) + "` \n\n" + parsmark(ref.wintext), parse_mode="Markdown")
        m = m + "@" +  parsmark(i.nicktele) + " с токеном `" + parsmark(i.textid) + "` \n"
        wc = wc + 1
        bot.edit_message_text(chat_id=mesfrom, message_id=me.id, text= "Отправил сообщение " + str(wc) + " победителям и " + str(lc) + " проигравшим")
        ti.sleep(0.1)
    bot.send_message(mesfrom, str(m) + " выиграл в этом розыгрыше!!!", parse_mode="Markdown")
    if len(w) == ucount:
        delref(ref)
        return
    for i in w:
        def check():
            for e in ch:
                if e == i:
                    return True
            return False
        if not check():
            showraff(i.idtele, ref)
            bot.send_message(i.idtele, "Bы проиграли(!!! с токеном `" + parsmark(i.textid) + "` \n", parse_mode="Markdown")
            lc = lc + 1
            bot.edit_message_text(chat_id=mesfrom, message_id=me.id, text= "Отправил сообщение " + str(wc) + " победителям и " + str(lc) + " проигравшим")
            ti.sleep(0.1)
    delref(ref)

def delref(ref):
    db.execute(raffles.delete().where(raffles.c.id == ref.id))
    db.execute(usersraf.delete().where(usersraf.c.idraf == ref.id))
    db.commit()

def nameend(mes, id):
    db.execute(raffles.update().values(name = mes.text).where(raffles.c.id == id))
    db.commit()
    r = db.execute(raffles.select().where(raffles.c.id == id)).one()
    bot.send_message(mes.from_user.id, "Принято!")
    for i in db.execute(usersraf.select().where(usersraf.c.idraf == id)).all():
        showraff(mes.from_user.id, r)
        bot.send_message(mes.from_user.id, "Администратор изменил название розыгрыша!")

def descrend(mes, id):
    db.execute(raffles.update().values(text = mes.text).where(raffles.c.id == id))
    db.commit()
    r = db.execute(raffles.select().where(raffles.c.id == id)).one()
    bot.send_message(mes.from_user.id, "Принято!")
    for i in db.execute(usersraf.select().where(usersraf.c.idraf == id)).all():
        showraff(mes.from_user.id, r)
        bot.send_message(mes.from_user.id, "Администратор изменил описание розыгрыша!")

def ucountend(mes, id):
    if (type(mes.text) == int):
        db.execute(raffles.update().values(ucount = mes.text).where(raffles.c.id == id))
        db.commit()
        r = db.execute(raffles.select().where(raffles.c.id == id)).one()
        bot.send_message(mes.from_user.id, "Принято!")
        for i in db.execute(usersraf.select().where(usersraf.c.idraf == id)).all():
            showraff(mes.from_user.id, r)
            bot.send_message(mes.from_user.id, "Администратор изменил количество победителей розыгрыша!")
    else:
        m = bot.send_message(mes.from_user.id, "Это не цифра!")
        bot.register_next_step_handler(m, ucount, id = id)

def wintextend(mes, id):
    db.execute(raffles.update().values(wintext = mes.text).where(raffles.c.id == id))
    db.commit()
    bot.send_message(mes.from_user.id, "Принято!")

def timeend(mes, id):
    try:
        d = datetime.datetime.strptime(mes.text, "%H %M %j %m %Y")
    except ValueError as e:
        m = bot.send_message(mes.from_user.id, "Надпись не соответствует формату ЧЧ ММ ДД ММ ГГГГ!")
        bot.register_next_step_handler(m, timeend, id=id)
        raise ValueError(e)
        return
    db.execute(raffles.update().values(time = mes.text).where(raffles.c.id == id))
    db.commit()
    r = db.execute(raffles.select().where(raffles.c.id == id)).one()
    bot.send_message(mes.from_user.id, "Принято!")
    for i in db.execute(usersraf.select().where(usersraf.c.idraf == id)).all():
        showraff(mes.from_user.id, r)
        bot.send_message(mes.from_user.id, "Администратор изменил время окончания конкурса розыгрыша!")
    
def name(mes, id):
    db.execute(raffles.update().values(name = mes.text).where(raffles.c.id == id))
    db.commit()
    m = bot.send_message(mes.from_user.id, "Введите описание:")
    bot.register_next_step_handler(m, descr, id = id)

def descr(mes, id):
    db.execute(raffles.update().values(text = mes.text).where(raffles.c.id == id))
    db.commit()
    m = bot.send_message(mes.from_user.id, "Введите количество победителей:")
    bot.register_next_step_handler(m, ucount, id = id)

def ucount(mes, id):
    try :
        if (type(int(mes.text)) == int):
            db.execute(raffles.update().values(ucount = mes.text).where(raffles.c.id == id))
            db.commit()
            m = bot.send_message(mes.from_user.id, "Введите текст для сообщения о выигрыше:")
            bot.register_next_step_handler(m, time, id = id)
        else:
            m = bot.send_message(mes.from_user.id, "Это не цифира!")
            bot.register_next_step_handler(m, ucount, id = id)
    except ValueError:
        m = bot.send_message(mes.from_user.id, "Это не цифира!")
        bot.register_next_step_handler(m, ucount, id = id)

def time(mes, id):
    db.execute(raffles.update().values(wintext = mes.text).where(raffles.c.id == id))
    db.commit()
    m = bot.send_message(mes.from_user.id, "Введите время выигрыша в формате ЧЧ ММ ДД ММ ГГГГ!:")
    bot.register_next_step_handler(m, end, id = id)

def end(mes, id):
    try:
        d = datetime.datetime.strptime(mes.text, "%H %M %j %m %Y")
    except ValueError:
        m = bot.send_message(mes.from_user.id, "Надпись не соответствует формату ЧЧ ММ ДД ММ ГГГГ!")
        bot.register_next_step_handler(m, end, id=id)
        return
    db.execute(raffles.update().values(time = mes.text).where(raffles.c.id == id))
    db.commit()
    r = db.execute(raffles.select().where(raffles.c.id == id)).one()
    showraff(mes.from_user.id, r)
    markup = telebot.types.InlineKeyboardMarkup()
    btn= telebot.types.InlineKeyboardButton(text='Отправить сообщение в канал', callback_data="post " + str(id))
    markup.add(btn)
    bot.send_message(mes.from_user.id, "Розыгрыш создан!\nСсылка t.me/" + bot_name + "?start=" + str(id), reply_markup=markup)

def greet():
    while True:
        ti.sleep(1)
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        for i in db.execute(raffles.select()).all():
            d = datetime.datetime.strptime(i.time, "%H %M %d %m %Y")
            if dt > d:
                inwin(i.fromm, i.id)

t1 = threading.Thread(target=greet, daemon=False)
t1.start()

t2 = threading.Thread(target=bot.infinity_polling(), daemon=True)
t2.start()