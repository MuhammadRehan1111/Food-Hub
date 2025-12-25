"""
Database utilities for managing menu, orders, and deals data.
Uses JSON files with file locking for thread safety.
"""
import json
import os
import filelock
from datetime import datetime
from typing import Dict, List, Optional, Any
import config

# File locks for thread safety
menu_lock = filelock.FileLock(str(config.MENU_FILE) + ".lock")
orders_lock = filelock.FileLock(str(config.ORDERS_FILE) + ".lock")
deals_lock = filelock.FileLock(str(config.DEALS_FILE) + ".lock")


# =============================================================================
# MENU MANAGEMENT
# =============================================================================

def load_menu() -> Dict[str, List[Dict]]:
    """Load the complete menu from JSON file."""
    try:
        with menu_lock:
            if config.MENU_FILE.exists():
                with open(config.MENU_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except Exception as e:
        print(f"Error loading menu: {e}")
    return {}


def save_menu(menu: Dict[str, List[Dict]]) -> bool:
    """Save the complete menu to JSON file."""
    try:
        with menu_lock:
            with open(config.MENU_FILE, 'w', encoding='utf-8') as f:
                json.dump(menu, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving menu: {e}")
        return False


def get_menu_item(item_id: str) -> Optional[Dict]:
    """Get a specific menu item by ID."""
    menu = load_menu()
    for category, items in menu.items():
        for item in items:
            if item['item_id'] == item_id:
                return item
    return None


def add_menu_item(category: str, item: Dict) -> bool:
    """Add a new item to a category."""
    menu = load_menu()
    if category not in menu:
        menu[category] = []
    menu[category].append(item)
    return save_menu(menu)


def update_menu_item(item_id: str, updated_item: Dict) -> bool:
    """Update an existing menu item."""
    menu = load_menu()
    for category, items in menu.items():
        for i, item in enumerate(items):
            if item['item_id'] == item_id:
                menu[category][i] = updated_item
                return save_menu(menu)
    return False


def delete_menu_item(item_id: str) -> bool:
    """Delete a menu item by ID."""
    menu = load_menu()
    for category, items in menu.items():
        for i, item in enumerate(items):
            if item['item_id'] == item_id:
                del menu[category][i]
                return save_menu(menu)
    return False


def get_available_items(category: str = None) -> Dict[str, List[Dict]]:
    """Get only available items, optionally filtered by category."""
    menu = load_menu()
    result = {}
    for cat, items in menu.items():
        if category and cat != category:
            continue
        available = [item for item in items if item.get('available', True)]
        if available:
            result[cat] = available
    return result


# =============================================================================
# DEALS MANAGEMENT
# =============================================================================

def load_deals() -> List[Dict]:
    """Load all deals from JSON file."""
    try:
        with deals_lock:
            if config.DEALS_FILE.exists():
                with open(config.DEALS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except Exception as e:
        print(f"Error loading deals: {e}")
    return []


def save_deals(deals: List[Dict]) -> bool:
    """Save all deals to JSON file."""
    try:
        with deals_lock:
            with open(config.DEALS_FILE, 'w', encoding='utf-8') as f:
                json.dump(deals, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving deals: {e}")
        return False


def get_active_deals() -> List[Dict]:
    """Get all active deals sorted by order."""
    deals = load_deals()
    active = [d for d in deals if d.get('active', False)]
    return sorted(active, key=lambda x: x.get('order', 999))


def add_deal(deal: Dict) -> bool:
    """Add a new deal."""
    deals = load_deals()
    if 'order' not in deal:
        deal['order'] = get_next_deal_order()
    deals.append(deal)
    return save_deals(deals)


def update_deal(deal_id: str, updated_deal: Dict) -> bool:
    """Update an existing deal."""
    deals = load_deals()
    for i, deal in enumerate(deals):
        if deal['deal_id'] == deal_id:
            deals[i] = updated_deal
            return save_deals(deals)
    return False


def delete_deal(deal_id: str) -> bool:
    """Delete a deal by ID."""
    deals = load_deals()
    for i, deal in enumerate(deals):
        if deal['deal_id'] == deal_id:
            del deals[i]
            return save_deals(deals)
    return False


def get_deal(deal_id: str) -> Optional[Dict]:
    """Get a specific deal by ID."""
    deals = load_deals()
    for deal in deals:
        if deal['deal_id'] == deal_id:
            return deal
    return None


def get_next_deal_id() -> str:
    """Generate the next deal ID."""
    deals = load_deals()
    if not deals:
        return "d01"
    max_num = 0
    for deal in deals:
        try:
            num = int(deal['deal_id'][1:])
            max_num = max(max_num, num)
        except:
            pass
    return f"d{max_num + 1:02d}"


def get_next_deal_order() -> int:
    """Get the next order number for a new deal."""
    deals = load_deals()
    if not deals:
        return 1
    return max(d.get('order', 0) for d in deals) + 1


# =============================================================================
# ORDER MANAGEMENT
# =============================================================================

def load_orders() -> List[Dict]:
    """Load all orders from JSON file."""
    try:
        with orders_lock:
            if config.ORDERS_FILE.exists():
                with open(config.ORDERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except Exception as e:
        print(f"Error loading orders: {e}")
    return []


def save_orders(orders: List[Dict]) -> bool:
    """Save all orders to JSON file."""
    try:
        with orders_lock:
            with open(config.ORDERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(orders, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving orders: {e}")
        return False


def get_next_order_id() -> int:
    """Generate the next order ID."""
    orders = load_orders()
    if not orders:
        return 1001  # Start from 1001
    max_id = max(order.get('order_id', 1000) for order in orders)
    return max_id + 1


def create_order(table_id: int, items: List[Dict], total_price: float) -> Dict:
    """Create a new order with Pending status."""
    order = {
        "order_id": get_next_order_id(),
        "table_id": table_id,
        "items": items,
        "total_price": round(total_price, 2),
        "status": "Pending",
        "payment_method": None,
        "timestamp": datetime.now().isoformat(),
        "paid_timestamp": None
    }
    
    orders = load_orders()
    orders.append(order)
    save_orders(orders)
    return order


def update_order_status(order_id: int, status: str, payment_method: str = None) -> bool:
    """Update order status (e.g., mark as Paid)."""
    orders = load_orders()
    for order in orders:
        if order['order_id'] == order_id:
            order['status'] = status
            if status == "Paid":
                order['payment_method'] = payment_method
                order['paid_timestamp'] = datetime.now().isoformat()
            return save_orders(orders)
    return False


def get_pending_orders() -> List[Dict]:
    """Get all pending (unpaid) orders."""
    orders = load_orders()
    return [o for o in orders if o.get('status') == 'Pending']


def get_paid_orders() -> List[Dict]:
    """Get all paid orders (for analytics)."""
    orders = load_orders()
    return [o for o in orders if o.get('status') == 'Paid']


def get_orders_by_table(table_id: int) -> List[Dict]:
    """Get all orders for a specific table."""
    orders = load_orders()
    return [o for o in orders if o.get('table_id') == table_id]


def get_order_by_id(order_id: int) -> Optional[Dict]:
    """Get a specific order by ID."""
    orders = load_orders()
    for order in orders:
        if order['order_id'] == order_id:
            return order
    return None




# =============================================================================
# CATEGORY MANAGEMENT
# =============================================================================

CATEGORIES_FILE = config.DATA_DIR / "categories.json"
categories_lock = filelock.FileLock(str(CATEGORIES_FILE) + ".lock")


def load_categories() -> List[Dict]:
    """Load all categories from JSON file."""
    try:
        with categories_lock:
            if CATEGORIES_FILE.exists():
                with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except Exception as e:
        print(f"Error loading categories: {e}")
    return []


def save_categories(categories: List[Dict]) -> bool:
    """Save all categories to JSON file."""
    try:
        with categories_lock:
            with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(categories, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving categories: {e}")
        return False


def get_active_categories() -> List[Dict]:
    """Get all active categories sorted by order."""
    categories = load_categories()
    active = [c for c in categories if c.get('active', True)]
    return sorted(active, key=lambda x: x.get('order', 999))


def add_category(category: Dict) -> bool:
    """Add a new category."""
    categories = load_categories()
    categories.append(category)
    return save_categories(categories)


def update_category(category_id: str, updated_category: Dict) -> bool:
    """Update an existing category."""
    categories = load_categories()
    for i, cat in enumerate(categories):
        if cat['id'] == category_id:
            categories[i] = updated_category
            return save_categories(categories)
    return False


def delete_category(category_id: str) -> bool:
    """Delete a category by ID."""
    categories = load_categories()
    for i, cat in enumerate(categories):
        if cat['id'] == category_id:
            del categories[i]
            return save_categories(categories)
    return False


def get_next_category_order() -> int:
    """Get the next order number for a new category."""
    categories = load_categories()
    if not categories:
        return 1
    return max(c.get('order', 0) for c in categories) + 1


# =============================================================================
# ORDER SEARCH
# =============================================================================

def search_orders(order_id: int = None, status: str = None) -> List[Dict]:
    """Search orders by various criteria."""
    orders = load_orders()
    results = orders
    
    if order_id is not None:
        results = [o for o in results if o.get('order_id') == order_id]
    
    if status is not None:
        results = [o for o in results if o.get('status') == status]
    
    return results
