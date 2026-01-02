"""
Customer Order Page - Premium Redesigned with 3 Main Tabs
Tabs: Chatbot (multilingual), Menu (with images), Deals
Dark luxury theme with gold accents.
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.database import (
    load_menu, create_order, get_menu_item,
    load_categories, get_active_categories,
    get_active_deals, get_deal
)
from utils.gemini_client import RestaurantChatbot
from utils.auth import check_password
import config

# Role-based access control
if 'role' not in st.session_state:
    st.session_state.role = "customer"

# Only Customer and Admin can see this page

# Auto-clear session for "New Customer" if requested or on first visit
if st.sidebar.button("🔄 Start New Order / Clear Chat"):
    for key in list(st.session_state.keys()):
        if key not in ['role', 'authenticated', 'admin_language']:
            del st.session_state[key]
    st.rerun()

# Page configuration
st.set_page_config(
    page_title="Order Food - Restaurant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Luxury Theme CSS
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Global dark theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f0f1a 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide Default Sidebar Navigation */
    /* [data-testid="stSidebarNav"] {
        display: none !important;
    } */
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(184, 134, 11, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(212, 175, 55, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .main-header h2 {
        font-family: 'Playfair Display', serif;
        color: #d4af37;
        margin: 0;
        font-size: 2rem;
    }
    
    .table-badge {
        display: inline-block;
        background: linear-gradient(135deg, #d4af37, #b8860b);
        color: #0a0a0f;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        margin-top: 0.75rem;
    }
    
    /* Category cards with images */
    .category-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.9) 0%, rgba(15, 15, 26, 0.95) 100%);
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid rgba(212, 175, 55, 0.2);
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
        padding: 1rem;
    }
    
    .category-card:hover {
        border-color: rgba(212, 175, 55, 0.6);
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .category-card.selected {
        border-color: #d4af37;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
    }
    
    .category-image {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 0.5rem;
        border: 2px solid rgba(212, 175, 55, 0.3);
    }
    
    .category-name {
        font-family: 'Playfair Display', serif;
        color: #d4af37; /* Golden color */
        font-size: 0.95rem;
        margin: 0;
        font-weight: 600;
    }
    
    /* Menu item cards */
    .menu-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.9) 0%, rgba(15, 15, 26, 0.95) 100%);
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(212, 175, 55, 0.2);
        transition: all 0.3s ease;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    
    .menu-card:hover {
        transform: translateY(-5px);
        border-color: rgba(212, 175, 55, 0.5);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4);
    }
    
    .menu-image {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }
    
    .menu-info {
        padding: 1.25rem;
    }
    
    .menu-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        color: #d4af37; /* Golden color */
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .menu-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #ffffff; /* White text */
        margin-bottom: 0.75rem;
    }
    
    .menu-price {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        color: #d4af37;
        font-weight: 600;
    }
    
    /* Deal cards */
    .deal-card {
        background: linear-gradient(145deg, rgba(212, 175, 55, 0.15) 0%, rgba(184, 134, 11, 0.1) 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .deal-badge {
        display: inline-block;
        background: linear-gradient(135deg, #d4af37, #b8860b);
        color: #0a0a0f;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    
    .deal-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        background: linear-gradient(135deg, #d4af37 0%, #f7e98e 50%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .deal-desc {
        font-family: 'Inter', sans-serif;
        color: #ffffff; /* White text */
        margin-bottom: 1rem;
    }
    
    /* Cart styling */
    .cart-header {
        font-family: 'Playfair Display', serif;
        color: #d4af37;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    
    .cart-item {
        background: rgba(26, 26, 46, 0.8);
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
    
    .cart-total {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        color: #d4af37;
        text-align: right;
        padding: 1rem 0;
        border-top: 1px solid rgba(212, 175, 55, 0.2);
        margin-top: 1rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(26, 26, 46, 0.5);
        padding: 10px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 10px;
        color: #ffffff; /* White text */
        font-family: 'Inter', sans-serif;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(184, 134, 11, 0.1));
        color: #d4af37;
    }
    
    /* Chat styling */
    .stChatMessage {
        background: #ffffff !important;
        border: 1px solid rgba(212, 175, 55, 0.5) !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] p {
        color: #1a1a2e !important; /* Dark text for readability on white */
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(184, 134, 11, 0.1)) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #d4af37 !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.3), rgba(184, 134, 11, 0.2)) !important;
        border-color: rgba(212, 175, 55, 0.6) !important;
        transform: translateY(-2px);
    }
    
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #d4af37, #b8860b) !important;
        color: #0a0a0f !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    /* Section header */
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        background: linear-gradient(135deg, #d4af37 0%, #f7e98e 50%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    /* Footer */
    .premium-footer {
        text-align: center;
        padding: 1.5rem;
        color: #ffffff; /* White text */
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        border-top: 1px solid rgba(212, 175, 55, 0.1);
        margin-top: 2rem;
    }
    
    /* Ensure white text on blue/dark backgrounds */
    .stAlert {
        color: #ffffff !important;
    }
    .stAlert [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }
    .stAlert [data-testid="stMarkdownContainer"] b {
        color: #d4af37 !important; /* Golden for bold text in alerts */
    }
    /* Fixed size for images in bill/summary */
    .bill-item-image {
        width: 60px !important;
        height: 60px !important;
        object-fit: cover !important;
        border-radius: 8px !important;
    }
    
    .category-image {
        width: 100px !important;
        height: 100px !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Get table_id from URL parameters or Session State
query_params = st.query_params
table_id = query_params.get("table_id", None)

if not table_id:
    table_id = st.session_state.get("table_id", None)

# Validate table_id
if table_id is None:
    st.markdown("""
    <div class="main-header">
        <h2>🍽️ Welcome to Our Restaurant</h2>
    </div>
    """, unsafe_allow_html=True)

    
    st.error("⚠️ No table detected!")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: rgba(212, 175, 55, 0.05); border-radius: 15px; border: 1px solid rgba(212, 175, 55, 0.1); margin-bottom: 2rem;">
        <h3 style="color: #d4af37; font-family: 'Playfair Display', serif; margin-bottom: 0.5rem;">How to Order</h3>
        <p style="color: #ffffff; font-family: 'Inter', sans-serif; font-size: 1.1rem; margin-bottom: 1.5rem;">Please scan the QR code at your table to start ordering.</p>
        <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.3), transparent); margin: 1.5rem 0;"></div>
        <p style="color: #d4af37; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">For Demo/Testing:</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<p style="color: #d4af37; font-weight: 600; margin-bottom: -15px;">Enter table number:</p>', unsafe_allow_html=True)
    demo_table = st.number_input("Enter table number:", min_value=1, max_value=50, value=1, label_visibility="collapsed")
    if st.button("Start Ordering", type="primary"):
        st.query_params["table_id"] = str(demo_table)
        st.rerun()
    st.stop()

try:
    table_id = int(table_id)
except ValueError:
    st.error("Invalid table ID. Please scan the QR code again.")
    st.stop()

# Header
st.markdown(f"""
<div class="main-header">
    <h2>Welcome to Our Restaurant</h2>
    <div class="table-badge">Table {table_id}</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state if not done
