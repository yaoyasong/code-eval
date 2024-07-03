import json
import argparse
import os
import difflib
from pathlib import Path
import logging
import time  # 导入time模块
from llm import Starcoder2LLM,CodeGemmaLLM,XinferenceLLM

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
    
    llm_option =  {
        "temperature": 0,
        "max_tokens": 100,
        "num_predict": 100
    }
    # llm = Starcoder2LLM("starcoder2:7b", llm_option)
    # llm = CodeGemmaLLM("codegemma:2b",llm_option)
    # llm = XinferenceLLM("custom-llm-normal", llm_option)
    llm = XinferenceLLM("starcoder2-7b", llm_option)
    return llm.generate(prompt)

def evaluate_tasks(tasks, results_file_path):
    """评估任务集并将结果保存到jsonl文件"""
    results = []
    completed_tasks = 0  # 已完成的任务数
    for task in tasks:
        prompt = task['prompt']
        logging.info(f"开始调用模型，prompt：{prompt[:10]}...")

        start_time = time.time()  # 获取调用前的时间戳
        generated_solution = llm_generate(prompt)
        end_time = time.time()  # 获取调用后的时间戳

        execution_time = end_time - start_time  # 计算执行时长
        logging.info(f"获得模型结果，generated_solution：{generated_solution[:10]}...")
        logging.info(f"调用模型执行时长：{execution_time}秒")

        solution = task['solution']
        solution_no_space = solution.strip()
        generated_solution_no_space = generated_solution.strip()
        
        # is_contained = solution_no_space in generated_solution
        # 判断solution去掉空格后是否与generated_solution相同
        is_equal = solution_no_space == generated_solution_no_space
        
        # 如果不相同，则计算相似度
        if not is_equal:
            similarity = difflib.SequenceMatcher(None, solution_no_space, generated_solution).ratio()
            # 这里假设相似度阈值为0.8，可以根据实际情况调整
            # is_passed = similarity >= 0.8
            is_passed = False
        else:
            is_passed = True
        
        result = {
            "task_id": task['task_id'],
            "passed": is_passed,
            "similarity": similarity if not is_equal else 1.0,
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
    parser = argparse.ArgumentParser(description="Evaluate tasks based on a given dataset.")
    parser.add_argument('--dataset', type=str, default='dataset/archui_eval.jsonl', help='Path to the dataset file or directory.')
    args = parser.parse_args()

    if os.path.isdir(args.dataset):
        # 如果是目录，遍历目录下的所有jsonl文件
        for file_name in os.listdir(args.dataset):
            if file_name.endswith('.jsonl'):
                file_path = os.path.join(args.dataset, file_name)
                tasks = load_dataset(file_path)
                dataset_name = os.path.splitext(file_name)[0]
                results_file_path = os.path.join("eval_result", f"{dataset_name}_results.jsonl")
                accuracy = evaluate_tasks(tasks, results_file_path)
                print(f"File: {file_name}, Accuracy: {accuracy*100:.2f}%")
    else:
        # 如果是文件，按原有逻辑处理
        tasks = load_dataset(args.dataset)
        dataset_name = Path(args.dataset).stem
        results_file_path = os.path.join("eval_result", f"{dataset_name}_results.jsonl")
        accuracy = evaluate_tasks(tasks, results_file_path)
        print(f"Accuracy: {accuracy*100:.2f}%")
