import collections
import math

class NaiveBayesClassifier:
    def __init__(self, alpha=1):
        self.alpha=alpha
        self.Pgood=0
        self.Pmaybe=0
        self.Pnever=0
        self.distribution=list()

    def fit(self, X, y):
#        Fit Naive Bayes classifier according to X, y.
        Gcount=0
        Mcount=0
        Ncount=0
#        Wordsgood=WordsHam Hcount=Gcount Scount=Mcount   Wordsumspam=Wordsummaybe
#        Wordsmaybe=WordsSpam  Pham=Pgood Pspam=Pmaybe  Wordsumham=Wordsumgood
        Wordsgood=collections.Counter()
        Wordsmaybe=collections.Counter()
        Wordsnever=collections.Counter()
        for i in range(len(X)):
            words=X[i].split(' ')
            if y[i] == 'good':
                for word in words:
                    Wordsgood.setdefault(word,0)
                    Wordsgood[word]+=1
            elif y[i]=='maybe':
                for word in words:
                    Wordsmaybe.setdefault(word,0)
                    Wordsmaybe[word]+=1
            else:
                for word in words:
                    Wordsnever.setdefault(word,0)
                    Wordsnever[word]+=1
        for classik in y:
            if classik=='good':
                Gcount+=1
            elif classik=='maybe':
                Mcount+=1
            else:
                Ncount+=1
        #фиксируем количество слов в классах
        wordconst1=dict(Wordsgood)
        wordconst2=dict(Wordsmaybe)
        wordconst3=dict(Wordsnever)
        
        #1 вероятность условия из всех условий
        self.Pgood=Gcount/len(y)
        self.Pmaybe=Mcount/len(y)
        self.Pnever=Ncount/len(y)
        
        # Количество слов в разделах
        Wordsumgood=sum(Wordsgood.values())
        Wordsummaybe=sum(Wordsmaybe.values())
        Wordsumnever=sum(Wordsnever.values())
        
        # вероятность встречи слова в конкретном условии
        for i in Wordsgood:
            Wordsgood[i]=Wordsgood[i]/len(Wordsgood)
        for i in Wordsmaybe:
            Wordsmaybe[i]=Wordsmaybe[i]/len(Wordsmaybe)
        for i in Wordsnever:
            Wordsnever[i]=Wordsnever[i]/len(Wordsnever)
            
        #Общее количество всех слов в тренировочном наборе
        total_words=Wordsgood | Wordsmaybe | Wordsnever
        self.vectors=[]
        
        for word in total_words:
            count=wordconst1.get(word,0)
            good=(count+self.alpha)/(Wordsumgood+len(total_words)*self.alpha)
            count=wordconst2.get(word,0)
            maybe=(count+self.alpha)/(Wordsummaybe+len(total_words)*self.alpha)
            count=wordconst3.get(word,0)
            never=(count+self.alpha)/(Wordsumnever+len(total_words)*self.alpha)
            val=good,maybe,never
            self.vectors.append(val)
        self.vectors=dict(zip(total_words,self.vectors))
        return self.vectors
        
    def predict(self, X):
#         Perform classification on an array of test vectors X.
        for i in range(len(X)):
            good=math.log(self.Pgood)
            maybe=math.log(self.Pmaybe)
            never=math.log(self.Pnever)
            sentence=X[i].lower().split(' ')
            for word in sentence:
                if self.vectors.get(word)!=None:
                    good+=math.log(self.vectors.get(word)[0])
                    maybe+=math.log(self.vectors.get(word)[1])
                    never+=math.log(self.vectors.get(word)[2])
            choose={good:'good',maybe:'maybe',never:'never'}
            val=max(good,maybe,never),choose.get(max(good,maybe,never)),X[i]
            self.distribution.append(val)
        return self.distribution
        
    def score(self, X_test, y_test):
#    Returns the mean accuracy on the given test data and labels.
        result=0
        maxresalut=len(X_test)
        for i in range(len(X_test)):
            if y_test[i]==self.distribution[i][1]:
                result+=1
        print('Обработано статей: ',maxresalut)
        print('Предсказание по разделам: ',result,'из',maxresalut)
        print('Вероятность распределения: ',result/maxresalut)
