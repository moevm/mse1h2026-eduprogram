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
        self.cache = {}
        
    def check_subtopic_similarity(self, subtopic1: str, subtopic2: str) -> bool:
        
        cache_key = f"{subtopic1}|{subtopic2}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""Определи, одинаковы ли эти учебные темы (да/нет):
                        Тема 1: {subtopic1}
                        Тема 2: {subtopic2}
                        Ответь только 'да' или 'нет'."""
        
        try:
            response = self.gigachat.query(prompt, prompt, 128)
            
            result = response.strip().lower() == 'да'
            
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"Ошибка при вызове LLM: {e}")
            return False
    
    def batch_check_similarity(self, pairs: List[Tuple[str, str]]) -> Dict[Tuple[str, str], bool]:
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
        
        pairs_text = "\n".join([f"{i+1}. {p[0]} || {p[1]}" for i, p in enumerate(uncached_pairs)])
        prompt = f"""Для каждой пары определи, одинаковы ли учебные темы (да/нет).
                    Ответь в формате JSON: {{"1": "да/нет", "2": "да/нет", ...}}
                    Пары:
                    {pairs_text}"""
        
        try:
            response = self.gigachat.query((prompt, prompt, 128))
            
            response_data = json.loads(response)
            
            for i, pair in enumerate(uncached_pairs):
                key = str(i + 1)
                if key in response_data:
                    is_similar = response_data[key].lower() == 'да'
                    results[pair] = is_similar
                    
                    cache_key = f"{pair[0]}|{pair[1]}"
                    self.cache[cache_key] = is_similar
                    
        except Exception as e:
            print(f"Ошибка при пакетной проверке: {e}")
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
        
        for candidate in candidates:
            if target_subtopic == candidate:
                return candidate
        
        candidates_text = "\n".join([f"{i+1}. {c}" for i, c in enumerate(candidates)])
        prompt = f"""Какая из этих тем наиболее похожа на тему "{target_subtopic}"?
                    Ответь только номером темы (1, 2, 3...).
                    Темы для сравнения:
                    {candidates_text}"""
        
        try:
            response = self.gigachat.query((prompt, prompt, 128))
            
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
        - Высокая (>0.85) -> считаем похожими, LLM не нужен
        - Низкая (<0.6) -> считаем непохожими, LLM не нужен
        - Средняя -> отправляем в LLM для уточнения
        """
        if heuristic_similarity >= 0.85:
            return True, "heuristic_high"
        elif heuristic_similarity <= 0.6:
            return False, "heuristic_low"
        else:
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