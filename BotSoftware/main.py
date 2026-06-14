# CandyBot main loop: turn the crank and speak; the robot serves or reloads.
#   python -m BotSoftware.main

from BotSoftware.services import api_client
from BotSoftware.controllers import crank_controller as crank
from BotSoftware.controllers import candy_controller
from BotSoftware.controllers import reload_controller
from BotSoftware.controllers import display_controller as display


def main():
    while True:
        display.idle()
        crank.wait_for_turn()
        display.listening()
        response = api_client.record_and_send_while(crank.is_turning)

        action = response.get("action")
        items  = response.get("items", [])
        print(f"action: {action}  items: {items}")

        if action == "dispense":
            candy_controller.dispense(items)
        elif action == "reload":
            reload_controller.reload_with_voice_cancel()
        # cancel / nothing -> wait for the next turn


if __name__ == "__main__":
    main()
