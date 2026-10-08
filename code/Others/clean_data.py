'''
把市场收益 vwretd 和无风险收益率 RF 整理到同一张月度表中，再计算 MKT−RF。
建议分三步做：
1. 先整理 RF 和官方因子文件
   提取 2000—2025 年的月度数据，将收益率除以 100，检查是否正好有 312 个月。
2. 再整理 vwretd
   从股票文件读取日期和 vwretd，确认同月数值一致后，每月保留一条。
   按行读取大文件，仅保留 MthCalDt 和 vwretd 两个字段。
   日期统一为 YYYYMM，检查 2000—2025 年的 312 个月连续、唯一、无缺失。
   同月数值不一致时停止；不取平均值，不直接取第一条掩盖差异。
   vwretd 已是小数单位，不再除以 100。
3. 合并并计算
   按月份匹配，计算 vwretd − RF，与官方 Mkt-RF 对比。
   检查两张表的月份唯一且都覆盖 312 个月；不能按行号直接拼接。
   所有收益已经是小数，合并后不再除以 100。
   差异 = 自建 MKT−RF − 官方 Mkt-RF，保留正负号。
把市场收益 vwretd 和无风险收益率 RF 整理到同一张月度表中，再计算 MKT−RF。
建议分三步做：
1. 先整理 RF 和官方因子文件
   提取 2000—2025 年的月度数据，将收益率除以 100，检查是否正好有 312 个月。
2. 再整理 vwretd
   从股票文件读取日期和 vwretd，确认同月数值一致后，每月保留一条。
   只读取日期 MthCalDt 和市场收益 vwretd。
   将日期转换为 YYYYMM，与刚整理好的 RF 数据保持一致。
   检查同一个月重复出现的 vwretd 是否一致，一致后每月保留一条。
   保留 2000—2025 年，检查是否有 312 个连续月份、无重复、无缺失。
    将结果保存到 data/processed。
    - vwretd 已是小数单位，不需要除以 100。
- 如果同一个月的 vwretd 不一致，应停止并检查原因，不能直接取第一条或平均值。
结果表保留两列：month（YYYYMM）和 vwretd，方便下一步与 RF 合并。

3. 合并并计算
   按月份匹配，计算 vwretd − RF，与官方 Mkt-RF 对比。
计算自建 MKT−RF，并与官方值比较。
1. 读取整理好的官方因子表和市场收益表。
2. 按 month 一对一合并，确认仍有 312 个月，无重复、无缺失。
3. 计算：\[
   \text{自建 MKT−RF} = vwretd - RF
   \]
   两列现在都是小数，不需要再除以 100。
4. 计算差异：自建 MKT−RF − 官方 Mkt-RF。
5. 保存结果：
month	vwretd	RF	自建 MKT−RF	官方 MKT−RF	差异


当前进度：本脚本已实现三步，得到以 CRSP 市场收益构造的 MKT−RF。
SMB、HML 目前仅为官方基准列，尚未从个股与财务数据自行构造。

输出文件的列名与含义：
    month  ：月份，格式 YYYYMM，例如 200001 表示 2000 年 1 月。
    Mkt-RF ：官方市场超额收益率，即市场收益率减去无风险收益率。
    SMB    ：官方规模因子，小盘股组合收益减去大盘股组合收益。
    HML    ：官方价值因子，高账面市值比组合收益减去低账面市值比组合收益。
    RF     ：月度无风险收益率，后续用它计算自建市场超额收益。
    四列收益均为小数：0.01 表示 1%，负数表示负收益；month 不进行单位转换。

第二步单独输出 crsp_market_monthly_2000_2025.csv，只有两列：
    month  ：月份，格式 YYYYMM，与第一步的月份格式相同。
    vwretd ：包含分配的 CRSP 市值加权市场收益，已是小数，尚未减 RF。

第三步输出 mkt_rf_comparison_monthly_2000_2025.csv，包含六列：
    month              ：月份，格式 YYYYMM。
    vwretd             ：CRSP 市场收益率。
    RF                 ：月度无风险收益率，来自整理后的官方表。
    mkt_rf_constructed ：自建市场超额收益，等于 vwretd - RF。
    mkt_rf_official    ：官方 Mkt-RF，作为对照值，不参与自建因子的计算。
    difference         ：自建值减官方值；正数表示自建值更高。
    五列数值均为小数；差异 0.001 表示 0.1 个百分点，即 10 个基点。
    CRSP 市场指数与官方市场组合可能存在覆盖口径差异，结果不一定完全相同。

运行方法：在项目根目录的终端中输入 python code/Others/clean_data.py。
运行成功会输出中文检查结果，并保存 data/processed 下的 CSV 文件。
保留英文列名是为了与原始数据对应，便于后续程序按月份合并。

第四步
第三步已完成，代码和中文注释已保存到 [clean_data.py](C:/Users/Leo/Desktop/Paper reproduction/LiuHao_3036536249/code/Others/clean_data.py)。
- 两张表按月份一对一合并，312 个月完整，无重复、无缺失。
- 已计算 自建 MKT−RF = vwretd − RF。
- 已计算 差异 = 自建值 − 官方值，逐月复核通过。
结果表包含月份、市场收益、RF、自建因子、官方因子和差异：
下一步可以计算描述性统计、相关系数和误差指标，并绘制对比图。
这里说的是：我们计算的 MKT−RF，与 Kenneth French 官方 MKT−RF 的对比图，只比较市场因子。
可以画三种图：
- 月度收益对比图：横轴是月份，两条线分别表示自建和官方 MKT−RF。
- 差异图：展示每个月“自建值 − 官方值”，看偏差出现在哪些月份。
- 累计收益对比图：比较两条因子序列按同一方法复合累计后的变化。
相关系数和误差指标也只针对这两条市场因子序列。
现在做，是为了先检查市场因子这一步是否正确；最终作业仍需要完成 SMB、HML，并分别与对应的官方因子比较。 也可以先构造另外两个因子，再统一做统计和画图。





'''

