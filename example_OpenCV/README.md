# Contents
- [🤖座標推定](#🤖座標推定)


---
# 🤖座標推定 

![](001.png)
--
![](002.png)
--
![](003.png)
--
![](004.png)
--
![](005.png)
--
![](006.png)
--
![](007.png)
--
![](008.png)
--
![](009.png)
--
![](010.png)
--
![](011.png)

[./estimate_position.py#L1](./estimate_position.py#L1)

---
OpenCVでは，HSV（Hue, Saturation, Value）色空間を使用して画像の色を定義できる．
Hue(色相)は色を表し，Saturation(彩度)は色の鮮やかさを表し，Value(明度)は色の明るさを表す．
値の範囲は，Hueは0〜179，SaturationとValueは0〜255である．

H（色相）：0から179
S（彩度）：0から255
V（明度）：0から255

| 色 | Hueの範囲 |
|---|---|
| 赤 | 0〜10, 170〜180 |
| 緑 | 40〜80 |
| 青 | 100〜140 |

[./trash/mask.py#L2](./trash/mask.py#L2)

---
