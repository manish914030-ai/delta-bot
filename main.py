from exchange import get_balance
from telegram_bot import send_message

def main():
    print("Delta Trading Bot Started")

    try:
        balance = get_balance()
        print(balance)

        send_message("✅ Delta Trading Bot Started Successfully")

    except Exception as e:
        print(e)
        send_message(f"❌ Bot Error: {e}")

if __name__ == "__main__":
    main()
