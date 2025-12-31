original_sql = """
select
 SUM(curtailment_contrac_theory_loss) as '限出力'
from
 ods_sis_report_phase_day_new_timetype_df_2
where
 type_flag = 4
 and time_type = 2
 and year(end_time) = year(CURDATE())
 and DATE_FORMAT(end_time, '%Y-%m-%d') = '2025-05-06'
group by
 DATE(end_time);
"""

# 方法1：替换换行符为空格
cleaned_sql = original_sql.replace('\n', ' ')

# 方法2：正则表达式去除所有换行符和多余空格
import re
cleaned_sql = re.sub(r'\s+', ' ', original_sql).strip()
print(cleaned_sql)
