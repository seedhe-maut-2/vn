import os, urllib.parse, asyncio
from pyrogram import filters
from core import userbot, app
from pyrogram.types import Message
from config import OWNER_ID, SUDO_USERS, LOGGER_GROUP
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatType


is_busy = False


async def valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        if not result.scheme or not result.netloc:
            return "No Hoster Found For This URL. You should given a valid URL."
        if not (result.scheme in ["http", "https"]):
            return "Invalid URL scheme. Only http and https are supported."
        return "valid"
    except ValueError:
        return "Invalid URL. Please try with a valid URL."
    except Exception as err:
        return f"While validating URL. The Following Issue Happened:\n{err}\n\n**HOW TO SOLVE :**\n- Check If you gave a wrong url.\n- A url looks like : https://t.me/social_bots"



async def url_parse(link):
    valid = await valid_url(link)
    if valid != "valid":
        return False, False, False
    modified_string = link.replace("https://t.me", "").lstrip("/")
    shorted_link = [part for part in modified_string.strip().split("/") if part]
    if shorted_link[0].lower() == "c":
        if len(shorted_link) == 4:
            if shorted_link[-3].startswith("-100"):
                return int(shorted_link[-3]), int(shorted_link[-2]), int(shorted_link[-1]), "private"
            else:
                return int("-100" + shorted_link[-3]), int(shorted_link[-2]), int(shorted_link[-1]), "private"
        elif len(shorted_link) == 3:
            if shorted_link[-3].startswith("-100"):
                return int(shorted_link[-2]), False, int(shorted_link[-1]), "private"
            else:
                return int("-100" + shorted_link[-2]), False, int(shorted_link[-1]), "private"
        else:
            return False, False, False, "invalid"
    elif len(shorted_link) >= 2:
        if len(shorted_link) == 3:
            return f"@{shorted_link[-3]}", int(shorted_link[-2]), int(shorted_link[-1]), "public"
        else:
            return f"@{shorted_link[-2]}", False, int(shorted_link[-1]), "public"
    else:
        False, False, False, "Invalid"




