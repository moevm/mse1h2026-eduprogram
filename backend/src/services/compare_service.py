from typing import Dict, List, Set, Tuple
from collections import defaultdict
import json

from subtopic_matcher import HeuristicSubtopicMatcher
from gigachat_matcher import GigachatMatcher
from src.rdf.rdf_controller import RdfController
from src.dataBase.dataBaseController import DataBaseController

class EducationProgramCompareService:
    
    def __init__(self, gigachat_service, db: DataBaseController, rdf: RdfController):
        self.heuristic_matcher = HeuristicSubtopicMatcher()
        self.llm_queries = GigachatMatcher(gigachat_service)
        self.db = db
        self.rdf = rdf
        self.stats = {
            'heuristic_comparisons': 0,
            'llm_comparisons': 0,
            'total_comparisons': 0
        }
    
    def compare_programs_for_graphs(self, id_user : str, university_name: str, program_name: str, compare_programs: List[ProgramReference]):
        other_programs = None
        target_program = None

        program = rdf.get_data_of_university_and_program(university_name, program_name, id_user)
        if program:
            other_programs.append(program)

        for program in compare_programs:
            university_name = program.university_name
            program_name = program.program_name

            program = rdf.get_data_of_university_and_program(university_name, program_name, id_user)
            if program:
                other_programs.append(program)

        comparison_result = self.compare_programs(target_program, other_programs)
        formatted_result = self.format_comparison_result_for_graphs(target_program, other_programs)
        rdf.add_program(university_name, comparison_result, id_user, True, True)

    return (
                status.HTTP_200_OK,
                {formatted_result}
            )

    def extract_subtopics_from_program(self, program: Dict) -> Set[str]:
        subtopics = set()
        
        for program_name, disciplines_list in program.items():
            for discipline_dict in disciplines_list:
                for discipline_name, discipline_data in discipline_dict.items():
                    topics = discipline_data.get('topics', [])
                    for topic in topics:
                        for topic_name, subtopic_list in topic.items():
                            subtopics.update(subtopic_list)
        
        return subtopics
    
    def extract_disciplines_with_subtopics(self, program: Dict) -> Dict[str, Set[str]]:
        result = {}
        
        for program_name, disciplines_list in program.items():
            for discipline_dict in disciplines_list:
                for discipline_name, discipline_data in discipline_dict.items():
                    discipline_subtopics = set()
                    topics = discipline_data.get('topics', [])
                    for topic in topics:
                        for topic_name, subtopic_list in topic.items():
                            discipline_subtopics.update(subtopic_list)
                    result[discipline_name] = discipline_subtopics
        
        return result
    
    def are_subtopics_similar(self, subtopic1: str, subtopic2: str) -> Tuple[bool, str, float]:
        self.stats['total_comparisons'] += 1
        
        if self.heuristic_matcher.exact_match(subtopic1, subtopic2):
            self.stats['heuristic_comparisons'] += 1
            return True, 'exact', 1.0
        
        if self.heuristic_matcher.normalized_match(subtopic1, subtopic2):
            self.stats['heuristic_comparisons'] += 1
            return True, 'normalized', 0.95
        
        heuristic_similarity = self.heuristic_matcher.combined_similarity(subtopic1, subtopic2)
        
        is_similar, method = self.llm_queries.are_semantically_similar(
            subtopic1, subtopic2, heuristic_similarity
        )
        
        if method == 'llm_verified':
            self.stats['llm_comparisons'] += 1
        else:
            self.stats['heuristic_comparisons'] += 1
        
        return is_similar, method, heuristic_similarity
    
    def calculate_subtopic_coverage(self, target_program: Dict, other_programs: List[Dict]) -> Dict:
        target_subtopics = self.extract_subtopics_from_program(target_program)
        
        other_subtopics_list = []
        for program in other_programs:
            other_subtopics_list.append(self.extract_subtopics_from_program(program))
        
        coverage_result = {}
        
        for target_sub in target_subtopics:
            programs_with_similar = 0
            similar_subtopics_found = []
            
            for prog_idx, other_subs in enumerate(other_subtopics_list):
                has_similar = False
                
                for other_sub in other_subs:
                    is_similar, method, confidence = self.are_subtopics_similar(target_sub, other_sub)
                    
                    if is_similar:
                        has_similar = True
                        similar_subtopics_found.append({
                            'program_index': prog_idx,
                            'subtopic': other_sub,
                            'method': method,
                            'confidence': confidence
                        })
                        break
            
            if has_similar:
                programs_with_similar += 1
            
            percentage = (programs_with_similar / len(other_programs)) * 100
            
            coverage_result[target_sub] = {
                'count': programs_with_similar,
                'percentage': round(percentage, 2),
                'similar_subtopics_found': similar_subtopics_found[:5],
                'is_common': percentage > 70,
                'is_rare': percentage < 30
            }
        
        return coverage_result
    
    def find_missing_popular_subtopics(self, target_program: Dict, other_programs: List[Dict], 
                                       popularity_threshold: float = 50.0) -> Dict:
        target_subtopics = self.extract_subtopics_from_program(target_program)
        target_disciplines = self.extract_disciplines_with_subtopics(target_program)
        
        all_other_subtopics = []
        other_programs_data = []
        
        for prog_idx, program in enumerate(other_programs):
            program_subtopics = self.extract_subtopics_from_program(program)
            program_disciplines = self.extract_disciplines_with_subtopics(program)
            all_other_subtopics.extend(list(program_subtopics))
            other_programs_data.append({
                'index': prog_idx,
                'subtopics': program_subtopics,
                'disciplines': program_disciplines
            })
        
        all_unique_subtopics = list(set(all_other_subtopics))
        clusters = self.heuristic_matcher.build_similarity_clusters(all_unique_subtopics, threshold=0.7)
        
        recommendations = []
        
        for cluster_key, cluster_members in clusters.items():
            has_in_target = False
            target_match = None
            
            for target_sub in target_subtopics:
                is_similar, _, _ = self.are_subtopics_similar(target_sub, cluster_members[0])
                if is_similar:
                    has_in_target = True
                    target_match = target_sub
                    break
            
            if not has_in_target:
                programs_with_cluster = set()
                discipline_examples = defaultdict(list)
                
                for prog_data in other_programs_data:
                    for cluster_member in cluster_members:
                        if cluster_member in prog_data['subtopics']:
                            programs_with_cluster.add(prog_data['index'])
                            for discipline, subs in prog_data['disciplines'].items():
                                if cluster_member in subs:
                                    discipline_examples[discipline].append(cluster_member)
                            break
                
                frequency = len(programs_with_cluster)
                percentage = (frequency / len(other_programs)) * 100
                
                if percentage >= popularity_threshold:
                    recommended_discipline = self._suggest_discipline(
                        cluster_members[0], target_disciplines, discipline_examples
                    )
                    
                    recommendations.append({
                        'subtopic_example': cluster_members[0],
                        'all_variants': cluster_members[:5],
                        'frequency_percent': round(percentage, 2),
                        'occurs_in_programs': frequency,
                        'recommended_discipline': recommended_discipline,
                        'found_in_disciplines': list(discipline_examples.keys())[:3]
                    })
        
        recommendations.sort(key=lambda x: x['frequency_percent'], reverse=True)
        
        return {
            'recommendations': recommendations,
            'statistics': self.get_comparison_stats()
        }
    
    def _suggest_discipline(self, subtopic: str, target_disciplines: Dict[str, Set[str]], 
                           examples: Dict[str, List[str]]) -> str:
        candidates = []
        
        for discipline, existing_subtopics in target_disciplines.items():
            for existing_sub in list(existing_subtopics)[:5]:
                is_similar, _, similarity = self.are_subtopics_similar(subtopic, existing_sub)
                if is_similar:
                    candidates.append((discipline, similarity))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        if examples:
            sorted_examples = sorted(examples.items(), key=lambda x: len(x[1]), reverse=True)
            return sorted_examples[0][0]
        
        return "Общая дисциплина"
    
    def compare_programs(self, target_program: Dict, other_programs: List[Dict]) -> Dict:
        print(f"Начинаем сравнение программы с {len(other_programs)} другими программами...")
        
        coverage = self.calculate_subtopic_coverage(target_program, other_programs)
        missing_popular = self.find_missing_popular_subtopics(target_program, other_programs)
        
        result = {
            'target_program_name': list(target_program.keys())[0] if target_program else "Unknown",
            'total_programs_compared': len(other_programs),
            'subtopic_coverage': coverage,
            'recommendations': missing_popular['recommendations'],
            'statistics': {
                'comparison_stats': self.get_comparison_stats(),
                'total_target_subtopics': len(self.extract_subtopics_from_program(target_program)),
                'total_other_subtopics': sum(
                    len(self.extract_subtopics_from_program(p)) for p in other_programs
                )
            }
        }
        
        return result
    
    def get_comparison_stats(self) -> Dict:
        total = self.stats['total_comparisons']
        heuristic_count = self.stats['heuristic_comparisons']
        llm_count = self.stats['llm_comparisons']
        
        return {
            'total_comparisons': total,
            'heuristic_comparisons': heuristic_count,
            'llm_comparisons': llm_count,
            'llm_saved_percent': round((heuristic_count / total * 100) if total > 0 else 100, 2),
            'llm_calls': llm_count,
            'cache_stats': self.llm_queries.get_cache_stats()
        }
    
    def reset_stats(self):
        self.stats = {
            'heuristic_comparisons': 0,
            'llm_comparisons': 0,
            'total_comparisons': 0
        }
        self.llm_queries.clear_cache()

    def format_comparison_result_for_graphs(self, target_program: Dict, other_programs: List[Dict]) -> Dict:
        comparison_result = self.compare_programs(target_program, other_programs)
        
        formatted_result = {}
        program_name = list(target_program.keys())[0]
        
        formatted_disciplines = []
        
        for discipline_dict in target_program[program_name]:
            for discipline_name, discipline_data in discipline_dict.items():
                formatted_discipline = {
                    discipline_name: {
                        "previousDisciplines": discipline_data.get("previousDisciplines", []),
                        "topics": []
                    }
                }
                
                for topic_obj in discipline_data.get("topics", []):
                    for topic_name, subtopics_list in topic_obj.items():
                        formatted_subtopics = []
                        
                        for subtopic in subtopics_list:
                            overlap_value = self._get_overlap_value(
                                subtopic, 
                                comparison_result['subtopic_coverage']
                            )
                            
                            formatted_subtopics.append({
                                subtopic: {"overlapValue": overlap_value}
                            })
                        
                        formatted_discipline[discipline_name]["topics"].append({
                            topic_name: formatted_subtopics
                        })
                
                formatted_disciplines.append(formatted_discipline)
        
        recommendations = self._generate_recommendations_text(comparison_result)
        
        formatted_result[program_name] = formatted_disciplines
        formatted_result["Recomendations"] = recommendations
        
        return formatted_result

    def _get_overlap_value(self, subtopic: str, coverage_data: Dict) -> int:
        if subtopic in coverage_data:
            return int(round(coverage_data[subtopic]['percentage']))
        else:
            return 0

    def _generate_recommendations_text(self, comparison_result: Dict) -> List[str]:
        recommendations = []
        
        popular_missing = comparison_result.get('recommendations', [])
        
        for rec in popular_missing[:5]:
            recommendations.append(
                f'Стоит добавить учебную единицу "{rec["subtopic_example"]}"'
            )
        
        rare_subtopics = []
        for subtopic, data in comparison_result['subtopic_coverage'].items():
            if data['is_rare'] and data['percentage'] < 20:
                rare_subtopics.append((subtopic, data['percentage']))
        
        rare_subtopics.sort(key=lambda x: x[1])
        
        for subtopic, percentage in rare_subtopics[:3]:
            recommendations.append(
                f'Стоит убрать учебную единицу "{subtopic}" (встречается только в {percentage}% программ)'
            )
        
        return recommendations

    def calculate_overlap_for_new_subtopic(self, subtopic: str, other_programs: List[Dict]) -> int:
        other_subtopics_list = []
        for program in other_programs:
            other_subtopics_list.append(self.extract_subtopics_from_program(program))
        
        count = 0
        for other_subtopics in other_subtopics_list:
            for other_sub in other_subtopics:
                is_similar, _, _ = self.are_subtopics_similar(subtopic, other_sub)
                if is_similar:
                    count += 1
                    break
        
        percentage = (count / len(other_programs)) * 100
        return int(round(percentage))