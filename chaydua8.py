import threading
import base64
import os
import time
import re
import requests
import socket
import sys
from time import sleep
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import json
from collections import Counter, deque, defaultdict
from urllib.parse import urlparse, parse_qs
import random
import math
import hashlib
import platform
import subprocess
import statistics
import string
import urllib.parse

# Check và cài đặt các thư viện cần thiết
try:
    from colorama import init, Fore, Style
    import pytz 
    from faker import Faker
    from requests import session
    import pystyle
    init(autoreset=True)
except ImportError:
    print('__Đang cài đặt thư viện, vui lòng chờ...__')
    os.system("pip install requests colorama pytz faker pystyle bs4") 
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

# =====================================================================================
# PHẦN 1: MÃ NGUỒN TỪ KEYV8.PY (LOGIC XÁC THỰC)
# =====================================================================================

# CONFIGURATION FOR VIP KEY
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/KEY-VIP.txt/main/KEY-VIP.txt"
VIP_CACHE_FILE = 'vip_cache.json'

# Encrypt and decrypt data using base64
def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

# Colors for display (từ keyv8.py)
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

# Đổi tên hàm banner của file banner.py để tránh xung đột
def authentication_banner():
    os.system("cls" if os.name == "nt" else "clear")
    # <<< THAY ĐỔI: Thay thế thông tin admin bằng "Tool VIP V8" >>>
    banner_text = f"""
{luc}████████╗ ██████╗░░ ██╗░░██╗░
{luc}╚══██╔══╝ ██╔══██╗░ ██║██╔╝░░
{luc}░░░██║░░░ ██║░░██║░ █████╔╝░░
{luc}░░░██║░░░ ██║░░██║░ ██╔═██╗░░
{luc}░░░██║░░░ ██║░░██║░ ██║░╚██╗░
{luc}░░░╚═╝░░░ ╚█████╔╝░ ╚═╝░░╚═╝░
{trang}══════════════════════════

{vang}Tool VIP V8
{trang}══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.0001)

# DEVICE ID AND IP ADDRESS FUNCTIONS
def get_device_id():
    """Generates a stable device ID based on CPU information."""
    system = platform.system()
    try:
        if system == "Windows":
            cpu_info = subprocess.check_output('wmic cpu get ProcessorId', shell=True, text=True, stderr=subprocess.DEVNULL)
            cpu_info = ''.join(line.strip() for line in cpu_info.splitlines() if line.strip() and "ProcessorId" not in line)
        else:
            try:
                cpu_info = subprocess.check_output("cat /proc/cpuinfo", shell=True, text=True)
            except:
                cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = platform.processor()
    except Exception:
        cpu_info = "Unknown"

    hash_hex = hashlib.sha256(cpu_info.encode()).hexdigest()
    only_digits = re.sub(r'\D', '', hash_hex)
    if len(only_digits) < 16:
        only_digits = (only_digits * 3)[:16]
    
    return f"DEVICE-{only_digits[:16]}"

def get_ip_address():
    """Gets the user's public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    """Displays the banner, IP address, and Device ID."""
    authentication_banner() # Gọi hàm banner đã đổi tên
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")
    
    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")


