# doudizhu
斗地主命令行游戏（GitHub 项目管理模拟）

## 发牌器（Dealer）

`dealer.py` 提供 `Card`、`Deck`、`Dealer`：生成 54 张牌、洗牌并给三位玩家发牌，支持随机种子以复现发牌结果。

在项目目录中可以直接运行：

```
python dealer.py
```

使用固定种子复现相同的发牌结果：

```
python dealer.py --seed 42
```

命令行输出使用 ASCII 花色缩写：`S` 黑桃、`H` 红桃、`C` 梅花、`D` 方块，`SJ`/`BJ` 分别表示小王/大王。

```python
from dealer import Dealer

result = Dealer(seed=42).deal()
for i, hand in enumerate(result.hands):
    print(f"玩家{i}: ", " ".join(str(card) for card in hand))
print("底牌: ", " ".join(str(card) for card in result.bottom))
```

运行测试：

```
python -m unittest
```