# below are functions.
@app.on_message(filters.command("save") & filters.user(SUDO_USERS))
async def save(client, message, ub=userbot):
    global is_busy
    if is_busy:
        return await message.reply_text("Bot is already doing another task so please wait for completing previews task.")
    saved = 0
    failed = 0
    msg_splited = message.text.split(" ")
    if len(msg_splited) == 3:
        msgs_ids = [] # do not delete this empty list
        pure_msgs = [] # same to this
        start_from = msg_splited[1]
        end_here = msg_splited[2]
        chat_id_1, topic_id, ostart_msg_id, chat_type_1 = await url_parse(start_from)
        #print(chat_id_1, topic_id, ostart_msg_id, chat_type_1)
        chat_id_2, topic_id, oend_msg_id, chat_type_2 = await url_parse(end_here)
        #print(chat_id_2, topic_id, oend_msg_id, chat_type_2)
        if ostart_msg_id > oend_msg_id:
            start_msg_id = oend_msg_id
            end_msg_id = ostart_msg_id
        else:
            start_msg_id = ostart_msg_id
            end_msg_id = oend_msg_id

        if chat_id_1 != chat_id_2:
            return await message.reply_text("LOL! You gave me two diff channels/groups's link. Check your given urls.")
        
        if not start_msg_id or not end_msg_id:
            return await message.reply_text("You didn't gave message link from where I'll start saving and from where I'll stop saving!\n\n**EXAMPLE:**\n/save https://t.me/msg_link/23432 https://t.me/msg_link/23440")

        try:
            info = await message.reply_text("⏳ **Loading message ids...**")
            #print(1)
            if topic_id:
                #rint(2)
                useless_list = []
                #print(3)
                await message.reply_text("**TOPIC WISE GROUP FOUND!**, Bot will work slow if there are many deleted files.")
                async for messagex in ub.get_discussion_replies(chat_id_1, topic_id):
                    if messagex.media:
                        pure_msgs.append(messagex)
                        msgs_ids.append(messagex.id)
                await info.edit_text(f"{len(msgs_ids)} media msgs are Loaded.")
            else:
                #print(4, chat_id_1, start_msg_id, end_msg_id)
                try:
                    if chat_type_1 == "public":
                        chat_fetch = await app.get_chat(chat_id_1)
                        chat_id_541 = chat_fetch.id
                    else:
                        chat_fetch = await ub.get_chat(chat_id_1)
                        chat_id_541 = chat_fetch.id
                except Exception as err:
                    await message.reply_text(f"Error Found But Bot is still trying!\n\n{err}")
                    chat_id_541 = chat_id_1
                try:
                    async for messagex in ub.get_chat_history(chat_id=chat_id_1, min_id=start_msg_id, max_id=end_msg_id):
                        #print(messagex)
                        if messagex.media:
                            pure_msgs.append(messagex)
                            msgs_ids.append(messagex.id)
                    #print(5)
                except Exception as err:
                    #print(err)
                    pass
            await info.edit_text(f"⌛ **{len(msgs_ids)} Media Messages are loaded! Trying to save...**")
            is_busy = True
            if chat_type_1 == "public":
                #print("running public protocol")
                if not msgs_ids:
                    return await message.reply_text("Userbot not loaded chat history of this public channel!\n\nPlease try /save_manual")
                for save_msg_id in msgs_ids:
                    #print(123)
                    try:
                        #print(234)
                        await app.copy_message(message.chat.id, chat_id_1, save_msg_id)
                        saved += 1
                    except FloodWait as t:
                        #print(3254)
                        await asyncio.sleep(t.value)
                        await app.copy_message(message.chat.id, chat_id_1, save_msg_id)
                        saved += 1
                    except Exception as err:
                        #print(453)
                        failed += 1
                        continue
                await message.reply_text(f"{saved} every type of media files are saved {f'and {failed} failed' if failed else ''}.")
            else:
                for mmsg in pure_msgs:
                    try:
                        mediafile = await ub.download_media(mmsg)
                        await app.send_document(message.chat.id, mediafile)
                        saved += 1
                        try:
                            os.remove(mediafile)
                        except Exception as err:
                            continue
                    except FloodWait as t:
                        await asyncio.sleep(t.value)
                        mediafile = await ub.download_media(mmsg)
                        await app.send_document(message.chat.id, mediafile)
                        saved += 1
                        try:
                            os.remove(mediafile)
                        except Exception as err:
                            continue
                    except Exception as err:
                        failed += 1
                        continue
                await message.reply_text(f"{saved} every type of media files are saved {f'and {failed} failed' if failed else None}.")
            is_busy = False
            return
        except FloodWait as t:
            await asyncio.sleep(t.value)
        except Exception as err:
            await message.reply_text(err)
            try:
                await info.delete()
            except:
                pass
            return
    elif len(msg_splited) == 2:
        chat_id_1, topic_id, start_msg_id, chat_type_1 = await url_parse(msg_splited[1])
        #chat_id_1, chat_type_1, start_msg_id = await channel_address_lookups()
        if not start_msg_id or not chat_id_1:
            return await message.reply_text("This is an invalid URL!")
        info = await message.reply_text("⏳ **Loading message ids...**")
        is_busy = True
        if chat_type_1 == "public":
            try:
                await app.copy_message(message.chat.id, chat_id_1, start_msg_id)
                saved += 1
            except FloodWait as t:
                await asyncio.sleep(t.value)
                await app.copy_message(message.chat.id, chat_id_1, start_msg_id)
                saved += 1
            except Exception as err:
                failed += 1
            await info.edit_text(f"{saved} every type of media files are saved {f'and {failed} failed' if failed else ''}.")
        else:
            try:
                lel = await ub.get_messages(chat_id_1, start_msg_id)
                if lel.text:
                    return await app.send_message(message.chat.id, lel.text)
                mediafile = await ub.download_media(lel)
                await app.send_document(message.chat.id, mediafile)
                saved += 1
                try:
                    os.remove(mediafile)
                except Exception as err:
                    pass
            except FloodWait as t:
                await asyncio.sleep(t.value)
                lel = await ub.get_messages(chat_id_1, start_msg_id)
                mediafile = await ub.download_media(lel)
                await app.send_document(message.chat.id, mediafile)
                saved += 1
                try:
                    os.remove(mediafile)
                except Exception as err:
                    pass
            except Exception as err:
                failed += 1
                pass
            await info.edit_text(f"{saved} every type of media files are saved {f'and {failed} failed' if failed else ''}.")
        is_busy = False
        return
    else:
        is_busy = False
        return await message.reply_text("Wrong command! Use this command like:\n\n/save https://t.me/lol/234234 https://t.me/lol/2342387")



