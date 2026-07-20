# 一、七国 AI 音乐 Geo A/B Test 计划

## 1. 研究目标

通过 Geo A/B Test，在七个国家中测试 AI 生成音乐的收益表现。

核心目标是：

**找到 AI 生成音乐收益表现最好的国家，并把后续音乐投放资源集中到该市场。**

这个实验的重点不是研究文化接受度，而是围绕 **Revenue Optimization**，判断哪个国家最值得继续投放。

## 2. 测试国家

| Group | Region | Countries |
| --- | --- | --- |
| Group A | Nordic Europe | Finland, Norway |
| Group B | Central Europe | Czechia, Hungary |
| Group C | Southern Europe | Greece |
| Group D | Southeast Asia | Thailand, Vietnam |

## 3. 样本量设计

实验单位：

- AI-generated songs

每个国家：

- 50 首 AI-generated songs

总样本：

- 7 个国家 × 50 首 = **350 首 AI 音乐作品**

每个国家 50 首，是为了避免单首爆款过度影响判断。

## 4. 控制变量

为了保证国家之间可以公平比较，需要尽量保持一致：

- 每个国家 50 首歌曲
- 相同观察周期
- 相同发行方式
- 相似曝光条件
- 相同数据来源

建议观察周期：

- 发布后 30 天收益表现

## 5. 数据来源

数据来源：

- Kandtric feedback data

主要使用：

- streams
- revenue
- country / territory breakdown
- store / platform breakdown

## 6. 核心指标

### Primary Metric

**Average Revenue per Song**

计算方式：

Average Revenue per Song = Total Revenue / Number of Songs

这个指标回答：

平均每首 AI 音乐在该国家能产生多少收益？

这是选择最终投放国家最重要的指标。

### Secondary Metrics

| Metric | Meaning |
| --- | --- |
| Total Revenue | 判断市场整体盈利规模 |
| Average Streams per Song | 判断用户播放表现 |
| Revenue per Stream | 判断播放转化为收入的效率 |

Revenue per Stream = Total Revenue / Total Streams

## 7. 记录表

| Group | Country | Songs | Total Streams | Total Revenue | Average Revenue / Song | Average Streams / Song | Revenue / Stream | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Group A | Finland | 50 |  |  |  |  |  |  |
| Group A | Norway | 50 |  |  |  |  |  |  |
| Group B | Czechia | 50 |  |  |  |  |  |  |
| Group B | Hungary | 50 |  |  |  |  |  |  |
| Group C | Greece | 50 |  |  |  |  |  |  |
| Group D | Thailand | 50 |  |  |  |  |  |  |
| Group D | Vietnam | 50 |  |  |  |  |  |  |

## 8. 区域对比

除了国家层面对比，也要做区域对比。

第一层：欧洲区域内对比

- Nordic Europe: Finland vs Norway
- Central Europe: Czechia vs Hungary
- Southern Europe: Greece 作为单独区域样本

第二层：东南亚区域内对比

- Southeast Asia: Thailand vs Vietnam
- 判断东南亚内部哪个国家收益表现更好

第三层：欧洲区域间对比

- Nordic Europe vs Central Europe vs Southern Europe
- 判断欧洲内部哪个区域的收益表现更好

第四层：欧洲 vs Southeast Asia

- 欧洲整体和 Southeast Asia 做方向性对比
- 判断后续资源更适合继续集中在欧洲，还是扩展东南亚

| Group | Region | Countries | Total Revenue | Average Revenue / Song | Revenue / Stream | Region Signal |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Group A | Nordic Europe | Finland, Norway |  |  |  |  |
| Group B | Central Europe | Czechia, Hungary |  |  |  |  |
| Group C | Southern Europe | Greece |  |  |  |  |
| Group D | Southeast Asia | Thailand, Vietnam |  |  |  |  |

注意：Southern Europe 目前只有 Greece，所以它可以参与欧洲区域对比，但结论需要更谨慎。

## 9. 决策逻辑

优先继续投放的国家：

- Average Revenue per Song 最高
- Revenue per Stream 高
- Total Revenue 有规模
- Average Streams per Song 不低

需要谨慎判断的情况：

- Total Revenue 高，但 Average Revenue per Song 不高
- Streams 高，但 Revenue per Stream 低
- 只有少数歌曲贡献大部分收益

降低优先级的国家：

- Average Revenue per Song 低
- Total Revenue 低
- Revenue per Stream 低
- 播放量和收益都弱

# 二、假设结论

不考虑 AI Interest Index，只根据现有 matrix 数据，测试前假设如下：

## 1. 国家假设排序

核心判断逻辑：

- 本地语言供给越少，代表内容缺口越明显，AI 音乐进入机会越大。
- Music Revenue 用来观察市场是否有足够变现基础。
- 所以优先看 **低供给 + 有收入基础** 的国家。

| Tier | Country | Music Revenue | Annual Country-Artist Songs | Local-Language Songs | Local-Language Supply Share | Supply Opportunity | Hypothesis |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Strong | Finland | ~$66.0M | 24.4K | 1.2K | ~4.9% | High | 本地语言供给最低之一，同时有稳定音乐收入，AI 本地化内容机会较大 |
| Strong | Greece | ~$112.48M | 22,063 | 1,285 | ~5.8% | High | 本地语言供给低，但音乐收入最高，供给缺口 + 需求基础都强 |
| Strong | Czechia | ~$99.3M | about 21.8K | about 1.6K | ~7.3% | Medium-High | Czech-language 供给不高，且收入接近 $100M，商业化测试价值高 |
| Medium | Norway | ~$93.0M | 31.2K | 1.8K | ~5.8% | Medium-High | 本地语言供给比例低，但整体 artist/song supply 较大，竞争可能更强 |
| Medium | Hungary | ~$39.0M | 16,729 | 1,780 | ~10.6% | Medium | 供给不算高，但 music revenue 最低，收益上限需要验证 |
| Observe | Thailand | ~$100.9M | 25,736 | 2,945 | ~11.4% | Medium-Low | 收入和人口不错，但 Thai-language supply 更高，内容缺口没有欧洲小语种明显 |
| Observe | Vietnam | ~$66.07M | 28,046 | 4,343 | ~15.5% | Low | 本地语言供给最高，且平台结构复杂，AI 新内容缺口相对较小 |

## 2. 区域假设

| Comparison | Data Signal | Hypothesis |
| --- | --- | --- |
| Nordic Europe: Finland vs Norway | Finland local-language supply ~1.2K, Norway ~1.8K; Norway revenue higher | Finland 供给缺口更明显，Norway 变现基础更强，二者都值得重点测试 |
| Central Europe: Czechia vs Hungary | Czechia revenue ~$99.3M > Hungary ~$39.0M; Czechia supply share ~7.3%, Hungary ~10.6% | Czechia 的供给机会和变现基础都强于 Hungary |
| Southeast Asia: Thailand vs Vietnam | Thailand local-language songs 2,945; Vietnam 4,343; both高于多数欧洲国家 | 东南亚本地语言供给更高，内容缺口不如欧洲明显 |
| Europe region comparison | Finland / Greece / Czechia / Norway 的 local-language supply share 大多低于 8% | 欧洲小语种市场更符合“低供给 + 可变现”的假设 |
| Europe vs Southeast Asia | Southeast Asia 人口更大，但 local-language supply 更高且平台更复杂 | 第一轮假设欧洲更可能跑出更好的 Average Revenue per Song |