# FREE KEY HANDLING FUNCTIONS
def luu_thong_tin_ip(ip, key, expiration_date):
    """Saves free key information to a json file."""
    data = {ip: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open('ip_key.json', 'w') as file:
        file.write(encrypted_data)

def tai_thong_tin_ip():
    """Loads free key information from the json file."""
    try:
        with open('ip_key.json', 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def kiem_tra_ip(ip):
    """Checks for a saved free key for the current IP."""
    data = tai_thong_tin_ip()
    if data and ip in data:
        try:
            expiration_date = datetime.fromisoformat(data[ip]['expiration_date'])
            if expiration_date > datetime.now():
                return data[ip]['key']
        except (ValueError, KeyError):
            return None
    return None

def generate_key_and_url(ip_address):
    """Creates a free key and a URL to bypass the link."""
    ngay = int(datetime.now().day)
    key1 = str(ngay * 27 + 27)
    ip_numbers = ''.join(filter(str.isdigit, ip_address))
    key = f'VTD8{key1}{ip_numbers}'
    expiration_date = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
    url = f'https://keyvtdv8.blogspot.com/2025/09/key-vtdv8_18.html?m={key}'
    return url, key, expiration_date

def get_shortened_link_phu(url):
    """Shortens the link to get the free key."""
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": "Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(ip_address):
    """Handles the entire process of obtaining a free key."""
    url, key, expiration_date = generate_key_and_url(ip_address)
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        yeumoney_future = executor.submit(get_shortened_link_phu, url)
        yeumoney_data = yeumoney_future.result()

    if yeumoney_data and yeumoney_data.get('status') == "error":
        print(yeumoney_data.get('message'))
        return False
    
    link_key_yeumoney = yeumoney_data.get('shortenedUrl')
    print(f'{trang}[{do}<>{trang}] {hong}Link Để Vượt Key Là {xnhac}: {link_key_yeumoney}{trang}')

    while True:
        keynhap = input(f'{trang}[{do}<>{trang}] {vang}Key Đã Vượt Là: {luc}')
        if keynhap == key:
            print(f'{luc}Key Đúng! Mời Bạn Dùng Tool{trang}')
            sleep(2)
            luu_thong_tin_ip(ip_address, keynhap, expiration_date)
            return True
        else:
            print(f'{trang}[{do}<>{trang}] {hong}Key Sai! Vui Lòng Vượt Lại Link {xnhac}: {link_key_yeumoney}{trang}')


# VIP KEY HANDLING FUNCTIONS
def save_vip_key_info(device_id, key, expiration_date_str):
    """Saves VIP key information to a local cache file."""
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    """Loads VIP key information from the local cache file."""
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
    """Calculates and displays the remaining time for a VIP key."""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        now = datetime.now()
        
        if expiry_date > now:
            delta = expiry_date - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"{xnhac}Key VIP của bạn còn lại: {luc}{days} ngày, {hours} giờ, {minutes} phút.{trang}")
        else:
            print(f"{do}Key VIP của bạn đã hết hạn.{trang}")
    except ValueError:
        print(f"{vang}Không thể xác định ngày hết hạn của key.{trang}")

def check_vip_key(machine_id, user_key):
    """Checks the VIP key from the URL on GitHub."""
    print(f"{vang}Đang kiểm tra Key VIP...{trang}")
    try:
        response = requests.get(VIP_KEY_URL, timeout=10)
        if response.status_code != 200:
            print(f"{do}Lỗi: Không thể tải danh sách key (Status code: {response.status_code}).{trang}")
            return 'error', None

        key_list = response.text.strip().split('\n')
        for line in key_list:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                key_ma_may, key_value, _, key_ngay_het_han = parts
                
                if key_ma_may == machine_id and key_value == user_key:
                    try:
                        expiry_date = datetime.strptime(key_ngay_het_han, '%d/%m/%Y')
                        if expiry_date.date() >= datetime.now().date():
                            return 'valid', key_ngay_het_han
                        else:
                            return 'expired', None
                    except ValueError:
                        continue
        return 'not_found', None
    except requests.exceptions.RequestException as e:
        print(f"{do}Lỗi kết nối đến server key: {e}{trang}")
        return 'error', None

# MAIN AUTHENTICATION FLOW
def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)

    if not ip_address or not device_id:
        print(f"{do}Không thể lấy thông tin thiết bị cần thiết. Vui lòng kiểm tra kết nối mạng.{trang}")
        return False

    cached_vip_info = load_vip_key_info()
    if cached_vip_info and cached_vip_info.get('device_id') == device_id:
        try:
            expiry_date = datetime.strptime(cached_vip_info['expiration_date'], '%d/%m/%Y')
            if expiry_date.date() >= datetime.now().date():
                print(f"{luc}Đã tìm thấy Key VIP hợp lệ, tự động đăng nhập...{trang}")
                display_remaining_time(cached_vip_info['expiration_date'])
                sleep(3)
                return True
            else:
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng lấy hoặc nhập key mới.{trang}")
        except (ValueError, KeyError):
            print(f"{do}Lỗi file lưu key. Vui lòng nhập lại key.{trang}")

    if kiem_tra_ip(ip_address):
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn. Mời bạn dùng tool...{trang}")
        time.sleep(2)
        return True

    while True:
        print(f"{trang}========== {vang}MENU LỰA CHỌN{trang} ==========")
        print(f"{trang}[{luc}1{trang}] {xduong}Nhập Key VIP{trang}")
        print(f"{trang}[{luc}2{trang}] {xduong}Lấy Key Free (Dùng trong ngày){trang}")
        print(f"{trang}======================================")

        try:
            choice = input(f"{trang}[{do}<>{trang}] {xduong}Nhập lựa chọn của bạn: {trang}")
            print(f"{trang}═══════════════════════════════════")

            if choice == '1':
                vip_key_input = input(f'{trang}[{do}<>{trang}] {vang}Vui lòng nhập Key VIP: {luc}')
                status, expiry_date_str = check_vip_key(device_id, vip_key_input)
                
                if status == 'valid':
                    print(f"{luc}Xác thực Key VIP thành công!{trang}")
                    save_vip_key_info(device_id, vip_key_input, expiry_date_str)
                    display_remaining_time(expiry_date_str)
                    sleep(3)
                    return True
                elif status == 'expired':
                    print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
                elif status == 'not_found':
                    print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
                else:
                    print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
                sleep(2)

            elif choice == '2':
                if process_free_key(ip_address):
                    return True
                else: 
                    return False
            
            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except (KeyboardInterrupt):
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()

