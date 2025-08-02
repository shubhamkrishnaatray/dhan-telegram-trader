import os
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Load credentials from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Base URL for Dhan API
DHAN_ORDER_URL = "https://api.dhan.co/orders"

# Basic order function for Dhan
def place_dhan_order(action, symbol, quantity):
    headers = {
        "access-token": DHAN_ACCESS_TOKEN,
        "Content-Type": "application/json",
        "Client-Id": DHAN_CLIENT_ID
    }

    order_payload = {
        "transactionType": action.upper(),  # BUY or SELL
        "exchangeSegment": "NSE_EQ",
        "productType": "INTRADAY",
        "orderType": "MARKET",
        "validity": "DAY",
        "tradingSymbol": symbol.upper(),
        "quantity": int(quantity),
        "price": 0,
        "disclosedQuantity": 0,
        "afterMarketOrder": False,
        "boProfitValue": 0,
        "boStopLossValue": 0
    }

    response = requests.post(DHAN_ORDER_URL, headers=headers, json=order_payload)
    return response.json()

# Telegram message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or str(message.chat_id) != CHANNEL_ID:
        return

    text = message.text.strip()
    try:
        action, symbol, quantity = text.split()
        if action.lower() not in ["buy", "sell"]:
            await message.reply_text("Invalid action. Use 'buy' or 'sell'")
            return

        result = place_dhan_order(action, symbol, quantity)
        if result.get("status") == "success":
            await message.reply_text(f"Order placed: {action.upper()} {symbol.upper()} x {quantity}")
        else:
            await message.reply_text(f"Order failed: {result}")

    except Exception as e:
        await message.reply_text(f"Error processing order: {e}")

# Main function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

