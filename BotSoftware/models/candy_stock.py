import sqlite3
from pathlib import Path

DB_PATH      = Path(__file__).parent.parent / "candy_stock.db"
VALID_COLORS = {"red", "orange", "yellow", "green", "purple"}


def _validate_color(color):
    if color.lower() not in VALID_COLORS:
        raise ValueError(f"Invalid color: '{color}'")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                color TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
            )
        """)
        for color in VALID_COLORS:
            conn.execute(
                "INSERT OR IGNORE INTO stock (color, quantity) VALUES (?, 0)", (color,)
            )
        conn.commit()


def get_stock(color=None):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        if color:
            _validate_color(color)
            row = conn.execute(
                "SELECT quantity FROM stock WHERE color = ?", (color.lower(),)
            ).fetchone()
            return {"color": color.lower(), "quantity": row[0] if row else 0}
        rows = conn.execute("SELECT color, quantity FROM stock ORDER BY color").fetchall()
        return {r[0]: r[1] for r in rows}


def add_candy(color, quantity=1):
    """Add candies and return the new total for that colour."""
    _validate_color(color)
    if quantity <= 0:
        raise ValueError("Quantity must be positive.")
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE stock SET quantity = quantity + ? WHERE color = ?",
            (quantity, color.lower())
        )
        conn.commit()
    return get_stock(color)["quantity"]


def remove_candy(color, quantity=1):
    _validate_color(color)
    if quantity <= 0:
        raise ValueError("Quantity must be positive.")
    if get_stock(color)["quantity"] < quantity:
        raise ValueError("Insufficient stock.")
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE stock SET quantity = quantity - ? WHERE color = ?",
            (quantity, color.lower())
        )
        conn.commit()


def set_stock(color, quantity):
    _validate_color(color)
    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE stock SET quantity = ? WHERE color = ?", (quantity, color.lower())
        )
        conn.commit()


def set_all(quantity):
    """Set every colour to the same quantity (handy for tests)."""
    for color in VALID_COLORS:
        set_stock(color, quantity)


def reset():
    """Empty the stock: every colour back to 0."""
    set_all(0)


def check_availability(items):
    init_db()
    missing = []
    for item in items:
        color     = item["color"].lower()
        quantity  = item.get("quantity", 1)
        available = get_stock(color)["quantity"]
        if available < quantity:
            missing.append({"color": color, "requested": quantity, "available": available})
    return {"ok": len(missing) == 0, "missing": missing}


def consume_from_command(items):
    check = check_availability(items)
    if not check["ok"]:
        raise ValueError(f"Insufficient stock: {check['missing']}")
    for item in items:
        remove_candy(item["color"], item.get("quantity", 1))