import csv  # Python 自带的 CSV 读写工具，无需安装额外软件包。
import re  # 正则表达式工具，用于识别六位数的月度日期。
from datetime import date  # 校验股票文件中的日期是否有效。
from decimal import Decimal, InvalidOperation  # 精确转换小数，并识别无效数字。
from pathlib import Path  # 处理文件路径。


# 一、设置输入路径、输出路径和需要处理的字段
# -----------------------------------------------------------------------------
# 根据脚本的位置寻找项目根目录，在不同工作目录运行时也能找到数据。
# parents[0] 是 Others，parents[1] 是 code，parents[2] 是项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# 原始文件只用于读取；其中既有月度数据，也有说明文字和年度汇总。
SOURCE_FILE = (
    PROJECT_ROOT
    / "data/raw/restricted/02_Monthly_Stocks_and_Factors"
    / "02_Monthly_Stocks_and_Factors/data/F-F factors and RF.csv"
)
# 清洗后的数据单独保存，保留原始数据以便复查。
OUTPUT_FILE = PROJECT_ROOT / "data/processed/ff_factors_monthly_2000_2025.csv"
# 顺序必须与官方 CSV 的列顺序一致，避免将不同因子的数值错配。
FACTOR_COLUMNS = ["Mkt-RF", "SMB", "HML", "RF"]
# 第二步的股票输入与市场收益输出，和第一步文件分别保存。
STOCK_FILE = SOURCE_FILE.with_name("monthly_stock.csv")
MARKET_OUTPUT_FILE = PROJECT_ROOT / "data/processed/crsp_market_monthly_2000_2025.csv"
# 第三步生成独立比较表，不覆盖前两步的输入。
COMPARISON_OUTPUT_FILE = (
    PROJECT_ROOT / "data/processed/mkt_rf_comparison_monthly_2000_2025.csv"
)


