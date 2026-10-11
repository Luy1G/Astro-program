import random
import time
import os
import sys

SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣ ", "⭐"]
SYMBOL_NAMES = ["樱桃", "柠檬", "橙子", "葡萄", "铃铛", "钻石", "七", "星星"]

PAYOUTS = {
    "🍒": 2,
    "🍋": 3,
    "🍊": 4,
    "🍇": 5,
    "🔔": 8,
    "💎": 15,
    "7️⃣ ": 25,
    "⭐": 50,
}

WEIGHTS = [25, 20, 18, 15, 10, 7, 3, 2]

BET_OPTIONS = [10, 25, 50, 100, 200, 500]


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def weighted_choice():
    total = sum(WEIGHTS)
    r = random.randint(1, total)
    cumulative = 0
    for i, w in enumerate(WEIGHTS):
        cumulative += w
        if r <= cumulative:
            return SYMBOLS[i]
    return SYMBOLS[0]


def spin_reel(stop_symbol=None, delay=0.1):
    spins = random.randint(8, 15)
    for i in range(spins):
        sym = random.choice(SYMBOLS)
        sys.stdout.write(f"\r  [ {sym} ]")
        sys.stdout.flush()
        time.sleep(delay)
    if stop_symbol:
        sys.stdout.write(f"\r  [ {stop_symbol} ]")
        sys.stdout.flush()
    print()


def calculate_winnings(reel1, reel2, reel3, bet):
    if reel1 == reel2 == reel3:
        multiplier = PAYOUTS.get(reel1, 2)
        return bet * multiplier, "三连！"
    elif reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
        matching = reel1 if reel1 == reel2 or reel1 == reel3 else reel2
        multiplier = max(PAYOUTS.get(matching, 2) // 3, 1)
        return bet * multiplier, "两连！"
    else:
        return 0, ""


def display_game(balance, bet, reels=None, message="", win_amount=0):
    clear_screen()
    print("=" * 50)
    print("          ★ 幸运老虎机 ★")
    print("=" * 50)
    print()
    print(f"  💰 余额: ¥{balance:<10}  🎯 下注: ¥{bet}")
    print()
    print("  ┌─────────────────────────┐")
    if reels:
        print(f"  │  [ {reels[0]} ] [ {reels[1]} ] [ {reels[2]} ]  │")
    else:
        print(f"  │  [ ? ] [ ? ] [ ? ]  │")
    print("  └─────────────────────────┘")
    print()
    if message:
        if win_amount > 0:
            print(f"  🎉 {message} 赢得 ¥{win_amount}！🎉")
        else:
            print(f"  😔 {message}")
    print()
    print("─" * 50)
    print("  赔率表:")
    print("  ┌────────┬────────┬────────┐")
    print("  │  符号  │ 三连倍 │ 两连倍 │")
    print("  ├────────┼────────┼────────┤")
    for sym in SYMBOLS:
        idx = SYMBOLS.index(sym)
        name = SYMBOL_NAMES[idx]
        triple = PAYOUTS[sym]
        double = max(triple // 3, 1)
        print(f"  │ {sym} {name} │  x{triple:<4} │  x{double:<4} │")
    print("  └────────┴────────┴────────┘")
    print()
    print("─" * 50)
    print("  操作: [空格]旋转  [↑↓]调整下注  [q]退出")
    print("=" * 50)


def get_key():
    if os.name == "nt":
        import msvcrt
        key = msvcrt.getch()
        if key == b'\xe0':
            key = msvcrt.getch()
            if key == b'H':
                return 'up'
            elif key == b'P':
                return 'down'
        elif key == b' ':
            return 'space'
        elif key == b'q' or key == b'Q':
            return 'q'
        elif key == b'\r':
            return 'space'
        return ''
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            if key == '\x1b':
                key = sys.stdin.read(2)
                if key == '[A':
                    return 'up'
                elif key == '[B':
                    return 'down'
            elif key == ' ':
                return 'space'
            elif key == 'q' or key == 'Q':
                return 'q'
            elif key == '\r':
                return 'space'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ''


def animate_spin(bet):
    reel1 = weighted_choice()
    reel2 = weighted_choice()
    reel3 = weighted_choice()

    print("\n  旋转中...")
    time.sleep(0.3)

    print("  第1列: ", end="")
    spin_reel(reel1, 0.05)
    time.sleep(0.2)

    print("  第2列: ", end="")
    spin_reel(reel2, 0.05)
    time.sleep(0.2)

    print("  第3列: ", end="")
    spin_reel(reel3, 0.05)
    time.sleep(0.3)

    return reel1, reel2, reel3


def main():
    balance = 1000
    bet_index = 0
    bet = BET_OPTIONS[bet_index]
    reels = None
    message = "按空格键开始旋转！"
    win_amount = 0

    while True:
        display_game(balance, bet, reels, message, win_amount)

        if balance <= 0:
            print("\n  💸 你已经破产了！游戏结束！")
            print("  按任意键退出...")
            get_key()
            break

        key = get_key()

        if key == 'q':
            clear_screen()
            print(f"\n  最终余额: ¥{balance}")
            print("  感谢游玩！再见！\n")
            break
        elif key == 'up':
            bet_index = min(bet_index + 1, len(BET_OPTIONS) - 1)
            bet = BET_OPTIONS[bet_index]
            message = ""
            win_amount = 0
        elif key == 'down':
            bet_index = max(bet_index - 1, 0)
            bet = BET_OPTIONS[bet_index]
            message = ""
            win_amount = 0
        elif key == 'space':
            if bet > balance:
                message = "余额不足！请减少下注金额"
                win_amount = 0
                continue

            balance -= bet
            display_game(balance, bet, None, "旋转中...", 0)

            reel1, reel2, reel3 = animate_spin(bet)
            reels = [reel1, reel2, reel3]

            winnings, result_type = calculate_winnings(reel1, reel2, reel3, bet)

            if winnings > 0:
                balance += winnings
                win_amount = winnings
                message = f"{result_type} 恭喜！"
            else:
                win_amount = 0
                message = "没有中奖，再试试！"

            if balance < bet:
                for i in range(len(BET_OPTIONS)):
                    if BET_OPTIONS[i] <= balance:
                        bet_index = i
                bet = BET_OPTIONS[bet_index]
                if bet > balance:
                    bet_index = 0
                    bet = BET_OPTIONS[0]


if __name__ == "__main__":
    main()
