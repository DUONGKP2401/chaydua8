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
import platform
import subprocess
import hashlib
import statistics
import string
import urllib.parse

# Check và cài đặt các thư viện cần thiết
try:
    from faker import Faker
    from requests import session
    from colorama import Fore, Style, init
    import pystyle
    init(autoreset=True) # init() từ v9.py để đảm bảo màu sắc reset đúng cách
except ImportError:
    print('__Đang cài đặt các thư viện cần thiết, vui lòng chờ...__')
    os.system("pip install faker requests colorama bs4 pystyle rich")
    os.system("pip3 install requests pysocks")
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()


# =====================================================================================
# PHẦN 2: MÃ NGUỒN TỪ FILE banner.py (HỆ THỐNG XÁC THỰC)
# =====================================================================================

# --- Cấu hình và các biến màu sắc ---
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/KEY-VIP.txt/main/KEY-VIP.txt"
VIP_CACHE_FILE = 'vip_cache.json'
xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

# Đổi tên hàm 'banner' của file banner.py thành 'authentication_banner' để tránh xung đột
def authentication_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_text = f"""
{luc}████████╗ ██████╗░░ ██╗░░██╗░
{luc}╚══██╔══╝ ██╔══██╗░ ██║██╔╝░░
{luc}░░░██║░░░ ██║░░██║░ █████╔╝░░
{luc}░░░██║░░░ ██║░░██║░ ██╔═██╗░░
{luc}░░░██║░░░ ██║░░██║░ ██║░╚██╗░
{luc}░░░╚═╝░░░ ╚█████╔╝░ ╚═╝░░╚═╝░
{trang}══════════════════════════

{vang}Admin: DUONG PHUNG
{vang}Nhóm Zalo: https://zalo.me/g/ddxsyp497
{vang}Tele: @tankeko12
{trang}══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        sleep(0.0001)

# --- Các hàm lấy thông tin thiết bị ---
def get_device_id():
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
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json().get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    authentication_banner() # Gọi hàm banner đã đổi tên
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")
    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")

# --- Các hàm xử lý Key Free ---
def luu_thong_tin_ip(ip, key, expiration_date):
    data = {ip: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open('ip_key.json', 'w') as file:
        file.write(encrypted_data)

def tai_thong_tin_ip():
    try:
        with open('ip_key.json', 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def kiem_tra_ip(ip):
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
    ngay = int(datetime.now().day)
    key1 = str(ngay * 27 + 27)
    ip_numbers = ''.join(filter(str.isdigit, ip_address))
    key = f'VTD9{key1}{ip_numbers}'
    expiration_date = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
    url = f'https://tdkvuatocdo.blogspot.com/2025/09/key-vtdv9_18.html?m={key}'
    return url, key, expiration_date

def get_shortened_link_phu(url):
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={url}"
        response = requests.get(api_url, timeout=5)
        return response.json() if response.status_code == 200 else {"status": "error", "message": "Lỗi kết nối dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(ip_address):
    url, key, expiration_date = generate_key_and_url(ip_address)
    yeumoney_data = get_shortened_link_phu(url)
    if yeumoney_data.get('status') == "error":
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

# --- Các hàm xử lý Key VIP ---
def save_vip_key_info(device_id, key, expiration_date_str):
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        now = datetime.now()
        if expiry_date > now:
            delta = expiry_date - now
            days, remainder = delta.days, delta.seconds
            hours, remainder = divmod(remainder, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"{xnhac}Key VIP của bạn còn lại: {luc}{days} ngày, {hours} giờ, {minutes} phút.{trang}")
        else:
            print(f"{do}Key VIP của bạn đã hết hạn.{trang}")
    except ValueError:
        print(f"{vang}Không thể xác định ngày hết hạn của key.{trang}")

def check_vip_key(machine_id, user_key):
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
                        return ('valid', key_ngay_het_han) if expiry_date.date() >= datetime.now().date() else ('expired', None)
                    except ValueError: continue
        return 'not_found', None
    except requests.exceptions.RequestException as e:
        print(f"{do}Lỗi kết nối đến server key: {e}{trang}")
        return 'error', None

# --- Luồng xác thực chính ---
def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)
    if not ip_address or not device_id:
        print(f"{do}Không thể lấy thông tin thiết bị. Vui lòng kiểm tra kết nối mạng.{trang}")
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
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng nhập key mới.{trang}")
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
                elif status == 'expired': print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
                elif status == 'not_found': print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
                else: print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
                sleep(2)
            elif choice == '2':
                return process_free_key(ip_address)
            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")
        except KeyboardInterrupt:
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()

# =====================================================================================
# PHẦN 3: MÃ NGUỒN TỪ FILE v9.py (TOOL GAME AI)
# =====================================================================================
NV = {
    1: '⚔️ Bậc thầy tấn công', 2: '👊 Quyền sắt', 3: '🤿 Thợ lặn sâu',
    4: '⚽ Cơn lốc sân cỏ', 5: '🏇 Hiệp sĩ phi nhanh', 6: '⚾ Vua home run'
}

class SmartAI:
    def __init__(self):
        self.total_logics = 50
        self.current_logic = 0
        self.selection_history = deque(maxlen=10)
        self.result_history = deque(maxlen=20)
        self.logic_performance = {i: {'wins': 0, 'total': 0, 'win_rate': 0.0} for i in range(1, self.total_logics + 1)}

    def add_result(self, selected, actual_winner):
        is_win = (selected != actual_winner)
        self.result_history.append({'selected': selected, 'winner': actual_winner, 'is_win': is_win, 'logic_used': self.current_logic})
        if self.current_logic in self.logic_performance:
            perf = self.logic_performance[self.current_logic]
            perf['total'] += 1
            if is_win: perf['wins'] += 1
            perf['win_rate'] = perf['wins'] / perf['total'] if perf['total'] > 0 else 0.0

    def check_triple_pattern(self):
        if len(self.selection_history) >= 3:
            last_three = list(self.selection_history)[-3:]
            if len(set(last_three)) == 1: return True, last_three[0]
        return False, None

    def get_safe_alternatives(self, avoid_char, top100_data):
        alternatives = [i for i in range(1, 7) if i != avoid_char]
        try:
            win_counts = [(char, top100_data[1][char - 1]) for char in alternatives]
            win_counts.sort(key=lambda x: x[1])
            return [char for char, _ in win_counts]
        except: return alternatives

    def logic_1_min_wins_100(self, top10, top100):
        try:
            min_wins = min(top100[1])
            return random.choice([i + 1 for i, wins in enumerate(top100[1]) if wins == min_wins])
        except: return random.randint(1, 6)

    def logic_2_avoid_last_winner(self, top10, top100):
        try:
            if top10[1]:
                return random.choice([i for i in range(1, 7) if i != top10[1][0]])
        except: pass
        return self.logic_1_min_wins_100(top10, top100)

    def logic_3_balanced_distribution(self, top10, top100):
        try:
            avg_wins = sum(top100[1]) / len(top100[1])
            return max(range(1, 7), key=lambda i: avg_wins - top100[1][i - 1])
        except: return random.randint(1, 6)

    def logic_4_contrarian_strategy(self, top10, top100):
        try:
            if len(top10[1]) >= 3:
                most_common = Counter(top10[1][:3]).most_common(1)[0][0]
                return random.choice([i for i in range(1, 7) if i != most_common])
        except: pass
        return self.logic_1_min_wins_100(top10, top100)
    
    def logic_5_fibonacci_sequence(self, top10, top100):
        fib = [1, 1, 2, 3, 5, 8]
        return ((fib[len(self.result_history) % 6] - 1) % 6) + 1

    def logic_6_golden_ratio(self, top10, top100):
        phi = (1 + math.sqrt(5)) / 2
        return int((len(self.result_history) * phi) % 6) + 1
    
    def logic_7_entropy_maximization(self, top10, top100):
        if not self.selection_history: return self.logic_1_min_wins_100(top10, top100)
        return max(range(1, 7), key=lambda c: -sum( (v/sum(Counter(list(self.selection_history)+[c]).values())) * math.log2(v/sum(Counter(list(self.selection_history)+[c]).values())) for v in Counter(list(self.selection_history)+[c]).values()))

    def logic_8_markov_chain(self, top10, top100):
        try:
            if len(self.result_history) < 2: return self.logic_1_min_wins_100(top10, top100)
            transitions = defaultdict(list)
            for i in range(len(self.result_history) - 1):
                transitions[self.result_history[i]['winner']].append(self.result_history[i+1]['winner'])
            last_winner = self.result_history[-1]['winner']
            if last_winner in transitions:
                next_counts = Counter(transitions[last_winner])
                predicted_next = min(next_counts, key=next_counts.get)
                return random.choice([i for i in range(1, 7) if i != predicted_next])
        except: pass
        return self.logic_1_min_wins_100(top10, top100)

    def logic_9_regression_mean(self, top10, top100):
        try:
            mean_wins = statistics.mean(top100[1])
            return max(range(1, 7), key=lambda i: mean_wins - top100[1][i-1] if top100[1][i-1] < mean_wins else -1)
        except: return random.randint(1, 6)

    def logic_10_monte_carlo(self, top10, top100):
        try:
            total_wins = sum(top100[1]) or 1
            return max(range(1, 7), key=lambda char: sum(1 for _ in range(100) if random.random() < (1 - (top100[1][char-1] / total_wins))))
        except: return random.randint(1, 6)

    def get_logic_function(self, logic_id):
        base_logics = {1: self.logic_1_min_wins_100, 2: self.logic_2_avoid_last_winner, 3: self.logic_3_balanced_distribution, 4: self.logic_4_contrarian_strategy, 5: self.logic_5_fibonacci_sequence, 6: self.logic_6_golden_ratio, 7: self.logic_7_entropy_maximization, 8: self.logic_8_markov_chain, 9: self.logic_9_regression_mean, 10: self.logic_10_monte_carlo}
        if logic_id <= 10: return base_logics[logic_id]
        base_logic_func = base_logics[(logic_id - 1) % 10 + 1]
        
        def enhanced_logic(top10, top100):
            base_result = base_logic_func(top10, top100)
            if logic_id <= 20 and len(top10[1]) >= 2:
                avoid_list = top10[1][:2]
                if base_result in avoid_list: return random.choice([i for i in range(1, 7) if i not in avoid_list] or [base_result])
            elif logic_id <= 30 and len(self.selection_history) >= 2 and len(set(list(self.selection_history)[-2:])) == 1:
                last_selected = list(self.selection_history)[-1]
                if base_result == last_selected: return random.choice([i for i in range(1, 7) if i != last_selected])
            elif logic_id <= 40 and len(top10[1]) >= 5:
                trend_char = Counter(top10[1][:5]).most_common(1)[0][0]
                if base_result == trend_char: return random.choice([i for i in range(1, 7) if i != trend_char])
            elif logic_id > 40 and len(self.result_history) >= 5:
                recent_perf = [r for r in list(self.result_history)[-5:] if r['logic_used'] == ((logic_id - 1) % 10 + 1)]
                if recent_perf and sum(r['is_win'] for r in recent_perf) / len(recent_perf) < 0.3:
                    return random.choice([i for i in range(1, 7) if i != base_result])
            return base_result
        return enhanced_logic

    def next_logic(self):
        self.current_logic = (self.current_logic % self.total_logics) + 1
        return self.current_logic

    def analyze_and_select(self, top10_data, top100_data):
        try:
            is_triple, repeated_char = self.check_triple_pattern()
            if is_triple:
                safe_alternatives = self.get_safe_alternatives(repeated_char, top100_data)
                selected = safe_alternatives[0] if safe_alternatives else random.randint(1, 6)
                logic_name = f"🛡️ ANTI-PATTERN (tránh {NV.get(repeated_char, 'N/A')})"
            else:
                current_logic_id = self.next_logic()
                logic_function = self.get_logic_function(current_logic_id)
                selected = logic_function(top10_data, top100_data)
                logic_name = f"🧠 LOGIC_{current_logic_id}"
            
            selected = int(selected)
            if not (1 <= selected <= 6): selected = random.randint(1, 6)
            self.selection_history.append(selected)
            return selected, logic_name
        except Exception as e:
            prints(255, 0, 0, f'❌ Lỗi AI: {e}')
            fallback = random.randint(1, 6)
            self.selection_history.append(fallback)
            return fallback, "🚨 FALLBACK_MODE"

smart_ai = SmartAI()

def clear_screen():
    os.system('cls' if platform.system() == "Windows" else 'clear')

def prints(r, g, b, text="text", end="\n"):
    print("\033[38;2;{};{};{}m{}\033[0m".format(r, g, b, text), end=end)

# Đổi tên hàm 'banner' của file v9.py thành 'game_banner' để tránh xung đột
def game_banner(game):
    banner_txt = """
