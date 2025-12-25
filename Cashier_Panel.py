"""
Cashier Panel - Order Payment Processing
Premium redesigned with dark luxury theme and golden accents.
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.database import (
    get_pending_orders, 
    get_paid_orders, 
    update_order_status, 
    load_orders,
    get_order_by_id,
    search_orders,
    save_orders,
    get_deal,
    get_menu_item
)
from utils.auth import check_password, logout # Added auth imports
import config

# Role-based access control
if 'role' not in st.session_state:
    st.session_state.role = "customer"

# Only Cashier and Admin can see this page

# Page configuration
st.set_page_config(
    page_title="Cashier Panel - Restaurant",
    page_icon=None,
    layout="wide"
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .cashier-header {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(184, 134, 11, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(212, 175, 55, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .cashier-header h2 {
        font-family: 'Playfair Display', serif;
        color: #d4af37;
        margin: 0;
        font-size: 2.2rem;
        background: linear-gradient(135deg, #d4af37 0%, #f7e98e 50%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    .cashier-header p {
        font-family: 'Inter', sans-serif;
        color: #ffffff; /* White text */
        margin: 0.5rem 0 0 0;
        letter-spacing: 1px;
    }
    
    .order-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.9) 0%, rgba(15, 15, 26, 0.95) 100%);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    
    .order-card:hover {
        border-color: rgba(212, 175, 55, 0.5);
        transform: translateY(-3px);
    }
    
    .pending-badge {
        background: rgba(212, 175, 55, 0.1);
        color: #d4af37;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    .paid-badge {
        background: rgba(40, 167, 69, 0.1);
        color: #28a745;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(40, 167, 69, 0.3);
    }
    
    .table-number {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #d4af37;
        margin: 0;
    }
    
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        background: linear-gradient(135deg, #d4af37 0%, #f7e98e 50%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.2rem;
        font-weight: 700;
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
    
    /* Metric styling */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.8) 0%, rgba(15, 15, 26, 0.9) 100%);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 15px;
        padding: 1rem;
    }
    
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #ffffff !important; /* White text */
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
    
    .receipt-box {
        background: rgba(10, 10, 15, 0.8);
        border: 1px solid rgba(212, 175, 55, 0.3);
        padding: 1.5rem;
        border-radius: 15px;
        font-family: 'Courier New', monospace;
        color: #d4af37;
    }
    
    /* Global label and header contrast fixes */
    label[data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    h3 {
        color: #d4af37 !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
    }
    
    /* Expander (Order Box) styling */
    [data-testid="stExpander"] {
        background: rgba(26, 26, 46, 0.5) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 12px !important;
        margin-bottom: 0.8rem !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stExpander"]:hover {
        border-color: rgba(212, 175, 55, 0.6) !important;
        background: rgba(26, 26, 46, 0.7) !important;
    }
    
    [data-testid="stExpander"] summary p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: transparent !important;
        padding: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="cashier-header">
    <h2>Cashier Panel</h2>
    <p>Process Payments & Manage Orders</p>
</div>
""", unsafe_allow_html=True)

# Search section
st.markdown('<p class="section-header">Search Orders</p>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_id = st.number_input("Search by Order ID", min_value=0, value=0, step=1, 
                                 help="Enter order ID to search")
with col2:
    search_status = st.selectbox("Filter by Status", ["All", "Pending", "Paid"])
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("Search", use_container_width=True)

