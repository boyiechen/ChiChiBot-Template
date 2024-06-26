import sqlite3

def import_vocabularies(vocab_file, db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    with open(vocab_file, 'r') as f:
        vocab_list = f.read().split()

    for word in vocab_list:
        c.execute('''
            INSERT INTO vocabularies (word, count, human_weight)
            VALUES (?, 1, 0)
            ON CONFLICT(word) DO UPDATE SET count = count + 1
        ''', (word,))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    import_vocabularies('./bot_preconfig/vocabulary.txt', './app/data/chichibot.db')
