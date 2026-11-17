# 86_kidc — 32호 KIDC(복합 판정 2015-2023) 래퍼(2026-11-17, 86_kids 복제): 86 원문을 읽어 연도 창·지속성 범례만 9년용으로 바꿔 exec(원본 86 불변).
import os, sys
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "86_yearly_maps_ehsa.py"), encoding="utf-8").read()
rep = [('SETS = {"2011-2024": [True] * T, "2011-2019": [y <= 2019 for y in YRS], "2020-2024": [y >= 2020 for y in YRS]}',
        'SETS = {"2015-2023": [True] * T, "2015-2019": [y <= 2019 for y in YRS], "2020-2023": [y >= 2020 for y in YRS]}'),
       ('{"W1_2011-15": (2011, 2015), "W2_2016-19": (2016, 2019), "W3_2020-24": (2020, 2024)}', '{"W1_2015-18": (2015, 2018), "W2_2019-23": (2019, 2023)}'),
       ('PB = [-0.5, 0.5, 2.5, 4.5, 6.5, 9.5, 13.5, 14.5]; PL = ["0", "1-2", "3-4", "5-6", "7-9", "10-13", "14"]; PP = ["#ffffff", "#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026", "#67000d"]',
        'PB = [-0.5, 0.5, 2.5, 4.5, 6.5, 8.5, 9.5]; PL = ["0", "1-2", "3-4", "5-6", "7-8", "9"]; PP = ["#ffffff", "#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"]')]
for a, b in rep:
    assert src.count(a) == 1, a[:40]; src = src.replace(a, b)
sys.argv[0] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "86_yearly_maps_ehsa.py")
exec(compile(src, sys.argv[0], "exec"))
