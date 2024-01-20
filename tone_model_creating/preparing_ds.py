import re


def filter_by_id(text):
    id_pattern = re.compile(r'.*\d+$')
    lines = text.split('\n')
    filtered_lines = [line for line in lines if id_pattern.match(line)]
    filtered_text = '\n'.join(filtered_lines)
    return filtered_text


def process_file(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        text = input_file.read()
        filtered_text = filter_by_id(text)

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(filtered_text)


def clear_bad_strs():
    input_file_path = 'rusentitweet_test.txt'
    output_file_path = 'prepared_rusentitweet_test.txt'
    process_file(input_file_path, output_file_path)

    input_file_path = 'rusentitweet_train.txt'
    output_file_path = 'prepared_rusentitweet_train.txt'
    process_file(input_file_path, output_file_path)


def filter_by_label(text, label):
    label_pattern = re.compile(f'.*{label}.*$')
    lines = text.split('\n')
    filtered_lines = [re.sub(r',\w+,\d+$', '', line) for line in lines if label_pattern.match(line)]
    filtered_text = '\n'.join(filtered_lines)
    return filtered_text


def process_file(input_file_path, positive_output_path, negative_output_path):
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        text = input_file.read()
        positive_text = filter_by_label(text, "positive")
        negative_text = filter_by_label(text, "negative")

    with open(positive_output_path, 'w', encoding='utf-8') as positive_output_file:
        positive_output_file.write(positive_text)

    with open(negative_output_path, 'w', encoding='utf-8') as negative_output_file:
        negative_output_file.write(negative_text)


if __name__ == "__main__":
    process_file('prepared_rusentitweet_test.txt', 'pos_prepared_rusentitweet_test.txt',
                 'neg_prepared_rusentitweet_test.txt')
    process_file('prepared_rusentitweet_train.txt', 'pos_prepared_rusentitweet_train.txt',
                 'neg_prepared_rusentitweet_train.txt')