# 二、定义清洗函数：读取、筛选、转换单位、检查、保存
# -----------------------------------------------------------------------------
def clean_official_factors(
    source_file: Path = SOURCE_FILE,
    output_file: Path = OUTPUT_FILE,
) -> Path:
    """整理官方月度基准，全部检查通过后保存。

    参数：source_file 为原始 CSV 路径，output_file 为整理后 CSV 路径。
    返回：保存成功的输出文件路径。
    单位：四列收益从百分数转换为小数，RF 已是月度值，不再除以 12。
    异常：发现重复月份、缺月或无效收益值时停止，不用零填补问题数据。
    """
    # 生成完整的目标月份列表，26 年 × 12 个月 = 312 个月。
    # range 的结束值不包含在内；02d 将月份补成两位，例如 1 写成 01。
    expected_months = [
        f"{year}{month:02d}"
        for year in range(2000, 2026)
        for month in range(1, 13)
    ]
    monthly_values = {}  # 按“月份: 四列小数收益”的形式保存数据。
    header_found = False  # 确认读到了预期表头后，才允许接收月度数值。

    # 第一步：跳过说明文字、空行、年度数据和页脚，只读取月度数据。
    # utf-8-sig 兼容带字节顺序标记的 UTF-8 文件；newline 交由 CSV 工具处理。
    with source_file.open("r", encoding="utf-8-sig", newline="") as source:
        for line_number, row in enumerate(csv.reader(source), start=1):
            if not row:
                continue
            row = [cell.strip() for cell in row]  # 删除每个字段两侧的空格。
            if row == ["", *FACTOR_COLUMNS]:
                header_found = True
                continue

            month = row[0]
            # 月度日期为 200001 等六位数字；年度行只有 2000 等四位数字。
            if not re.fullmatch(r"\d{6}", month):
                continue
            if not "200001" <= month <= "202512":
                continue

            # 检查日期、列数和唯一性，防止错误数据被静默接受。
            if not header_found:
                raise ValueError("读取月度数据前未找到预期的官方因子表头。")
            if month not in expected_months:
                raise ValueError(f"第 {line_number} 行包含无效月份：{month}")
            if len(row) != 5:
                raise ValueError(f"第 {line_number} 行列数错误，预期日期及四列收益。")
            if month in monthly_values:
                raise ValueError(f"月份重复：{month}，请检查源数据。")

            # 第二步：检查数值，并将百分数除以 100。Decimal 避免浮点尾数。
            values = []
            # row[1:] 跳过日期，只处理 Mkt-RF、SMB、HML、RF 四列。
            for column, raw_value in zip(FACTOR_COLUMNS, row[1:]):
                try:
                    value = Decimal(raw_value)
                except InvalidOperation as exc:
                    raise ValueError(f"{month} 的 {column} 不是有效数字。") from exc
                # 排除非有限值及常用的源数据缺失代码；这些不是实际收益。
                if not value.is_finite() or value in (
                    Decimal("-99.99"), Decimal("-999")
                ):
                    raise ValueError(f"{month} 的 {column} 缺失或无效：{raw_value}")
                # 例如原始 RF=0.41 表示 0.41%，转换后为 0.0041。
                values.append(value / Decimal("100"))
            monthly_values[month] = values

    # 第三步：校验完整月份集合；只数行数不足以发现缺月或重复月。
    # 集合差找出“应该存在，但实际没有读到”的月份。
    missing_months = sorted(set(expected_months) - set(monthly_values))
    if missing_months:
        raise ValueError(f"目标样本缺少月份：{', '.join(missing_months)}")
    if len(monthly_values) != 312:
        raise ValueError(f"预期 312 个月，实际为 {len(monthly_values)} 个。")
    if source_file.resolve() == output_file.resolve():
        raise ValueError("输出路径不能与原始数据相同。")

    # 第四步：全部检查通过后保存，按月份排序；不修改原始 CSV。
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["month", *FACTOR_COLUMNS])  # 第一行写入五个字段名。
        for month in expected_months:
            writer.writerow([
                month,
                # 用普通小数形式保存，避免科学计数法；这里不再除以 100。
                *(format(value, "f") for value in monthly_values[month]),
            ])

    print("官方月度因子整理完成：2000-01 至 2025-12，共 312 个月。")
    print("检查通过：无重复月份、无缺失月份、四列收益均为有效数值。")
    print("收益单位：小数（0.01 表示 1%）；Mkt-RF、SMB、HML、RF 均已除以 100。")
    print(f"输出：{output_file}")
    return output_file