if 'cart_items' not in st.session_state:
    st.session_state.cart_items = []
if 'cart_version' not in st.session_state:
    st.session_state.cart_version = 0
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "🌟 Welcome to our restaurant! I'm your AI assistant. How can I help you discover our delicious menu today? / ہمارے ریستوراں میں خوش آمدید! میں آپ کا AI اسسٹنٹ ہوں۔ میں آج آپ کو ہمارا لذیذ مینو دریافت کرنے میں کس طرح مدد کر سکتا ہوں؟ / مرحبًا بكم في مطعمنا! أنا مساعدك الذكي. كيف يمكنني مساعدتك في اكتشاف قائمتنا اللذيذة اليوم؟"}
    ]
if 'order_submitted' not in st.session_state:
    st.session_state.order_submitted = False
if 'active_order' not in st.session_state:
    st.session_state.active_order = None

# Load data once
menu = load_menu()
categories = get_active_categories()

# Ensure chatbot is initialized
if 'chatbot' not in st.session_state or st.session_state.chatbot is None:
    st.session_state.chatbot = RestaurantChatbot(
        menu_data=menu,
        table_id=table_id,
        deals=get_active_deals()
    )

# Helper function to add item to cart
def add_to_cart(item_id: str, name: str, price: float, quantity: int = 1):
    # Check if item already exists in cart
    for i, item in enumerate(st.session_state.cart_items):
        if item['item_id'] == item_id:
            item['quantity'] += quantity
            new_qty = item['quantity']
            
            # Increment version to force widget refresh
            st.session_state.cart_version += 1
                
            # Trigger state update explicitly
            st.session_state.cart_items = st.session_state.cart_items
            return new_qty
            
    # If not found, add new
    st.session_state.cart_items.append({
        "item_id": item_id,
        "name": name,
        "price": round(float(price), 2),
        "quantity": quantity
    })
    st.session_state.cart_version += 1
    return quantity

