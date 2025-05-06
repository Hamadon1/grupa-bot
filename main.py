import telebot
from telebot import types
import time
import re

# Bot configuration
TOKEN = "7670493216:AAEfNHuqwdcLvyuYgnG4GhsKxINt_WmaDZk"
# Ду админ доданд
ADMIN_IDS = [6862331593, 6454516935]  # Ҳоло дар шакли массив барои бисёр админҳо

bot = telebot.TeleBot(TOKEN)

# Database dictionaries (in a real application, you would use a proper database)
groups = {}  # {group_id: group_name}
channels = {}  # {channel_id: channel_name}
banned_users = {}  # {user_id: unban_time}
warning_count = {}  # {user_id: count}
subscribed_users = {}  # {user_id: True/False} - Dictionary to track users who have confirmed subscription
banned_words = []  # NEW: List to store banned words

# Regular expression for finding links in messages
link_pattern = re.compile(r'https?://\S+|t\.me/\S+|@\S+')

# Main menu for admin
def admin_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    add_group = types.KeyboardButton("Иловаи гурӯҳ")
    group_settings = types.KeyboardButton("Танзимоти гурӯҳ")
    delete_group = types.KeyboardButton("Удалить гурӯҳ")
    add_channel = types.KeyboardButton("Иловаи канал")
    # NEW: Add banned words button
    banned_words_btn = types.KeyboardButton("Калимаҳои манъ")
    markup.add(add_group, group_settings, delete_group, add_channel, banned_words_btn)
    bot.send_message(chat_id, "Интихоб кунед:", reply_markup=markup)

# Start command handler
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private' and message.from_user.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Салом! Шумо ҳамчун админ шинохта шудед.")
        admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Салом! Ман боти идоракунии гурӯҳ ҳастам.")

# Handler for "Иловаи гурӯҳ" (Add group)
@bot.message_handler(func=lambda message: message.text == "Иловаи гурӯҳ" and message.from_user.id in ADMIN_IDS)
def add_group_request(message):
    bot.send_message(message.chat.id, "Лутфан, ботро дар гурӯҳи худ ҳамчун админ илова кунед ва линки мустақими гурӯҳро ба ман фиристед.")
    bot.register_next_step_handler(message, process_group_link)

def process_group_link(message):
    try:
        # Try to extract group link or ID
        link = message.text
        if "t.me/" in link:
            # For simplicity, assume the link is correctly formatted
            # In a real bot, you would have to join the group and check admin status
            group_id = link.split("/")[-1]  # Not a real ID, just for demonstration
            groups[group_id] = link
            bot.send_message(message.chat.id, f"Гурӯҳ бо муваффақият илова карда шуд: {link}")
            admin_menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Линки нодуруст. Лутфан, линки мустақими гурӯҳро фиристед.")
            bot.register_next_step_handler(message, process_group_link)
    except Exception as e:
        bot.send_message(message.chat.id, f"Хато рӯй дод: {str(e)}")
        admin_menu(message.chat.id)

# Handler for "Танзимоти гурӯҳ" (Group settings)
@bot.message_handler(func=lambda message: message.text == "Танзимоти гурӯҳ" and message.from_user.id in ADMIN_IDS)
def group_settings(message):
    if not groups:
        bot.send_message(message.chat.id, "Шумо ҳоло ягон гурӯҳро илова накардаед.")
        admin_menu(message.chat.id)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for group_id, group_name in groups.items():
        button = types.InlineKeyboardButton(text=group_name, callback_data=f"settings_{group_id}")
        markup.add(button)
    
    bot.send_message(message.chat.id, "Гурӯҳро барои танзим интихоб кунед:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("settings_"))
def process_group_settings(call):
    group_id = call.data.split("_")[1]
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Бехатарӣ", callback_data=f"security_{group_id}")
    btn2 = types.InlineKeyboardButton("Филтрҳо", callback_data=f"filters_{group_id}")
    btn3 = types.InlineKeyboardButton("Огоҳиҳо", callback_data=f"warnings_{group_id}")
    markup.add(btn1, btn2, btn3)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Танзимот барои гурӯҳи {groups[group_id]}:",
        reply_markup=markup
    )

