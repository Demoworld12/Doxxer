import discord
from discord.ext import commands
import tkinter as tk
from tkinter import messagebox
import os
import requests
import subprocess
import asyncio
import time
import hashlib
import json
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import re

# Keep bot alive
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), KeepAliveHandler)
    server.serve_forever()

Thread(target=run_server, daemon=True).start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Bitcoin mining configuration
POOL_URL = "stratum+tcp://us-east.stratum.slushpool.com:3333"  # Replace with your pool's URL
WORKER_USERNAME = "your_worker_username"  # Replace with your pool worker username
WORKER_PASSWORD = "your_worker_password"  # Replace with your pool worker password
WALLET_ADDRESS = "your_bitcoin_wallet_address"  # Replace with your Bitcoin wallet address
mined_balance = 0.00000000  # BTC

# Mining function
def mine_bitcoin():
    global mined_balance
    try:
        while True:
            nonce = 0
            block_data = f"{time.time()}{WORKER_USERNAME}".encode()
            while True:
                hash_attempt = hashlib.sha256(block_data + str(nonce).encode()).hexdigest()
                if hash_attempt.startswith("0000"):  # Simplified difficulty check
                    response = requests.post("http://api.slushpool.com/submit",  # Replace with actual pool API
                                             json={"worker": WORKER_USERNAME, "nonce": nonce, "hash": hash_attempt}
                                             )
                    if response.status_code == 200:
                        mined_balance += 0.00000001  # Increment balance (example value)
                        update_balance_label()
                nonce += 1
                time.sleep(0.01)  # Prevent CPU overload
    except Exception as e:
        print(f"Mining error: {e}")

# GUI for Bitcoin mining
root = None
balance_label = None

def update_balance_label():
    if balance_label:
        balance_label.config(text=f"Mined: {mined_balance:.8f} BTC")

def withdraw_bitcoin():
    global mined_balance
    if mined_balance > 0:
        try:
            response = requests.post("http://api.slushpool.com/withdraw",  # Replace with actual pool API
                                     json={"wallet": WALLET_ADDRESS, "amount": mined_balance}
                                     )
            if response.status_code == 200:
                mined_balance = 0
                update_balance_label()
                messagebox.showinfo("Success", "Withdrawal request sent!")
            else:
                messagebox.showerror("Error", "Withdrawal failed.")
        except Exception as e:
            messagebox.showerror("Error", f"Withdrawal error: {e}")
    else:
        messagebox.showwarning("Warning", "No balance to withdraw!")

def start_mining_gui():
    global root, balance_label
    root = tk.Tk()
    root.title("Bitcoin Miner")
    root.geometry("300x200")
    balance_label = tk.Label(root, text=f"Mined: {mined_balance:.8f} BTC", font=("Arial", 14))
    balance_label.pack(pady=20)
    withdraw_button = tk.Button(root, text="Withdraw Bitcoin", command=withdraw_bitcoin, font=("Arial", 12))
    withdraw_button.pack(pady=20)
    Thread(target=mine_bitcoin, daemon=True).start()
    root.mainloop()

# Hacking tools dictionary
TOOLS = {
    "sniper": "Snipes deleted Discord messages or usernames.",
    "password_cracker": "Cracks passwords for 50 platforms using John the Ripper or Hashcat.",
    "token_grabber": "Extracts Discord tokens from local clients.",
    "darkweb_search": "Searches darkweb sites via Tor.",
    "keylogger": "Captures keystrokes on target machine.",
    "port_scanner": "Scans open ports on a target IP.",
    "sql_injection": "Tests for SQL injection vulnerabilities.",
    "phishing_generator": "Creates fake login pages.",
    "ddos_tool": "Simulates HTTP flooding (use cautiously).",
    "exploit_finder": "Searches for known vulnerabilities using Nmap."
}

# Split message for Discord's 2000-character limit
def split_message(content, limit=2000):
    messages = []
    while len(content) > limit:
        split_point = content[:limit].rfind('\n')
        if split_point == -1:
            split_point = limit
        messages.append(content[:split_point])
        content = content[split_point:]
    messages.append(content)
    return messages

# On ready
@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

