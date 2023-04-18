from enum import Enum
import charlogger, tls_client, typing, time, argparse

"""
Made by github.com/chaarlottte
OOP is life
"""

class RelationshipType(Enum):
    NONE = 0
    FRIEND = 1
    BLOCKED = 2
    PENDING_INCOMING = 3
    PENDING_OUTGOING = 4
    IMPLICIT = 5

class FriendRemover():
    def __init__(self, token: str) -> None:
        self.session = tls_client.Session(client_identifier="chrome_112")
        self.logger = charlogger.Logger(debug=True)

        self.token = token
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Authorization": self.token
        })
        pass

    def start(self) -> None:
        requests = self.get_pending_requests()
        self.logger.info(title="SCRAPER", data=f"Found {len(requests)} incoming friend requests. Removing...")

        for req in requests:
            success, wait = self.reject_request(req)
            if not success:
                requests.append(req)
            time.sleep(wait)

        self.logger.info("Completed! :)")
    
    def reject_request(self, req: dict) -> typing.Tuple[bool, float]:
        user_id = req.get("user").get("id")
        user_name = req.get("user").get("username") + "#" + req.get("user").get("discriminator")

        resp = self.session.delete(f"https://discord.com/api/v9/users/@me/relationships/{user_id}")

        if resp.status_code == 204:
            self.logger.valid(title="REMOVED", data=f"Rejected {user_name}'s friend request successfully!")
            return True, 0
        else:
            self.logger.error(title="ERROR", data=f"Encountered error ({resp.status_code}): {resp.text}")
            # Was going to make this wait as long as you were ratelimited,
            # But I never encountered a rate limit during my testing, lol.
            return False, 3

    def get_pending_requests(self) -> list:
        pending_reqs = []

        resp = self.session.get("https://discord.com/api/v9/users/@me/relationships")

        if resp.status_code == 200:
            for rel in resp.json():
                if rel.get("type") == RelationshipType.PENDING_INCOMING.value:
                    pending_reqs.append(rel)
        elif resp.status_code == 401:
            self.logger.error(title="ERROR", data=f"Your token is invalid! :(")
            exit()
        else:
            self.logger.error(title="ERROR", data=f"Unknown error :( (code: {resp.status_code} - error: {resp.text})")
            exit()
        
        return pending_reqs

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--token", help="Your Discord account's token.", required=True)
    args = argParser.parse_args()

    FriendRemover(token=args.token).start()