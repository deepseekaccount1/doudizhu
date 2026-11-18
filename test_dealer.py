"""Issue #1 发牌器的单元测试。"""
from contextlib import redirect_stdout
from io import StringIO
import random
import unittest

from dealer import (
    RANK_BIG_JOKER,
    RANK_SMALL_JOKER,
    RANK_TWO,
    Card,
    Dealer,
    build_deck,
    main,
)


class BuildDeckTests(unittest.TestCase):
    def test_deck_has_54_unique_cards(self):
        deck = build_deck()
        self.assertEqual(len(deck), 54)
        self.assertEqual(len(set(deck)), 54)


class DealerDealTests(unittest.TestCase):
    def test_command_line_entry_point_prints_three_hands_and_bottom_cards(self):
        output = StringIO()
        with redirect_stdout(output):
            main(["--seed", "42"])

        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 4)
        self.assertIn("Player 1 (17 cards):", lines[0])
        self.assertIn("Player 2 (17 cards):", lines[1])
        self.assertIn("Player 3 (17 cards):", lines[2])
        self.assertIn("Bottom (3 cards):", lines[3])

    def test_command_line_seed_is_reproducible(self):
        outputs = []
        for _ in range(2):
            output = StringIO()
            with redirect_stdout(output):
                main(["--seed", "42"])
            outputs.append(output.getvalue())

        self.assertEqual(outputs[0], outputs[1])

    def test_deal_covers_all_54_cards_without_duplicates_or_omissions(self):
        for seed in range(50):
            with self.subTest(seed=seed):
                result = Dealer(seed=seed).deal()
                self.assertEqual(len(result.hands), 3)
                for hand in result.hands:
                    self.assertEqual(len(hand), 17)
                self.assertEqual(len(result.bottom), 3)

                dealt = [card for hand in result.hands for card in hand] + result.bottom
                self.assertEqual(len(dealt), 54)
                self.assertEqual(set(dealt), set(build_deck()))

    def test_many_seeds_round_trip(self):
        # 验收标准要求的循环发牌压力测试：多个种子反复发牌，校验张数和不重复。
        full_deck = set(build_deck())
        for seed in range(1000):
            result = Dealer(seed=seed).deal()
            dealt = [card for hand in result.hands for card in hand] + result.bottom
            self.assertEqual(len(dealt), 54)
            self.assertEqual(set(dealt), full_deck)

    def test_same_seed_is_reproducible(self):
        first = Dealer(seed=42).deal()
        second = Dealer(seed=42).deal()
        self.assertEqual(first.hands, second.hands)
        self.assertEqual(first.bottom, second.bottom)

    def test_different_seeds_usually_differ(self):
        results = [Dealer(seed=seed).deal().hands for seed in range(10)]
        # 抽样验证：10 个不同种子里至少要出现不同的发牌结果。
        self.assertTrue(any(results[0] != other for other in results[1:]))

    def test_no_seed_is_random_each_time(self):
        first = Dealer().deal()
        second = Dealer().deal()
        # 不传种子时极大概率得到不同结果；两次完全相同的概率可忽略不计。
        self.assertNotEqual(first.hands, second.hands)

    def test_hands_are_sorted_ascending_by_rank(self):
        result = Dealer(seed=7).deal()
        for hand in result.hands:
            ranks = [card.rank for card in hand]
            self.assertEqual(ranks, sorted(ranks))
        self.assertEqual(
            [card.rank for card in result.bottom],
            sorted(card.rank for card in result.bottom),
        )

    def test_rank_order_matches_spec(self):
        # 3 < ... < K < A < 2 < 小王 < 大王
        self.assertLess(Card(rank=13).rank, Card(rank=14).rank)  # K < A
        self.assertLess(Card(rank=14).rank, Card(rank=RANK_TWO).rank)  # A < 2
        self.assertLess(Card(rank=RANK_TWO).rank, Card(rank=RANK_SMALL_JOKER).rank)
        self.assertLess(Card(rank=RANK_SMALL_JOKER).rank, Card(rank=RANK_BIG_JOKER).rank)

    def test_dealer_uses_independent_rng_not_global_state(self):
        random.seed(12345)
        state_before = random.getstate()
        Dealer(seed=1).deal()
        state_after = random.getstate()
        # 发牌器不应该读取/改变全局随机状态。
        self.assertEqual(state_before, state_after)


if __name__ == "__main__":
    unittest.main()
