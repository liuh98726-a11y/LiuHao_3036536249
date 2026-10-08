"""市场因子的阶段性检查：相关系数、误差指标和月度差异图。

运行：在项目根目录执行 python code/Others/check_market_factor.py。
输入：第三步比较表，以及前两步的市场收益和官方因子表。
输出：outputs/tables 下的指标与偏差最大月份，outputs/figures 下的中文图，
      以及 outputs/mkt_rf_validation.md 中文检查说明。
这里不构造 SMB/HML，也不制作三个因子的最终描述性统计和累计收益图。
计算仅需 Python 标准库；绘图需要 reportlab 和 pypdfium2。
"""

import csv
import math
from decimal import Decimal
from pathlib import Path
from statistics import correlation, mean

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = PROJECT_ROOT / "data/processed"
OUTPUTS = PROJECT_ROOT / "outputs"


def read_monthly(path: Path) -> list[dict]:
    """核查月份范围和唯一性；返回按月份排序的数据，禁止缺月后继续计算。"""
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    months = [row["month"] for row in rows]
    expected = [f"{year}{month:02d}" for year in range(2000, 2026) for month in range(1, 13)]
    if sorted(months) != expected:
        raise ValueError(f"{path.name} 必须恰好包含 312 个连续且唯一的月份。")
    return sorted(rows, key=lambda row: row["month"])


def checked_number(value: str) -> Decimal:
    """使用十进制精确数核查减法，并阻止缺失及非有限数值进入统计。"""
    number = Decimal(value)
    if not number.is_finite():
        raise ValueError(f"存在无效数值：{value}")
    return number


