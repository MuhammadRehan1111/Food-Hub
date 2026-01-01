"""
Google Gemini API client for the multilingual restaurant chatbot.
Handles conversation management and language detection.
Includes fallback mode when API is unavailable.
"""
import google.generativeai as genai
from typing import List, Dict, Optional
import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=config.GEMINI_API_KEY)


def get_available_model() -> Optional[str]:
    """Find an available Gemini model for chat."""
    try:
        models = genai.list_models()
        # Preferred models in order
        preferred = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        available_names = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                clean_name = model.name.replace('models/', '')
                available_names.append(clean_name)
        
        logger.info(f"Available Gemini models: {available_names}")
        
        # Try preferred models first
        for pref in preferred:
            if pref in available_names:
                logger.info(f"Selected preferred model: {pref}")
                return pref
        
        # Return first available model that supports generateContent
        if available_names:
            logger.info(f"Selected fallback model: {available_names[0]}")
            return available_names[0]
        
        logger.warning("No suitable Gemini model found.")
        return None
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return None


def get_system_prompt(table_id: int, menu: Dict, deals: List[Dict]) -> str:
    """Generate the system prompt for the restaurant chatbot."""
    
    # Format menu for the prompt
    menu_text = ""
    for category, items in menu.items():
        menu_text += f"\n### {category}:\n"
        for item in items:
            if item.get('available', True):
                name = item['name'].get('en', 'Unknown')
                price = item['price']
                desc = item.get('description', {}).get('en', '')
                menu_text += f"- {name} (ID: {item['item_id']}) - {price} SAR"
                if desc:
                    menu_text += f" - {desc}"
                menu_text += "\n"

    # Format deals for the prompt
    deals_text = ""
    for deal in deals:
        if deal.get('active', True):
            name = deal['name'].get('en', 'Premium Deal')
            price = deal['price']
            desc = deal.get('description', {}).get('en', '')
            did = f"deal_{deal['deal_id']}"
            deals_text += f"- {name} (ID: {did}) - {price} SAR\n"
            if desc:
                deals_text += f"  *Description: {desc}*\n"
    
    
    return f"""You are a warm, friendly, and enthusiastic restaurant assistant! 🌟 The customer is at Table {table_id}.

YOUR PERSONALITY:
- Be genuinely warm and welcoming - like greeting a friend!
- Use a conversational, friendly tone (not robotic or formal)
- Show enthusiasm about the food and make it sound delicious
- Be helpful and patient

LANGUAGE HANDLING:
- Detect the customer's language (English, Urdu/Roman Urdu, or Arabic) 
- ALWAYS respond in the SAME language they use
- If they write in Urdu, respond in Urdu
- If they write in Arabic, respond in Arabic

YOUR ROLE:
- Help customers explore our **Full Menu** and **Premium Deals**!
- Suggest dishes they'll love and highlight our best bundles.
- Take their order in a friendly, conversational way.
- Confirm orders (items or deals) before finalizing.

IMPORTANT - ORDER TAKING:
- When a customer confirms they want to order specific items or deals, you MUST output a special hidden tag so the system can record it.
- Format: [ORDER: item_or_deal_id, quantity]
- Examples: 
  - If they want 2 Burgers (ID: 101): "Great! I've added 2 Burgers to your order. [ORDER: 101, 2]"
  - If they want 1 Family Feast deal (ID: deal_d01): "Excellent choice! [ORDER: deal_d01, 1]"
- ALWAYS include these tags when an order is confirmed. Do not show the ID to the user in the text, just the tag at the end.

AVAILABLE DEALS:
{deals_text}

FULL MENU:
{menu_text}

Remember: Be warm, be helpful, make them feel special!"""