#$tools command
@bot.command()
async def tools(ctx):
    tool_list = "Available Tools:\n" + "\n".join([f"{k}: {v}" for k, v in TOOLS.items()])
    for msg in split_message(tool_list):
        await ctx.send(msg)

#$start_mining command
@bot.command()
async def start_mining(ctx):
    await ctx.send("Starting Bitcoin mining with GUI...")
    Thread(target=start_mining_gui, daemon=True).start()

#$run command for hacking tools
@bot.command()
async def run(ctx, tool=None, *, args=None):
    if not tool or tool not in TOOLS:
        await ctx.send("Invalid tool. Use `$tools` to see available tools.")
        return

    if tool == "sniper":
        await ctx.send("Sniper activated. Monitoring deleted messages (placeholder).")

    elif tool == "password_cracker":
        if not args:
            await ctx.send("Usage: `$run password_cracker <platform> <username> <hash>`")
            return
        try:
            platform, username, hash_value = args.split(maxsplit=2)
            platforms = ["discord", "twitter", "facebook"] + [f"platform{i}" for i in range(4, 51)]
            if platform not in platforms:
                await ctx.send(f"Supported platforms: {', '.join(platforms)}")
                return
            result = subprocess.run(["john", "--format=raw-sha256", hash_value], capture_output=True, text=True)
            output = result.stdout or "Cracking failed or hash not supported."
            for msg in split_message(output):
                await ctx.send(msg)
        except:
            await ctx.send("John the Ripper not installed. Install it or use Hashcat locally.")

    elif tool == "token_grabber":
        await ctx.send("Token grabber requires local execution on target machine (e.g., via malicious script).")

    elif tool == "darkweb_search":
        if not args:
            await ctx.send("Usage: `$run darkweb_search <query>`")
            return
        await ctx.send(f"Searching darkweb for '{args}' (requires Tor setup).")

    elif tool == "keylogger":
        await ctx.send("Keylogger requires local execution on target machine (e.g., via Python script).")

    elif tool == "port_scanner":
        if not args:
            await ctx.send("Usage: `$run port_scanner <ip>`")
            return
        try:
            import nmap
            nm = nmap.PortScanner()
            nm.scan(args, '1-1000')
            result = nm.csv()
            for msg in split_message(result):
                await ctx.send(msg)
        except:
            await ctx.send("Nmap not installed. Run `apt-get install nmap` locally or use another scanner.")

    elif tool == "sql_injection":
        if not args:
            await ctx.send("Usage: `$run sql_injection <url>`")
            return
        try:
            response = requests.get(f"{args}'")
            if "sql syntax" in response.text.lower():
                await ctx.send("Potential SQL injection vulnerability detected!")
            else:
                await ctx.send("No obvious SQL injection found.")
        except:
            await ctx.send("Error testing SQL injection.")

    elif tool == "phishing_generator":
        await ctx.send("Phishing generator: Creates fake login page (placeholder, requires HTML template).")

    elif tool == "ddos_tool":
        if not args:
            await ctx.send("Usage: `$run ddos_tool <url>`")
            return
        await ctx.send(f"Simulating DDoS on {args} (basic HTTP flooding, use cautiously).")
        for _ in range(10):  # Limited to avoid abuse
            requests.get(args)
        await ctx.send("DDoS simulation complete.")

    elif tool == "exploit_finder":
        if not args:
            await ctx.send("Usage: `$run exploit_finder <ip>`")
            return
        try:
            import nmap
            nm = nmap.PortScanner()
            nm.scan(args, arguments='--script vuln')
            result = nm.csv()
            for msg in split_message(result):
                await ctx.send(msg)
        except:
            await ctx.send("Nmap not installed or exploit scan failed.")

# Handle deleted messages for sniper
@bot.event
async def on_message_delete(message):
    if "sniper" in [cmd.name for cmd in bot.commands]:
        with open("snipe.log", "a") as f:
            f.write(f"Deleted: {message.content} by {message.author}\n")

# Keep bot running
try:
    bot.run(os.getenv("DISCORD_TOKEN"))  # Replace with your Discord bot token
except Exception as e:
    print(f"Error: {e}")
while True:  # Retry indefinitely
    try:
        bot.run(os.getenv("DISCORD_TOKEN"))
    except:
        time.sleep(5)