# Helper function to calculate cart total
def get_cart_total():
    return sum(item['price'] * item['quantity'] for item in st.session_state.cart_items)

def format_bill():
    """Format the current cart as a readable bill."""
    if not st.session_state.cart_items:
        return ""
    
    bill = "```\n"
    bill += "╔════════════════════════════════════╗\n"
    bill += "║            CURRENT BILL            ║\n"
    bill += "╠════════════════════════════════════╣\n"
    bill += f"║ {'Item':<18} {'Qty':>4} {'Price':>10} ║\n"
    bill += "╟────────────────────────────────────╢\n"
    
    total = 0
    for item in st.session_state.cart_items:
        name = item['name']
        item_id = str(item['item_id'])
        qty = item['quantity']
        price = item['price'] * qty
        
        # Display main item line
        name_trunc = name[:18]
        bill += f"║ {name_trunc:<18} {qty:>4} {price:>10.2f} ║\n"
        
        # If it's a deal, show breakdown
        if item_id.startswith('deal_'):
            did = item_id.replace('deal_', '')
            deal = get_deal(did)
            if deal and 'applicable_items' in deal:
                # Count items in the deal
                from collections import Counter
                item_counts = Counter(deal['applicable_items'])
                for uid, count in item_counts.items():
                    # Get item name
                    menu_item = get_menu_item(uid)
                    if menu_item:
                        sub_name = menu_item['name'].get('en', 'Item')
                        # Indent sub-items
                        bill += f"║   - {count}x {sub_name[:12]:<12} {'':<4} {'':<10} ║\n"

        total += price
    
    bill += "╠════════════════════════════════════╣\n"
    bill += f"║ {'TOTAL':<18} {'':>4} {total:>10.2f} ║\n"
    bill += "╚════════════════════════════════════╝\n"
    bill += "```"
    return bill

