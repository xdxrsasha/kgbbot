from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
import random
import sqlite3
import time
from datetime import datetime, timedelta
from collections import defaultdict

# Глобальный пул соединений
conn = sqlite3.connect('kgb_data.db', check_same_thread=False)
c = conn.cursor()

# Инициализация базы данных
def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS players
                 (user_id INTEGER PRIMARY KEY, money INTEGER, businesses TEXT, houses TEXT, cars TEXT, phones TEXT, planes TEXT, yachts TEXT,
                  helicopters TEXT, mines TEXT, xp INTEGER, level INTEGER, unlocked_ores TEXT, resources TEXT, quests TEXT, energy INTEGER,
                  rating INTEGER, bitcoin REAL, deposit INTEGER, last_bonus TEXT, nickname TEXT, status TEXT, treasury INTEGER)''')
    conn.commit()

# Кэш данных игроков
player_cache = defaultdict(dict)

def load_player(user_id):
    if user_id in player_cache:
        return player_cache[user_id].copy()
    c.execute("SELECT money, businesses, houses, cars, phones, planes, yachts, helicopters, mines, xp, level, unlocked_ores, resources, quests, energy, rating, bitcoin, deposit, last_bonus, nickname, status, treasury FROM players WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if result:
        player = {
            "user_id": user_id, "money": result[0], "businesses": eval(result[1]) if result[1] else [], "houses": eval(result[2]) if result[2] else [],
            "cars": eval(result[3]) if result[3] else [], "phones": eval(result[4]) if result[4] else [], "planes": eval(result[5]) if result[5] else [],
            "yachts": eval(result[6]) if result[6] else [], "helicopters": eval(result[7]) if result[7] else [], "mines": eval(result[8]) if result[8] else [],
            "xp": result[9] or 0, "level": result[10] or 1, "unlocked_ores": eval(result[11]) if result[11] else ["Copper", "Iron"],
            "resources": eval(result[12]) if result[12] else {"Wood": 0, "Stone": 0}, "quests": eval(result[13]) if result[13] else [],
            "energy": result[14] or 100, "rating": result[15] or 0, "bitcoin": result[16] or 0.0, "deposit": result[17] or 0,
            "last_bonus": result[18], "nickname": result[19], "status": result[20], "treasury": result[21] or 0
        }
    else:
        player = {
            "user_id": user_id, "money": 0, "businesses": [], "houses": [], "cars": [], "phones": [], "planes": [], "yachts": [],
            "helicopters": [], "mines": [], "xp": 0, "level": 1, "unlocked_ores": ["Copper", "Iron"],
            "resources": {"Wood": 0, "Stone": 0}, "quests": [],
            "energy": 100, "rating": 0, "bitcoin": 0.0, "deposit": 0, "last_bonus": None, "nickname": f"User_{user_id}", "status": "Обычный",
            "treasury": 0
        }
        save_player(user_id, player)
    player_cache[user_id] = player.copy()
    return player.copy()

def load_player_by_nickname(nickname):
    c.execute("SELECT user_id, money, businesses, houses, cars, phones, planes, yachts, helicopters, mines, xp, level, unlocked_ores, resources, quests, energy, rating, bitcoin, deposit, last_bonus, nickname, status, treasury FROM players WHERE nickname = ?", (nickname,))
    result = c.fetchone()
    if result:
        user_id = result[0]
        if user_id in player_cache:
            return player_cache[user_id].copy()
        player = {
            "user_id": user_id, "money": result[1], "businesses": eval(result[2]) if result[2] else [], "houses": eval(result[3]) if result[3] else [],
            "cars": eval(result[4]) if result[4] else [], "phones": eval(result[5]) if result[5] else [], "planes": eval(result[6]) if result[6] else [],
            "yachts": eval(result[7]) if result[7] else [], "helicopters": eval(result[8]) if result[8] else [], "mines": eval(result[9]) if result[9] else [],
            "xp": result[10] or 0, "level": result[11] or 1, "unlocked_ores": eval(result[12]) if result[12] else ["Copper", "Iron"],
            "resources": eval(result[13]) if result[13] else {"Wood": 0, "Stone": 0}, "quests": eval(result[14]) if result[14] else [],
            "energy": result[15] or 100, "rating": result[16] or 0, "bitcoin": result[17] or 0.0, "deposit": result[18] or 0,
            "last_bonus": result[19], "nickname": result[20], "status": result[21], "treasury": result[22] or 0
        }
        player_cache[user_id] = player.copy()
        return player.copy()
    return None

# Сохранение данных игрока
def save_player(user_id, data):
    c.execute("INSERT OR REPLACE INTO players (user_id, money, businesses, houses, cars, phones, planes, yachts, helicopters, mines, xp, level, unlocked_ores, resources, quests, energy, rating, bitcoin, deposit, last_bonus, nickname, status, treasury) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (user_id, data["money"], str(data["businesses"]), str(data["houses"]), str(data["cars"]), str(data["phones"]), str(data["planes"]),
               str(data["yachts"]), str(data["helicopters"]), str(data["mines"]), data["xp"], data["level"], str(data["unlocked_ores"]),
               str(data["resources"]), str(data["quests"]), data["energy"], data["rating"], data["bitcoin"], data["deposit"], data["last_bonus"],
               data["nickname"], data["status"], data["treasury"]))
    conn.commit()
    player_cache[user_id] = data.copy()

# Проверка уровня
def check_level_up(data):
    xp_needed = data["level"] * 100
    if data["xp"] >= xp_needed:
        data["level"] += 1
        data["money"] += 500
        return f"🎉 Поздравляю! Новый уровень {data['level']}! +$500."
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = load_player(user_id)
    text = update.message.text.lower()
    words = text.split()

    if "босс" in text:
        await update.message.reply_text("😎 Да, босс? Чего изволите?")
    elif "статус" in text:
        level_up_msg = check_level_up(data)
        if level_up_msg:
            await update.message.reply_text(level_up_msg)
            save_player(user_id, data)
        await update.message.reply_text(f"💰 Деньги: ${data['money']}\n🎯 Уровень: {data['level']}\n⭐ Опыт: {data['xp']}\n🏢 Бизнесы: {len(data['businesses'])}\n🏠 Дома: {len(data['houses'])}\n🚗 Машины: {len(data['cars'])}")
    elif "статус тип" in text:
        await update.message.reply_text(f"🎩 Твой текущий статус: {data['status']}\nДоступные VIP-статусы: Золотой ($1000), Платиновый ($5000), Алмазный ($10000).")
    elif "купить статус" in text and len(words) >= 2:
        new_status = words[1]
        vip_statuses = {"Золотой": 1000, "Платиновый": 5000, "Алмазный": 10000}
        if new_status not in vip_statuses:
            await update.message.reply_text("😢 Такого статуса нет! Выбери: Золотой, Платиновый, Алмазный.")
            return
        price = vip_statuses[new_status]
        if data["money"] < price:
            await update.message.reply_text(f"💸 Недостаточно денег! Нужно ${price}, у тебя ${data['money']}.")
            return
        data["money"] -= price
        data["status"] = new_status
        await update.message.reply_text(f"🎉 Куплен статус {new_status} за ${price}! Теперь у тебя ${data['money']}.")
        save_player(user_id, data)
    elif "купить" in text and len(words) == 2 and words[1] in ["business", "house", "car", "phone", "plane", "yacht", "helicopter"]:
        type_ = words[1]
        prices = {"business": 500, "house": 1000, "car": 800, "phone": 300, "plane": 5000, "yacht": 10000, "helicopter": 8000}
        if data["money"] < prices[type_]:
            await update.message.reply_text(f"😢 Тебе не хватает ${prices[type_] - data['money']}, лох!")
            return
        data["money"] -= prices[type_]
        if type_ == "business":
            data["businesses"].append(f"Business_{len(data['businesses'])+1}")
        elif type_ == "house":
            data["houses"].append(f"House_{len(data['houses'])+1}")
        elif type_ == "car":
            data["cars"].append(f"Car_{len(data['cars'])+1}")
        elif type_ == "phone":
            data["phones"].append(f"Phone_{len(data['phones'])+1}")
        elif type_ == "plane":
            data["planes"].append(f"Plane_{len(data['planes'])+1}")
        elif type_ == "yacht":
            data["yachts"].append(f"Yacht_{len(data['yachts'])+1}")
        elif type_ == "helicopter":
            data["helicopters"].append(f"Helicopter_{len(data['helicopters'])+1}")
        await update.message.reply_text(f"🎁 Куплено {type_}! Теперь у тебя ${data['money']}.")
        save_player(user_id, data)
    elif "копать" in text and len(words) >= 2:
        ore_name = words[1].capitalize()
        if data["energy"] < 10:
            await update.message.reply_text("⚡ Энергия закончилась, отдохни!")
            return
        if not data["mines"]:
            await update.message.reply_text("⛏ У тебя нет шахт, иди разберись, даун!")
            return
        ores = {
            "Copper": {"xp": 10, "chance": 0.5, "value": 100, "req_xp": 0},
            "Iron": {"xp": 20, "chance": 0.3, "value": 250, "req_xp": 0},
            "Gold": {"xp": 500, "chance": 0.15, "value": 1000, "req_xp": 150},
            "Diamond": {"xp": 1000, "chance": 0.05, "value": 5000, "req_xp": 300},
            "Platinum": {"xp": 5000, "chance": 0.02, "value": 20000, "req_xp": 1000},
            "Titan": {"xp": 50000, "chance": 0.005, "value": 100000, "req_xp": 5000},
            "Uranium": {"xp": 100000, "chance": 0.001, "value": 500000, "req_xp": 10000}
        }
        if ore_name not in ores or ore_name not in data["unlocked_ores"]:
            await update.message.reply_text(f"💎 Руды {ore_name} нет или она ещё не открыта! Доступны: {', '.join(data['unlocked_ores'])}")
            return
        if random.random() < ores[ore_name]["chance"]:
            earnings = ores[ore_name]["value"]
            xp_gain = ores[ore_name]["xp"]
            data["money"] += earnings
            data["xp"] += xp_gain
            data["energy"] -= 10
            await update.message.reply_text(f"⛏ Добыто {ore_name}! +${earnings} и +{xp_gain} опыта. Энергия: {data['energy']}/100.")
            level_up_msg = check_level_up(data)
            if level_up_msg:
                await update.message.reply_text(level_up_msg)
            for ore, ore_data in ores.items():
                if ore not in data["unlocked_ores"] and data["xp"] >= ore_data["req_xp"]:
                    data["unlocked_ores"].append(ore)
                    await update.message.reply_text(f"🎉 Поздравляю! Открыта новая руда: {ore}! Требуется {ore_data['req_xp']} опыта.")
        else:
            data["energy"] -= 10
            await update.message.reply_text(f"😢 {ore_name} не добыта, попробуй ещё! Энергия: {data['energy']}/100.")
        save_player(user_id, data)
    elif "ресурсы" in text:
        if data["energy"] < 5:
            await update.message.reply_text("⚡ Энергия низкая, отдохни!")
            return
        if not data["mines"]:
            await update.message.reply_text("⛏ У тебя нет шахт для автосбора, даун!")
            return
        data["resources"]["Wood"] += random.randint(10, 50)
        data["resources"]["Stone"] += random.randint(5, 30)
        money_earned = random.randint(50, 200)
        data["money"] += money_earned
        data["energy"] -= 5
        await update.message.reply_text(f"🌲 Автосбор ресурсов: +{data['resources']['Wood']} Wood, +{data['resources']['Stone']} Stone, +${money_earned}. Энергия: {data['energy']}/100.")
        save_player(user_id, data)
    elif "квесты" in text:
        if not data["quests"]:
            data["quests"] = [{"name": "Собери 100 Wood", "goal": 100, "progress": 0, "reward": 200}]
        quest = data["quests"][0]
        if quest["progress"] >= quest["goal"]:
            data["money"] += quest["reward"]
            data["quests"] = []
            await update.message.reply_text(f"🎯 Квест завершен! +${quest['reward']}. Теперь у тебя ${data['money']}.")
        else:
            await update.message.reply_text(f"🎮 Квест: {quest['name']}. Прогресс: {quest['progress']}/{quest['goal']}.")
    elif text == "/help":
        await update.message.reply_text(
            "💡 Список команд:\n"
            "/start - Начать работу с ботом\n"
            "💰 статус - Показать твои активы\n"
            "🎩 статус тип - Показать VIP-статусы\n"
            "💸 купить статус - Купить статус (Золотой/Платиновый/Алмазный)\n"
            "🎁 купить тип - Купить (business/house/car/phone/plane/yacht/helicopter)\n"
            "⛏ копать [руда] - Добыть руду\n"
            "🌲 ресурсы - Автосбор ресурсов\n"
            "🎮 квесты - Показать квесты\n"
            "/help - Показать это\n"
            "💸 б - Баланс\n"
            "🎒 инвентарь - Показать инвентарь\n"
            "💎 курс руды - Показать курс руд\n"
            "💰 ограбить казну - Попытаться украсть из казны\n"
            "🏦 банк положить/снять сумма/всё - Управление банком\n"
            "💼 депозит положить/снять сумма/всё - Управление депозитом\n"
            "🎁 дать (ник) сумма - Передать деньги\n"
            "₿ биткоин курс/купить/продать кол-во - Управление биткоинами\n"
            "₿ биткоины - Показать биткоины\n"
            "🎁 ежедневный бонус - Получить бонус\n"
            "🏦 казна - Показать казну\n"
            "👤 сменить ник - Изменить ник\n"
            "👤 мой ник - Показать ник\n"
            "🎖 мой статус - Показать статус\n"
            "🎖 статусы - Показать доступные статусы\n"
            "🏆 рейтинг - Показать рейтинг\n"
            "💸 продать рейтинг - Продать рейтинг\n"
            "⚡ энергия - Показать энергию\n"
            "⛏ шахта - Показать шахты\n"
            "🚗 машины - Показать машины\n"
            "📱 телефоны - Показать телефоны\n"
            "✈ самолёты - Показать самолёты\n"
            "🏠 дома - Показать дома\n"
            "⛵ яхты - Показать яхты\n"
            "🚁 вертолёты - Показать вертолёты\n"
            "🎰 казино сумма - Играть в казино"
        )
    elif "б" in text:
        await update.message.reply_text(f"💸 Баланс: ${data['money']}")
    elif "инвентарь" in text:
        await update.message.reply_text(f"🎒 Инвентарь: Бизнесы: {len(data['businesses'])}, Дома: {len(data['houses'])}, Машины: {len(data['cars'])}, Телефоны: {len(data['phones'])}, Самолёты: {len(data['planes'])}, Яхты: {len(data['yachts'])}, Вертолёты: {len(data['helicopters'])}")
    elif "курс руды" in text:
        ores = {"Copper": 100, "Iron": 250, "Gold": 1000, "Diamond": 5000, "Platinum": 20000, "Titan": 100000, "Uranium": 500000}
        await update.message.reply_text(f"💎 Курс руд: {', '.join(f'{ore}: ${value}' for ore, value in ores.items())}")
    elif "ограбить казну" in text:
        if data["energy"] < 50:
            await update.message.reply_text("⚡ Недостаточно энергии для ограбления!")
            return
        if random.random() < 0.3:  # 30% шанс успеха
            stolen = min(1000, data["treasury"])
            data["money"] += stolen
            data["treasury"] -= stolen
            data["energy"] -= 50
            await update.message.reply_text(f"💰 Успешное ограбление! +${stolen}. Теперь у тебя ${data['money']}. Энергия: {data['energy']}/100.")
        else:
            data["energy"] -= 50
            await update.message.reply_text(f"😢 Провал ограбления! Энергия: {data['energy']}/100.")
        save_player(user_id, data)
    elif "банк" in text and len(words) >= 2:
        action = words[1]
        if action in ["положить", "снять"] and len(words) >= 3:
            amount = words[2]
            if amount == "всё":
                amount = data["money"] if action == "положить" else data["deposit"]
            else:
                try:
                    amount = int(amount)
                except ValueError:
                    await update.message.reply_text("💡 Введи сумму или 'всё'!")
                    return
            if action == "положить":
                if data["money"] < amount:
                    await update.message.reply_text("😢 Недостаточно денег!")
                    return
                data["money"] -= amount
                data["deposit"] += amount
                await update.message.reply_text(f"🏦 Положено ${amount} в банк. Баланс: ${data['money']}, Депозит: ${data['deposit']}.")
            elif action == "снять":
                if data["deposit"] < amount:
                    await update.message.reply_text("😢 Недостаточно на депозите!")
                    return
                data["deposit"] -= amount
                data["money"] += amount
                await update.message.reply_text(f"🏦 Снято ${amount} из банка. Баланс: ${data['money']}, Депозит: ${data['deposit']}.")
            save_player(user_id, data)
    elif "депозит" in text and len(words) >= 2:
        action = words[1]
        if action in ["положить", "снять"] and len(words) >= 3:
            amount = words[2]
            if amount == "всё":
                amount = data["money"] if action == "положить" else data["deposit"]
            else:
                try:
                    amount = int(amount)
                except ValueError:
                    await update.message.reply_text("💡 Введи сумму или 'всё'!")
                    return
            if action == "положить":
                if data["money"] < amount:
                    await update.message.reply_text("😢 Недостаточно денег!")
                    return
                data["money"] -= amount
                data["deposit"] += amount
                await update.message.reply_text(f"💼 Положено ${amount} на депозит. Баланс: ${data['money']}, Депозит: ${data['deposit']}.")
            elif action == "снять":
                if data["deposit"] < amount:
                    await update.message.reply_text("😢 Недостаточно на депозите!")
                    return
                data["deposit"] -= amount
                data["money"] += amount
                await update.message.reply_text(f"💼 Снято ${amount} с депозита. Баланс: ${data['money']}, Депозит: ${data['deposit']}.")
            save_player(user_id, data)
    elif "дать" in text and len(words) >= 3:
        recipient_nick = words[1]
        try:
            amount = int(words[2])
            if amount > data["money"]:
                await update.message.reply_text("😢 У тебя нет столько, лох!")
                return
            recipient = load_player_by_nickname(recipient_nick)
            if not recipient:
                await update.message.reply_text(f"👤 Игрок с ником {recipient_nick} не найден!")
                return
            data["money"] -= amount
            recipient["money"] += amount
            save_player(user_id, data)
            save_player(recipient["user_id"], recipient)
            await update.message.reply_text(f"🎁 Передано ${amount} игроку {recipient_nick}. Теперь у тебя ${data['money']}.")
        except ValueError:
            await update.message.reply_text("💡 Введи сумму после ника, например 'дать User123 500'!")
    elif "биткоин" in text and len(words) >= 2:
        if words[1] == "курс":
            await update.message.reply_text(f"₿ Курс биткоина: $50000 (фиктивный курс).")
        elif words[1] == "купить" and len(words) == 3:
            try:
                amount = float(words[2])
                price = amount * 50000
                if data["money"] < price:
                    await update.message.reply_text(f"😢 Тебе не хватает ${price - data['money']}!")
                    return
                data["money"] -= price
                data["bitcoin"] += amount
                await update.message.reply_text(f"₿ Куплено {amount} BTC за ${price}. Баланс: ${data['money']}, BTC: {data['bitcoin']}.")
                save_player(user_id, data)
            except ValueError:
                await update.message.reply_text("💡 Введи количество BTC, например 'биткоин купить 0.1'!")
        elif words[1] == "продать" and len(words) == 3:
            try:
                amount = float(words[2])
                if data["bitcoin"] < amount:
                    await update.message.reply_text("😢 У тебя нет столько BTC!")
                    return
                price = amount * 50000
                data["bitcoin"] -= amount
                data["money"] += price
                await update.message.reply_text(f"₿ Продано {amount} BTC за ${price}. Баланс: ${data['money']}, BTC: {data['bitcoin']}.")
                save_player(user_id, data)
            except ValueError:
                await update.message.reply_text("💡 Введи количество BTC, например 'биткоин продать 0.1'!")
        elif words[1] == "биткоины":
            await update.message.reply_text(f"₿ Биткоины: {data['bitcoin']} BTC")
    elif "ежедневный бонус" in text:
        now = datetime.now()
        if data["last_bonus"] and (now - datetime.fromisoformat(data["last_bonus"]).days < 1):
            await update.message.reply_text("⏰ Бонус можно взять раз в 24 часа!")
            return
        bonus = random.randint(100, 500)
        data["money"] += bonus
        data["last_bonus"] = now.isoformat()
        await update.message.reply_text(f"🎁 Ежедневный бонус: +${bonus}! Теперь у тебя ${data['money']}.")
        save_player(user_id, data)
    elif "казна" in text:
        await update.message.reply_text(f"🏦 Казна: ${data['treasury']}")
    elif "сменить ник" in text and len(words) >= 2:
        new_nick = " ".join(words[1:])
        if len(new_nick) > 20:
            await update.message.reply_text("😢 Ник слишком длинный (максимум 20 символов)!")
            return
        data["nickname"] = new_nick
        await update.message.reply_text(f"👤 Новый ник: {new_nick}")
        save_player(user_id, data)
    elif "мой ник" in text:
        await update.message.reply_text(f"👤 Твой ник: {data['nickname']}")
    elif "мой статус" in text:
        await update.message.reply_text(f"🎖 Твой статус: {data['status']}")
    elif "статусы" in text:
        await update.message.reply_text("🎖 Доступные статусы: Золотой ($1000), Платиновый ($5000), Алмазный ($10000).")
    elif "рейтинг" in text:
        await update.message.reply_text(f"🏆 Твой рейтинг: {data['rating']}")
    elif "продать рейтинг" in text and len(words) == 2:
        try:
            amount = int(words[1])
            if data["rating"] < amount:
                await update.message.reply_text("😢 Недостаточно рейтинга!")
                return
            data["rating"] -= amount
            data["money"] += amount * 10
            await update.message.reply_text(f"💰 Продан рейтинг {amount} за ${amount * 10}. Теперь рейтинг: {data['rating']}, деньги: ${data['money']}.")
            save_player(user_id, data)
        except ValueError:
            await update.message.reply_text("💡 Введи количество рейтинга, например 'продать рейтинг 50'!")
    elif "энергия" in text:
        await update.message.reply_text(f"⚡ Энергия: {data['energy']}/100")
    elif "шахта" in text:
        await update.message.reply_text(f"⛏ Шахты: {len(data['mines'])}")
    elif "машины" in text:
        await update.message.reply_text(f"🚗 Машины: {', '.join(data['cars']) or 'Пусто'}")
    elif "телефоны" in text:
        await update.message.reply_text(f"📱 Телефоны: {', '.join(data['phones']) or 'Пусто'}")
    elif "самолёты" in text:
        await update.message.reply_text(f"✈ Самолёты: {', '.join(data['planes']) or 'Пусто'}")
    elif "дома" in text:
        await update.message.reply_text(f"🏠 Дома: {', '.join(data['houses']) or 'Пусто'}")
    elif "яхты" in text:
        await update.message.reply_text(f"⛵ Яхты: {', '.join(data['yachts']) or 'Пусто'}")
    elif "вертолёты" in text:
        await update.message.reply_text(f"🚁 Вертолёты: {', '.join(data['helicopters']) or 'Пусто'}")
    elif "казино" in text and len(words) == 2:
        try:
            bet = int(words[1])
            if data["money"] < bet:
                await update.message.reply_text("😢 Недостаточно денег!")
                return
            data["money"] -= bet
            if random.random() < 0.5:
                win = bet * 2
                data["money"] += win
                await update.message.reply_text(f"🎰 Вы выиграли! +${win}. Теперь у вас ${data['money']}.")
            else:
                await update.message.reply_text(f"🎰 Вы проиграли ${bet}. Теперь у вас ${data['money']}.")
            save_player(user_id, data)
        except ValueError:
            await update.message.reply_text("💡 Введи сумму, например 'казино 100'!")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Добро пожаловать! Я бот с рудами, бизнесом и многим другим. Используй /help для списка команд.")

# Настройка бота
TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise ValueError("Токен не установлен. Укажи TOKEN в переменных окружения.")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

if __name__ == "__main__":
    init_db()  # Инициализация базы данных при запуске
    run()
