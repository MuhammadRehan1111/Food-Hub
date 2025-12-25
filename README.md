# 🍽️ Restaurant Ordering System

A premium, elegant restaurant management and ordering application built with Streamlit and powered by Google Gemini AI.

## ✨ Features

- **💎 Premium UI/UX:** Dark luxury theme with gold accents, smooth transitions, and responsive design.
- **🤖 AI Ordering Assistant:** Intelligent chatbot powered by Google Gemini to help customers browse the menu and place orders.
- **🛒 Customer Ordering:** Easy-to-use interface for browsing categories, viewing deals, and managing the cart.
- **💰 Cashier Panel:** Streamlined interface for managing active orders, processing payments, and printing itemized bills.
- **🔐 Admin Dashboard:** Comprehensive analytics, menu management, category configuration, and site settings.
- **🌍 Multilingual Support:** Supports English, Urdu, and Arabic.

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **AI Engine:** Google Generative AI (Gemini)
- **Data Storage:** JSON (Local storage)
- **Styling:** Custom CSS (Vanilla CSS for premium aesthetics)

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A Google Gemini API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd restaurant_app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory (or use the provided one) and add your API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## 🔐 Credentials

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Cashier** | `cashier` | `cashier123` |

> [!IMPORTANT]
> Change these credentials in `config.py` or `.env` before deploying to a production environment.

## 📂 Project Structure

- `app.py`: Main entry point and home page.
- `config.py`: Centralized configuration and settings.
- `pages/`: 
    - `1_🍽️_Customer_Order.py`: Customer-facing ordering interface.
    - `2_💰_Cashier_Panel.py`: Order processing for staff.
    - `3_🔐_Admin_Panel.py`: Management dashboard.
- `utils/`: Helper functions and API clients.
- `data/`: JSON files for persistent storage.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
