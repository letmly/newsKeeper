from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
import pickle
import re, string, random


def remove_noise(tweet_tokens, stop_words=()):
    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens, lang='rus'):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)
        token = re.sub("(@[A-Za-z0-9_]+)", "", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token


def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)


def get_tokens_from_text(input_text_path):
    with open(input_text_path, 'r', encoding='utf-8') as input_file:
        text = input_file.read()
        lines = text.split('\n')
        res = [word_tokenize(line) for line in lines]
        return res


if __name__ == "__main__":

    # positive_tweets = twitter_samples.strings('positive_tweets.json')
    # negative_tweets = twitter_samples.strings('negative_tweets.json')
    # text = twitter_samples.strings('tweets.20150430-223406.json')
    # tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]

    stop_words = stopwords.words('russian')

    pos_tweet_tokens_train = get_tokens_from_text('pos_prepared_rusentitweet_train.txt')
    pos_tweet_tokens_test = get_tokens_from_text('pos_prepared_rusentitweet_test.txt')
    positive_tweet_tokens = pos_tweet_tokens_train + pos_tweet_tokens_test

    neg_tweet_tokens_train = get_tokens_from_text('neg_prepared_rusentitweet_train.txt')
    neg_tweet_tokens_test = get_tokens_from_text('neg_prepared_rusentitweet_test.txt')
    negative_tweet_tokens = neg_tweet_tokens_train + neg_tweet_tokens_test

    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    all_pos_words = get_all_words(positive_cleaned_tokens_list)

    freq_dist_pos = FreqDist(all_pos_words)
    print(freq_dist_pos.most_common(10))

    positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
    negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

    positive_dataset = [(tweet_dict, "Позитивная")
                        for tweet_dict in positive_tokens_for_model]

    negative_dataset = [(tweet_dict, "Негативная")
                        for tweet_dict in negative_tokens_for_model]

    dataset = positive_dataset + negative_dataset

    random.shuffle(dataset)
    print(len(dataset))
    train_data = dataset[:int(len(dataset) * .85)]
    test_data = dataset[int(len(dataset) * .85):]

    classifier = NaiveBayesClassifier.train(train_data)

    print("Accuracy is:", classify.accuracy(classifier, test_data))

    print(classifier.show_most_informative_features(10))

    custom_tweets = [
        "господи как же круто, так красиво",
        "спасибо большое за перевод ты большая умничка🧡",
        "я купила самый милый чехол на планете всего за 149 рублей",
        "Сука я злюсь на весь мир",
        'Глава Волгограда возложил цветы к мемориальной доске. 29 декабря Волгоград и вся страна вспоминают трагические события 2013 года. В этот день 10 лет назад в здании железнодорожного вокзала Волгограда был совершен теракт. Взрыв произошел в 12:45. Он прогремел на первом этаже вокзала между входом в здание и турникетом. Теракт унес жизни 18 человек, десятки людей получили ранения. Сегодня, 29 декабря, глава Волгограда Владимир Марченко возложил цветы к мемориальной доске, установленной у железнодорожного вокзала Волгоград-I. Он почтил минутой молчания память жертв теракта. Также сегодня глава региона Андрей Бочаров почтил память погибших в терактах 2013 года.',
        'Они установлены на станции "Комсомольская" и в скором времени будут запущены в эксплуатацию. Сегодня, 3 января, в рамках выездного рабочего совещания на станции метротрама "Комсомольская" губернатор Волгоградской области Андрей Бочаров лично протестировал новые современные эскалаторы. В эксплуатацию они войдут в самое ближайшее время, после прохождения технической экспертизы. Новые эскалаторы скоро заработают и на другой подземной станции - "Площадь Ленина". Обсуждая процесс модернизации и обновления самого популярного городского общественного транспорта в областной столице, глава региона также поставил задачу по внедрению современных технологий в организацию работы станций, в частности турникетов. - Мы выходим на эксплуатацию новых эскалаторов, но нужно посмотреть и дальше, - акцентировал внимание Андрей Бочаров, - в холлах подземных станций большое пространство, в них можно поставить турникеты. В целях безопасности нельзя оставлять и лавочки с открытым пространством под ними. Губернатор отметил, что первый этап реконструкции скоростного трамвая полностью завершен. До конца месяца будут завершены пусконаладочные работы и начнут работать эскалаторы. - Все задачи, которые мы ставили на 2023 год, Волгоградская область выполнила в полном объеме, - сказал губернатор. - Это касается и замены шпал, рельсов, всех тех конструкций, которые были определены в трехстороннем инвестиционном соглашении. Мы осуществили закупку нового подвижного состава. В целом задачи на 2024 год полностью определены, объем финансовых средств полностью есть. В текущем году предстоит реконструкция путей скоростного трамвая от остановки «Пл. Возрождения» до остановки «ТРК Европа». Также запланированы модернизации тяговых подстанций, кабельных и воздушных линий СТ, выход на линию закупленных 50 односекционных и 12 трехсекционных трамваев;, проектирование новых участков строительства и модернизации (нового участка СТ до ТРК «Акварель»), трамвайных линий в Красноармейском районе.'
    ]
    sentiments = [
        "pos",  # "Just had an amazing experience with AwesomeServices, their customer support is top-notch!"
        "pos",  # "I can't believe the quality of the product I received from FantasticGoods, exceeded my expectations!"
        "pos",  # "Ordered from SuperQuickDelivery and got my package within hours. Impressed!"
        "neg",  # "Had a terrible experience with SlowServiceInc, will never use their services again."
        "neg",  # "In love with the new features of the latest app update. Great job, TechInnovators!"
        "neg",  # "Huge shoutout to DeliciousEats for the tasty food. Will definitely order again!"
    ]
    for i, tweet in enumerate(custom_tweets):
        custom_tokens = remove_noise(word_tokenize(tweet))
        print(f"{i + 1})\n\t{tweet}")
        print("\tPredict: ", classifier.classify(dict([token, True] for token in custom_tokens)))
        print(f"\tReal: {sentiments[i]}\n")

    f = open('my_classifier.pickle', 'wb')
    pickle.dump(classifier, f)
    f.close()

# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger_ru')
# nltk.download('stopwords')
# nltk.download('punkt')
