import os
import logging
from time import sleep
from datetime import datetime
import json
import config
import forward
import threading

msg_num = 0
recevied_num = 0


def main():
    global msg_num, recevied_num

    # get message list
    output_message_output = "received"
    output_message_output = os.popen(
        'mmcli -m 0 --messaging-list-sms --output-json').read()
    output_message_list = json.loads(output_message_output)
    if (output_message_list["modem.messaging.sms"] == []):
        return 0
    elif (output_message_list["modem.messaging.sms"] != []):
        # count number of messages by rows
        output_message_num = len(output_message_list["modem.messaging.sms"])
        if (output_message_num > msg_num):
            msg_num = output_message_num
        else:
            return 0
    else:
        logging.error(output_message_output)
        return 0
    # get new message
    # use for to sovle to receive two or more message at the time
    for msg_index in range(recevied_num, msg_num):
        # In rare cases, SMS content loading is delayed
        sleep(0.3)
        msg_content = os.popen(
            "mmcli -m 0 -s %d --output-json" % (msg_index)).read()
        msg_content = json.loads(msg_content)
        number = msg_content["sms"]["content"]["number"]
        content = msg_content["sms"]["content"]["text"]
        timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        # save message
        if (config.save_messages):
            msg_save_content = json.dumps(
                {"number": number, "content": content, "timestamp": timestamp}, ensure_ascii=False)
            with open(config.save_messages_path, "a") as f:
                f.write(msg_save_content+"\n")

        logging.info("Recevied a new message Number: %s Content: %s Timestamp: %s" % (
            number, content, timestamp))

        # forward part
        for _, func in forward.__dict__.items():
            if callable(func) and func.__name__.startswith('forward_to_'):
                thread = threading.Thread(
                    target=func, args=(number, content, timestamp))
                thread.start()

        # update the received_num
        recevied_num = msg_num


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
    logging.info("SMS Forwarder started")
    logging.info("https://github.com/ryltech/sms_forwarder")

    while True:
        try:
            main()
        except Exception as e:
            logging.error(e)
        sleep(config.refresh_time)