# =====================================================================================
# PHẦN 2: MÃ NGUỒN TỪ T22.PY (TOOL CHÍNH)
# =====================================================================================

# Bảng màu
class Colors:
    RED = "\033[1;31m"; GREEN = "\033[1;32m"; YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"; MAGENTA = "\033[1;35m"; CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"; RESET = "\033[0m"; HEADER = "\033[38;2;255;185;0m"
    BORDER = "\033[38;2;100;100;100m"; PROFIT = "\033[38;2;0;255;127m"
    LOSS = "\033[38;2;255;80;80m"; TEXT_LABEL = "\033[38;2;175;175;175m"
    TEXT_VALUE = "\033[38;2;255;255;255m"

NV = {
    1: 'Bậc thầy tấn công', 2: 'Quyền sắt', 3: 'Thợ lặn sâu',
    4: 'Cơn lốc sân cỏ', 5: 'Hiệp sĩ phi nhanh', 6: 'Vua home run'
}

# Logic AI
class LogicEngine:
    def __init__(self, recency_window=20):
        self.history_data = deque(maxlen=200)
        self.losing_streak_count = 0
        self.recency_window = recency_window 
        self.last_bet_on = None
    def add_result(self, winner): self.history_data.append(winner)
    def record_win(self): self.losing_streak_count = 0; self.last_bet_on = None
    def record_loss(self, bet_on_char): self.losing_streak_count += 1; self.last_bet_on = bet_on_char
    def _get_frequency_scores(self, data):
        scores = defaultdict(int)
        for winner in data: scores[winner] += 1
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)
    def _get_coldest_character(self):
        if len(self.history_data) < len(NV) * 2: return None
        last_seen_index = {char_id: -1 for char_id in NV.keys()}
        for i in range(len(self.history_data) - 1, -1, -1):
            char = self.history_data[i]
            if last_seen_index[char] == -1: last_seen_index[char] = i
            if all(v != -1 for v in last_seen_index.values()): break
        seen_chars = {k: v for k, v in last_seen_index.items() if v != -1}
        if not seen_chars: return None
        coldest_char = min(seen_chars, key=seen_chars.get)
        return coldest_char
    def analyze_and_select(self, user_id, issue_id):
        if len(self.history_data) < self.recency_window: return random.choice(list(NV.keys()))
        overall_scores = self._get_frequency_scores(self.history_data)
        recent_history = list(self.history_data)[-self.recency_window:]
        recent_scores = self._get_frequency_scores(recent_history)
        coldest_char = self._get_coldest_character()
        last_winner = self.history_data[-1] if self.history_data else None
        top_overall = [char for char, score in overall_scores]
        top_recent = [char for char, score in recent_scores] if recent_scores else [top_overall[0]]
        base_candidate = None
        if self.losing_streak_count >= 2: base_candidate = top_overall[0]
        else:
            strategy_selector = issue_id % 3
            if strategy_selector == 0: base_candidate = top_overall[0]
            elif strategy_selector == 1: base_candidate = top_recent[0]
            else:
                common_candidates = set(top_overall[:3]).intersection(set(top_recent[:2]))
                if common_candidates: base_candidate = sorted(list(common_candidates), key=lambda x: top_overall.index(x))[0]
                else: base_candidate = top_overall[0]
        final_choice = base_candidate
        fallback_options = [c for c in top_overall if c != final_choice][:3]
        if final_choice == last_winner: final_choice = fallback_options[0]
        if final_choice == coldest_char: final_choice = fallback_options[0] if fallback_options[0] != coldest_char else fallback_options[1]
        if self.losing_streak_count > 0 and final_choice == self.last_bet_on:
             potential_choice = fallback_options[0]
             if potential_choice == last_winner or potential_choice == coldest_char:
                 potential_choice = fallback_options[1] if len(fallback_options) > 1 else top_overall[2]
             final_choice = potential_choice
        return final_choice

