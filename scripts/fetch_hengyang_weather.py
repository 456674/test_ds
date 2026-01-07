"""
Fetch the last five days of weather data for Hengyang, China and produce a
simple analysis.

The script downloads daily weather metrics from the Open-Meteo API using the
coordinates for Hengyang (26.8930° N, 112.5720° E). It writes the raw daily
values to ``data/hengyang_weather_last5days.csv`` and a brief analysis summary
to ``analysis/hengyang_weather_summary.md``.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import pathlib
from typing import Dict, List
from urllib import parse, request


BASE_URL = "https://api.open-meteo.com/v1/forecast"
LATITUDE = 26.893  # Hengyang, China
LONGITUDE = 112.572
TIMEZONE = "Asia/Shanghai"

DATA_PATH = pathlib.Path("data") / "hengyang_weather_last5days.csv"
SUMMARY_PATH = pathlib.Path("analysis") / "hengyang_weather_summary.md"


def daterange(days: int = 5) -> tuple[str, str]:
    """Return start and end dates (YYYY-MM-DD) covering the last ``days``."""
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=days - 1)
    return start_date.isoformat(), end_date.isoformat()


def fetch_weather(start_date: str, end_date: str) -> List[Dict[str, float]]:
    """Fetch daily weather data from the Open-Meteo API."""
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "timezone": TIMEZONE,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "precipitation_sum",
                "precipitation_hours",
                "windspeed_10m_max",
            ]
        ),
    }

    encoded_params = parse.urlencode(params)
    url = f"{BASE_URL}?{encoded_params}"
    req = request.Request(
        url,
        headers={
            "User-Agent": "weather-fetcher/1.0 (+https://openai.com/)",
            "Accept": "application/json",
        },
    )
    opener = request.build_opener(request.ProxyHandler({}))

    with opener.open(req, timeout=30) as resp:
        payload = resp.read().decode("utf-8")

    payload = json.loads(payload)
    daily = payload["daily"]

    records = []
    for idx, date_str in enumerate(daily["time"]):
        records.append(
            {
                "date": date_str,
                "temp_max_c": daily["temperature_2m_max"][idx],
                "temp_min_c": daily["temperature_2m_min"][idx],
                "apparent_temp_max_c": daily["apparent_temperature_max"][idx],
                "apparent_temp_min_c": daily["apparent_temperature_min"][idx],
                "precipitation_mm": daily["precipitation_sum"][idx],
                "precip_hours": daily["precipitation_hours"][idx],
                "wind_speed_max_m_s": daily["windspeed_10m_max"][idx],
            }
        )
    return records


def fallback_weather(start_date: str, end_date: str) -> List[Dict[str, float]]:
    """Return a deterministic fallback dataset when the API is unreachable."""
    base_date = dt.date.fromisoformat(start_date)
    end = dt.date.fromisoformat(end_date)
    template = [
        {
            "temp_max_c": 13.5,
            "temp_min_c": 6.2,
            "apparent_temp_max_c": 12.8,
            "apparent_temp_min_c": 5.0,
            "precipitation_mm": 2.6,
            "precip_hours": 3.0,
            "wind_speed_max_m_s": 6.2,
        },
        {
            "temp_max_c": 14.1,
            "temp_min_c": 7.0,
            "apparent_temp_max_c": 13.2,
            "apparent_temp_min_c": 5.8,
            "precipitation_mm": 0.0,
            "precip_hours": 0.0,
            "wind_speed_max_m_s": 5.1,
        },
        {
            "temp_max_c": 12.3,
            "temp_min_c": 6.5,
            "apparent_temp_max_c": 11.5,
            "apparent_temp_min_c": 5.0,
            "precipitation_mm": 4.8,
            "precip_hours": 6.0,
            "wind_speed_max_m_s": 7.4,
        },
        {
            "temp_max_c": 11.8,
            "temp_min_c": 5.9,
            "apparent_temp_max_c": 10.9,
            "apparent_temp_min_c": 4.2,
            "precipitation_mm": 9.2,
            "precip_hours": 8.0,
            "wind_speed_max_m_s": 8.3,
        },
        {
            "temp_max_c": 10.6,
            "temp_min_c": 4.8,
            "apparent_temp_max_c": 9.0,
            "apparent_temp_min_c": 3.2,
            "precipitation_mm": 1.5,
            "precip_hours": 2.0,
            "wind_speed_max_m_s": 6.8,
        },
    ]

    records: List[Dict[str, float]] = []
    for offset, values in enumerate(template):
        current_date = base_date + dt.timedelta(days=offset)
        if current_date > end:
            break
        record = {"date": current_date.isoformat()}
        record.update(values)
        records.append(record)

    return records


def write_csv(records: List[Dict[str, float]], path: pathlib.Path) -> None:
    """Write records to CSV at ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def analyze(records: List[Dict[str, float]], source: str) -> str:
    """Generate a markdown summary from daily records."""
    temp_max_values = [item["temp_max_c"] for item in records]
    temp_min_values = [item["temp_min_c"] for item in records]
    precip_values = [item["precipitation_mm"] for item in records]

    warmest = max(records, key=lambda r: r["temp_max_c"])
    coolest = min(records, key=lambda r: r["temp_min_c"])
    wettest = max(records, key=lambda r: r["precipitation_mm"])
    windiest = max(records, key=lambda r: r["wind_speed_max_m_s"])

    lines = [
        "# 衡阳近五天天气概览",
        "",
        f"时间范围：{records[0]['date']} 至 {records[-1]['date']}（共 {len(records)} 天）",
        f"数据来源：{source}",
        "",
        "## 统计摘要",
        f"- 平均最高气温：{sum(temp_max_values) / len(temp_max_values):.1f}°C",
        f"- 平均最低气温：{sum(temp_min_values) / len(temp_min_values):.1f}°C",
        f"- 最高气温出现在：{warmest['date']}（{warmest['temp_max_c']:.1f}°C）",
        f"- 最低气温出现在：{coolest['date']}（{coolest['temp_min_c']:.1f}°C）",
        f"- 总降水量：{sum(precip_values):.1f} mm",
        f"- 最大降水日：{wettest['date']}（{wettest['precipitation_mm']:.1f} mm，"
        f"{wettest['precip_hours']} 小时）",
        f"- 最大阵风日：{windiest['date']}（{windiest['wind_speed_max_m_s']:.1f} m/s）",
        "",
        "## 日度详情",
        "| 日期 | 最高气温 (°C) | 最低气温 (°C) | 体感最高 (°C) | 体感最低 (°C) | 降水量 (mm) | 降水时长 (h) | 最大风速 (m/s) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for record in records:
        lines.append(
            "| {date} | {temp_max_c:.1f} | {temp_min_c:.1f} | "
            "{apparent_temp_max_c:.1f} | {apparent_temp_min_c:.1f} | "
            "{precipitation_mm:.1f} | {precip_hours:.1f} | "
            "{wind_speed_max_m_s:.1f} |".format(**record)
        )

    return "\n".join(lines)


def write_summary(summary: str, path: pathlib.Path) -> None:
    """Write analysis summary to markdown."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(summary, encoding="utf-8")


def main() -> None:
    start_date, end_date = daterange()
    source = "Open-Meteo API"

    try:
        records = fetch_weather(start_date, end_date)
    except Exception as exc:  # pragma: no cover - defensive path
        print(f"实时数据获取失败（{exc}），使用预置样例数据。")
        records = fallback_weather(start_date, end_date)
        source = "预置样例数据（请在有网络时重新运行以获取实时信息）"

    write_csv(records, DATA_PATH)
    summary = analyze(records, source)
    write_summary(summary, SUMMARY_PATH)
    print(f"Wrote {len(records)} records to {DATA_PATH}")
    print(f"Summary saved to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
