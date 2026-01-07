# 衡阳近五天天气数据分析

该仓库包含一个用于抓取并分析中国衡阳最近五天天气数据的脚本，以及生成的数据与分析结果。

## 使用方法

1. 运行抓取与分析脚本（默认会覆盖已有文件）：

   ```bash
   python scripts/fetch_hengyang_weather.py
   ```

2. 生成的文件：
   - `data/hengyang_weather_last5days.csv`：每日天气指标数据。
   - `analysis/hengyang_weather_summary.md`：统计摘要与每日详情表格。

> 注：当前环境无法直接访问外网，脚本会自动使用预置的样例数据并在有网络时自动恢复使用实时数据。若需要最新数据，请在具备网络访问时重新运行脚本。