logic_engine = LogicEngine()

# Các hàm tiện ích và giao diện
def clear_screen():
    os.system('cls' if platform.system() == "Windows" else 'clear')

def format_time(seconds):
    if seconds < 0: return "0 ngày 0 giờ 0 phút"
    days = int(seconds // (24 * 3600)); seconds %= (24 * 3600)
    hours = int(seconds // 3600); seconds %= 3600
    minutes = int(seconds // 60)
    return f"{days} ngày {hours} giờ {minutes} phút"

def add_log(logs_deque, message):
    hanoi_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    timestamp = datetime.now(hanoi_tz).strftime('%H:%M:%S')
    logs_deque.append(f"{Colors.WHITE}{timestamp}{Colors.RESET} {message}")

# =====================================================================================
# >>> BẮT ĐẦU THAY ĐỔI THEO YÊU CẦU <<<
# =====================================================================================
def display_dashboard(config, stats, wallet_asset, htr, logs, coin_type, status_message=""):
    clear_screen()
    
    # 1. HIỂN THỊ LOGS TRƯỚC TIÊN
    print(f"{Colors.GREEN}{'─' * 28} LOGS {'─' * 29}")
    for log_entry in reversed(logs): print(log_entry)
    print(Colors.GREEN + '─' * 64 + Colors.RESET)
    print("\n") # Thêm một khoảng trống

    # 2. HIỂN THỊ BẢNG THÔNG TIN CHÍNH
    bet_amount0 = config['bet_amount0']; heso = config['heso']; start_time = config['start_time']
    total_games = stats['win'] + stats['lose']
    last_result_str = f"{Colors.GREEN}THẮNG" if htr and htr[-1]['kq'] else f"{Colors.LOSS}THUA"
    if not htr: last_result_str = f"{Colors.WHITE}CHƯA CÓ"
    profit = wallet_asset.get(coin_type, 0) - stats['asset_0']
    profit_color = Colors.GREEN if profit >= 0 else Colors.LOSS
    profit_str = f"{profit_color}{profit:+.4f} {coin_type}{Colors.RESET}"
    ls1 = stats.get('lose_streak_1', 0); ls2 = stats.get('lose_streak_2', 0)
    ls3 = stats.get('lose_streak_3', 0); ls4 = stats.get('lose_streak_4', 0)
    WIDTH = 64; BORDER_COLOR = Colors.CYAN
    T_L, T_R, B_L, B_R = "+", "+", "+", "+"; H, V = "-", "|"
    def get_visible_len(s): return len(re.sub(r'\033\[[0-9;]*m', '', s))
    def print_bordered_line(text=""):
        visible_len = get_visible_len(text); padding_len = WIDTH - visible_len
        print(f"{BORDER_COLOR}{V} {text}{' ' * (padding_len)} {BORDER_COLOR}{V}{Colors.RESET}")
    print(f"{BORDER_COLOR}{T_L}{H * (WIDTH + 2)}{T_R}{Colors.RESET}")
    print_bordered_line(f"{Colors.BLUE}Tool VIP V8")
    print_bordered_line(f"{Colors.WHITE}Loại:         {Colors.CYAN}LOGIC V8")
    print_bordered_line(f"{Colors.WHITE}Cược Cơ Bản:   {Colors.CYAN}{bet_amount0}")
    print_bordered_line(f"{Colors.WHITE}Hệ Số:        {Colors.CYAN}{heso}")
    print_bordered_line(f"{Colors.WHITE}Lợi Nhuận:    {profit_str}")
    print_bordered_line(f"{Colors.WHITE}Trận thắng:   {Colors.CYAN}{stats['win']} / {total_games}")
    print_bordered_line(f"{Colors.WHITE}Chuỗi Thắng:  {Colors.GREEN}{stats['streak']}{Colors.WHITE} || MAX: {stats['max_streak']}")
    print_bordered_line(f"{Colors.WHITE}Chuỗi Thua:   {Colors.LOSS}{stats['lose_streak']}")
    print_bordered_line(f"{Colors.WHITE}Số Lần Thua (1/2/3/4): {Colors.CYAN}{ls1} / {ls2} / {ls3} / {ls4}")
    title = "Tổng Hợp Số Dư"; padding = (WIDTH - len(title)) // 2
    print_bordered_line(f"{' ' * padding}{Colors.WHITE}{title}")
    print_bordered_line(f"{Colors.YELLOW}BUILD:        {wallet_asset.get('BUILD', 0.0):,.4f}")
    print_bordered_line(f"{Colors.MAGENTA}WORLD:        {wallet_asset.get('WORLD', 0.0):,.4f}")
    print_bordered_line(f"{Colors.GREEN}USDT:         {wallet_asset.get('USDT', 0.0):,.4f}")
    print_bordered_line(f"{Colors.WHITE}Kết Quả Trận Trước: {last_result_str}")
    print_bordered_line(f"{Colors.WHITE}Thời Gian chạy:     {Colors.CYAN}{format_time(time.time() - start_time)}")
    print(f"{BORDER_COLOR}{B_L}{H * (WIDTH + 2)}{B_R}{Colors.RESET}")

    # 3. HIỂN THỊ THÔNG BÁO TRẠNG THÁI CUỐI CÙNG
    if status_message: print(f"\n{status_message}")
# =====================================================================================
# >>> KẾT THÚC THAY ĐỔI THEO YÊU CẦU <<<
# =====================================================================================


# Các hàm tương tác API
def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        print(f"{Colors.CYAN}Tìm thấy file dữ liệu đã lưu. Bạn có muốn sử dụng không? (y/n): {Colors.WHITE}", end='')
        if input().lower() == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f: return json.load(f)
    print(f"\n{Colors.YELLOW}Hướng dẫn lấy link:\n1. Truy cập xworld.io và đăng nhập\n2. Vào game 'Chạy đua tốc độ'\n3. Copy link của trang game và dán vào đây{Colors.RESET}")
    print(f"{Colors.CYAN}📋 Vui lòng nhập link của bạn: {Colors.WHITE}", end=''); link = input()
    user_id = re.search(r'userId=(\d+)', link).group(1)
    secret_key = re.search(r'secretKey=([a-zA-Z0-9]+)', link).group(1)
    print(f"{Colors.GREEN}    ✓ Lấy thông tin thành công! User ID: {user_id}")
    json_data = {'user-id': user_id, 'user-secret-key': secret_key}
    with open('data-xw-cdtd.txt', 'w+', encoding='utf-8') as f: json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data
def populate_initial_history(s, headers):
    print(f"\n{Colors.GREEN}Đang lấy dữ liệu lịch sử ban đầu...{Colors.RESET}")
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            for issue_data in reversed(response['data']['recent_10']): logic_engine.add_result(issue_data['result'][0])
            print(f"{Colors.GREEN}✓ Nạp thành công lịch sử {len(response['data']['recent_10'])} ván.{Colors.RESET}"); return True
    except Exception as e: print(f"{Colors.RED}Lỗi khi nạp lịch sử: {e}{Colors.RESET}")
    return False
def fetch_latest_issue_info(s, headers):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        if response and response['data']['recent_10']:
            latest_issue = response['data']['recent_10'][0]; return latest_issue['issue_id'], latest_issue
    except Exception: return None, None
    return None, None
def check_issue_result(s, headers, kq, ki):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers, timeout=5).json()
        for issue in response['data']['recent_10']:
            if int(issue['issue_id']) == int(ki):
                actual_winner = issue['result'][0]; return actual_winner != kq, actual_winner
    except Exception: return None, None
    return None, None
def user_asset(s, headers):
    try:
        json_data = {'user_id': int(headers['user-id']), 'source': 'home'}
        return s.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json=json_data, timeout=5).json()['data']['user_asset']
    except Exception as e:
        print(f"{Colors.LOSS}Lỗi khi lấy số dư: {e}. Thử lại...{Colors.RESET}"); time.sleep(2); return user_asset(s, headers)
def bet_cdtd(s, headers, ki, kq, Coin, bet_amount):
    try:
        json_data = {'issue_id': int(ki), 'bet_group': 'not_winner', 'asset_type': Coin, 'athlete_id': kq, 'bet_amount': bet_amount}
        response = s.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=json_data, timeout=10).json()
        if not (response.get('code') == 0 and response.get('msg') == 'ok'):
            log_msg = f"{Colors.RED}Lỗi cược: {response.get('msg', 'Không rõ lỗi')}"; add_log(logs, log_msg)
        return response
    except requests.exceptions.RequestException as e:
        add_log(logs, f"{Colors.RED}Lỗi mạng khi đặt cược: {e}"); return None