# 三、提取每月唯一的 CRSP 市场收益
# -----------------------------------------------------------------------------
def clean_market_returns(
    source_file: Path = STOCK_FILE,
    output_file: Path = MARKET_OUTPUT_FILE,
) -> Path:
    """核查全部目标期股票记录的市场收益，每月一致后保留一个值。

    原始股票文件较大，按行读取，不将整个文件载入内存。
    CSV 工具需要解析整行，但只提取日期和市场收益，其他字段不保留。
    对目标期内的缺失或无效收益、同月冲突及缺月均报错，检查通过才写文件。
    返回保存路径；不转换收益单位，也不在本步骤减去 RF。
    """
    expected_months = [
        f"{year}{month:02d}"
        for year in range(2000, 2026)
        for month in range(1, 13)
    ]
    monthly_values = {}  # 每个月已经核查到的市场收益。
    date_to_month = {}  # 缓存日期转换，避免重复解析同一个日期。
    target_rows = 0  # 实际参与核查的目标期股票记录数，不是股票数量。

    # 1. 读取表头，定位所需两列。原文件列顺序调整也不影响提取。
    with source_file.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        header = [cell.strip() for cell in next(reader, [])]
        for column in ("MthCalDt", "vwretd"):
            if header.count(column) != 1:
                raise ValueError(f"股票文件必须包含唯一的 {column} 列。")
        date_index = header.index("MthCalDt")
        return_index = header.index("vwretd")

        for line_number, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError(f"股票文件第 {line_number} 行列数与表头不一致。")

            # 2. 将有效日历日期转换成 YYYYMM，然后筛选目标年份。
            raw_date = row[date_index].strip()
            if raw_date not in date_to_month:
                try:
                    parsed_date = date.fromisoformat(raw_date)
                except ValueError as exc:
                    raise ValueError(
                        f"股票文件第 {line_number} 行日期缺失或无效：{raw_date}"
                    ) from exc
                date_to_month[raw_date] = parsed_date.strftime("%Y%m")
            month = date_to_month[raw_date]
            if not "200001" <= month <= "202512":
                continue

            # 3. 核查每条市场收益，不因同月已出现过就跳过后续记录。
            raw_value = row[return_index].strip()
            try:
                value = Decimal(raw_value)
            except InvalidOperation as exc:
                raise ValueError(
                    f"第 {line_number} 行、{month} 的 vwretd 缺失或不是有效数字。"
                ) from exc
            if not value.is_finite() or value in (
                Decimal("-99.99"), Decimal("-999")
            ):
                raise ValueError(f"第 {line_number} 行 vwretd 无效：{raw_value}")

            # 数值相等即可，例如 0.01 与 0.010 相同；发现冲突则停止保存。
            if month in monthly_values and monthly_values[month] != value:
                raise ValueError(
                    f"{month} 的 vwretd 不一致：此前为 {monthly_values[month]}，"
                    f"第 {line_number} 行为 {value}。请核查，不能直接取第一条。"
                )
            monthly_values[month] = value
            target_rows += 1

    # 4. 校验完整月份集合，防止“虽然有数据，但缺少某些月份”。
    missing_months = sorted(set(expected_months) - set(monthly_values))
    if missing_months:
        raise ValueError(f"市场收益缺少月份：{', '.join(missing_months)}")
    if len(monthly_values) != 312:
        raise ValueError(f"市场收益预期 312 个月，实际为 {len(monthly_values)} 个。")
    if source_file.resolve() == output_file.resolve():
        raise ValueError("输出路径不能与原始股票数据相同。")

    # 5. 一个月写一行，按时间排序，收益原值保留，不求和也不除以 100。
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["month", "vwretd"])
        for month in expected_months:
            writer.writerow([month, format(monthly_values[month], "f")])

    print(f"市场收益整理完成：核查 {target_rows:,} 条目标期原始记录。")
    print("检查通过：同月 vwretd 一致，2000-01 至 2025-12 共 312 个连续月份。")
    print("输出每月一行，无重复、无缺失；vwretd 保持小数单位，尚未减 RF。")
    print(f"输出：{output_file}")
    return output_file