class RestaurantChatbot:
    """Manages the restaurant ordering chatbot using Gemini."""
    
    def __init__(self, menu_data: Dict, table_id: int, deals: List[Dict]):
        self.table_id = table_id
        self.menu_data = menu_data
        self.deals = deals
        self.system_prompt = get_system_prompt(table_id, menu_data, deals)
        self.chat = None
        self.order_items = []
        self.api_available = False
        self.model = None
        self._initialize_chat()
    
    def _initialize_chat(self):
        """Initialize the chat session with system context."""
        try:
            # Try to find an available model
            model_name = get_available_model()
            
            if model_name:
                self.model = genai.GenerativeModel(model_name)
                # system_prompt = get_system_prompt(self.table_id, self.menu_data, self.deals) # Already generated
                
                try:
                    self.chat = self.model.start_chat(history=[])
                    # Send system context as first message
                    self.chat.send_message(f"""[SYSTEM CONTEXT - Do not repeat this to users]
{self.system_prompt}

Now, greet the customer at Table {self.table_id} and ask what they would like to order. Show the main categories.""")
                    self.api_available = True
                    logger.info("Chatbot session initialized successfully.")
                except Exception as e:
                    logger.error(f"Error during start_chat or initial message: {e}")
                    self.api_available = False
            else:
                logger.error("No available Gemini model found during init.")
                self.api_available = False
                
        except Exception as e:
            logger.critical(f"Failed to initialize Gemini chat: {e}")
            self.api_available = False
    
    def send_message(self, user_message: str) -> str:
        """Send a message and get response from the chatbot."""
        if not self.api_available:
            logger.warning("API not available, using fallback response.")
            return self._fallback_response(user_message)
        
        try:
            response = self.chat.send_message(user_message)
            return response.text
        except Exception as e:
            logger.error(f"Error sending message to Gemini: {e}")
            # Try to re-initialize if it might be a session issue (optional, for now just fallback)
            # If it's a quote limit or server error, we should tell the user
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str:
                return "I'm currently receiving too many requests. Please try again in a moment, or use the Quick Menu tab."
            
            return f"I apologize, but I'm having trouble processing your request right now. Please use the Quick Menu tab to place your order. (Technical details: {str(e)[:50]}...)"
    
    def _fallback_response(self, user_message: str) -> str:
        """Provide basic responses when API is unavailable."""
        msg_lower = user_message.lower()
        
        if any(word in msg_lower for word in ['menu', 'food', 'order', 'eat', 'hungry']):
            return """**Our Menu Categories:**

• **Fast Food** - Burgers, Chicken, Fries
• **Pizza** - Pepperoni, BBQ Chicken, Veggie
• **Meat & BBQ** - Steaks, Ribs, Grilled Items
• **Tea** - Karak, Green Tea, Masala Chai
• **Ice Cream** - Vanilla, Chocolate, Mango

Please use the **Quick Menu** tab above to browse items and place your order!"""
        
        
        else:
            return f"""Welcome to our restaurant! You are at **Table {self.table_id}**.

I'm currently in offline mode, but you can still order easily!

👉 Use the **Quick Menu** tab to browse our menu and add items to your cart.

Our categories: Fast Food, Pizza, Meat & BBQ, Tea, Ice Cream"""
    
    def get_welcome_message(self) -> str:
        """Get the initial welcome message."""
        if self.api_available:
            try:
                # The welcome was sent during initialization, get it from history
                if self.chat and self.chat.history and len(self.chat.history) >= 2:
                    return self.chat.history[1].parts[0].text
            except Exception as e:
                logger.warning(f"Could not retrieve welcome message from history: {e}")
                pass
        
        # Fallback welcome message - warm and friendly
        return f"""**Hey there! Welcome to our restaurant!**

So happy to have you here at **Table {self.table_id}**!

I'm your friendly assistant, and I'm here to help you discover some amazing dishes!

**What are you in the mood for today?**

• **Fast Food** - Burgers, crispy chicken & more!
• **Pizza** - Fresh from the oven!
• **Meat & BBQ** - Perfectly grilled goodness!
• **Tea** - Warm & refreshing!
• **Ice Cream** - Sweet treats!

Just tell me what sounds good, or ask me anything! I'm here to help!"""
    
    def parse_order_from_conversation(self, conversation: List[Dict]) -> List[Dict]:
        """Extract ordered items from the conversation (for manual parsing if needed)."""
        # This is a placeholder - in practice, we'll use structured order selection
        return self.order_items
    
    def add_to_order(self, item_id: str, quantity: int):
        """Add an item to the current order."""
        item = None
        for category, items in self.menu_data.items():
            for menu_item in items:
                if menu_item['item_id'] == item_id:
                    item = menu_item
                    break
            if item:
                break
        
        if item:
            self.order_items.append({
                "item_id": item_id,
                "name": item['name'].get('en', 'Unknown'),
                "quantity": quantity,
                "price": item['price']
            })
    
    def get_order_total(self) -> float:
        """Calculate the total price of the current order."""
        return sum(item['price'] * item['quantity'] for item in self.order_items)
    
    def clear_order(self):
        """Clear the current order."""
        self.order_items = []
    
    def get_order_summary(self) -> str:
        """Get a formatted order summary."""
        if not self.order_items:
            return "No items in your order yet."
        
        summary = "**Order Summary:**\n\n"
        for item in self.order_items:
            subtotal = item['price'] * item['quantity']
            summary += f"• {item['name']} x{item['quantity']} = {subtotal} SAR\n"
        
        summary += f"\n**Total: {self.get_order_total()} SAR**"
        return summary


def test_connection() -> bool:
    """Test the Gemini API connection."""
    try:
        model_name = get_available_model()
        if model_name:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'API Connected' in exactly 2 words.")
            return "connected" in response.text.lower()
        return False
    except Exception as e:
        logger.error(f"Gemini API connection error: {e}")
        return False


def list_available_models() -> List[str]:
    """List all available models for debugging."""
    try:
        models = genai.list_models()
        return [model.name for model in models]
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return []
