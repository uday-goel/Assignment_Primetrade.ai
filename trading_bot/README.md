# Binance Futures Testnet Trading Bot

A clean, beginner-friendly Python trading bot that places **Market**, **Limit**, and **Stop-Market** orders on the [Binance Futures Testnet](https://testnet.binancefuture.com) via a simple command-line interface.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # package marker
│   ├── client.py            # Binance REST API wrapper (signs & sends requests)
│   ├── orders.py            # order placement logic + response formatting
│   ├── validators.py        # input validation (runs before any API call)
│   └── logging_config.py   # sets up file + console logging
├── cli.py                   # entry point — run this file
├── logs/
│   └── trading_bot.log      # auto-created; all requests/responses logged here
├── .env.example             # template — copy to .env and fill in your keys
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup (step-by-step for beginners)

### Step 1 — Make sure Python is installed

Open a terminal and run:
```bash
python --version
```
You need Python **3.8 or higher**. Download from https://python.org if needed.

---

### Step 2 — Get a Binance Futures Testnet account & API keys

1. Go to **https://testnet.binancefuture.com**
2. Click **"Login"** → sign up with Google or GitHub (it's free, no real money)
3. Once logged in, go to the **top-right menu → "API Management"** (or "API Key")
4. Click **"Generate Key"** / **"Create"** — copy both the **API Key** and **Secret Key** somewhere safe (the secret is only shown once!)

---

### Step 3 — Download / clone this project

If you have git:
```bash
git clone <your-repo-url>
cd trading_bot
```

Or just unzip the folder and `cd` into it.

---

### Step 4 — Create a virtual environment (recommended but optional)

```bash
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

---

### Step 5 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 6 — Add your API keys

Copy the example env file:
```bash
# On Mac/Linux:
cp .env.example .env

# On Windows:
copy .env.example .env
```

Open `.env` in any text editor and replace the placeholder values:
```
BINANCE_TESTNET_API_KEY=paste_your_api_key_here
BINANCE_TESTNET_API_SECRET=paste_your_secret_key_here
```

> **Never share your `.env` file or commit it to GitHub.**

---

## How to Run

All commands are run from the `trading_bot/` folder with:
```
python cli.py [arguments]
```

### See all available options
```bash
python cli.py --help
```

---

### Place a MARKET BUY order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a MARKET SELL order
```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### Place a LIMIT BUY order (price required)
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 30000
```

### Place a LIMIT SELL order
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

### Place a STOP_MARKET SELL order (bonus feature)
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 28000
```

---

## Example Output

```
──────────────────────────────────────────────────
          ORDER REQUEST SUMMARY
──────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
──────────────────────────────────────────────────

──────────────────────────────────────────────────
          ORDER RESPONSE DETAILS
──────────────────────────────────────────────────
  Order ID      : 4739281
  Client Ord ID : x-abc123def456
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Status        : FILLED
  Quantity      : 0.001
  Executed Qty  : 0.001
  Avg Price     : 67823.50
  Price         : 0
  Time in Force : GTC
──────────────────────────────────────────────────

  ✅  Order placed SUCCESSFULLY!
```

---

## Log File

Every run appends to `logs/trading_bot.log`. Example entries:

```
2025-06-01 10:15:02 | INFO     | Placing MARKET BUY order | Symbol: BTCUSDT | Qty: 0.001
2025-06-01 10:15:03 | INFO     | Order placed successfully | orderId: 4739281
```

The log includes:
- Every API request (parameters, minus the signature)
- Every API response (HTTP status + body preview)
- All validation errors and API errors
- Success/failure of each order

---

## Error Handling

| Situation | What happens |
|---|---|
| Missing API keys | Prints a setup guide and exits |
| Invalid symbol / side / type | Prints the exact problem and exits before calling the API |
| Price missing for LIMIT order | Explains which argument is needed |
| Binance API error (e.g. insufficient balance) | Prints the error code and message |
| Network failure / timeout | Prints a connection error message |

---

## Dependencies

| Package | Purpose |
| `requests` | HTTP calls to Binance REST API |
| `python-dotenv` | Load `.env` file into environment variables |
| `colorama` | Cross-platform terminal color support |
| `tabulate` | (available for future table formatting) |

---

## Assumptions

1. **Testnet only** — this bot is hard-coded to `https://testnet.binancefuture.com`. No real money is used.
2. **USDT-M Futures** — all symbols should be USDT-margined futures pairs (e.g. `BTCUSDT`, `ETHUSDT`).
3. **Minimum quantity** — Binance enforces minimum order sizes. For BTCUSDT, the minimum is typically `0.001 BTC`. Check the testnet exchange info if you get a filter error.
4. **Limit orders** — placed with `timeInForce=GTC` (Good Till Cancel) by default.
5. **API keys** — must be stored in a `.env` file (never hardcoded).

---

## Bonus Feature Implemented

**Stop-Market orders** — a third order type (`STOP_MARKET`) is supported. Use `--type STOP_MARKET --stop-price <price>` to place a stop order that triggers a market sell/buy when the price hits your stop level.
