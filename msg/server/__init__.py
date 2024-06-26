"""Main logic of server program."""
import shlex
import asyncio
import gettext
from ..common import *
from art import text2art
from cowsay import cowsay
from pathlib import Path


_podir = str(Path(__file__).parents[1])
LOCALE = {
    "ru_RU.UTF-8": gettext.translation("msg", _podir, ["ru"], fallback=True),
    "en_US.UTF8": gettext.NullTranslations(),
}


def _(locale, text):
    return LOCALE.get(locale, LOCALE["en_US.UTF8"]).gettext(text)


def ngettext(locale: str, *args):
    """Translate."""
    return LOCALE.get(locale, LOCALE["en_US.UTF8"]).ngettext(*args)


def parse_create_chat(args: list):
    """Parse arguments for chat settings."""
    try:
        assert isinstance(args[0], str)
        print('0 done')

        result = {
            'name': args[0],
            'limit': None,
            'security_mode': False,
            'password': None,
            'autoright': Rights.EDITOR
        }

        for i in range(1, len(args)):
            match args[i]:
                case '-l' | '--limit':
                    assert args[i + 1].isdigit()
                    print('1 done')
                    result['limit'] = args[i + 1]
                case '-s' | '--security_mode':
                    print('2 done')
                    result['security_mode'] = True
                case '-p' | '--password':
                    print('3 done')
                    result['security_mode'] = True
                    result['password'] = args[i + 1]
                case '-a' | '--autoright':
                    assert args[i + 1] in ['Administrator', 'Editor', 'Reader', '0', '1', '2']
                    print('4 done')
                    result['autoright'] = arg2Rights(args[i + 1])
                case _:
                    continue
    except Exception:
        return {}

    print("LOG:", result)
    return result


def send_preparing(response: Message, chat: Chat = None) -> str:
    """Handle for sending command."""
    answer = []

    print(f'LOG:')
    print(response)

    answer.append(f'<{response._msg_ID}>')
    answer.append(f'({response._sender.username})')
    if response.reply_ID is not None:
        answer.append(f'Reply on <{response.reply_ID}>: \"{chat.stream[response.reply_ID].text}\"')
    answer.append('\n')

    match response.mode:
        case None:
            text = response.text
        case 'art':
            text = text2art(response.text, font=(response.style if response.style is not None else 'rand'))
        case 'cowsay':
            text = cowsay(response.text, cow=(response.style if response.style is not None else 'default'))
    answer.append(text + '\n')

    return '\n'.join(answer)

