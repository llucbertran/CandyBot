from Software.services.api_client import record_and_send
from Software.models.candy_stock import (
    check_availability,
    consume_from_command,
    get_stock
)


def process_command():
    """Flux principal del CandyBot"""

    # 1. Mostrar stock actual
    stock = get_stock()
    print("\n── Stock actual ──")
    for color, qty in stock.items():
        print(f"{color}: {qty}")

    # 2. Obtenir comanda (API)
    print("\nGravant i enviant àudio...")
    response = record_and_send(seconds=4)

    action = response.get("action")
    items = response.get("items", [])

    print(f"\n→ Acció rebuda: {action}")
    print(f"→ Items: {items}")

    # 3. Validar acció
    if action != "dispense":
        print("No s'ha de dispensar res.")
        return

    if not items:
        print("No hi ha items a la comanda.")
        return

    # 4. Comprovar stock
    check = check_availability(items)

    if not check["ok"]:
        print("\nStock insuficient per a:")
        for m in check["missing"]:
            print(
                f"- {m['color']}: demanat {m['requested']}, disponible {m['available']}"
            )
        print("No s'ha dispensat res.")
        return

    # 5. SIMULACIÓ de dispensar (hardware)
    print("\nStock disponible. Dispensant:")
    for item in items:
        print(f"- {item['quantity']}x {item['color']}")

    # 👉 aquí anirà servo_control en futur

    # 6. Consumir stock
    consume_from_command(items)

    # 7. Mostrar stock actualitzat
    new_stock = get_stock()
    print("\n── Nou stock ──")
    for color, qty in new_stock.items():
        print(f"{color}: {qty}")
