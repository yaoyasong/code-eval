import os
import json
import argparse
import re

def process_directory(dir_path, exclude_folders):
    task_id_counter = 1
    test_sets = []
    comment_pattern = re.compile(r'/\*{1,2}[\s\S]*?\*/', re.MULTILINE)
    # 将exclude_folders中的路径转换为绝对路径
    exclude_folders = set(os.path.abspath(folder) for folder in exclude_folders)

    for root, dirs, files in os.walk(dir_path):
        # 将root转换为绝对路径
        abs_root = os.path.abspath(root)
        # 检查当前目录是否应该被排除
        if any(abs_root.startswith(exclude_folder) for exclude_folder in exclude_folders):
            continue

        for file in files:
            if file.endswith('.cpp'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        file_content = f.read()
                        file_content = re.sub(comment_pattern, '', file_content, count=1)
                        test_sets.append({
                            "id": task_id_counter,
                            "repo_name": "vk3d",
                            "repo_path": file_path,
                            "content": file_content.strip()
                        })
                        task_id_counter += 1
                except Exception as e:
                    print(f'Failed to process file: {file_path}, error msg: {e}')
    return test_sets

#dump to jsonl
def write_to_file(test_sets, file_path):
    # 获取文件扩展名
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.jsonl':
        # 如果文件扩展名为.jsonl，使用JSON Lines格式导出
        with open(file_path, 'w', encoding='utf-8') as f:
            for test_set in test_sets:
                f.write(json.dumps(test_set, ensure_ascii=False) + '\n')
    elif file_extension.lower() == '.json':
        # 如果文件扩展名为.json，使用标准JSON格式导出
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_sets, f, ensure_ascii=False, indent=4)
    else:
        raise ValueError("Unsupported file extension. Please use .json or .jsonl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some directories and write to a file.")
    parser.add_argument('--src', type=str, default='C:\\workspace\\vk3d\\Vk3D_Proto\\src\\architecture',
                        help='The directory to process')
    parser.add_argument('--output', type=str, default='pt\\dataset\\archui_pt.jsonl',
                        help='The output file path')
    parser.add_argument('--exclude_folders', nargs='*', default=[],
                        help='List of folder names to exclude from processing')

    args = parser.parse_args()

    test_sets = process_directory(args.src, args.exclude_folders)
    write_to_file(test_sets, args.output)
