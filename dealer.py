"""发牌器：生成一副斗地主牌（54 张），洗牌并给三位玩家发牌。

实现 Issue #1 的需求：
- Card / Deck 的数据定义。
- 生成 54 张牌、洗牌、发牌（三人各 17 张，底牌 3 张）。
- 支持随机种子，便于测试时复现同一次发牌结果。
"""
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Optional

# 花色：黑桃、红桃、梅花、方块（王没有花色）。
SUITS = ("♠", "♥", "♣", "♦")

# 普通牌点 3~10, J, Q, K, A 对应整数 3~14；2 单独取 16，
# 以便满足大小顺序 3 < ... < K < A < 2 < 小王 < 大王。
NORMAL_RANKS = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16)
RANK_TWO = 16
RANK_SMALL_JOKER = 17
RANK_BIG_JOKER = 18

_RANK_NAMES = {
    3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "J", 12: "Q", 13: "K", 14: "A", RANK_TWO: "2",
    RANK_SMALL_JOKER: "小王", RANK_BIG_JOKER: "大王",
}


@dataclass(frozen=True)
class Card:
    """一张牌：牌点（rank）与花色（suit，王没有花色）。"""

    rank: int
    suit: Optional[str] = None

    def __str__(self) -> str:  # 便于调试和展示
        name = _RANK_NAMES.get(self.rank, str(self.rank))
        return name if self.suit is None else f"{self.suit}{name}"


@dataclass
class DealResult:
    """一次发牌的结果：三手牌（已排序）与三张底牌（已排序）。"""

    hands: List[List[Card]]
    bottom: List[Card]


def build_deck() -> List[Card]:
    """生成一副全新的 54 张牌（3 种普通花色牌 * 13 种牌点 + 大小王）。"""
    deck = [Card(rank=rank, suit=suit) for rank in NORMAL_RANKS for suit in SUITS]
    deck.append(Card(rank=RANK_SMALL_JOKER))
    deck.append(Card(rank=RANK_BIG_JOKER))
    return deck


def _sort_key(card: Card) -> int:
    return card.rank


class Deck:
    """一副牌，负责持有牌堆并提供洗牌能力。"""

    def __init__(self) -> None:
        self.cards: List[Card] = build_deck()

    def shuffle(self, rng: random.Random) -> None:
        rng.shuffle(self.cards)

    def __len__(self) -> int:
        return len(self.cards)


class Dealer:
    """发牌器：使用独立的随机实例洗牌、发牌，不依赖全局随机状态。"""

    PLAYER_COUNT = 3
    HAND_SIZE = 17
    BOTTOM_SIZE = 3

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def deal(self) -> DealResult:
        deck = Deck()
        deck.shuffle(self._rng)
        cards = deck.cards

        hands = [
            sorted(cards[i * self.HAND_SIZE:(i + 1) * self.HAND_SIZE], key=_sort_key)
            for i in range(self.PLAYER_COUNT)
        ]
        bottom_start = self.PLAYER_COUNT * self.HAND_SIZE
        bottom = sorted(cards[bottom_start:bottom_start + self.BOTTOM_SIZE], key=_sort_key)
        return DealResult(hands=hands, bottom=bottom)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="洗牌并为三位斗地主玩家发牌。")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="随机种子；传入后可复现相同的发牌结果。",
    )
    args = parser.parse_args(argv)

    result = Dealer(seed=args.seed).deal()

    def format_card(card: Card) -> str:
        suit_names = {"♠": "S", "♥": "H", "♣": "C", "♦": "D"}
        rank_name = {RANK_SMALL_JOKER: "SJ", RANK_BIG_JOKER: "BJ"}.get(
            card.rank, _RANK_NAMES.get(card.rank, str(card.rank))
        )
        return f"{suit_names[card.suit]}{rank_name}" if card.suit else rank_name

    for player_number, hand in enumerate(result.hands, start=1):
        cards = " ".join(format_card(card) for card in hand)
        print(f"Player {player_number} ({len(hand)} cards): {cards}")
    bottom = " ".join(format_card(card) for card in result.bottom)
    print(f"Bottom ({len(result.bottom)} cards): {bottom}")


if __name__ == "__main__":
    main()