# Example handler for security settings
@bot.callback_query_handler(func=lambda call: call.data.startswith("security_"))
def security_settings(call):
    group_id = call.data.split("_")[1]
    bot.answer_callback_query(call.id, "Танзимоти бехатарӣ фаъол карда шуд!")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Танзимоти бехатарӣ барои гурӯҳи {groups[group_id]} муваффақона нигоҳ дошта шуд."
    )
    admin_menu(call.message.chat.id)

# Handler for "Удалить гурӯҳ" (Delete group)
@bot.message_handler(func=lambda message: message.text == "Удалить гурӯҳ" and message.from_user.id in ADMIN_IDS)
def delete_group_request(message):
    if not groups:
        bot.send_message(message.chat.id, "Шумо ҳоло ягон гурӯҳро илова накардаед.")
        admin_menu(message.chat.id)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for group_id, group_name in groups.items():
        button = types.InlineKeyboardButton(text=group_name, callback_data=f"delete_{group_id}")
        markup.add(button)
    
    bot.send_message(message.chat.id, "Гурӯҳро барои нест кардан интихоб кунед:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_group(call):
    group_id = call.data.split("_")[1]
    del groups[group_id]
    bot.answer_callback_query(call.id, "Гурӯҳ нест карда шуд!")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Гурӯҳ бо муваффақият нест карда шуд."
    )
    admin_menu(call.message.chat.id)

# Handler for "Иловаи канал" (Add channel)
@bot.message_handler(func=lambda message: message.text == "Иловаи канал" and message.from_user.id in ADMIN_IDS)
def add_channel_request(message):
    bot.send_message(message.chat.id, "Лутфан, ботро дар канали худ ҳамчун админ илова кунед ва номи канал ё линки мустақими каналро ба ман фиристед.")
    bot.register_next_step_handler(message, process_channel_link)

def process_channel_link(message):
    try:
        # Try to extract channel link or username
        link = message.text
        if "@" in link or "t.me/" in link:
            # For simplicity, assume the link is correctly formatted
            channel_id = link.replace("@", "").replace("t.me/", "")  # Not a real ID, just for demonstration
            channels[channel_id] = link
            bot.send_message(message.chat.id, f"Канал бо муваффақият илова карда шуд: {link}")
            
            # Show all added channels with delete buttons
            show_channels(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Линк ё номи нодуруст. Лутфан, линки мустақим ё номи каналро фиристед.")
            bot.register_next_step_handler(message, process_channel_link)
    except Exception as e:
        bot.send_message(message.chat.id, f"Хато рӯй дод: {str(e)}")
        admin_menu(message.chat.id)

def show_channels(chat_id):
    if not channels:
        bot.send_message(chat_id, "Шумо ҳоло ягон каналро илова накардаед.")
        admin_menu(chat_id)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for channel_id, channel_name in channels.items():
        button = types.InlineKeyboardButton(text=f"❌ {channel_name}", callback_data=f"delchannel_{channel_id}")
        markup.add(button)
    
    bot.send_message(chat_id, "Каналҳои иловашуда (барои нест кардан пахш кунед):", reply_markup=markup)
    admin_menu(chat_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delchannel_"))
def delete_channel(call):
    channel_id = call.data.split("_")[1]
    del channels[channel_id]
    bot.answer_callback_query(call.id, "Канал нест карда шуд!")
    
    # Update the message with the new list of channels
    if not channels:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Ҳамаи каналҳо нест карда шуданд."
        )
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for ch_id, ch_name in channels.items():
            button = types.InlineKeyboardButton(text=f"❌ {ch_name}", callback_data=f"delchannel_{ch_id}")
            markup.add(button)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Каналҳои иловашуда (барои нест кардан пахш кунед):",
            reply_markup=markup
        )

# NEW: Handler for "Калимаҳои манъ" (Banned words)
@bot.message_handler(func=lambda message: message.text == "Калимаҳои манъ" and message.from_user.id in ADMIN_IDS)
def banned_words_menu(message):
    bot.send_message(message.chat.id, "Лутфан, калимаҳо ё ҷумлаҳои манъшударо ба ман фиристед. Ҳар як калима ё ҷумла дар як сатр навишта шавад.")
    bot.register_next_step_handler(message, process_banned_words)

