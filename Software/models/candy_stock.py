
# models/candy_stock.py

import sqlite3
from pathlib import Path
from typing import Optional

# Ruta de la base de dades
DB_PATH = Path(__file__).parent.parent / "candy_stock.db"

# Colors vàlids
VALID_COLORS = {"red", "orange", "yellow", "green", "purple"}


# ── INIT ─────────────────────────────────────────────

def init_db():
    """Crea la BD i la taula si no existeixen."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                color TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
            )
        """)

        for color in VALID_COLORS:
            conn.execute(
                "INSERT OR IGNORE INTO stock (color, quantity) VALUES (?, 0)",
                (color,)
            )

        conn.commit()


def _validate_color(color: str):
    if color.lower() not in VALID_COLORS:
        raise ValueError(f"Color no vàlid: '{color}'")


# ── LECTURA ──────────────────────────────────────────

def get_stock(color: Optional[str] = None) -> dict:
    """Retorna tot el stock o el d’un color concret."""
    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        if color:
            _validate_color(color)
            row = conn.execute(
                "SELECT quantity FROM stock WHERE color = ?",
                (color.lower(),)
            ).fetchone()
            return {"color": color.lower(), "quantity": row[0] if row else 0}

        else:
            rows = conn.execute(
                "SELECT color, quantity FROM stock ORDER BY color"
            ).fetchall()
            return {r[0]: r[1] for r in rows}


# ── MODIFICACIÓ ─────────────────────────────────────

def add_candy(color: str, quantity: int = 1):
    """Afegeix caramels."""
    _validate_color(color)

    if quantity <= 0:
        raise ValueError("La quantitat ha de ser positiva.")

    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE stock SET quantity = quantity + ? WHERE color = ?",
            (quantity, color.lower())
        )
        conn.commit()


def remove_candy(color: str, quantity: int = 1):
    """Resta caramels."""
    _validate_color(color)

    if quantity <= 0:
        raise ValueError("La quantitat ha de ser positiva.")

    current = get_stock(color)["quantity"]

    if current < quantity:
        raise ValueError("Stock insuficient.")

    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE stock SET quantity = quantity - ? WHERE color = ?",
            (quantity, color.lower())
        )
        conn.commit()


def set_stock(color: str, quantity: int):
    """Fixa el valor exacte."""
    _validate_color(color)

    if quantity < 0:
        raise ValueError("No pot ser negatiu.")

    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE stock SET quantity = ? WHERE color = ?",
            (quantity, color.lower())
        )
        conn.commit()


# ── LÒGICA DE COMANDES ──────────────────────────────

def check_availability(items: list) -> dict:
    """Comprova si hi ha suficient stock."""
    init_db()

    missing = []

    for item in items:
        color = item["color"].lower()
        quantity = item.get("quantity", 1)

        available = get_stock(color)["quantity"]

        if available < quantity:
            missing.append({
                "color": color,
                "requested": quantity,
                "available": available,
            })

    return {
        "ok": len(missing) == 0,
        "missing": missing
    }


def consume_from_command(items: list):
    """Resta stock si tot és correcte."""
    check = check_availability(items)

    if not check["ok"]:
        raise ValueError(f"Stock insuficient: {check['missing']}")

    for item in items:
        remove_candy(item["color"], item.get("quantity", 1))