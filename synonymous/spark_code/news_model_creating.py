from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from pyspark.ml.feature import Word2Vec, Word2VecModel

from lxml import etree
import re
import string


def remove_punctuation(text):

    """
    Удаление пунктуации из текста
    """
    return text.translate(str.maketrans('', '', string.punctuation))

def remove_linebreaks(text):

    """
    Удаление разрыва строк из текста
    """
    return text.strip()

def get_only_words(tokens):

    """
    Получение списка токенов, содержащих только слова
    """
    return list(filter(lambda x: re.sub(r'[^a-zA-Zа-яА-Я]+', '', x), tokens))

spark = SparkSession\
    .builder\
    .appName("SimpleApplication")\
    .getOrCreate()

spark.sparkContext.setLogLevel('WARN')


input_data = spark.sparkContext.wholeTextFiles('tomat/news_texts1/*.txt')

print(input_data.take(1))

# Обработка текста
prepared_data = input_data.map(lambda x: (x[0], remove_punctuation(x[1]))) \
    .map(lambda x: (x[0], remove_linebreaks(x[1])))
# Перобразлвание в датафрейм
print(prepared_data.take(1))
prepared_df = prepared_data.toDF().selectExpr('_1 as news_path', '_2 as news_text')
prepared_df.show(1)

# Разбить claims на токены
tokenizer = Tokenizer(inputCol="news_text", outputCol="words")
words_data = tokenizer.transform(prepared_df)

# Отфильтровать токены, оставив только слова
filtered_words_data = words_data.rdd.map(lambda x: (x[0], x[1], get_only_words(x[2])))
filtered_df = filtered_words_data.toDF().selectExpr('_1 as news_path', '_2 as news_text', '_3 as words')

# Удалить стоп-слова (союзы, предлоги, местоимения и т.д.)
stop_words = StopWordsRemover.loadDefaultStopWords('russian')
remover = StopWordsRemover(inputCol='words', outputCol='filtered', stopWords = stop_words)
filtered = remover.transform(filtered_df)
filtered.select('words', 'filtered').show(1, truncate = False)

# vectorizer = CountVectorizer(inputCol='filtered', outputCol='raw_features').fit(filtered)
# featurized_data = vectorizer.transform(filtered)
# featurized_data.cache()

# vocabular = vectorizer.vocabulary
# print(vocabular[:100])

# spark.sparkContext.setLogLevel('INFO')

word2VecNews = Word2Vec(inputCol='filtered', outputCol='model', maxIter=20)
model = word2VecNews.fit(filtered)

modelPath = "newsmodel2/"
model.write().overwrite().save(modelPath) 

model.getVectors().show(10)
words = model.getVectors()
word = [0] * 10
for i in range(10):
    word[i] = words.collect()[i]['word']

print(word)

for w in word:
    print("Поиск синонимов для слова ", w)
    model.findSynonyms(w, 5).show(truncate = False)


spark.stop()


# str_to_find = "START"
# st = "stop"
# while str_to_find != st:
#     str_to_find = input("Введите слово для поиска или stop")
#     print("Поиск синонимов для слова", str_to_find, "...")
#     model.findSynonyms("surface", 5).select("word").show(truncate = False)
    
# print("Поиск синонимов для слова surface...")
# model.findSynonyms("surface", 5).show(truncate = False)

# print("Поиск синонимов для слова liquid...")
# model.findSynonyms("liquid", 5).show(truncate = False)

# print("Поиск синонимов для слова properties...")
# model.findSynonyms("properties", 5).show(truncate = False)

# print("Поиск синонимов для слова writing...")
# model.findSynonyms("writing", 5).show(truncate = False)

# print("Поиск синонимов для слова embedded...")
# model.findSynonyms("embedded", 5).show(truncate = False)

# modelPath = "strongmodel/"
# model.write().overwrite().save(modelPath) 

# if input("хотите сохранить модель - [y/n]") == 'y':
#     modelPath = "/word2vec-model"
#     model.save(modelPath) 
