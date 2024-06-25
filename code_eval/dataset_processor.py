import os
import random
import json
import clang.cindex
import re
import argparse
from clang.cindex import Index, CursorKind
clang.cindex.Config.set_library_path('C:/tools/clang18.1.7/bin')

def extract_functions(file_path):
    index = Index.create()
    tu = index.parse(file_path)
    functions = [node for node in tu.cursor.get_children() if node.kind == CursorKind.CXX_METHOD]
    return functions

def generate_test_set(function, file_content, min_lines=4, max_lines=8):
    lines = file_content.split('\n')[function.extent.start.line-1:function.extent.end.line]
    if len(lines) > min_lines:
        start_line = 0
        end_line = random.randint(min_lines, min(max_lines, len(lines)))
        prompt_lines = lines[start_line:end_line]
        last_line = prompt_lines[-1]
        # 检查去掉空格后的长度是否小于15，并且是否以//开始
        stripped_line = last_line.strip()
        if len(stripped_line) < 15 or stripped_line.startswith("//"):
            return None
        # 查找第一个完整单词的最后位置
        first_word_match = re.search(r'\w+', last_line)
        if first_word_match is None:
            return None
        split_index = first_word_match.end()

        prompt = '\n'.join(prompt_lines[:-1] + [last_line[:split_index]])
        solution = last_line[split_index:].strip()
        if len(solution) < 5:
            return None
        return (prompt, solution)
    else:
        return None

def process_directory(dir_path):
    test_sets = []
    task_id_counter = 1  # 初始化任务编号计数器
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.cpp'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    functions = extract_functions(file_path)
                    # 只处理最多3个函数
                    for function in functions[:3]:
                        test_set = generate_test_set(function, file_content)
                        if test_set is not None:
                            test_sets.append({
                                'task_id': f'CPP/{task_id_counter}',                          
                                'prompt': test_set[0],
                                'solution': test_set[1],
                                'file_path': file_path
                            })
                            task_id_counter += 1  # 更新任务编号计数器
                except Exception as e:
                    print(f'Failed to process file: {file_path}, error msg: {e}')
    return test_sets


def write_to_file(test_sets, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for test_set in test_sets:
            f.write(json.dumps(test_set, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some directories and write to a file.")
    parser.add_argument('--src', type=str, default='C:\\workspace\\vk3d\\Vk3D_Proto\\src\\architecture',
                        help='The directory to process')
    parser.add_argument('--output', type=str, default='dataset\\archui_eval.jsonl',
                        help='The output file path')

    args = parser.parse_args()

    test_sets = process_directory(args.src)
    write_to_file(test_sets, args.output)

