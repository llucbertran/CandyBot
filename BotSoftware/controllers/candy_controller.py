from BotSoftware.controllers import servo_controller
from BotSoftware.controllers import display_controller as display
from BotSoftware.models.candy_stock import check_availability, consume_from_command


def dispense(items):
    """Dispense the requested items, if there's enough stock."""
    if not items:
        display.empty_command()
        return

    check = check_availability(items)
    if not check["ok"]:
        for m in check["missing"]:
            print(f"  {m['color']}: demanat {m['requested']}, disponible {m['available']}")
        m = check["missing"][0]
        display.low_stock(m["color"], m["available"])
        return

    for item in items:
        color, qty = item["color"], item["quantity"]
        print(f"  Dispensant {qty}x {color}")
        display.dispensing(color, qty)
        servo_controller.dispense(color, qty)

    consume_from_command(items)
    display.served()