# Search results
if search_id > 0:
    found_order = get_order_by_id(search_id)
    if found_order:
        st.success(f"Found Order #{search_id}")
        with st.expander(f"📋 Order #{found_order['order_id']} - Table {found_order['table_id']}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<p style="color: #ffffff; font-weight: 600; margin-bottom: 0.5rem;">Items:</p>', unsafe_allow_html=True)
                for item in found_order.get('items', []):
                    subtotal = item['price'] * item['quantity']
                    st.markdown(f'<p style="color: #ffffff; margin: 0 0 0.2rem 0;">• {item["name"]} x{item["quantity"]} = <span style="color: #d4af37; font-weight: 600;">{subtotal:.2f} SAR</span></p>', unsafe_allow_html=True)
                st.markdown(f'<h3 style="margin-top: 1rem;">Total: <span style="color: #f7e98e;">{found_order["total_price"]:.2f} SAR</span></h3>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<p style="color: #ffffff; font-weight: 600; margin-bottom: 0.5rem;">Details:</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #ffffff; margin: 0;">**Order ID:** <span style="color: #d4af37;">#{found_order["order_id"]}</span></p>', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #ffffff; margin: 0;">**Table:** <span style="color: #d4af37;">{found_order["table_id"]}</span></p>', unsafe_allow_html=True)
                
                status = found_order.get('status', 'Unknown')
                if status == 'Pending':
                    st.markdown('<span class="pending-badge">PENDING</span>', unsafe_allow_html=True)
                    st.markdown("")
                    payment = st.selectbox("Payment Method", config.PAYMENT_METHODS, key="search_payment")
                    if st.button("Mark as Paid", key="search_pay", type="primary", use_container_width=True):
                        update_order_status(found_order['order_id'], "Paid", payment)
                        st.success("Order marked as paid!")
                        st.rerun()
                else:
                    st.markdown('<span class="paid-badge">PAID</span>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: #ffffff; margin: 0.5rem 0 0 0;">**Payment:** <span style="color: #d4af37;">{found_order.get("payment_method", "N/A")}</span></p>', unsafe_allow_html=True)
    else:
        st.warning(f"No order found with ID #{search_id}")

st.divider()

# Load data for both tabs
pending_orders_all = get_pending_orders()
paid_orders_all = get_paid_orders()

# Sorting: Newest first
pending_orders_all = sorted(pending_orders_all, key=lambda x: x.get('timestamp', ''), reverse=True)
paid_orders_all = sorted(paid_orders_all, key=lambda x: x.get('timestamp', ''), reverse=True)

# Filtering: Only show orders from the last 7 days
from datetime import datetime, timedelta
one_week_ago = datetime.now() - timedelta(days=7)

def is_recent(order):
    try:
        ts = order.get('timestamp')
        if not ts: return True
        return datetime.fromisoformat(ts) > one_week_ago
    except:
        return True

pending_orders = [o for o in pending_orders_all if is_recent(o)]
paid_orders = [o for o in paid_orders_all if is_recent(o)]

# Tabs for pending and paid orders
tab1, tab2 = st.tabs(["Pending Orders", "Paid Orders"])

# =============================================================================
# TAB 1: PENDING ORDERS
# =============================================================================
with tab1:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<p class="section-header">Orders Awaiting Payment</p>', unsafe_allow_html=True)
    with col2:
        if st.button("Refresh", key="refresh_pending", use_container_width=True):
            st.rerun()
    
    if not pending_orders:
        st.info("No pending orders! All orders have been paid.")
    else:
        for order in pending_orders:
            st.markdown(f"""
            <div class="order-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p class="table-number">Table {order['table_id']}</p>
                        <p style="color: #ffffff; margin: 0; opacity: 0.8;">Order #{order['order_id']}</p>
                    </div>
                    <div class="pending-badge">PENDING</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown('<p style="color: #ffffff; font-weight: 600; margin-bottom: 0.5rem;">Order Items:</p>', unsafe_allow_html=True)
                for item in order.get('items', []):
                    subtotal = item['price'] * item['quantity']
                    st.markdown(f'<p style="color: #ffffff; margin: 0 0 0.2rem 0;">• {item["name"]} x{item["quantity"]} = <span style="color: #d4af37; font-weight: 600;">{subtotal:.2f} SAR</span></p>', unsafe_allow_html=True)
                
                order_time = order.get('timestamp', '')
                if order_time:
                    try:
                        dt = datetime.fromisoformat(order_time)
                        st.markdown(f'<p style="color: #ffffff; font-size: 0.85rem; margin-top: 0.8rem; opacity: 0.8;">Ordered: {dt.strftime("%H:%M:%S")}</p>', unsafe_allow_html=True)
                    except:
                        pass
            
            with col2:
                st.markdown(f'<h3 style="margin-top: 0;">Total: <span style="color: #f7e98e;">{order["total_price"]:.2f} SAR</span></h3>', unsafe_allow_html=True)
                payment_method = st.selectbox(
                    "Payment",
                    options=config.PAYMENT_METHODS,
                    key=f"payment_{order['order_id']}"
                )
                
                if st.button("Mark as Paid", key=f"pay_{order['order_id']}", type="primary", use_container_width=True):
                    update_order_status(order['order_id'], "Paid", payment_method)
                    st.success(f"Order #{order['order_id']} paid!")
                    st.rerun()
            
            st.divider()

# =============================================================================
# TAB 2: PAID ORDERS WITH RECEIPTS
# =============================================================================
with tab2:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<p class="section-header">Completed Orders</p>', unsafe_allow_html=True)
    with col2:
        if st.button("Refresh", key="refresh_paid", use_container_width=True):
            st.rerun()
    
    paid_orders = get_paid_orders()
    
    if not paid_orders:
        st.info("No paid orders yet.")
    else:
        # Sort by paid_timestamp (newest first)
        paid_orders.sort(key=lambda x: x.get('paid_timestamp', ''), reverse=True)
        
        # Show only recent orders
        recent_paid = paid_orders[:15]
        
        for order in recent_paid:
            with st.expander(f"Order #{order['order_id']} | Table {order['table_id']} | {order['total_price']:.0f} SAR"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Receipt:**")
                    
                    # Generate receipt
                    receipt = f"""
┌{'─' * 38}┐
│{'RESTAURANT RECEIPT':^38}│
├{'─' * 38}┤
│ Order #: {order['order_id']:<28}│
│ Table: {order['table_id']:<30}│
├{'─' * 38}┤
│ {'Item':<20} {'Qty':>3} {'Price':>12} │
├{'─' * 38}┤
"""
                    for item in order.get('items', []):
                        subtotal = item['price'] * item['quantity']
                        name_trunc = item['name'][:20] 
                        receipt += f"│ {name_trunc:<20} {item['quantity']:>3} {subtotal:>10.2f} SAR │\n"
                        
                        # Add deal breakdown if deal
                        if str(item.get('item_id', '')).startswith('deal_'):
                            did = str(item['item_id']).replace('deal_', '')
                            deal = get_deal(did)
                            if deal and 'applicable_items' in deal:
                                from collections import Counter
                                item_counts = Counter(deal['applicable_items'])
                                for uid, count in item_counts.items():
                                    menu_item = get_menu_item(uid)
                                    if menu_item:
                                        sub_name = menu_item['name'].get('en', 'Item')
                                        receipt += f"│   - {count}x {sub_name[:12]:<12} {'':>3} {'':>14} │\n"
                    
                    receipt += f"""├{'─' * 38}┤
│ {'TOTAL':<20} {'':<3} {order['total_price']:>10.2f} SAR │
├{'─' * 38}┤
│ Payment: {order.get('payment_method', 'N/A'):<28}│
└{'─' * 38}┘"""
                    
                    st.markdown(f'<div class="receipt-box"><pre style="color: #d4af37; margin: 0;">{receipt}</pre></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<p style="color: #ffffff; font-weight: 600; margin-bottom: 0.5rem;">Details:</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: #ffffff; margin: 0;">**Order ID:** <span style="color: #d4af37;">#{order["order_id"]}</span></p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: #ffffff; margin: 0;">**Table:** <span style="color: #d4af37;">{order["table_id"]}</span></p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: #ffffff; margin: 0;">**Total:** <span style="color: #d4af37;">{order["total_price"]:.2f} SAR</span></p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: #ffffff; margin: 0;">**Payment:** <span style="color: #d4af37;">{order.get("payment_method", "N/A")}</span></p>', unsafe_allow_html=True)
                    
                    paid_time = order.get('paid_timestamp', '')
                    if paid_time:
                        try:
                            dt = datetime.fromisoformat(paid_time)
                            st.markdown(f'<p style="color: #ffffff; margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;">**Paid at:** {dt.strftime("%Y-%m-%d %H:%M")}</p>', unsafe_allow_html=True)
                        except:
                            pass

# Summary statistics
st.divider()
st.markdown('<p class="section-header">Today\'s Summary</p>', unsafe_allow_html=True)

all_orders = load_orders()
today = datetime.now().date()

# Filter today's orders
today_orders = []
for order in all_orders:
    try:
        order_date = datetime.fromisoformat(order.get('timestamp', '')).date()
        if order_date == today:
            today_orders.append(order)
    except:
        pass

today_pending = [o for o in today_orders if o.get('status') == 'Pending']
today_paid = [o for o in today_orders if o.get('status') == 'Paid']
today_revenue = sum(o.get('total_price', 0) for o in today_paid)
cash_revenue = sum(o.get('total_price', 0) for o in today_paid if o.get('payment_method') == 'Cash')
card_revenue = sum(o.get('total_price', 0) for o in today_paid if o.get('payment_method') == 'Card')

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Orders", len(today_orders))
with col2:
    st.metric("Pending", len(today_pending))
with col3:
    st.metric("Paid", len(today_paid))
with col4:
    st.metric("Revenue", f"{today_revenue:.0f} SAR")

# Payment breakdown
col1, col2 = st.columns(2)
with col1:
    st.metric("Cash", f"{cash_revenue:.0f} SAR")
with col2:
    st.metric("Card", f"{card_revenue:.0f} SAR")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #ffffff; padding: 1rem;">
    Cashier Panel | Premium Restaurant Management
</div>
""", unsafe_allow_html=True)
