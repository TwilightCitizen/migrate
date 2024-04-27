from kik_unofficial.client import KikClient
from kik_unofficial.callbacks import KikClientCallback
import kik_unofficial.datatypes.xmpp.chatting as chatting
from kik_unofficial.datatypes.xmpp.errors import LoginError
from kik_unofficial.datatypes.xmpp.login import ConnectionFailedResponse, TempBanElement
from kik_unofficial.datatypes.xmpp.roster import PeersInfoResponse

authentication_details = {
    "username": "username",
    "email_address": "email_address",
    "password": "password"
}

default_group_config = {
    "greeting": "Welcome!",
    "farewell": "Farewell!",
    "limit_users": True,
    "user_limit": 98,
    "limit_silence": True,
    "silence_limit": 1,
    # "expect_specific_phrase": "phrase"
}


class JoyBot(KikClientCallback):
    def __init__(self):
        self.client = KikClient(self, "username", "password", enable_console_logging=True)
        self.user_groups = dict()

        self.client.wait_for_messages()

    # def on_chat_message_received(self, chat_message: chatting.IncomingChatMessage):
    #     self.client.send_chat_message(chat_message.from_jid, f'"{chat_message.from_jid}" said "{chat_message.body}"!')

    def on_login_error(self, login_error: LoginError):
        print("Login Error")

        if login_error.is_captcha():
            login_error.solve_captcha_wizard(self.client)

    def on_connection_failed(self, response: ConnectionFailedResponse):
        print("Connection Failed")
        print(response.message)

        if response.is_backoff:
            print(response.backoff_seconds)

    def on_temp_ban_received(self, response: TempBanElement):
        print("Temp Ban Received")
        print(response.ban_title)
        print(response.ban_message)
        print(response.ban_end_time)

    def on_disconnected(self):
        print("Disconnected")

    def on_group_status_received(self, response: chatting.IncomingGroupStatus):
        user_jid = response.status_jid
        group_jid = response.group_jid
        status = response.status

        print("Group Status Received")
        print(response.raw_element)

        if "has joined the chat" in status or "has been invited to the group by" in status:
            print(f'User with JID of {user_jid} joined Group with JID of {group_jid}.')

            if user_jid in self.user_groups.keys():
                self.user_groups[user_jid].append(group_jid)
            else:
                self.user_groups[user_jid] = [group_jid]

            self.client.request_info_of_users(response.status_jid)

    def on_peer_info_received(self, response: PeersInfoResponse):
        user = response.users[0]

        print("Peer Info Received")
        print(response.raw_element)

        if user.profile_pic is None and user.jid in self.user_groups.keys():
            user_groups = self.user_groups.pop(user.jid)

            for group in user_groups:
                self.client.send_chat_message(group,
                  f'{user.display_name}, you have no profile picture set. '
                  + 'You are being removed from the group. '
                  + 'You may come back once you have set a profile picture. '
                  + 'Do not bother appealing this decision to the group admins.')

                self.client.remove_peer_from_group(group, user.jid)

    def on_group_sysmsg_received(self, response: chatting.IncomingGroupSysmsg):
        print("Group Sysmsg Received")
        print(response.sysmsg)


if __name__ == '__main__':
    # Creates the bot and start listening for incoming chat messages
    callback = JoyBot()
