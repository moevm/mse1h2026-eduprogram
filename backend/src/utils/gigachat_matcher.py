from typing import List, Dict, Tuple, Optional
import json

class GigachatMatcher:
    """
    Класс для формирования запросов к LLM и обработки ответов
    Инкапсулирует всю логику взаимодействия с Gigachat API
    """
    
    def __init__(self, gigachat_service):
        """
        :param gigachat_service: экземпляр сервиса для работы с Gigachat API
        """
        self.gigachat = gigachat_service
        self.cache = {}  # Кэш результатов LLM для экономии токенов
        
    def check_subtopic_similarity(self, subtopic1: str, subtopic2: str) -> bool:
        """
        Проверяет, являются ли две подтемы семантически похожими
        Использует LLM для сложных случаев (синонимы, разные формулировки)
        
        Промпт оптимизирован для минимального использования токенов
        """
        # Проверяем кэш
        cache_key = f"{subtopic1}|{subtopic2}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Оптимизированный промпт (мало токенов)
        prompt = f"""Определи, одинаковы ли эти учебные темы (да/нет):
                        Тема 1: {subtopic1}
                        Тема 2: {subtopic2}
                        Ответь только 'да' или 'нет'."""
        
        try:
            # Вызов Gigachat API
            response = self.gigachat.query(prompt)
            
            # Парсим ответ
            result = response.strip().lower() == 'да'
            
            # Сохраняем в кэш
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"Ошибка при вызове LLM: {e}")
            # В случае ошибки считаем, что не похожи
            return False
    
    def batch_check_similarity(self, pairs: List[Tuple[str, str]]) -> Dict[Tuple[str, str], bool]:
        """
        Пакетная проверка нескольких пар подтем
        Экономит токены, отправляя несколько пар в одном запросе
        """
        # Отфильтровываем уже закэшированные пары
        uncached_pairs = []
        results = {}
        
        for pair in pairs:
            cache_key = f"{pair[0]}|{pair[1]}"
            if cache_key in self.cache:
                results[pair] = self.cache[cache_key]
            else:
                uncached_pairs.append(pair)
        
        if not uncached_pairs:
            return results
        
        # Формируем пакетный промпт
        pairs_text = "\n".join([f"{i+1}. {p[0]} || {p[1]}" for i, p in enumerate(uncached_pairs)])
        prompt = f"""Для каждой пары определи, одинаковы ли учебные темы (да/нет).
                    Ответь в формате JSON: {{"1": "да/нет", "2": "да/нет", ...}}
                    Пары:
                    {pairs_text}"""
        
        try:
            response = self.gigachat.query(prompt)
            
            # Парсим JSON ответ
            response_data = json.loads(response)
            
            # Сохраняем результаты
            for i, pair in enumerate(uncached_pairs):
                key = str(i + 1)
                if key in response_data:
                    is_similar = response_data[key].lower() == 'да'
                    results[pair] = is_similar
                    
                    # Сохраняем в кэш
                    cache_key = f"{pair[0]}|{pair[1]}"
                    self.cache[cache_key] = is_similar
                    
        except Exception as e:
            print(f"Ошибка при пакетной проверке: {e}")
            # В случае ошибки считаем все непроверенные пары непохожими
            for pair in uncached_pairs:
                results[pair] = False
        
        return results
    
    def find_best_match(self, target_subtopic: str, candidates: List[str]) -> Optional[str]:
        """
        Находит лучший семантический матч для целевой подтемы среди кандидатов
        Использует LLM для ранжирования похожести
        """
        if not candidates:
            return None
        
        # Проверяем точные совпадения без LLM
        for candidate in candidates:
            if target_subtopic == candidate:
                return candidate
        
        # Формируем промпт для LLM
        candidates_text = "\n".join([f"{i+1}. {c}" for i, c in enumerate(candidates)])
        prompt = f"""Какая из этих тем наиболее похожа на тему "{target_subtopic}"?
                    Ответь только номером темы (1, 2, 3...).
                    Темы для сравнения:
                    {candidates_text}"""
        
        try:
            response = self.gigachat.query(prompt)
            
            # Извлекаем номер
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                idx = int(numbers[0]) - 1
                if 0 <= idx < len(candidates):
                    return candidates[idx]
            
            return None
            
        except Exception as e:
            print(f"Ошибка при поиске лучшего матча: {e}")
            return None
    
    def are_semantically_similar(self, subtopic1: str, subtopic2: str, 
                                 heuristic_similarity: float) -> Tuple[bool, str]:
        """
        Расширенная проверка с учетом эвристической схожести
        Решает, нужно ли вызывать LLM или можно обойтись без него
        
        Стратегия:
        - Высокая уверенность (>0.85) -> считаем похожими, LLM не нужен
        - Низкая уверенность (<0.6) -> считаем непохожими, LLM не нужен
        - Средняя уверенность -> отправляем в LLM для уточнения
        """
        if heuristic_similarity >= 0.85:
            return True, "heuristic_high"
        elif heuristic_similarity <= 0.6:
            return False, "heuristic_low"
        else:
            # Пограничный случай - используем LLM
            llm_result = self.check_subtopic_similarity(subtopic1, subtopic2)
            return llm_result, "llm_verified"
    
    def clear_cache(self):
        """Очищает кэш LLM запросов"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Возвращает статистику кэша"""
        return {
            'cache_size': len(self.cache),
            'estimated_tokens_saved': len(self.cache) * 50  # Примерная оценка
        }