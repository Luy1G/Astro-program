import random
import time

class BaccaratGame:
    def __init__(self):
        self.balance = 10000
        self.current_bet = 0
        self.bet_amount = 100
        self.bet_type = None
        self.deck = []
        self.player_cards = []
        self.banker_cards = []
        self.create_deck()
        self.shuffle_deck()
    
    def create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        for _ in range(8):
            for suit in suits:
                for rank in ranks:
                    self.deck.append({'rank': rank, 'suit': suit})
    
    def shuffle_deck(self):
        random.shuffle(self.deck)
    
    def draw_card(self):
        if len(self.deck) < 10:
            self.create_deck()
            self.shuffle_deck()
        return self.deck.pop()
    
    def get_card_value(self, card):
        if card['rank'] == 'A':
            return 1
        elif card['rank'] in ['J', 'Q', 'K']:
            return 0
        else:
            return int(card['rank'])
    
    def calculate_score(self, cards):
        total = sum(self.get_card_value(card) for card in cards)
        return total % 10
    
    def display_cards(self, cards, name):
        print(f"{name}的牌:")
        for card in cards:
            print(f"  {card['rank']}{card['suit']}")
        score = self.calculate_score(cards)
        print(f"{name}的点数: {score}")
        print()
    
    def select_bet_type(self):
        print("\n请选择下注类型:")
        print("1. 玩家 (赔率 1:1)")
        print("2. 庄家 (赔率 0.95:1)")
        print("3. 和局 (赔率 8:1)")
        
        while True:
            choice = input("请输入选择 (1-3): ")
            if choice == '1':
                return 'player'
            elif choice == '2':
                return 'banker'
            elif choice == '3':
                return 'tie'
            else:
                print("输入无效，请重新输入")
    
    def select_bet_amount(self):
        print(f"\n当前余额: ¥{self.balance}")
        print(f"当前下注金额: ¥{self.bet_amount}")
        print("1. 增加下注金额")
        print("2. 减少下注金额")
        print("3. 确认下注")
        
        while True:
            choice = input("请输入选择 (1-3): ")
            if choice == '1':
                if self.bet_amount + 100 <= self.balance:
                    self.bet_amount += 100
                    print(f"下注金额已调整为: ¥{self.bet_amount}")
                else:
                    print("余额不足，无法增加下注金额")
            elif choice == '2':
                if self.bet_amount > 100:
                    self.bet_amount -= 100
                    print(f"下注金额已调整为: ¥{self.bet_amount}")
                else:
                    print("下注金额已达到最小值")
            elif choice == '3':
                return self.bet_amount
            else:
                print("输入无效，请重新输入")
    
    def deal(self):
        self.player_cards = []
        self.banker_cards = []
        
        self.player_cards.append(self.draw_card())
        self.banker_cards.append(self.draw_card())
        self.player_cards.append(self.draw_card())
        self.banker_cards.append(self.draw_card())
        
        print("\n=== 发牌中 ===")
        time.sleep(1)
        self.display_cards(self.player_cards, "玩家")
        time.sleep(1)
        self.display_cards(self.banker_cards, "庄家")
        time.sleep(1)
        
        player_score = self.calculate_score(self.player_cards)
        banker_score = self.calculate_score(self.banker_cards)
        
        if player_score >= 8 or banker_score >= 8:
            return
        
        if player_score <= 5:
            print("玩家要牌...")
            time.sleep(1)
            self.player_cards.append(self.draw_card())
            self.display_cards(self.player_cards, "玩家")
            time.sleep(1)
            
            new_player_score = self.calculate_score(self.player_cards)
            third_card_value = self.get_card_value(self.player_cards[2])
            
            if banker_score <= 2:
                print("庄家要牌...")
                time.sleep(1)
                self.banker_cards.append(self.draw_card())
                self.display_cards(self.banker_cards, "庄家")
            elif banker_score == 3 and third_card_value != 8:
                print("庄家要牌...")
                time.sleep(1)
                self.banker_cards.append(self.draw_card())
                self.display_cards(self.banker_cards, "庄家")
            elif banker_score == 4 and 2 <= third_card_value <= 7:
                print("庄家要牌...")
                time.sleep(1)
                self.banker_cards.append(self.draw_card())
                self.display_cards(self.banker_cards, "庄家")
            elif banker_score == 5 and 4 <= third_card_value <= 7:
                print("庄家要牌...")
                time.sleep(1)
                self.banker_cards.append(self.draw_card())
                self.display_cards(self.banker_cards, "庄家")
            elif banker_score == 6 and 6 <= third_card_value <= 7:
                print("庄家要牌...")
                time.sleep(1)
                self.banker_cards.append(self.draw_card())
                self.display_cards(self.banker_cards, "庄家")
        else:
            if banker_score <= 5:
                print("庄家要牌...")
                time.sleep(1)
                self.banker_cards.append(self.draw_card())
                self.display_cards(self.banker_cards, "庄家")
    
    def determine_winner(self):
        player_score = self.calculate_score(self.player_cards)
        banker_score = self.calculate_score(self.banker_cards)
        
        print("\n=== 最终结果 ===")
        print(f"玩家点数: {player_score}")
        print(f"庄家点数: {banker_score}")
        
        if player_score > banker_score:
            return 'player'
        elif banker_score > player_score:
            return 'banker'
        else:
            return 'tie'
    
    def play_round(self):
        print("\n" + "=" * 50)
        print("🎲 百家乐游戏")
        print("=" * 50)
        
        self.bet_type = self.select_bet_type()
        self.current_bet = self.select_bet_amount()
        
        if self.current_bet > self.balance:
            print("余额不足，无法下注")
            return
        
        self.balance -= self.current_bet
        print(f"\n下注成功！当前余额: ¥{self.balance}")
        
        self.deal()
        result = self.determine_winner()
        
        if result == self.bet_type:
            if result == 'tie':
                winnings = self.current_bet * 8
                self.balance += winnings
                print(f"\n🎉 和局！赢得 ¥{winnings}！")
                print(f"当前余额: ¥{self.balance}")
            elif result == 'banker':
                winnings = int(self.current_bet * 0.95)
                self.balance += self.current_bet + winnings
                print(f"\n🎉 庄家获胜！赢得 ¥{winnings}！")
                print(f"当前余额: ¥{self.balance}")
            else:
                winnings = self.current_bet
                self.balance += self.current_bet + winnings
                print(f"\n🎉 玩家获胜！赢得 ¥{winnings}！")
                print(f"当前余额: ¥{self.balance}")
        elif result == 'tie':
            self.balance += self.current_bet
            print(f"\n🤝 和局！下注返还 ¥{self.current_bet}")
            print(f"当前余额: ¥{self.balance}")
        else:
            print(f"\n😔 下注失败，损失 ¥{self.current_bet}")
            print(f"当前余额: ¥{self.balance}")
    
    def start_game(self):
        print("欢迎来到百家乐游戏！")
        print(f"初始余额: ¥{self.balance}")
        print()
        print("游戏规则:")
        print("• 玩家和庄家各发两张牌，点数高的一方获胜")
        print("• J、Q、K算0点，A算1点，2-9按实际点数计算")
        print("• 总点数取个位数，例如：14点算4点")
        print("• 下注玩家获胜赔率1:1，庄家获胜赔率0.95:1，和局赔率8:1")
        print()
        
        while self.balance > 0:
            self.play_round()
            
            if self.balance <= 0:
                print("\n💸 你已经破产了！游戏结束！")
                break
            
            play_again = input("\n是否继续游戏？ (y/n): ")
            if play_again.lower() != 'y':
                print(f"\n游戏结束！最终余额: ¥{self.balance}")
                break

if __name__ == "__main__":
    game = BaccaratGame()
    game.start_game()