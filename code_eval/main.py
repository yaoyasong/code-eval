import argparse
from code_eval.dataset_processor import process_directory, write_to_file
from code_eval.evaluator import load_dataset, evaluate_tasks

def main():
    parser = argparse.ArgumentParser(description="Code Eval Tool")
    subparsers = parser.add_subparsers(dest='command')

    # 子命令 prepare
    parser_prepare = subparsers.add_parser('prepare', help='Prepare dataset')
    parser_prepare.add_argument('--src', type=str, required=True, help='The directory to process')
    parser_prepare.add_argument('--output', type=str, required=True, help='The output file path')

    # 子命令 evaluate
    parser_evaluate = subparsers.add_parser('evaluate', help='Evaluate tasks')
    parser_evaluate.add_argument('--dataset', type=str, required=True, help='Path to the dataset file.')

    args = parser.parse_args()

    if args.command == 'prepare':
        test_sets = process_directory(args.src)
        write_to_file(test_sets, args.output)
    elif args.command == 'evaluate':
        tasks = load_dataset(args.dataset)
        dataset_name = args.dataset.split('/')[-1].split('.')[0]
        results_file_path = f"eval_result/{dataset_name}_results.jsonl"
        evaluate_tasks(tasks, results_file_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
