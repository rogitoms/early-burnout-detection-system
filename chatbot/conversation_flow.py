from enum import Enum
from typing import Dict, List, Any

class QuestionType(Enum):
    TEXT_INPUT = "text_input"

class ConversationFlow:
    @staticmethod
    def get_questions() -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "type": QuestionType.TEXT_INPUT.value,
                "question": "Over the past month, how would you describe your typical energy levels and motivation for work?",
                "placeholder": "e.g., 'consistently high energy with good recovery', 'energy drains by mid-week', 'constantly drained despite time off'",
                "field": "energy_patterns"
            },
            {
                "id": 2,
                "type": QuestionType.TEXT_INPUT.value,
                "question": "What's been your general stress level at work, and what situations have been most challenging?",
                "placeholder": "e.g., 'mostly manageable stress', 'periodic high-stress situations', 'consistently overwhelmed by workload or deadlines'",
                "field": "stress_patterns"
            },
            {
                "id": 3,
                "type": QuestionType.TEXT_INPUT.value,
                "question": "How satisfied have you felt with your work accomplishments and team relationships recently?",
                "placeholder": "e.g., 'generally satisfied and well-connected', 'mixed feelings about recent projects', 'increasingly disconnected from work purpose'",
                "field": "satisfaction_connection"
            },
            {
                "id": 4, 
                "type": QuestionType.TEXT_INPUT.value,
                "question": "How well are you coping with your current workload and responsibilities?",
                "placeholder": "e.g., 'managing effectively with good systems', 'keeping up but feeling stretched thin', 'struggling to stay on top of everything'",
                "field": "coping_ability"
            },
            {
                "id": 5,
                "type": QuestionType.TEXT_INPUT.value,
                "question": "How successful have you been at maintaining boundaries between work and personal life?",
                "placeholder": "e.g., 'excellent boundaries with clear separation', 'sometimes work spills into evenings/weekends', 'constant struggle to disconnect from work demands'",
                "field": "work_life_boundaries"
            },
            {
                "id": 6,
                "type": QuestionType.TEXT_INPUT.value,
                "question": "Based on these experiences, what are your current thoughts about your future in this role?",
                "placeholder": "e.g., 'committed and planning to stay long-term', 'considering some adjustments or internal moves', 'actively exploring other options outside'",
                "field": "future_outlook"
            }
        ]
    
    @staticmethod
    def get_question_by_id(question_id: int) -> Dict[str, Any]:
        questions = ConversationFlow.get_questions()
        for question in questions:
            if question['id'] == question_id:
                return question
        return None
    
    @staticmethod
    def get_next_question_id(current_question_id: int) -> int:
        questions = ConversationFlow.get_questions()
        current_index = next((i for i, q in enumerate(questions) if q['id'] == current_question_id), -1)
        if current_index < len(questions) - 1:
            return questions[current_index + 1]['id']
        return None