#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import logging
import sys

import pytchat
from pytchat import config

from command.gift_purchase import GiftRedemption
from command.gift_redemption import GiftPurchase
from command.new_sponsor import NewSponsor
from command.super_chat import SuperChat
from command.super_sticker import SuperSticker
from command.text_message import TextMessage
from const import isOpenBrowser, CHANNELS
from define.enum_youtube import ChatType
from library.browser_util import get_web_driver, open_browser
from library.rcon_server import RconServer, disconnect_command, connect_command

global chat, vid, cid, cn


def main():
    global chat
    chat = pytchat.create(video_id=vid, logger=config.logger(__name__, logging.DEBUG))
    rc = RconServer()
    try:
        rc.connect()
        connect_command(rc, f"say [Debug] Connect Server: https://www.youtube.com/watch?v={vid}")
        while chat.is_alive():
            for c in chat.get().sync_items():
                chat_type = c.type
                id = hashlib.md5(c.id.encode()).hexdigest()
                if chat_type == ChatType.SUPER_CHAT.value:
                    # スーパチャット時のClass呼び出し処理
                    super_chat = SuperChat(rc)
                    super_chat.send_view_chat_command(c)
                    pass
                elif chat_type == ChatType.TEXT_MESSAGE.value:
                    # 通常チャット送信時のClass呼び出し処理
                    text_message = TextMessage(rc)
                    text_message.send_view_chat_command(c, cid, cn)
                    pass
                elif chat_type == ChatType.SUPER_STICKER.value:
                    # スーパスティッカー送信時のClass呼び出し処理
                    super_sticker = SuperSticker(rc)
                    super_sticker.send_view_chat_command(c)
                    pass
                elif chat_type == ChatType.NEW_SPONSOR.value:
                    # メンバー登録時のClass呼び出し処理
                    new_sponsor = NewSponsor(rc)
                    new_sponsor.send_view_chat_command(c)
                    pass
                elif chat_type == ChatType.GIFT_REDEMPTION.value:
                    # メンバーシップギフト受信(誰かが受け取った)時のClass呼び出し処理
                    gift_redemption = GiftRedemption(rc)
                    gift_redemption.send_view_chat_command(c)
                    pass
                elif chat_type == ChatType.GIFT_PURCHASE.value:
                    # メンバーシップギフト送信(誰かが送信した)時のClass呼び出し処理
                    gift_purchase = GiftPurchase(rc)
                    gift_purchase.send_view_chat_command(c)
                    pass
                else:
                    print(f'Error: unsupported chat type {chat_type}', file=sys.stderr)
                print(f"{c.datetime} {id} {c.type} {c.author.name}: {c.message} {c.amountString}")
    except pytchat.ChatdataFinished:
        print("chat data finished")
    except Exception as e:
        print(type(e), str(e))
    finally:
        chat.terminate()
        disconnect_command(rc, f"say [Debug] Disconnect Server: https://www.youtube.com/watch?v={vid}")
        rc.disconnect()


if __name__ == '__main__':
    global vid, cid, cn
    print("Start")
    print(f"受信する放送を選んでください (0 ~ {len(CHANNELS) - 1})")
    for k in CHANNELS:
        print(f'{k} : {CHANNELS[k]["channel_name"]} / https://www.youtube.com/watch?v={CHANNELS[k]["video_id"]}')

    TARGET_ID = int(input('Enter number: '))
    vid = CHANNELS[TARGET_ID]["video_id"]
    cid = CHANNELS[TARGET_ID]["channel_id"]
    cn = CHANNELS[TARGET_ID]["channel_name"]

    if isOpenBrowser:
        driver = get_web_driver()
        open_browser(driver=driver, url=f"https://www.youtube.com/live_chat?v={vid}")
    main()
    if isOpenBrowser:
        driver.close()
        driver.quit()
