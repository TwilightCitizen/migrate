import time
import threading

from kik_unofficial.client import KikClient
from kik_unofficial.callbacks import KikClientCallback

import kik_unofficial.datatypes.xmpp.chatting as chatting

from kik_unofficial.datatypes.xmpp.errors import LoginError
from kik_unofficial.datatypes.xmpp.login import ConnectionFailedResponse, TempBanElement
from kik_unofficial.datatypes.xmpp.roster import PeersInfoResponse
from kik_unofficial.datatypes.xmpp.xiphias import GroupSearchResponse


class JoinBombCallback(KikClientCallback):
    def __init__(self, username, password, target_group, join_message):
        self.client = KikClient(self, username, password, enable_console_logging=True)
        self.target_group = target_group
        self.join_message = join_message
        self.group_jid = None

        threading.Thread(target=self.client.wait_for_messages).start()

    def on_login_error(self, login_error: LoginError):
        if login_error.is_captcha():
            login_error.solve_captcha_wizard(self.client)

    def on_authenticated(self):
        global logged_in_count
        logged_in_count += 1

    def search_target_group(self):
        self.client.search_group(self.target_group)

    def on_group_search_response(self, response: GroupSearchResponse):
        found_group = response.groups[0]

        found_group_hashtag = found_group.hashtag
        found_group_jid = found_group.jid
        found_group_join_token = found_group.group_join_token

        self.group_jid = found_group_jid

        self.client.join_group_with_token(found_group_hashtag, found_group_jid, found_group_join_token)
        time.sleep(1)

        global joined_count
        joined_count += 1

        self.client.send_chat_message(found_group_jid, self.join_message)

    def leave_target_group(self):
        self.client.leave_group(self.group_jid)


join_bombs_credentials = [
    ["afriendlyreminder1", "xfarofur@sharklasers.com", "abc123ABC!@#"],
    ["afreindlyreminder2", "ujnlmpzi@sharklasers.com", "abc123ABC!@#"],
    ["afriendlyreminder3", "rggrufwr@sharklasers.com", "abc123ABC!@#"],
    ["afriendlyreminder4", "nxnosmnq@sharklasers.com", "abc123ABC!@#"],
    ["afriendlyreminder5", "rmsriggh@sharklasers.com", "abc123ABC!@#"]
]

index_username = 0
index_email_address = 1
index_password = 2

join_bombs = []

target_group = "dmvcdluv"
join_message = "Five burners raiding this group is quite harmless.  What's the toll if 100 burners raided them all?"

logged_in_count = 0
joined_count = 0

if __name__ == '__main__':
    for credentials in join_bombs_credentials:
        logged_in_so_far = logged_in_count

        join_bombs.append(JoinBombCallback(
            credentials[index_username],
            credentials[index_password],
            target_group,
            join_message))

        while logged_in_so_far == logged_in_count:
            time.sleep(1)

    for join_bomb in join_bombs:
        joined_so_far = joined_count

        join_bomb.search_target_group()

        while joined_so_far == joined_count:
            time.sleep(5)

    for join_bomb in join_bombs:
        join_bomb.leave_target_group()