async def handler(reader, writer):
    """Async logic of handler."""
    client = writer.get_extra_info("peername")
    print(f'New Client on {client}')
    my_user = User(user_id=hash(client), username=hash(client))
    TM_users[my_user._user_id] = my_user
    TLB_names[my_user._user_id] = my_user._user_id


    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(my_user.queue.get())

    while not reader.at_eof():
        done, pending = await asyncio.wait(
            [send, receive],
            return_when=asyncio.FIRST_COMPLETED)

        for request in done:
            if request is send:
                send = asyncio.create_task(reader.readline())
                print(f'{client}: {request.result()}')
                if (not request.result()):
                    break

                args = shlex.split(request.result().decode())
                cmd, args = (args[0], args[1:]) if len(args) > 0 else ("", args)
                
                print("LOG: ", client, request.result().decode())
                print("LOG: ", args)
                answer = ""

                match cmd:
                    case 'entrance':
                        name = args[0]
                        my_user.username = name
                        del TLB_names[my_user._user_id]
                        TLB_names[name] = my_user._user_id
                        locale = my_user.get_locale()
                        answer = _(locale, "Welcome to Terminal Messenger, {}\n").format(my_user.username)

                    case 'show_chatlist':
                        Avaliable = []
                        Hidden = []
                        locale = my_user.get_locale()
                        Avaliable.append(_(locale, 'Avaliable chats:'))
                        Avaliable.append('_' * 20 + '\n')
                        Hidden.append(_(locale, 'Hidden chats:'))
                        Hidden.append('_' * 20 + '\n')

                        response = my_user.show_chatlist()
                        Avaliable.append(
                            '\n'.join(
                                [
                                    f" - {chat['name']} {chat['rights'] if chat['rights'] else ''}"
                                    for chat in response[0]
                                ]
                            )
                        )
                        Hidden.append(
                            '\n'.join(
                                [
                                    f" - {chat['name']} {chat['rights'] if chat['rights'] else ''}"
                                    for chat in response[1]
                                ]
                            )
                        )

                        answer = '\n'.join(Avaliable + Hidden) + '\n'

                    case 'open_chat':
                        name, *password = args
                        chat: Chat = TM_chats[name]
                        access = True
                        locale = my_user.get_locale()

                        if chat.security_mode:
                            access = chat.check_password(
                                password_to_check=password[0] if password else None
                            )

                        if not access:
                            answer = _(locale, "No access to chat\n")
                        else:
                            if my_user.open_chat(name):
                                for user_id in chat.people_in_chat_IRL:
                                    if user_id is not my_user._user_id:
                                        await chat.users[user_id]['queue'].put(
                                            _(locale, '{} join the chat').format(my_user.username)
                                        )

                            answer = '{0:_^30}\n'.format(name.upper())

                    case 'create_chat':
                        chat_statistics = parse_create_chat(args)
                        locale = my_user.get_locale()

                        if not chat_statistics:
                            answer = _(locale, "Broken data\n")
                        else:
                            my_user.create_chat(
                                name=chat_statistics["name"],
                                limit=chat_statistics["limit"],
                                security_mode=chat_statistics["security_mode"],
                                password=chat_statistics["password"],
                                autoright=chat_statistics["autoright"]
                            )

                            answer = '{0: ^30}\n'.format(
                                _(locale, 'You successfully create new chat {}').format(chat_statistics["name"])
                            )

                    case 'update_chat':
                        chat_statistics = parse_create_chat(args)
                        locale = my_user.get_locale()

                        if not chat_statistics:
                            answer = _(locale, "Broken data\n")
                        else:
                            try:
                                print(f"LOG: {chat_statistics}")
                                response = my_user.update_chat(
                                    name=chat_statistics["name"],
                                    limit=chat_statistics["limit"],
                                    security_mode=chat_statistics["security_mode"],
                                    password=chat_statistics["password"],
                                    autoright=chat_statistics["autoright"]
                                )
                            except TerminalError as e:
                                response = [e.__str__()]

                            answer = '\n'.join(response)

                    case 'add_to_chat':
                        username, name = args
                        user_id = TLB_names[username]
                        locale = my_user.get_locale()
                        
                        try:
                            response = my_user.add_to_chat(user_id=user_id, name=name)
                            await TM_users[user_id].queue.put(
                                _(locale, '{} invited you to {}').format(my_user.username, name)
                            )
                        except TerminalError as e:
                            response = [e.__str__()]


                        answer = '\n'.join(response)

                    case 'quit_chat':
                        my_user.quit_chat(args[0])
                        locale = my_user.get_locale()

                        for user_id in chat.people_in_chat_IRL:
                            await chat.users[user_id]['queue'].put(
                                _(locale, '{} leaves the chat').format(my_user.username)
                            )

                        answer = '{0: ^30}\n'.format(_(locale, 'You leave chat {}').format(args[0]))

                    case 'delete_chat':
                        chat: Chat = TM_chats[args[0]]
                        locale = my_user.get_locale()
                        try:
                            chat.check_Rights(my_user, Rights.ADMINISTRATOR)

                            for user_id in chat.people_in_chat_IRL:
                                if user_id is not my_user._user_id:
                                    await chat.users[user_id]['queue'].put(
                                        _(locale, '{} deletes the chat').format(my_user.username)
                                    )

                            my_user.delete_chat(chat.name)
                            answer = '{0: ^30}\n'.format(_(locale, 'You delete chat {}').format(args[0]))

                        except Exception as e:
                            answer = e.__str__()


                    case 'info_chat':
                        chat: Chat = TM_chats[args[0]]
                        locale = my_user.get_locale()

                        response = my_user.info_chat(chat.name)

                        answer = []
                        answer.append(_(locale, 'Name: {}').format(response["Name"]))
                        answer.append(_(locale, 'Creator: {}').format(response["Creator"]))
                        answer.append(_(locale, 'Participants:'))
                        for item in response['Participants']:
                            answer.append(f'  - {item[0]}({item[1]})' + ('\tonline' if item[0] in response['Online'] else ''))

                        answer = '\n'.join(answer)

                    case 'send':
                        response = []
                        try:
                            match len(args):
                                case 1:
                                    response = my_user.send(msg=args[0])
                                case 3:
                                    assert args[1] == '-m'
                                    response = my_user.send(msg=args[0], mode=args[2])
                                case 4:
                                    assert args[1] == '-m'
                                    response = my_user.send(msg=args[0], mode=args[2], style=args[3])
                                case _:
                                    assert False
                        except UnvalidChatError as e:
                            answer = str(e)
                        except Exception as q:
                            locale = my_user.get_locale()
                            answer = _(locale, 'broken data\n')

                        if isinstance(response, Message):
                            answer = send_preparing(response)
                            for user_id in my_user.current_chat.people_in_chat_IRL:
                                if user_id is not my_user._user_id:
                                    await chat.users[user_id]['queue'].put(answer)

                    case 'reply':
                        response = []
                        try:
                            assert args[0].isdigit()

                            match len(args):
                                case 2:
                                    response = my_user.send(msg=args[1], reply_id=int(args[0]))
                                case 4:
                                    assert args[2] == '-m'
                                    response = my_user.send(msg=args[1], mode=args[3], reply_id=int(args[0]))
                                case 5:
                                    assert args[2] == '-m'
                                    response = my_user.send(msg=args[1], mode=args[3], style=args[4], reply_id=int(args[0]))
                                case _:
                                    assert False
                        except UnvalidChatError as e:
                            answer = str(e)
                        except Exception as q:
                            locale = my_user.get_locale()
                            answer = _(locale, 'broken data\n')

                        print('LOG: in reply')
                        print(response)

                        if isinstance(response, Message):
                            answer = send_preparing(response, my_user.current_chat)
                            for user_id in my_user.current_chat.people_in_chat_IRL:
                                if user_id is not my_user._user_id:
                                    await chat.users[user_id]['queue'].put(answer)

                    case 'add_to_favourites':
                        try:
                            answer = ''
                            my_user.add_to_favourites(args[0])
                        except TerminalError as e:
                            answer = str(e)

                    case 'exit':
                        try:
                            answer = ''
                            my_user.exit_chat()
                        except TerminalError as e:
                            answer = str(e)

                    case 'locale':
                        my_user.set_locale(args[0])
                        answer = _(args[0], "Set up locale: {}").format(args[0])

                    case _:
                        continue

                print(f"~~~{answer}~~~")
                writer.write(answer.encode())

            if request is receive:
                receive = asyncio.create_task(my_user.queue.get())
                writer.write(f"{request.result()}\n".encode())
                await writer.drain()

    send.cancel()
    receive.cancel()
    del TM_users[my_user._user_id]
    writer.close()
    await writer.wait_closed()
    print(f'{client} left')


async def main(port=1337):
    """Async logic of server."""
    print('Start working')
    server = await asyncio.start_server(handler, '0.0.0.0', port)
    print('activate server')
    async with server:
        print('Server Forever')
        await server.serve_forever()


def start(port=1337):
    """Start the server."""
    asyncio.run(main(port))