async def generate_sequence(start_from, number_of_msgs):
    result = []  # Empty list to store the sequence

    if int(number_of_msgs) < 0:
        for i in range(start_from, start_from + int(number_of_msgs), -1):
            result.append(i)
    elif int(number_of_msgs) > 0:
        for i in range(start_from, start_from + int(number_of_msgs)):
            result.append(i)
    else:
        result.append(start_from)

    return result  # Return the generated sequence as a list


# below are functions.
@app.on_message(filters.command("save_manual") & filters.user(SUDO_USERS))
async def save(client, message, ub=userbot):
    global is_busy
    if is_busy:
        return await message.reply_text("Bot is already doing another task so please wait for completing previews task.")
    saved = 0
    failed = 0
    msg_splited = message.text.split(" ")
    if len(msg_splited) == 3:
        start_from = msg_splited[1]
        end_here = msg_splited[2]
        chat_id_1, topic_id, start_msg_id, chat_type_1 = await url_parse(start_from)
        #print(chat_id_1, topic_id, ostart_msg_id, chat_type_1)
        try:
            number_of_messages = int(end_here)
        except Exception as err:
            return await message.reply_text(err)
        #print(chat_id_2, topic_id, oend_msg_id, chat_type_2)
        
        try:
            info = await message.reply_text("⏳ **Loading message ids...**")
            try:
                msgs_ids = await generate_sequence(start_msg_id, end_here)
            except Exception as err:
                return await message.reply_text(err)
            await info.edit_text(f"⌛ **{len(msgs_ids)} Media Messages are loaded! Trying to save...**")
            is_busy = True
            if chat_type_1 == "public":
                for save_msg_id in msgs_ids:
                    try:
                        await app.copy_message(message.chat.id, chat_id_1, save_msg_id)
                        saved += 1
                    except FloodWait as t:
                        await asyncio.sleep(t.value)
                        await app.copy_message(message.chat.id, chat_id_1, save_msg_id)
                        saved += 1
                    except Exception as err:
                        failed += 1
                        continue
                await message.reply_text(f"{saved} every type of media files are saved {f'and {failed} failed' if failed else ''}.")

            else:
                for mag_id in msgs_ids:
                    try:
                        mmsg = await app.get_messages(chat_id_1, mag_id)
                    except:
                        continue
                    try:
                        if mmsg.media:
                            mediafile = await ub.download_media(mmsg)
                            await app.send_document(message.chat.id, mediafile)
                            saved += 1
                            try:
                                os.remove(mediafile)
                            except FloodWait as t:
                                await asyncio.sleep(t.value)
                            except Exception as err:
                                continue
                    except FloodWait as t:
                        await asyncio.sleep(t.value)
                        mediafile = await ub.download_media(mmsg)
                        await app.send_document(message.chat.id, mediafile)
                        saved += 1
                        try:
                            os.remove(mediafile)
                        except FloodWait as t:
                            await asyncio.sleep(t.value)
                        except Exception as err:
                            continue
                    except Exception as err:
                        failed += 1
                        continue
                await message.reply_text(f"{saved} every type of media files are saved {f'and {failed} failed' if failed else None}.")
            is_busy = False
            return
        except FloodWait as t:
            await asyncio.sleep(t.value)
        except Exception as err:
            await message.reply_text(err)
            try:
                await info.delete()
            except:
                pass
            return
    else:
        is_busy = False
        return await message.reply_text("Wrong command! Use this command like:\n\n/save https://t.me/lol/100 -69")


@app.on_message(filters.command("free") & filters.user(SUDO_USERS))
async def save(client, message, ub=userbot):
    global is_busy
    if not is_busy:
        return await message.reply_text(f"Bot isn't in busy mode.\nis_busy = {is_busy}")
    else:
        is_busy = False
        return await message.reply_text(f"Is_busy var is forcefully changed to {is_busy} by {message.from_user.mention}")
