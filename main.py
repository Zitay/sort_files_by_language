from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import spacy
from spacy.language import Language
from spacy_language_detection import LanguageDetector
import shutil
import os
from tika import parser
import time
import psutil
from queue import Queue


files_in_process = set()
files_in_process_lock = Lock()


def get_lang_detector(nlp, name):
    return LanguageDetector(seed=42)  # We use the seed 42


def detect_lan(text, nlp_he, num_words=40):
    if not text.strip():
        return None  # or a default language code
    words = text.split()
    total_words = len(words)

    # Calculate the middle point
    mid_index = total_words // 2

    # Calculate starting and ending indices
    start_index = max(mid_index - num_words // 2, 0)
    end_index = min(start_index + num_words, total_words)

    # Extract the middle words
    middle_words = ' '.join(words[start_index:end_index])

    if 'language_detector' not in nlp_he.pipe_names:
        Language.factory("language_detector", func=get_lang_detector)
        nlp_he.add_pipe('language_detector', last=True)

    doc = nlp_he(middle_words)
    language_code = doc._.language['language']
    return language_code


def sort_files_by_lan(text, file_, filename, extension, nlp_he):
    if not os.path.exists(file_):
        print(f"File does not exist: {file_}")
        return
    lan = detect_lan(text, nlp_he)
    destination_path = ""

    if lan == 'he':
        destination_path = os.path.join("E:", "cv files",'2', "hebrew")
    elif lan == 'en':
        destination_path = os.path.join("E:", "cv files",'2', "english")
    else:
        return  # or handle other languages

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    try:
        shutil.move(file_, destination_path)
        print(f"Successfully moved {filename + extension} to {destination_path}")
    except Exception as e:
        print(f"Error moving file: {e}")


def process_file(file_queue, nlp_he, extensions):
    while not file_queue.empty():
        file_path = file_queue.get()
        filename, extension = os.path.splitext(file_path)
        if extension.lower() in extensions:
            try:
                raw = parser.from_file(file_path)
                text = raw.get('content', '').strip()
                if text:
                    sort_files_by_lan(text, file_path,filename,extension, nlp_he)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
            finally:
                file_queue.task_done()


def main():
    start_time = time.time()
    nlp_he = spacy.load("he_ner_news_trf", disable=["tagger", "parser"])

    filesPath = r'C:\Users\Itay\Dropbox\PC\Downloads\files2'
    extensions = ['.pdf', '.doc', '.docx', '.rtf']
    max_files = 500000
    max_workers = (psutil.cpu_count(logical=True)) - 1
    multi_threading = True

    if multi_threading:
        file_queue = Queue()
        for dirpath, _, filenames in os.walk(filesPath):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                if os.path.isfile(file_path):
                    file_queue.put(file_path)

        with ThreadPoolExecutor(max_workers=4) as executor:
            for _ in range(max_workers):
                executor.submit(process_file, file_queue, nlp_he, extensions)

        file_queue.join()
    else:
        times = 0
        for dirpath, dirnames, filenames in os.walk(filesPath):
            for file in filenames:
                times +=1
                if not os.path.isfile(os.path.join(dirpath, file)):
                    continue
                process_file(file, dirpath, nlp_he, filesPath, extensions)
                if times >=max_files:
                    break

    end_time = time.time()
    print(f"Runtime: {end_time - start_time} seconds")



if __name__ == "__main__":
    logical_cpus = psutil.cpu_count()

    # Total physical cores (ignores hyper-threading)
    physical_cores = psutil.cpu_count(logical=False)

    print(f"Logical CPUs (including hyper-threading): {logical_cpus}")
    print(f"Physical Cores: {physical_cores}")
    main()