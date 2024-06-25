import json
import requests
import argparse
import os
import difflib
from pathlib import Path
import logging
import time  # 导入time模块

# 设置日志的配置：日志级别为INFO，日志格式包括时间戳、日志级别和日志消息
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_dataset(file_path):
    """加载数据集"""
    tasks = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            tasks.append(json.loads(line))
    return tasks

def llm_generate(prompt):
    """调用本地模型进行代码补全"""
    url = "http://localhost:11434/api/generate"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "starcoder2:3b",
        "prompt": f"<fim_prefix>{prompt}<fim_suffix><fim_middle>",
        "options": {
            "temperature": 0,
            "num_predict": 100,
            "stop":["\n","<fim_prefix>","<fim_suffix>","<fim_middle>","<|endoftext|>", "<file_sep>"]
        },
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        # 根据新的响应格式，直接获取'response'字段
        if 'response' in response_data:
            return response_data['response']
        else:
            print("No 'response' in response.")
            return None
    else:
        print("Error calling ollama:", response.text)
        return None

def evaluate_tasks(tasks, results_file_path):
    """评估任务集并将结果保存到jsonl文件"""
    results = []
    completed_tasks = 0  # 已完成的任务数
    for task in tasks:
        prompt = task['prompt']
        logging.info(f"开始调用ollama模型，prompt：{prompt[:10]}...")

        start_time = time.time()  # 获取调用前的时间戳
        generated_solution = llm_generate(prompt)
        end_time = time.time()  # 获取调用后的时间戳

        execution_time = end_time - start_time  # 计算执行时长
        logging.info(f"获得模型结果，generated_solution：{generated_solution[:10]}...")
        logging.info(f"调用模型执行时长：{execution_time}秒")

        solution = task['solution']
        solution_no_space = solution.strip()        
        
        # 判断solution去掉空格后是否包含在generated_solution里
        is_contained = solution_no_space in generated_solution
        
        # 如果不包含，则计算相似度
        if not is_contained:
            similarity = difflib.SequenceMatcher(None, solution_no_space, generated_solution).ratio()
            # 这里假设相似度阈值为0.8，可以根据实际情况调整
            # is_passed = similarity >= 0.8
            is_passed = False
        else:
            is_passed = True
        
        result = {
            "task_id": task['task_id'],
            "passed": is_passed,
            "similarity": similarity if not is_contained else 1.0,
            "solution": solution,
            "generated_solution": generated_solution,
        }
        results.append(result)
        if is_passed:
            print(f"Task {task['task_id']} passed.")
        else:
            print(f"Task {task['task_id']} failed. Similarity: {result.get('similarity', 'N/A')}")

        completed_tasks += 1
        progress = completed_tasks / len(tasks) * 100  # 计算进度百分比
        logging.info(f"进度：{completed_tasks}/{len(tasks)} ({progress:.2f}%)")

    # 计算准确率
    passed_count = sum(1 for result in results if result['passed'])
    accuracy = passed_count / len(tasks) if tasks else 0

    # 将结果保存到jsonl文件
    with open(results_file_path, 'w', encoding='utf-8') as file:
        # 保存准确率结果
        accuracy_result = {
            "accuracy": f"{accuracy*100:.2f}%",
            "passed": f"{passed_count} / {len(tasks)}"
        }
        file.write(json.dumps(accuracy_result) + "\n\n")

        for result in results:
            file.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    return accuracy


if __name__ == "__main__":
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="Evaluate tasks based on a given dataset.")
    # 添加 dataset 参数
    parser.add_argument('--dataset', type=str, default='dataset/archui_eval.jsonl', help='Path to the dataset file.')
    # 解析命令行输入的参数
    args = parser.parse_args()

    # 使用命令行提供的路径加载数据集
    tasks = load_dataset(args.dataset)

    # 从数据集路径中提取文件名（不包括扩展名）
    dataset_name = Path(args.dataset).stem

    # 构造结果文件的路径，使其名称与数据集文件名对应
    results_file_path = os.path.join("eval_result", f"{dataset_name}_results.jsonl")

    accuracy = evaluate_tasks(tasks, results_file_path)
    print(f"Accuracy: {accuracy*100:.2f}%")