def make_difference_plot(rows: list[dict], errors: list[float], path: Path) -> None:
    """标准折线图展示自建值减官方值；纵轴用百分点，横轴按日历月份。"""
    from reportlab.graphics import renderPDF
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.shapes import Circle, Drawing, Line, String
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import pypdfium2 as pdfium

    # 嵌入 Windows 微软雅黑，保证中文图标题与标注可正确渲染。
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    if not font_path.exists():
        raise FileNotFoundError("绘图需要中文字体，请将 font_path 改为可用的中文字体路径。")
    pdfmetrics.registerFont(TTFont("Chinese", str(font_path), subfontIndex=0))
    drawing = Drawing(920, 455)
    ink = colors.HexColor("#183047")
    muted = colors.HexColor("#536574")
    blue = colors.HexColor("#256A9B")
    orange = colors.HexColor("#BE5729")
    drawing.add(String(65, 416, "市场因子：自建值与官方值的月度差异", fontName="Chinese", fontSize=20, fillColor=ink))
    drawing.add(String(65, 387, "2000年1月—2025年12月  |  312个月  |  差异 = 自建 MKT−RF − 官方 MKT−RF", fontName="Chinese", fontSize=11, fillColor=muted))
    drawing.add(String(65, 349, "差异（百分点）", fontName="Chinese", fontSize=10, fillColor=muted))

    # 0.01 的小数收益差对应 1 个百分点，因此纵轴绘图数值乘以 100。
    plot = LinePlot()
    plot.x, plot.y, plot.width, plot.height = 80, 102, 785, 228
    plot.data = [[(index, value * 100) for index, value in enumerate(errors)]]
    plot.lines[0].strokeColor = blue
    plot.lines[0].strokeWidth = 1.1
    plot.xValueAxis.valueMin, plot.xValueAxis.valueMax = 0, 311
    plot.xValueAxis.valueSteps = [0, 60, 120, 180, 240, 300]
    plot.xValueAxis.labelTextFormat = lambda value: str(2000 + int(value) // 12)
    plot.yValueAxis.valueMin, plot.yValueAxis.valueMax = -1.6, 1.8
    plot.yValueAxis.valueSteps = [-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5]
    plot.yValueAxis.labelTextFormat = "%.1f"
    for axis in [plot.xValueAxis, plot.yValueAxis]:
        axis.labels.fontName = "Chinese"
        axis.labels.fontSize = 10
        axis.labels.fillColor = muted
        axis.strokeColor = colors.HexColor("#CCD4DA")
    plot.yValueAxis.visibleGrid = True
    plot.yValueAxis.gridStrokeColor = colors.HexColor("#E7EDF1")
    drawing.add(plot)

    # 明确标出零线，便于判断自建市场因子偏高还是偏低。
    def y_position(value_pp: float) -> float:
        return plot.y + (value_pp + 1.6) / 3.4 * plot.height

    drawing.add(Line(plot.x, y_position(0), plot.x + plot.width, y_position(0), strokeColor=muted, strokeWidth=0.8))
    worst_index = max(range(len(errors)), key=lambda i: abs(errors[i]))
    x = plot.x + worst_index / 311 * plot.width
    y = y_position(errors[worst_index] * 100)
    drawing.add(Circle(x, y, 3, fillColor=orange, strokeColor=orange))
    month = rows[worst_index]["month"]
    drawing.add(String(x + 9, y + 5, f"最大绝对差异：{month[:4]}-{month[4:]}，{errors[worst_index] * 100:+.4f} 个百分点", fontName="Chinese", fontSize=10, fillColor=orange))
    drawing.add(String(80, 57, "正值：自建值高于官方值；负值：自建值低于官方值。1 个百分点 = 100 个基点。", fontName="Chinese", fontSize=10, fillColor=muted))
    drawing.add(String(80, 33, "来源：课程 CRSP 市场收益与 Kenneth French 官方因子；收益差不等同于相对误差百分比。", fontName="Chinese", fontSize=9, fillColor=muted))

    # 图先在内存中生成嵌入字体的页面，再栅格化为独立 PNG，不生成临时 PDF。
    document = pdfium.PdfDocument(renderPDF.drawToString(drawing))
    try:
        page = document[0]
        try:
            bitmap = page.render(scale=2)
            try:
                bitmap.to_pil().save(path)
            finally:
                bitmap.close()
        finally:
            page.close()
    finally:
        document.close()


def main() -> None:
    # 一、逐月复核第三步的输入值和公式，不仅检查相关系数。
    rows = read_monthly(PROCESSED / "mkt_rf_comparison_monthly_2000_2025.csv")
    market = {r["month"]: r for r in read_monthly(PROCESSED / "crsp_market_monthly_2000_2025.csv")}
    factors = {r["month"]: r for r in read_monthly(PROCESSED / "ff_factors_monthly_2000_2025.csv")}
    for row in rows:
        month = row["month"]
        values = {key: checked_number(value) for key, value in row.items() if key != "month"}
        checks = [
            values["vwretd"] == checked_number(market[month]["vwretd"]),
            values["RF"] == checked_number(factors[month]["RF"]),
            values["mkt_rf_official"] == checked_number(factors[month]["Mkt-RF"]),
            values["mkt_rf_constructed"] == values["vwretd"] - values["RF"],
            values["difference"] == values["mkt_rf_constructed"] - values["mkt_rf_official"],
        ]
        if not all(checks):
            raise ValueError(f"{month} 的输入对齐或减法有误，停止生成检查结果。")

    # 二、统计定义：误差均为“自建值减官方值”；MAE/RMSE 保留幅度信息。
    constructed = [float(r["mkt_rf_constructed"]) for r in rows]
    official = [float(r["mkt_rf_official"]) for r in rows]
    errors = [float(r["difference"]) for r in rows]
    corr = correlation(constructed, official)  # Pearson 相关系数，衡量共同波动。
    bias = mean(errors)  # 平均误差，有正负抵消。
    mae = mean(abs(e) for e in errors)  # 平均绝对误差，不允许正负抵消。
    rmse = math.sqrt(mean(e * e for e in errors))  # 均方根误差，对大偏差更敏感。
    ranked = sorted(rows, key=lambda r: abs(Decimal(r["difference"])), reverse=True)[:10]
    metrics = [
        ("n_months", "有效月份数", len(rows), "月"),
        ("pearson_correlation", "皮尔逊相关系数", corr, "无单位"),
        ("mean_error", "平均误差（自建减官方）", bias * 100, "百分点"),
        ("mae", "平均绝对误差", mae * 100, "百分点"),
        ("rmse", "均方根误差", rmse * 100, "百分点"),
        ("max_absolute_error", "最大绝对误差", max(abs(e) for e in errors) * 100, "百分点"),
    ]

    # 三、保存带中文说明的结果；原始数据与已处理输入均不覆盖。
    table_dir, figure_dir = OUTPUTS / "tables", OUTPUTS / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    with (table_dir / "mkt_rf_validation_metrics.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "中文说明", "value", "单位"])
        writer.writerows(metrics)
    with (table_dir / "mkt_rf_largest_differences.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["month", "自建收益_百分比", "官方收益_百分比", "差异_百分点", "绝对差异_百分点"])
        for row in ranked:
            e = Decimal(row["difference"]) * 100
            writer.writerow([row["month"], Decimal(row["mkt_rf_constructed"]) * 100, Decimal(row["mkt_rf_official"]) * 100, e, abs(e)])
    figure = figure_dir / "mkt_rf_monthly_difference.png"
    make_difference_plot(rows, errors, figure)

    metric_lines = "\n".join(f"| {label} | {value:.6f} | {unit} |" for _, label, value, unit in metrics)
    worst_lines = "\n".join(
        f"| {r['month'][:4]}-{r['month'][4:]} | {Decimal(r['mkt_rf_constructed']) * 100:.4f}% | {Decimal(r['mkt_rf_official']) * 100:.4f}% | {Decimal(r['difference']) * 100:+.4f} |"
        for r in ranked[:3]
    )
    note = f"""# 市场因子阶段性检查

样本为 2000 年 1 月至 2025 年 12 月，共 312 个月。本检查只针对 MKT−RF；SMB、HML 尚未自行构造。

## 检查结果

月份连续且唯一，所用收益无缺失。逐月复核了市场收益、RF、官方市场因子的来源对齐，以及两项减法，全部通过。

| 指标 | 数值 | 单位 |
|---|---:|---|
{metric_lines}

两条序列的共同波动很接近，但水平存在差异。平均误差为 {bias * 100:+.4f} 个百分点；平均绝对误差为 {mae * 100:.4f} 个百分点（{mae * 10000:.2f} 个基点）。不能仅凭高相关系数判断已精确复现官方市场因子。

## 偏差最大的月份

下表列出绝对差异最大的三个月，前十个月另见表格文件。

| 月份 | 自建 MKT−RF | 官方 MKT−RF | 差异（百分点） |
|---|---:|---:|---:|
{worst_lines}

![月度市场因子差异](figures/mkt_rf_monthly_difference.png)

## 已确认的事实与待核实的原因

- 自建值等于 `vwretd − RF`，差异等于自建值减官方值，逐月十进制精确运算均正确；输入已是小数，没有重复除以 100。
- 两条因子使用同一官方 RF，因此差异也等于 `vwretd − (官方 Mkt-RF + RF)`。减去 RF 这一步不是当前偏差的来源，差异存在于 CRSP 市场收益与官方因子隐含的市场收益之间。
- 官方因子来自课程文件标注的 202607 CRSP 数据库版本。当前尚未确认课程股票文件的提取版本与其完全一致。
- 市场股票覆盖范围、历史数据修订及收益构造口径是需要核实的候选原因，目前不能断言某一项就是原因。官方因子原始数值的显示精度也可能造成很小的舍入差异，不能解释百分点级的大偏差。
- 这份结果确认了当前数据下的日期对齐和运算正确，并不等于已经完成严格同口径的市场组合重建。

## 下一步

保留现有市场因子结果，在报告中说明其使用 CRSP 现成市场指数的口径。继续准备 SMB、HML，随后统一制作三个因子的正式描述性统计与累计收益图。如要求更严格贴合官方市场因子，应核实数据版本和市场股票筛选范围，再决定是否从个股重新构造市场组合。

官方口径参考：[三因子定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html)、[数据版本与 CIZ 说明](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)。

运行脚本：`python code/Others/check_market_factor.py`。Python 绘图依赖为 `reportlab`、`pypdfium2`；中文字体使用 Windows 微软雅黑。
"""
    (OUTPUTS / "mkt_rf_validation.md").write_text(note, encoding="utf-8")
    for _, label, value, unit in metrics:
        print(f"{label}：{value:.6f} {unit}")
    print(f"图已保存：{figure}")
    print(f"中文检查说明：{OUTPUTS / 'mkt_rf_validation.md'}")


if __name__ == "__main__":
    main()
