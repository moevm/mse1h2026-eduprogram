"""
subtopic_matcher.py
Модуль для сравнения подтем без использования LLM (эвристические методы)
Содержит методы точного, нормализованного и векторного сравнения
"""

import re
import numpy as np
from typing import Tuple, List, Dict, Set
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

class HeuristicSubtopicMatcher:
    """
    Класс для эвристического сравнения подтем без использования LLM
    Использует: точное совпадение, нормализацию, расстояние Левенштейна, TF-IDF
    """
    
    def __init__(self):
        # TF-IDF векторизатор для символьных n-грамм (работает хорошо для коротких текстов)
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='char',  # Анализируем по символам, а не по словам
            ngram_range=(2, 4),  # 2-4 символьные n-граммы
            lowercase=True,
            max_features=1000  # Ограничиваем размер словаря
        )
        self.tfidf_matrix = None
        self.is_fitted = False
        
    def normalize_text(self, text: str) -> str:
        """
        Нормализация текста для точного сравнения
        Удаляем пунктуацию, приводим к нижнему регистру, убираем лишние пробелы
        """
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Удаляем пунктуацию
        text = re.sub(r'\s+', ' ', text)      # Схлопываем пробелы
        return text
    
    def exact_match(self, subtopic1: str, subtopic2: str) -> bool:
        """Уровень 1: Точное совпадение строк"""
        return subtopic1 == subtopic2
    
    def normalized_match(self, subtopic1: str, subtopic2: str) -> bool:
        """Уровень 2: Совпадение после нормализации"""
        return self.normalize_text(subtopic1) == self.normalize_text(subtopic2)
    
    def levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        Уровень 3: Коэффициент схожести на основе расстояния Левенштейна
        Возвращает значение от 0 до 1, где 1 - полное совпадение
        """
        def levenshtein_distance(a: str, b: str) -> int:
            """Расчет расстояния Левенштейна"""
            if len(a) < len(b):
                return levenshtein_distance(b, a)
            if len(b) == 0:
                return len(a)
            
            previous_row = list(range(len(b) + 1))
            for i, ca in enumerate(a):
                current_row = [i + 1]
                for j, cb in enumerate(b):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (ca != cb)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]
        
        # Нормализуем строки перед сравнением
        s1_norm = self.normalize_text(s1)
        s2_norm = self.normalize_text(s2)
        
        max_len = max(len(s1_norm), len(s2_norm))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(s1_norm, s2_norm)
        return 1 - (distance / max_len)
    
    def fit_tfidf(self, texts: List[str]):
        """
        Обучаем TF-IDF векторизатор на списке текстов
        Вызываем один раз для всех подтем, чтобы не переобучать каждый раз
        """
        if not self.is_fitted and texts:
            processed_texts = [self.normalize_text(t) for t in texts]
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_texts)
            self.is_fitted = True
    
    def get_tfidf_similarity(self, text1: str, text2: str) -> float:
        """
        Уровень 4: Векторное сходство через TF-IDF
        Работает хорошо для семантически близких, но разных по написанию терминов
        """
        # Нормализуем тексты
        text1_norm = self.normalize_text(text1)
        text2_norm = self.normalize_text(text2)
        
        # Если векторизатор еще не обучен, обучаем на этих двух текстах
        if not self.is_fitted:
            self.fit_tfidf([text1_norm, text2_norm])
        
        # Трансформируем тексты в векторы
        vectors = self.tfidf_vectorizer.transform([text1_norm, text2_norm])
        
        # Вычисляем косинусное сходство
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return float(similarity)
    
    def combined_similarity(self, subtopic1: str, subtopic2: str) -> float:
        """
        Комбинированная оценка схожести без LLM
        Используем взвешенную сумму разных методов
        """
        # Проверяем точное совпадение (максимальный вес)
        if self.exact_match(subtopic1, subtopic2):
            return 1.0
        
        # Нормализованное совпадение
        if self.normalized_match(subtopic1, subtopic2):
            return 0.95
        
        # Комбинируем Левенштейна и TF-IDF
        lev_sim = self.levenshtein_similarity(subtopic1, subtopic2)
        tfidf_sim = self.get_tfidf_similarity(subtopic1, subtopic2)
        
        # Веса: TF-IDF важнее для семантики, Левенштейн - для опечаток
        combined = (lev_sim * 0.3) + (tfidf_sim * 0.7)
        
        return combined
    
    def are_similar_heuristic(self, subtopic1: str, subtopic2: str, threshold: float = 0.75) -> Tuple[bool, float]:
        """
        Определяет, похожи ли подтемы, используя только эвристические методы
        Возвращает: (похожи ли, уверенность)
        """
        similarity = self.combined_similarity(subtopic1, subtopic2)
        return similarity >= threshold, similarity
    
    def build_similarity_clusters(self, subtopics: List[str], threshold: float = 0.75) -> Dict[str, List[str]]:
        """
        Группирует похожие подтемы в кластеры
        Это позволяет сократить количество сравнений с O(n²) до O(n)
        
        Алгоритм:
        1. Берем первую подтему как ядро кластера
        2. Находим все похожие на нее подтемы
        3. Удаляем их из списка и повторяем
        """
        remaining = subtopics.copy()
        clusters = {}
        
        while remaining:
            # Берем ядро кластера
            core = remaining.pop(0)
            cluster = [core]
            to_remove = []
            
            # Ищем похожие подтемы
            for other in remaining:
                is_similar, _ = self.are_similar_heuristic(core, other, threshold)
                if is_similar:
                    cluster.append(other)
                    to_remove.append(other)
            
            # Удаляем сгруппированные элементы
            for item in to_remove:
                remaining.remove(item)
            
            # Используем нормализованное имя как ключ кластера
            cluster_key = self.normalize_text(core)
            clusters[cluster_key] = cluster
        
        return clusters
    
    def create_inverted_index(self, subtopics: List[str]) -> Dict[str, List[str]]:
        """
        Создает обратный индекс по нормализованным подтемам
        Ускоряет поиск похожих подтем O(1) вместо O(n)
        """
        inverted_index = defaultdict(list)
        for subtopic in subtopics:
            normalized = self.normalize_text(subtopic)
            inverted_index[normalized].append(subtopic)
        return dict(inverted_index)