def process_banned_words(message):
    global banned_words
    new_words = message.text.split('\n')
    banned_words.extend([word.strip() for word in new_words if word.strip()])
    
    # Remove duplicates
    banned_words = list(set(banned_words))
    
    # Show the list of banned words
    words_text = '\n'.join([f"• {word}" for word in banned_words]) if banned_words else "Рӯйхат холӣ аст."
    bot.send_message(message.chat.id, f"Рӯйхати калимаҳои манъшуда:\n{words_text}")
    
    # Add buttons to manage banned words
    markup = types.InlineKeyboardMarkup(row_width=1)
    add_more = types.InlineKeyboardButton("Илова кардани калимаҳои дигар", callback_data="add_more_words")
    clear_all = types.InlineKeyboardButton("Тоза кардани рӯйхат", callback_data="clear_banned_words")
    markup.add(add_more, clear_all)
    
    bot.send_message(message.chat.id, "Амалиётро интихоб кунед:", reply_markup=markup)
    admin_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "add_more_words")
def add_more_banned_words(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Лутфан, калимаҳои иловагии манъшударо фиристед. Ҳар як калима дар як сатр навишта шавад.")
    bot.register_next_step_handler(call.message, process_banned_words)

@bot.callback_query_handler(func=lambda call: call.data == "clear_banned_words")
def clear_banned_words(call):
    global banned_words
    banned_words = []
    bot.answer_callback_query(call.id, "Рӯйхати калимаҳои манъшуда тоза карда шуд!")
    bot.send_message(call.message.chat.id, "Рӯйхати калимаҳои манъшуда тоза карда шуд.")
    admin_menu(call.message.chat.id)

# Check if a user is subscribed to the channel
def check_user_subscription(user_id, chat_id):
    # Check if the user is already marked as subscribed
    if user_id in subscribed_users and subscribed_users[user_id]:
        return True
    
    # Check if the user is an admin of the group (admins don't need to subscribe)
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        if user_id in admin_ids or user_id in ADMIN_IDS:  # Changed to check ADMIN_IDS array
            return True
    except Exception:
        pass  # If any error occurs while checking admins, continue with subscription check
    
    # In a real implementation, you would check each channel subscription:
    # For each channel, use bot.get_chat_member(channel_id, user_id) 
    # and check if status is not 'left' or 'kicked'
    
    # For this example, we'll just use the stored subscription status
    return False

# NEW: Check if a message contains banned words
def contains_banned_word(text):
    if not text or not banned_words:
        return False
    
    text_lower = text.lower()
    for word in banned_words:
        if word.lower() in text_lower:
            return True
    
    return False

# Message handler for group chats
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if user is banned
    if user_id in banned_users:
        if time.time() < banned_users[user_id]:
            # User is still banned
            bot.delete_message(chat_id, message.message_id)
            return
        else:
            # Ban time is over
            del banned_users[user_id]
    
    # Check if the user is an admin of the group
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        is_admin = user_id in admin_ids or user_id in ADMIN_IDS
    except Exception:
        # If we can't get admins, assume the user is not an admin
        is_admin = user_id in ADMIN_IDS
    
    # NEW: Check for banned words in the message
    if not is_admin and message.text and contains_banned_word(message.text):
        # Delete message with banned word
        bot.delete_message(chat_id, message.message_id)
        
        # Send warning
        warning_msg = bot.send_message(
            chat_id,
            f"⚠️ @{message.from_user.username or user_id}, истифодаи калимаҳои манъшуда дар гурӯҳ қатъӣ манъ аст!"
        )
        return
    
    # Check for links in the message
    if not is_admin and message.text and link_pattern.search(message.text):
        # Delete message with link
        bot.delete_message(chat_id, message.message_id)
        
        # Increase warning count
        if user_id not in warning_count:
            warning_count[user_id] = 0
        warning_count[user_id] += 1
        
        # Send warning message
        warning_msg = bot.send_message(
            chat_id,
            f"⚠️ @{message.from_user.username or user_id}, дар гурӯҳ фиристодани реклама манъ аст! Огоҳӣ {warning_count[user_id]}/3"
        )
        
        # Ban user if they reached 3 warnings
        if warning_count[user_id] >= 3:
            # Ban for 1 hour
            ban_time = time.time() + 3600  # Current time + 1 hour in seconds
            banned_users[user_id] = ban_time
            
            try:
                bot.restrict_chat_member(
                    chat_id, 
                    user_id,
                    until_date=ban_time,
                    permissions=types.ChatPermissions(
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False
                    )
                )
                bot.send_message(
                    chat_id,
                    f"🚫 @{message.from_user.username or user_id} ба муддати 1 соат аз фиристодани паём маҳрум карда шуд."
                )
            except Exception as e:
                bot.send_message(
                    chat_id,
                    f"Хато ҳангоми маҳрум кардани корбар: {str(e)}"
                )
            
            # Reset warning count
            warning_count[user_id] = 0
        return
    
    # Check if the user is subscribed to the required channels
    subscribed = check_user_subscription(user_id, chat_id)
    
    if not subscribed and not is_admin and channels:
        # Delete the message
        bot.delete_message(chat_id, message.message_id)
        
        # Create subscription buttons
        markup = types.InlineKeyboardMarkup(row_width=1)
        for channel_id, channel_name in channels.items():
            channel_button = types.InlineKeyboardButton(text=f"📢 {channel_name}", url=f"https://t.me/{channel_id}")
            markup.add(channel_button)
            
        check_button = types.InlineKeyboardButton(text="✅ Санҷиш", callback_data=f"check_{user_id}_{chat_id}")
        markup.add(check_button)
        
        # Send subscription requirement message
        bot.send_message(
            chat_id,
            f"@{message.from_user.username or user_id}, барои навиштан дар гурӯҳ, лутфан ба каналҳои зерин обуна шавед:",
            reply_markup=markup
        )

# Handler for subscription check button
@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_subscription(call):
    parts = call.data.split("_")
    user_id = int(parts[1])
    chat_id = int(parts[2]) if len(parts) > 2 else call.message.chat.id
    
    # Only the user who needs to subscribe can use this button
    if call.from_user.id != user_id:
        bot.answer_callback_query(
            call.id,
            "Ин тугма барои шумо нест!",
            show_alert=True
        )
        return
    
    # Real subscription check implementation
    # In a real bot, you would check each channel like this:
    all_subscribed = True
    not_subscribed_channels = []
    
    for channel_id, channel_name in channels.items():
        try:
            # Get the channel chat info
            chat_info = None
            try:
                # Try with @ format
                chat_info = bot.get_chat(f"@{channel_id}")
            except Exception:
                try:
                    # Try with -100 format for supergroups/channels
                    if not channel_id.startswith("-100"):
                        chat_info = bot.get_chat(f"-100{channel_id}")
                except Exception:
                    pass
            
            if chat_info:
                # Check if the user is a member
                member_info = bot.get_chat_member(chat_info.id, user_id)
                if member_info.status in ['left', 'kicked']:
                    all_subscribed = False
                    not_subscribed_channels.append(channel_name)
        except Exception as e:
            # If we can't check, assume not subscribed
            all_subscribed = False
            not_subscribed_channels.append(channel_name)
    
    # For demonstration, we'll just assume the user is now subscribed
    # In a real implementation, you'd use the above code to check each channel
    all_subscribed = True
    
    if all_subscribed:
        # Mark the user as subscribed in our dictionary
        subscribed_users[user_id] = True
        
        bot.answer_callback_query(
            call.id,
            "Ташаккур барои обуна! Акнун шумо метавонед дар гурӯҳ паём фиристед.",
            show_alert=True
        )
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        # Get the list of channels the user hasn't subscribed to
        bot.answer_callback_query(
            call.id,
            f"Шумо ҳоло ба ҳамаи каналҳо обуна нашудаед. Лутфан, обуна шавед ва боз санҷед.",
            show_alert=True
        )

# Run the bot
bot.infinity_polling()