# Vòng lặp chính của tool
def main_cdtd():
    s = requests.Session()
    data = load_data_cdtd()
    headers = {'user-id': data['user-id'], 'user-secret-key': data['user-secret-key'], 'user-agent': 'Mozilla/5.0'}
    asset = user_asset(s, headers)
    clear_screen()
    print(f"\n{Colors.CYAN}Chọn loại tiền bạn muốn chơi:{Colors.RESET}\n  1. USDT\n  2. BUILD\n  3. WORLD")
    while True:
        print(f"{Colors.CYAN}Nhập lựa chọn (1/2/3): {Colors.WHITE}", end=''); x = input()
        if x in ['1', '2', '3']: Coin = ['USDT', 'BUILD', 'WORLD'][int(x)-1]; break
        else: print(f"{Colors.LOSS}Lựa chọn không hợp lệ, vui lòng nhập lại...{Colors.RESET}")
    bet_amount0 = float(input(f'{Colors.CYAN}Nhập số {Coin} muốn đặt ban đầu: {Colors.WHITE}'))
    heso = int(input(f'{Colors.CYAN}Nhập hệ số cược sau khi thua: {Colors.WHITE}'))
    delay1 = int(input(f'{Colors.CYAN}Chơi bao nhiêu ván thì nghỉ (999 nếu không nghỉ): {Colors.WHITE}'))
    delay2 = int(input(f'{Colors.CYAN}Nghỉ trong bao nhiêu ván: {Colors.WHITE}'))
    stats = {'win': 0, 'lose': 0, 'streak': 0, 'max_streak': 0, 'lose_streak': 0, 'asset_0': asset.get(Coin, 0), 'total_bet': 0.0, 'lose_streak_1': 0, 'lose_streak_2': 0, 'lose_streak_3': 0, 'lose_streak_4': 0}
    config = {'bet_amount0': bet_amount0, 'heso': heso, 'start_time': time.time()}
    htr = []; logs = deque(maxlen=15); tong_van = 0
    populate_initial_history(s, headers); time.sleep(2)
    last_known_id, _ = fetch_latest_issue_info(s, headers)
    if not last_known_id: print(f"{Colors.RED}Không thể lấy ID ván đầu tiên. Vui lòng kiểm tra lại mạng và API.{Colors.RESET}"); sys.exit()
    while True:
        try:
            current_asset = user_asset(s, headers)
            status_msg = f"{Colors.YELLOW}Đang chờ ván #{last_known_id + 1} bắt đầu...{Colors.RESET}"
            display_dashboard(config, stats, current_asset, htr, logs, Coin, status_message=status_msg)
            newly_completed_id = last_known_id
            while newly_completed_id == last_known_id:
                time.sleep(1)
                newly_completed_id, newly_completed_issue_data = fetch_latest_issue_info(s, headers)
                if newly_completed_id is None: newly_completed_id = last_known_id
            last_known_id = newly_completed_id
            if newly_completed_issue_data and 'result' in newly_completed_issue_data:
                logic_engine.add_result(newly_completed_issue_data['result'][0])
            target_issue_id = last_known_id + 1; tong_van += 1
            bet_amount = bet_amount0
            if stats['lose_streak'] > 0: bet_amount = bet_amount0 * (heso ** stats['lose_streak'])
            kq = logic_engine.analyze_and_select(data['user-id'], target_issue_id)
            cycle = delay1 + delay2; pos = (tong_van - 1) % cycle if cycle > 0 else 0
            is_resting = pos >= delay1
            if not is_resting and kq is not None:
                response = bet_cdtd(s, headers, target_issue_id, kq, Coin, bet_amount)
                if response and response.get('code') == 0:
                    stats['total_bet'] += bet_amount
                    start_wait_time = time.time()
                    while True:
                        result, actual_winner = check_issue_result(s, headers, kq, target_issue_id)
                        if result is not None: break
                        elapsed = int(time.time() - start_wait_time)
                        wait_message = f"{Colors.YELLOW}⏳ Đang đợi kết quả kì #{target_issue_id}: {elapsed}s | {Colors.CYAN}Đã cược: {Colors.WHITE}{bet_amount:.4f} {Coin} (Né {NV.get(kq, kq)})"
                        display_dashboard(config, stats, current_asset, htr, logs, Coin, status_message=wait_message)
                        time.sleep(1)
                    htr.append({'kq': result, 'bet_amount': bet_amount})
                    log_msg = ""
                    if result:
                        ended_lose_streak = stats['lose_streak']
                        if ended_lose_streak == 1: stats['lose_streak_1'] += 1
                        elif ended_lose_streak == 2: stats['lose_streak_2'] += 1
                        elif ended_lose_streak == 3: stats['lose_streak_3'] += 1
                        elif ended_lose_streak == 4: stats['lose_streak_4'] += 1
                        logic_engine.record_win(); stats['win'] += 1; stats['streak'] += 1; stats['lose_streak'] = 0
                        stats['max_streak'] = max(stats['max_streak'], stats['streak'])
                        log_msg = (f"{Colors.GREEN}THẮNG{Colors.RESET} - Cược né {Colors.WHITE}{NV.get(kq, kq)}{Colors.RESET}, KQ về {Colors.CYAN}{NV.get(actual_winner, actual_winner)}{Colors.RESET}")
                    else:
                        logic_engine.record_loss(kq); stats['lose'] += 1; stats['lose_streak'] += 1; stats['streak'] = 0
                        log_msg = (f"{Colors.LOSS}THUA{Colors.RESET} - Cược né {Colors.WHITE}{NV.get(kq, kq)}{Colors.RESET}, KQ về {Colors.RED}{NV.get(actual_winner, actual_winner)}{Colors.RESET} (Trùng)")
                    add_log(logs, log_msg)
                    final_asset = user_asset(s, headers)
                    display_dashboard(config, stats, final_asset, htr, logs, Coin)
                    delay_next_round = random.uniform(5, 10); time.sleep(delay_next_round)
            else:
                rest_msg = ""
                if kq is None: rest_msg = f"{Colors.YELLOW}💤 Bỏ qua ván này do không đủ dữ liệu."
                else: rest_msg = f"{Colors.YELLOW}💤 Ván này tạm nghỉ. Tiếp tục sau {cycle - pos} ván nữa."
                add_log(logs, rest_msg)
                display_dashboard(config, stats, current_asset, htr, logs, Coin, status_message=rest_msg)
                time.sleep(30)
        except KeyboardInterrupt: print(f"\n\n{Colors.YELLOW}Đã dừng tool. Cảm ơn bạn đã sử dụng!{Colors.RESET}"); sys.exit()
        except Exception as e: add_log(logs, f"{Colors.RED}Lỗi không xác định: {e}. Tự khởi động lại sau 10s."); time.sleep(10)

def show_banner():
    clear_screen()
    banner = f"""
{Colors.CYAN}
 ████████╗██████╗ ██╗  ██╗
 ╚══██╔══╝██╔══██╗██║ ██╔╝
    ██║   ██║  ██║█████╔╝ 
    ██║   ██║  ██║██╔═██╗ 
    ██║   ██████╔╝██║  ██╗
    ╚═╝   ╚═════╝ ╚═╝  ╚═╝ 
{Colors.RESET}
    """
    print(banner)
    # <<< THAY ĐỔI: Thay thế thông tin admin bằng "Tool VIP V8" >>>
    print(f"{Colors.CYAN}Tool VIP V8{Colors.RESET}\n")
    time.sleep(3)

# <<< SỬA LỖI: Sửa lại khối thực thi chính để chạy xác thực trước >>>
if __name__ == "__main__":
    # 1. Chạy quá trình xác thực key trước.
    authentication_successful = main_authentication()

    # 2. Nếu xác thực thành công, mới chạy tool chính.
    if authentication_successful:
        show_banner()
        main_cdtd()
    else:
        # Nếu xác thực thất bại, in thông báo và thoát.
        print(f"\n{do}Xác thực không thành công. Vui lòng chạy lại tool.{end}")
        sys.exit()