████████╗██████╗ ██╗  ██╗
╚══██╔══╝██╔══██╗██║ ██╔╝
   ██║   ██████╔╝█████╔╝ 
   ██║   ██╔═══╝ ██╔═██╗ 
   ██║   ██║     ██║  ██╗
   ╚═╝   ╚═╝     ╚═╝  ╚═╝  
    """
    for i in banner_txt.split('\n'):
        x, y, z = 200, 255, 255
        for j in range(len(i)):
            prints(x, y, z, i[j], end='')
            x -= 4; time.sleep(0.001)
        print()
    prints(247, 255, 97, "✨" + "═" * 45 + "✨")
    prints(32, 230, 151, f"🌟 XWORLD AI - {game} v9.0🌟".center(47))
    prints(247, 255, 97, "═" * 47)
    prints(255, 215, 0, "🧠 50 LOGIC AI ANALYSIS SYSTEM 🧠".center(47))
    prints(255, 100, 100, "🛡️ ANTI-PATTERN PROTECTION 🛡️".center(47))
    prints(100, 255, 100, "🎯 MAXIMUM SAFETY & ACCURACY 🎯".center(47))
    prints(247, 255, 97, "═" * 47)
    prints(7, 205, 240, "📱 Telegram: @tankeko12")
    prints(7, 205, 240, "👥 Nhóm Zalo: https://zalo.me/g/ddxsyp497 ")
    prints(7, 205, 240, "👨‍💼 Admin: Duong Phung ")
    prints(247, 255, 97, "═" * 47)

def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        prints(0, 255, 243, 'Bạn có muốn sử dụng thông tin đã lưu hay không? (y/n): ', end='')
        if input().lower() == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f:
                return json.load(f)
        prints(247, 255, 97, "═" * 47)
    guide = "Huướng dẫn lấy link:\n1.Truy cập xworld.io\n2.Đăng nhập\n3.Vào Chạy đua tốc độ\n4.Nhấn 'Lập tức truy cập'\n5.Copy link và dán vào đây"
    prints(218, 255, 125, guide)
    prints(247, 255, 97, "═" * 47)
    prints(125, 255, 168, '📋Nhập link của bạn: ', end=' ')
    link = input()
    user_id = link.split('?userId=')[1].split('&')[0]
    user_secretkey = link.split('secretKey=')[1].split('&')[0]
    prints(218, 255, 125, f'    User id: {user_id}')
    prints(218, 255, 125, f'    User secret key: {user_secretkey}')
    json_data = {'user-id': user_id, 'user-secret-key': user_secretkey}
    with open('data-xw-cdtd.txt', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data

def top_100_cdtd(s):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_100_issues', headers={'user-agent': 'Mozilla/5.0'}).json()
        return list(range(1, 7)), [response['data']['athlete_2_win_times'][str(i)] for i in range(1, 7)]
    except Exception as e:
        prints(255, 0, 0, f'Lỗi khi lấy top 100: {e}'); time.sleep(2); return top_100_cdtd(s)

def top_10_cdtd(s, headers):
    try:
        response = s.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=headers).json()
        data = response['data']['recent_10']
        return [i['issue_id'] for i in data], [i['result'][0] for i in data]
    except Exception as e:
        prints(255, 0, 0, f'Lỗi khi lấy top 10: {e}'); time.sleep(2); return top_10_cdtd(s, headers)

def kiem_tra_kq_cdtd(s, headers, kq, ki):
    start = time.time()
    prints(0, 255, 37, f'⏰ Đang đợi kết quả của kì #{ki}...')
    while True:
        data_top10_cdtd = top_10_cdtd(s, headers)
        if int(data_top10_cdtd[0][0]) == int(ki):
            actual_winner = data_top10_cdtd[1][0]
            prints(0, 255, 30, f'🏆 Kết quả kì {ki}: {NV[int(actual_winner)]}')
            smart_ai.add_result(kq, actual_winner)
            if actual_winner == kq:
                prints(255, 0, 0, '😔 Bạn đã thua. Chúc bạn may mắn lần sau!'); return False
            else:
                prints(0, 255, 37, '🎉 Xin chúc mừng! Bạn đã thắng!'); return True
        prints(0, 255, 197, f'⏳ Đang đợi kết quả... {time.time() - start:.0f}s', end='\r')
        time.sleep(2)

def user_asset(s, headers):
    try:
        response = s.post('https://wallet.3games.io/api/wallet/user_asset', headers=headers, json={'user_id': int(headers['user-id']), 'source': 'home'}).json()
        asset_data = response.get('data', {}).get('user_asset', {})
        return {'USDT': float(asset_data.get('USDT', 0)), 'WORLD': float(asset_data.get('WORLD', 0)), 'BUILD': float(asset_data.get('BUILD', 0))}
    except Exception as e:
        prints(255, 0, 0, f'Lỗi khi lấy số dư: {e}'); return {'USDT': 0.0, 'WORLD': 0.0, 'BUILD': 0.0}

def print_stats_cdtd(stats, s, headers, Coin):
    try:
        asset = user_asset(s, headers)
        prints(70, 240, 234, '📊 Thống kê AI Performance:')
        win_rate = stats["win"] / (stats["win"] + stats["lose"]) * 100 if (stats["win"] + stats["lose"]) > 0 else 0
        prints(50, 237, 65, f'🎯 Tỷ lệ thắng: {stats["win"]}/{stats["win"]+stats["lose"]} ({win_rate:.1f}%)')
        prints(50, 237, 65, f'🔥 Chuỗi thắng: {stats["streak"]} (Max: {stats["max_streak"]})')
        loi = asset.get(Coin, 0) - stats.get('asset_0', 0)
        color, symbol = ((0, 255, 20), "📈") if loi >= 0 else ((255, 100, 100), "📉")
        prints(*color, f"{symbol} P&L: {loi:+.2f} {Coin}")
        best_logic = max(smart_ai.logic_performance.items(), key=lambda x: x[1]['win_rate'] if x[1]['total'] > 0 else -1)
        if best_logic[1]['total'] > 0:
            prints(150, 255, 150, f"🧠 Best Logic: #{best_logic[0]} ({best_logic[1]['win_rate']:.1%})")
    except Exception as e: prints(255, 0, 0, f'❌ Lỗi thống kê: {e}')

def print_wallet(asset):
    prints(23, 232, 159, f'💰 USDT: {asset.get("USDT", 0):.2f} | 🌍 WORLD: {asset.get("WORLD", 0):.2f} | 🏗️ BUILD: {asset.get("BUILD", 0):.2f}'.center(60))

def bet_cdtd(s, headers, ki, kq, Coin, bet_amount):
    prints(255, 255, 0, f'💸 Đang đặt {bet_amount:.2f} {Coin} cho kì #{ki}...')
    try:
        json_data = {'issue_id': int(ki), 'bet_group': 'not_winner', 'asset_type': Coin, 'athlete_id': int(kq), 'bet_amount': float(bet_amount)}
        response = s.post('https://api.sprintrun.win/sprint/bet', headers=headers, json=json_data).json()
        if response.get('code') == 0 and response.get('msg') == 'ok':
            prints(0, 255, 19, f'✅ Đặt cược thành công vào "Ai không là quán quân"')
            prints(100, 255, 100, f'🎯 Target: Tránh {NV[int(kq)]}')
        else:
            prints(255, 100, 0, f'⚠️ Lỗi đặt cược: {response.get("msg", "Không rõ lỗi")}')
    except Exception as e:
        prints(255, 0, 0, f'❌ Lỗi hệ thống khi đặt cược: {e}')

def main_cdtd():
    s = requests.Session()
    game_banner("CHẠY ĐUA TỐC ĐỘ") # Gọi hàm banner đã đổi tên
    data = load_data_cdtd()
    headers = {'user-id': data['user-id'], 'user-secret-key': data['user-secret-key'], **{'accept': '*/*','user-agent': 'Mozilla/5.0','origin': 'https://xworld.info','referer': 'https://xworld.info/'}}
    asset = user_asset(s, headers)
    print_wallet(asset)
    prints(219, 237, 138, "💰 Chọn loại tiền:\n    1️⃣ USDT\n    2️⃣ BUILD\n    3️⃣ WORLD")
    while True:
        x = input('Nhập lựa chọn (1/2/3): ')
        if x in ['1', '2', '3']: Coin = ['USDT', 'BUILD', 'WORLD'][int(x)-1]; break
        else: prints(247, 30, 30, 'Nhập sai!', end='\r')
    bet_amount0 = float(input(f'Nhập số {Coin} muốn đặt: '))
    heso = float(input('Nhập hệ số cược sau thua: '))
    delay1 = int(input('Chơi bao nhiêu ván thì nghỉ (999 nếu không nghỉ): '))
    delay2 = int(input(f'Nghỉ bao nhiêu ván sau {delay1} ván chơi: '))
    stats = {'win': 0, 'lose': 0, 'streak': 0, 'max_streak': 0, 'asset_0': asset.get(Coin, 0)}
    clear_screen(); game_banner('CHẠY ĐUA TỐC ĐỘ')
    htr = []; tong = 0
    while True:
        tong += 1; prints(247, 255, 97, "═" * 47)
        print_wallet(user_asset(s, headers))

        # Lấy dữ liệu ban đầu để AI phân tích
        data_top10_for_analysis, data_top100 = top_10_cdtd(s, headers), top_100_cdtd(s)
        
        bet_amount = (heso * htr[-1]['bet_amount']) if htr and not htr[-1]['kq'] else bet_amount0
        
        # AI thực hiện phân tích dựa trên dữ liệu đã lấy
        kq, logic_name = smart_ai.analyze_and_select(data_top10_for_analysis, data_top100)
        
        print_stats_cdtd(stats, s, headers, Coin)
        prints(0, 246, 255, f'🤖 AI V9 CHỌN: {NV.get(int(kq), "N/A")} ({logic_name})')
        
        pos = (tong - 1) % (delay1 + delay2) if (delay1 + delay2) > 0 else 0
        stop = pos >= delay1

        # <<< SỬA LỖI: Lấy lại dữ liệu top 10 mới nhất ngay trước khi đặt cược để có ID phiên chính xác >>>
        try:
            latest_data_top10 = top_10_cdtd(s, headers)
            current_betting_issue_id = latest_data_top10[0][0] + 1
        except (requests.exceptions.RequestException, IndexError, TypeError) as e:
            prints(255, 0, 0, f"❌ Không thể lấy kì mới nhất để đặt cược: {e}")
            time.sleep(5)
            continue # Bỏ qua vòng lặp này và thử lại

        if not stop:
            # Sử dụng ID phiên mới nhất để đặt cược
            bet_cdtd(s, headers, current_betting_issue_id, kq, Coin, bet_amount)
        else:
            prints(255, 255, 0, 'Ván này tạm nghỉ theo lịch...'); bet_amount = bet_amount0
        
        # Sử dụng cùng một ID phiên đó để kiểm tra kết quả, đảm bảo tính nhất quán
        result = kiem_tra_kq_cdtd(s, headers, kq, current_betting_issue_id)

        if not stop:
            htr.append({'kq': result, 'bet_amount': bet_amount})
            if result: 
                stats['win'] += 1
                stats['streak'] += 1
                stats['max_streak'] = max(stats['max_streak'], stats['streak'])
            else: 
                stats['lose'] += 1
                stats['streak'] = 0
        time.sleep(10)

# =====================================================================================
# PHẦN 4: ĐIỂM KHỞI ĐỘNG CHÍNH CỦA CHƯƠNG TRÌNH
# =====================================================================================
if __name__ == "__main__":
    try:
        # Bước 1: Chạy quy trình xác thực
        authentication_successful = main_authentication()

        # Bước 2: Nếu xác thực thành công, chạy tool game
        if authentication_successful:
            print("\n" + luc + "✅ Xác thực thành công! Đang khởi động tool game..." + trang)
            time.sleep(2)
            main_cdtd()
        else:
            print("\n" + do + "❌ Xác thực không thành công. Không thể khởi động tool." + trang)
            time.sleep(3)
            sys.exit()
    except KeyboardInterrupt:
        print(f"\n{vang}Đã dừng tool theo yêu cầu người dùng. Tạm biệt!{trang}")
        sys.exit()
    except Exception as e:
        print(f"\n{do}Lỗi không xác định: {e}{trang}")
        # Ghi log lỗi để debug
        with open("error_log.txt", "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
        sys.exit()