# 四、按月份一对一合并，并计算市场超额收益和与官方值的差异
# -----------------------------------------------------------------------------
def calculate_market_factor(
    market_file: Path = MARKET_OUTPUT_FILE,
    factors_file: Path = OUTPUT_FILE,
    output_file: Path = COMPARISON_OUTPUT_FILE,
) -> Path:
    """使用前两步结果计算 MKT−RF，校验后保存六列月度比较表。

    输入必须覆盖目标期的全部 312 个月，月份唯一，所需收益列有效。
    按月份键匹配，不按行位置拼接，也不通过内连接静默丢弃缺失月份。
    这里只生成逐月结果；相关系数、误差汇总和图表在后续阶段完成。
    """
    expected_months = [
        f"{year}{month:02d}"
        for year in range(2000, 2026)
        for month in range(1, 13)
    ]

    def read_monthly_table(path: Path, value_columns: list[str]) -> dict:
        """按月份读取所需列；在合并前阻止重复键、缺月和无效数值。"""
        monthly_table = {}
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source)
            header = [cell.strip() for cell in next(reader, [])]
            for column in ["month", *value_columns]:
                if header.count(column) != 1:
                    raise ValueError(f"{path.name} 必须包含唯一的 {column} 列。")
            month_index = header.index("month")
            column_indexes = {column: header.index(column) for column in value_columns}

            for line_number, row in enumerate(reader, start=2):
                if not row:
                    continue
                if len(row) != len(header):
                    raise ValueError(f"{path.name} 第 {line_number} 行列数错误。")
                month = row[month_index].strip()
                if month not in expected_months:
                    raise ValueError(f"{path.name} 包含无效或目标期以外的月份：{month}")
                if month in monthly_table:
                    raise ValueError(f"{path.name} 的月份 {month} 重复，不能一对一合并。")

                values = {}
                for column, index in column_indexes.items():
                    try:
                        value = Decimal(row[index].strip())
                    except InvalidOperation as exc:
                        raise ValueError(
                            f"{path.name} 的 {month}、{column} 缺失或不是有效数字。"
                        ) from exc
                    if not value.is_finite():
                        raise ValueError(f"{path.name} 的 {month}、{column} 不是有限值。")
                    values[column] = value
                monthly_table[month] = values

        missing_months = sorted(set(expected_months) - set(monthly_table))
        if missing_months:
            raise ValueError(f"{path.name} 缺少月份：{', '.join(missing_months)}")
        if len(monthly_table) != 312:
            raise ValueError(f"{path.name} 必须恰好有 312 个月。")
        return monthly_table

    # 1. 读取并独立检查两张输入表，再确认它们的月份键完全相同。
    market = read_monthly_table(market_file, ["vwretd"])
    factors = read_monthly_table(factors_file, ["RF", "Mkt-RF"])
    if set(market) != set(factors):
        raise ValueError("市场收益表与官方因子表的月份不一致。")
    if output_file.resolve() in {market_file.resolve(), factors_file.resolve()}:
        raise ValueError("输出路径不能与任一输入表相同。")

    # 2. 按月匹配并计算。输入已统一为小数，禁止再次除以 100。
    result_rows = []
    for month in expected_months:
        vwretd = market[month]["vwretd"]
        rf = factors[month]["RF"]
        official = factors[month]["Mkt-RF"]
        constructed = vwretd - rf
        difference = constructed - official
        result_rows.append([
            month,
            *(format(value, "f") for value in (
                vwretd, rf, constructed, official, difference
            )),
        ])

    # 3. 全部检查通过后保存，按月份排序；每月只有一行。
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow([
            "month", "vwretd", "RF", "mkt_rf_constructed",
            "mkt_rf_official", "difference",
        ])
        writer.writerows(result_rows)

    print("第三步完成：两张表按月份一对一合并，共 312 个月，无重复、无缺失。")
    print("自建 MKT-RF = vwretd - RF；差异 = 自建值 - 官方值，均为小数单位。")
    print(f"输出：{output_file}")
    return output_file


# 五、运行入口：按顺序执行三步，也可导入后单独调用某一步函数。
# 直接运行本文件时执行清洗；被其他 Python 文件导入时不会自动读写数据。
if __name__ == "__main__":
    clean_official_factors()
    clean_market_returns()
    calculate_market_factor()
