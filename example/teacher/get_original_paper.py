"""
获取学生原卷示例
演示如何获取和解析学生的答题卡数据
"""

from zhixuewang import login_playwright

# 创建教师账号
tea = login_playwright("用户名", "密码").to_teacher()

# 获取原卷数据（不保存HTML文件）
user_id = "学生ID"
topic_set_id = "科目ID"

paper = tea.get_original_paper(user_id, topic_set_id)

# 显示基本信息
print(f"总分: {paper.total_score}")
print(f"答题详情数量: {len(paper.answer_details)}")
print()

# 显示客观题得分情况
print("=== 客观题得分 ===")
objective_questions = paper.objective_questions
print(f"客观题总数: {len(objective_questions)}")
print(f"客观题总分: {paper.total_objective_score}")
print()

# 显示前5道客观题详情
for detail in objective_questions[:5]:
    status = "✓" if detail.is_correct else "✗"
    print(f"第{detail.topic_number}题 ({detail.source_category_name}): "
          f"{status} {detail.score}/{detail.standard_score}分 "
          f"答案: {detail.answer}")

print()

# 显示主观题得分情况
print("=== 主观题得分 ===")
subjective_questions = paper.subjective_questions
print(f"主观题总数: {len(subjective_questions)}")
print(f"主观题总分: {paper.total_subjective_score}")
print()

# 显示主观题详情
for detail in subjective_questions:
    print(f"第{detail.topic_number}题 ({detail.source_category_name}): "
          f"{detail.score}/{detail.standard_score}分")
    
    # 如果有小题，显示小题得分
    if detail.sub_topics:
        for sub in detail.sub_topics:
            print(f"  小题{sub.sub_topic_index}: {sub.score}分")
            # 显示批改记录
            for marking in sub.teacher_marking_records:
                print(f"    批改教师: {marking.teacher_name or '未知'} "
                      f"给分: {marking.score}分")
    print()

# 显示答题卡图片URL
print("=== 答题卡图片 ===")
sheet_urls = paper.answer_sheet_images
for idx, url in enumerate(sheet_urls, 1):
    print(f"答题卡{idx}: {url}")

# 如果需要保存HTML文件，可以这样调用：
# paper = tea.get_original_paper(user_id, topic_set_id, save_to_path="original_paper.html")
