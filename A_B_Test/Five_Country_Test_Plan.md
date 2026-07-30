# 一、五国 AI 音乐 Geo A/B Test 计划

## 1. 研究目标

通过 Geo A/B Test，在五个欧洲国家中测试 AI 生成音乐的收益表现。

核心目标是：

**找到 AI 生成音乐收益表现最好的国家，并把后续音乐投放资源集中到该市场。**

这个实验的重点不是研究文化接受度，而是围绕 **Revenue Optimization**，判断哪个国家最值得继续投放。

## 2. 测试国家

| Group | Region | Countries |
| --- | --- | --- |
| Group A | Nordic Europe | Finland, Norway |
| Group B | Central Europe | Czechia, Hungary |
| Group C | Southern Europe | Greece |

## 3. 样本量设计

实验单位：

- AI-generated songs

每个国家：

- 20 首 AI-generated songs

总样本：

- 5 个国家 × 20 首 = **100 首 AI 音乐作品**

每个国家 20 首，是为了在控制成本的同时，避免只用少数歌曲造成判断偏差。

建议每个国家的歌曲类型分布：

| Type | Songs per Country |
| --- | ---: |
| Mainstream pop | 8 |
| Emotional ballad / sad pop | 5 |
| Dance pop / electronic pop | 5 |
| Hip-hop / rap pop | 2 |

## 4. 控制变量

为了保证国家之间可以公平比较，需要尽量保持一致：

- 每个国家 20 首歌曲
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
| Group A | Finland | 20 |  |  |  |  |  |  |
| Group A | Norway | 20 |  |  |  |  |  |  |
| Group B | Czechia | 20 |  |  |  |  |  |  |
| Group B | Hungary | 20 |  |  |  |  |  |  |
| Group C | Greece | 20 |  |  |  |  |  |  |

## 8. 区域对比

除了国家层面对比，也要做区域对比。

第一层：欧洲区域内对比

- Nordic Europe: Finland vs Norway
- Central Europe: Czechia vs Hungary
- Southern Europe: Greece 作为单独区域样本

第二层：欧洲区域间对比

- Nordic Europe vs Central Europe vs Southern Europe
- 判断欧洲内部哪个区域的收益表现更好

| Group | Region | Countries | Total Revenue | Average Revenue / Song | Revenue / Stream | Region Signal |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Group A | Nordic Europe | Finland, Norway |  |  |  |  |
| Group B | Central Europe | Czechia, Hungary |  |  |  |  |
| Group C | Southern Europe | Greece |  |  |  |  |

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

评分公式：每个指标按五国排序递进打分，第 1 名 = 10，第 2 名 = 8，第 3 名 = 6，第 4 名 = 4，第 5 名 = 2；并列名次取对应分数的平均值。Music Revenue 15% + YouTube Avg Views 20% + Local-Language Supply Share 20% + Annual Country-Artist Songs 15%（反向，越少分越高）+ YouTube Like Rate 15% + YouTube Comment Rate 15%。Local-Language Songs 只保留展示，不参与得分。

| Rank | Country | Music Revenue | Annual Country-Artist Songs | Local-Language Songs | Local-Language Supply Share | YouTube Avg Views | YouTube Like Rate | YouTube Comment Rate | Final Score |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Greece | ~$112.48M | 22,063 | 1,285 | ~5.8% | 66,452,786 | 0.748% | 0.017% | 6.90 |
| 2 | Czechia | ~$99.3M | about 21.8K | about 1.6K | ~7.3% | 2,800,417 | 0.557% | 0.019% | 6.70 |
| 3 | Hungary | ~$39.0M | 16,729 | 1,780 | ~10.6% | 8,491,013 | 0.509% | 0.025% | 6.60 |
| 4 | Finland | ~$66.0M | 24.4K | 1.2K | ~4.9% | 1,019,808 | 0.937% | 0.075% | 5.00 |
| 5 | Norway | ~$93.0M | 31.2K | 1.8K | ~5.8% | 1,117,519 | 0.541% | 0.035% | 4.80 |

## 2. 区域假设

按同地区国家 Final Score 平均值排序：

| Rank | Region | Countries | Average Final Score |
| --- | --- | --- | ---: |
| 1 | Southern Europe | Greece | 6.90 |
| 2 | Central Europe | Czechia, Hungary | 6.65 |
| 3 | Nordic Europe | Finland, Norway | 4.90 |