# Sidebar - Cart
with st.sidebar:
    st.markdown('<p class="cart-header">Your Order</p>', unsafe_allow_html=True)
    
    if st.session_state.order_submitted and st.session_state.active_order:
        st.success("✅ Order Submitted!")
        order = st.session_state.active_order
        st.markdown(f"**Order #{order['order_id']}**")
        st.markdown(format_bill()) # Changed to new format_bill
        st.markdown("""
        <div style="background: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
            <p style="color: #d4af37; font-weight: 600; margin: 0;">✨ Please proceed to cashier for payment. ✨</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("New Order", type="primary", use_container_width=True):
            st.session_state.cart_items = []
            st.session_state.order_submitted = False
            st.session_state.active_order = None
            st.rerun()
    
    elif not st.session_state.cart_items:
        st.markdown("""
        <div style="background: rgba(212, 175, 55, 0.1); border: 2px solid #d4af37; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0; box-shadow: 0 0 20px rgba(212, 175, 55, 0.15);">
            <p style="color: #ffffff; font-size: 1.1rem; margin: 0;">Your cart is empty.</p>
            <p style="color: #d4af37; font-weight: 700; font-size: 1.2rem; margin: 0.75rem 0 0 0; text-transform: uppercase; letter-spacing: 1px;">Add items from the menu!</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Cart with items
        for i, item in enumerate(st.session_state.cart_items):
            col_img, col_txt = st.columns([1, 3])
            with col_img:
                # Get item image
                if item['item_id'].startswith('deal_'):
                    deal_id = item['item_id'].replace('deal_', '')
                    item_details = get_deal(deal_id)
                else:
                    item_details = get_menu_item(item['item_id'].split('_')[0])
                    
                img_url = item_details.get('image', '') if item_details else ''
                if img_url:
                    if isinstance(img_url, str) and img_url.startswith('http'):
                        st.markdown(f'<img src="{img_url}" class="bill-item-image">', unsafe_allow_html=True)
                    elif isinstance(img_url, str) and Path(img_url).exists():
                        st.markdown(f'<img src="{img_url}" class="bill-item-image">', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="bill-item-image" style="background: #222; display: flex; align-items: center; justify-content: center;"></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="bill-item-image" style="background: #222; display: flex; align-items: center; justify-content: center;"></div>', unsafe_allow_html=True)
            
            with col_txt:
                st.markdown(f"**{item['name']}**")
                cols = st.columns([1, 1])
                with cols[0]:
                    new_qty = st.number_input(
                        "Qty", 
                        min_value=0, 
                        max_value=20, 
                        value=item['quantity'],
                        key=f"cart_qty_{item['item_id']}_{i}_v{st.session_state.get('cart_version', 0)}",
                        label_visibility="collapsed"
                    )
                with cols[1]:
                    st.write(f"{item['price'] * item['quantity']} SAR")
                
                if new_qty != item['quantity']:
                    if new_qty == 0:
                        st.session_state.cart_items.pop(i)
                    else:
                        st.session_state.cart_items[i]['quantity'] = new_qty
                    st.session_state.cart_version += 1
                    st.rerun()
        
        st.divider()
        st.markdown(format_bill())
        
        # Payment Status and Download Bill
        if st.session_state.get('active_order'):
            from utils.database import load_orders
            all_orders = load_orders()
            current_order = next((o for o in all_orders if o['order_id'] == st.session_state.active_order['order_id']), None)
            
            if current_order:
                if current_order['status'] == "Paid":
                    st.success("✅ Order Paid & Confirmed!")
                    
                    # Bill Download Button
                    receipt_text = f"RESTAURANT RECEIPT\nOrder #: {current_order['order_id']}\nTable: {current_order['table_id']}\n"
                    receipt_text += "-"*30 + "\n"
                    for itm in current_order['items']:
                        receipt_text += f"{itm['name']:<18} x{itm['quantity']:>2} {itm['price']*itm['quantity']:>8.2f} SAR\n"
                    receipt_text += "-"*30 + "\n"
                    receipt_text += f"TOTAL: {current_order['total_price']:>17.2f} SAR\n"
                    receipt_text += "Thank you for dining with us!"
                    
                    st.download_button(
                        label="📥 Download Bill",
                        data=receipt_text,
                        file_name=f"bill_{current_order['order_id']}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    if st.button("New Order", type="primary", use_container_width=True):
                        st.session_state.cart_items = []
                        st.session_state.order_submitted = False
                        st.session_state.active_order = None
                        st.rerun()
                else:
                    st.info("🕒 Order pending cashier confirmation...")
                    if st.button("Refresh Status"):
                        st.rerun()
        
        # Confirm Order Button (Only if no active order)
        if not st.session_state.get('active_order'):
            if st.button("Confirm Order", type="primary", use_container_width=True):
                if not st.session_state.cart_items:
                    st.error("Cart is empty!")
                else:
                    order = create_order(
                        table_id=table_id,
                        items=st.session_state.cart_items,
                        total_price=get_cart_total()
                    )
                    st.session_state.active_order = order
                    st.session_state.order_submitted = True
                    st.toast("Order confirmed! Please wait for cashier.", icon=None)
                    st.rerun()
        
        if not st.session_state.get('active_order'):
            if st.button("Clear Cart", use_container_width=True):
                st.session_state.cart_items = []
                st.rerun()

# Main content - Three tabs
tab1, tab2, tab3 = st.tabs(["Quick Menu", "AI Waiter", "Premium Deals"])

# =============================================================================
# TAB 1: QUICK MENU (with images)
# =============================================================================
with tab1:
    st.markdown('<p class="section-header">Explore Our Delicious Menu</p>', unsafe_allow_html=True)
    
    # Category selection
    if 'selected_menu_category' not in st.session_state:
        st.session_state.selected_menu_category = "All"
    
    # Display category buttons with images
    st.markdown('<p style="color: #d4af37; font-size: 1.2rem; font-weight: 600; font-family: \'Playfair Display\', serif;">Select a Category:</p>', unsafe_allow_html=True)
    
    # Filter categories to only active ones
    active_cats = [c for c in categories if c.get('active', True)]
    
    cols = st.columns(len(active_cats) + 1)
    
    # "All" category
    with cols[0]:
        is_all_selected = st.session_state.selected_menu_category == "All"
        st.markdown(f"""
        <div class="category-card {'selected' if is_all_selected else ''}">
            <img src="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200" class="category-image">
            <p class="category-name">All</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select All", key="cat_btn_all", use_container_width=True):
            st.session_state.selected_menu_category = "All"
            st.rerun()

    for i, cat in enumerate(active_cats):
        with cols[i + 1]:
            cat_image = cat.get('image', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200')
            is_selected = st.session_state.selected_menu_category == cat['name']
            
            st.markdown(f"""
            <div class="category-card {'selected' if is_selected else ''}">
                <img src="{cat_image}" class="category-image" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200'">
                <p class="category-name">{cat['name']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Select {cat['name']}", key=f"cat_btn_{cat['id']}", use_container_width=True):
                st.session_state.selected_menu_category = cat['name']
                st.rerun()
    
    st.divider()
    
    # Display menu items
    display_items = []
    if st.session_state.selected_menu_category == "All":
        for cat_name, items in menu.items():
            display_items.extend(items)
    elif st.session_state.selected_menu_category in menu:
        display_items = menu[st.session_state.selected_menu_category]
    
    # Filter available items
    available_items = [itm for itm in display_items if itm.get('available', True)]
    
    if not available_items:
        st.info("No items found in this section.")
    else:
        # Display in grid (3 columns)
        cols = st.columns(3)
        for i, item in enumerate(available_items):
            with cols[i % 3]:
                name = item['name'].get('en', 'Unknown')
                desc = item.get('description', {}).get('en', '')
                price = item['price']
                image_url = item.get('image', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400')
                
                st.markdown(f"""
                <div class="menu-card">
                    <img src="{image_url}" class="menu-image" alt="{name}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'">
                    <div class="menu-info">
                        <div class="menu-name">{name}</div>
                        <div class="menu-desc">{desc[:60] + '...' if len(desc) > 60 else desc}</div>
                        <div class="menu-price">{price} SAR</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Add to Cart", key=f"add_menu_{item['item_id']}_{i}", use_container_width=True):
                    new_qty = add_to_cart(item['item_id'], name, price)
                    st.toast(f"Added {name} (Qty: {new_qty})! ✨", icon="✅")
                    st.rerun()

# =============================================================================
# TAB 2: AI WAITER (Multilingual)
# =============================================================================
with tab2:
    st.markdown('<p class="section-header">Chat with our AI Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #ffffff; font-size: 0.9rem;">Supports English • اردو • العربية</p>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message... / اپنا پیغام لکھیں / اكتب رسالتك"):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Get chatbot response
        with st.spinner("..."):
            response = st.session_state.chatbot.send_message(prompt)
        
        # Parse for hidden order tags: [ORDER: item_id, quantity]
        import re
        order_tags = re.findall(r'\[ORDER:\s*([^,]+),\s*(\d+)\]', response)
        
        # Process orders if found
        items_added = []
        if order_tags:
            for item_id, qty in order_tags:
                try:
                    # Clean the ID (remove potential whitespace) and parse qty
                    item_id = item_id.strip() 
                    qty = int(qty)
                    
                    # Try menu first
                    item_details = get_menu_item(item_id)
                    if item_details:
                        name = item_details['name'].get('en', 'Unknown')
                        price = item_details['price']
                        add_to_cart(item_id, name, price, qty)
                        items_added.append(f"{qty}x {name}")
                    else:
                        # Try deals next
                        did = item_id.replace('deal_', '')
                        deal_details = get_deal(did)
                        if deal_details:
                            name = deal_details['name'].get('en', 'Deal')
                            price = deal_details.get('price', 0.0)
                            add_to_cart(f"deal_{did}", name, price, qty)
                            items_added.append(f"{qty}x {name}")
                except Exception as e:
                    print(f"Error processing tag: {e}")
            
            # Clean response text (remove tags)
            response = re.sub(r'\[ORDER:.*?\]', '', response).strip()
            
            if items_added:
                st.toast(f"Added to cart: {', '.join(items_added)} 🛒", icon="✅")
                # Add a visible reminder to confirm logic
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": "✅ **Items added to cart!** Please review your order in the sidebar and click **'Confirm Order'** to send it to the kitchen."
                })
        
        # Add assistant response
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Quick actions
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Show Menu", use_container_width=True):
            # Same as "View Menu" but via button
            st.session_state.selected_menu_category = "All"
            # Switch to tab 2? Streamlit tabs can't be switched programmatically easily without rerun trickery or just setting state.
            # But the quick action here was originally chatting.
            st.session_state.chat_messages.append({"role": "user", "content": "Show me the menu"})
            response = st.session_state.chatbot.send_message("Show me the full menu with prices")
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("View Deals", use_container_width=True):
            st.session_state.chat_messages.append({"role": "user", "content": "What deals are available?"})
            response = st.session_state.chatbot.send_message("Show me all the available deals and bundles.")
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("View Cart", use_container_width=True):
            if st.session_state.cart_items:
                bill = format_bill() # Already uses st.session_state.cart_items
                st.session_state.chat_messages.append({"role": "assistant", "content": f"Here's your current order:\n\n{bill}"})
            else:
                st.session_state.chat_messages.append({"role": "assistant", "content": "Your cart is empty. Would you like to see our special deals?"})
            st.rerun()
    
    with col4:
        if st.button("New Chat", use_container_width=True):
            st.session_state.chat_messages = []
            menu = load_menu()
            deals = get_active_deals()
            st.session_state.chatbot = RestaurantChatbot(menu, table_id, deals)
            welcome = st.session_state.chatbot.get_welcome_message()
            st.session_state.chat_messages.append({"role": "assistant", "content": welcome})
            st.rerun()

# =============================================================================
# TAB 3: DEALS (Premium Deals Only)
# =============================================================================
with tab3:
    st.markdown('<p class="section-header">Deals</p>', unsafe_allow_html=True)
    
    active_deals = get_active_deals()
    
    if not active_deals:
        st.info("No active deals at the moment. Please check back later!")
    else:
        # Create a grid for deals
        cols = st.columns(2)
        for idx, deal in enumerate(active_deals):
            with cols[idx % 2]:
                # Calculate original price
                discount = deal.get('discount_percent', 0)
                original_price = round(deal['price'] / (1 - discount / 100), 2) if discount < 100 else deal['price']
                
                st.markdown(f"""
                <div class="menu-card">
                    <img src="{deal.get('image', 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400')}" class="menu-image" onerror="this.src='https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400'">
                    <div class="menu-info">
                        <div class="menu-name">{deal['name'].get('en', 'Deal')}</div>
                        <div class="menu-desc">{deal.get('description', {}).get('en', '')}</div>
                        <div class="menu-price">{deal['price']} SAR {f'<span style="text-decoration: line-through; color: #888; font-size: 0.8rem;">{original_price} SAR</span>' if discount > 0 else ''}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Interaction area for the deal
                col_q, col_b = st.columns([1, 2])
                with col_q:
                    qty = st.number_input("Qty", min_value=1, max_value=10, value=1, key=f"qty_deal_{deal['deal_id']}")
                with col_b:
                    if st.button(f"Add to Cart", key=f"add_deal_{deal['deal_id']}", use_container_width=True):
                        add_to_cart(
                            item_id=f"deal_{deal['deal_id']}",
                            name=deal['name'].get('en', 'Deal'),
                            price=deal['price'],
                            quantity=qty
                        )
                        st.toast(f"Added {qty}x {deal['name'].get('en', 'Deal')} to cart!", icon="🛒")
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="premium-footer">
    Table {table_id} | Need help? Use the Chatbot!
</div>
""", unsafe_allow_html=True)
