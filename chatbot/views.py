from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import logging
from pathlib import Path

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer
from .conversation_flow import ConversationFlow
from .assessment_logic import assessment_calculator
from ml_model.llm_api_recommender import (
    llm_api_recommender,
    GroqAPIUnavailable,  
)

logger = logging.getLogger(__name__)

@api_view(['POST'])
@login_required
def start_chat_session(request):
    """Start a new burnout assessment session"""
    try:
        print(f"User starting session: {request.user}")
        print(f"Authenticated: {request.user.is_authenticated}")
        
        # Create new chat session
        chat_session = ChatSession.objects.create(user=request.user)
        
        # Get first question
        first_question = ConversationFlow.get_questions()[0]
        
        # Save first question as a message
        ChatMessage.objects.create(
            session=chat_session,
            message_type='question',
            content=first_question['question'],
            question_id=first_question['id']
        )
        
        serializer = ChatSessionSerializer(chat_session)
        return Response({
            'success': True,
            'session': serializer.data,
            'current_question': first_question
        })
        
    except Exception as e:
        logger.error(f"Failed to start chat session: {str(e)}")
        return Response(
            {'error': f'Failed to start session: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@login_required
def submit_answer(request):
    """Submit an answer and get next question or results"""
    try:
        question_id = request.data.get('question_id')
        answer = request.data.get('answer')
        
        if not question_id or not answer:
            return Response(
                {'error': 'Question ID and answer are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the latest active session for user
        chat_session = ChatSession.objects.filter(
            user=request.user, 
            is_complete=False
        ).order_by('-started_at').first()
        
        if not chat_session:
            return Response(
                {'error': 'No active chat session found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save user's answer
        ChatMessage.objects.create(
            session=chat_session,
            message_type='answer',
            content=answer,
            question_id=question_id
        )
        
        # Check if this is the last question
        next_question_id = ConversationFlow.get_next_question_id(question_id)
        
        if next_question_id is None:
            # All questions answered - calculate results
            return _complete_assessment(chat_session)
        else:
            # Get next question
            next_question = ConversationFlow.get_question_by_id(next_question_id)
            ChatMessage.objects.create(
                session=chat_session,
                message_type='question',
                content=next_question['question'],
                question_id=next_question['id']
            )
            
            serializer = ChatSessionSerializer(chat_session)
            return Response({
                'success': True,
                'session': serializer.data,
                'current_question': next_question,
                'progress': {
                    'current': question_id,
                    'total': len(ConversationFlow.get_questions()),
                    'percentage': int((question_id / len(ConversationFlow.get_questions())) * 100)
                }
            })
            
    except Exception as e:
        logger.error(f"Failed to process answer: {str(e)}")
        return Response(
            {'error': f'Failed to process answer: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _complete_assessment(chat_session):
    """Complete the assessment using ML model + LLM recommendations"""
    try:
        # Get all answers from the session
        answers = {}
        
        messages = chat_session.messages.all().order_by('timestamp')
        for message in messages:
            if message.message_type == 'answer':
                question = ConversationFlow.get_question_by_id(message.question_id)
                if question:
                    answers[question['field']] = message.content
        
        print(f"Processing assessment with {len(answers)} answers")
        
        # Calculate burnout score using ML model
        result = assessment_calculator.calculate_score_from_answers(answers)
        
        print(f"ML Model result: {result['level']} (Score: {result['score']})")
        
        # 🆕 CRITICAL: Save the score to database FIRST, before LLM processing
        chat_session.burnout_score = result['score']
        chat_session.burnout_level = result['level']
        chat_session.completed_at = timezone.now()
        chat_session.is_complete = True
        
        # ✅ Initialize with fallback values FIRST
        llm_recommendations = _get_score_based_recommendations(result['score'], result['level'])
        detailed_analysis = _get_score_based_analysis(result['score'], result['level'])
        
        # ✅ THEN try to override with LLM if available
        try:
            structured_answers = _structure_answers_for_llm(answers)
            if structured_answers:
                llm_payload = llm_api_recommender.generate_recommendations(structured_answers)
                llm_recommendations = _format_llm_recommendations(llm_payload.get('recommendations', []))
                detailed_analysis = llm_payload.get('summary')
                print("Hosted LLM recommendations generated successfully")
        except Exception as exc:
            print(f"LLM API failed: {exc}")
            # ✅ No action needed - fallback values are already set
        
        # Save LLM results
        chat_session.recommendation = llm_recommendations
        chat_session.detailed_analysis = detailed_analysis
        chat_session.save()  # 🆕 Save everything at once
        
        # Add result message
        ChatMessage.objects.create(
            session=chat_session,
            message_type='system',
            content=f"Assessment complete! Burnout level: {result['level']} (Score: {result['score']:.3f})"
        )
        
        # Prepare response
        response_result = {
            'level': result['level'],
            'score': result['score'],
            'llm_recommendations': llm_recommendations,
            'detailed_analysis': detailed_analysis
        }
        
        serializer = ChatSessionSerializer(chat_session)
        return Response({
            'success': True,
            'session': serializer.data,
            'result': response_result,
            'assessment_complete': True
        })
        
    except Exception as e:
        logger.error(f"Failed to complete assessment: {str(e)}")
        logger.error(f"Traceback:", exc_info=True)
        return Response(
            {'error': f'Failed to complete assessment: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
def _get_score_based_recommendations(score, level):
    """Generate detailed recommendations based on burnout score"""
    
    base_recommendations = {
        'LOW': {
            'title': "Maintaining Well-being",
            'recommendations': [
                {
                    'title': 'Continue Healthy Habits',
                    'description': 'Keep up your current routines that support work-life balance.',
                    'why_it_helps': 'Prevention is key to maintaining low stress levels.',
                    'timeframe': 'Continue ongoing',
                    'priority': 'low'
                },
                {
                    'title': 'Regular Self-Check-ins',
                    'description': 'Schedule monthly assessments of your stress levels and workload.',
                    'why_it_helps': 'Early detection prevents burnout progression.',
                    'timeframe': 'Monthly',
                    'priority': 'medium'
                },
                {
                    'title': 'Build Resilience',
                    'description': 'Develop skills like mindfulness and time management.',
                    'why_it_helps': 'Strong coping mechanisms protect against future stress.',
                    'timeframe': 'Next 2-3 months',
                    'priority': 'medium'
                }
            ]
        },
        'MODERATE': {
            'title': "Addressing Early Signs",
            'recommendations': [
                {
                    'title': 'Set Clear Boundaries',
                    'description': 'Establish firm work hours and learn to say no to additional responsibilities.',
                    'why_it_helps': 'Prevents work overload and protects personal time.',
                    'timeframe': 'Immediately',
                    'priority': 'high'
                },
                {
                    'title': 'Take Regular Breaks',
                    'description': 'Schedule 5-10 minute breaks every 2 hours during work.',
                    'why_it_helps': 'Prevents mental fatigue and maintains productivity.',
                    'timeframe': 'Starting tomorrow',
                    'priority': 'high'
                },
                {
                    'title': 'Practice Stress Reduction',
                    'description': 'Incorporate daily mindfulness or deep breathing exercises.',
                    'why_it_helps': 'Reduces cortisol levels and improves mental clarity.',
                    'timeframe': 'Daily, starting today',
                    'priority': 'high'
                },
                {
                    'title': 'Physical Activity',
                    'description': 'Aim for 30 minutes of moderate exercise 3-4 times per week.',
                    'why_it_helps': 'Releases endorphins and reduces stress hormones.',
                    'timeframe': 'This week',
                    'priority': 'medium'
                }
            ]
        },
        'HIGH': {
            'title': "Immediate Action Required",
            'recommendations': [
                {
                    'title': 'Establish Firm Work Boundaries',
                    'description': 'Set non-negotiable work hours and completely stop weekend work to reclaim personal time.',
                    'why_it_helps': 'Directly addresses work-life imbalance and prevents constant work spillover.',
                    'timeframe': 'Starting today',
                    'priority': 'critical'
                },
                {
                    'title': 'Address Workload and Deadlines',
                    'description': 'Have an urgent meeting with your manager about reducing context switching and extending unrealistic deadlines.',
                    'why_it_helps': 'Targets the chaotic workload and multiple urgent deadlines causing overwhelm.',
                    'timeframe': 'This week',
                    'priority': 'critical'
                },
                {
                    'title': 'Seek Professional Support',
                    'description': 'Consult with a mental health professional for exhaustion and coping strategies.',
                    'why_it_helps': 'Addresses the daily exhaustion and feeling of being completely drained.',
                    'timeframe': 'Within 1 week',
                    'priority': 'high'
                },
                {
                    'title': 'Take Recovery Time Off',
                    'description': 'Use sick leave for 3-5 days to completely disconnect and rest.',
                    'why_it_helps': 'Essential break from the overwhelming workload leading to mistakes.',
                    'timeframe': 'As soon as possible',
                    'priority': 'high'
                },
                {
                    'title': 'Find External Meaning and Support',
                    'description': 'Engage in non-work activities and seek social support outside your team.',
                    'why_it_helps': 'Counters feelings of meaninglessness and lack of team support.',
                    'timeframe': 'Starting this weekend',
                    'priority': 'high'
                }
            ]
        }
    }
    
    # Get recommendations for the specific level
    level_data = base_recommendations.get(level, base_recommendations['MODERATE'])
    
    # Format the recommendations
    formatted = []
    for idx, rec in enumerate(level_data['recommendations'], 1):
        parts = []
        parts.append(f"**{idx}. {rec['title']}**")
        parts.append(f"   {rec['description']}")
        parts.append(f"   **Why it helps:** {rec['why_it_helps']}")
        parts.append(f"   **When to start:** {rec['timeframe']}")
        parts.append(f"   **Priority:** {rec['priority'].replace('_', ' ').title()}")
        formatted.extend(parts)
        formatted.append("")
    
    # Remove last empty line and add header
    if formatted and formatted[-1] == "":
        formatted.pop()
    
    return "\n".join(formatted)

def _get_score_based_analysis(score, level):
    """Generate detailed analysis based on burnout score"""
    
    analysis_templates = {
        'LOW': (
            "You're currently managing well with healthy stress levels. "
            "Your responses indicate good work-life balance and effective coping strategies. "
            "Continue these positive habits to maintain your well-being."
        ),
        'MODERATE': (
            "You're showing early signs of burnout that need attention. "
            "Your responses suggest increasing stress levels and some difficulty with work-life balance. "
            "Implementing preventive measures now can help avoid more severe burnout."
        ),
        'HIGH': (
            "You're experiencing significant burnout symptoms that require immediate attention. "
            "Your responses indicate high stress levels, emotional exhaustion, and potential impact on your well-being. "
            "Taking proactive steps for recovery is essential for your health and long-term productivity."
        )
    }
    
    # Add score-specific details
    score_details = {
        'LOW': f"With a burnout score of {score:.1%}, you're in the healthy range.",
        'MODERATE': f"Your burnout score of {score:.1%} indicates moderate risk that warrants proactive measures.",
        'HIGH': f"Your burnout score of {score:.1%} indicates high risk requiring immediate action and professional support."
    }
    
    base_analysis = analysis_templates.get(level, analysis_templates['MODERATE'])
    score_analysis = score_details.get(level, "")
    
    return f"{base_analysis} {score_analysis}"

def _structure_answers_for_llm(answers: dict) -> list:
    """Map stored answers back to their original questions for LLM context."""
    structured = []
    for question in ConversationFlow.get_questions():
        field = question.get('field')
        if field in answers:
            structured.append({
                'question_id': question['id'],
                'question': question['question'],
                'response': answers[field]
            })
    return structured


def _build_answer_summary(answers: dict) -> str:
    """Human-friendly summary string reused by the offline LLM fallback."""
    summary = "Work burnout assessment answers: "
    for question in ConversationFlow.get_questions():
        field = question['field']
        if field in answers:
            summary += f"{question['question']} Answer: {answers[field]}. "
    return summary


def _format_llm_recommendations(recommendations: list) -> str:
    """Convert structured recommendations into properly formatted bullet points"""
    if not recommendations:
        return ""
    
    formatted_lines = []
    for idx, rec in enumerate(recommendations, start=1):
        title = rec.get('title', f'Recommendation {idx}').strip()
        description = rec.get('description', '').strip()
        why_it_helps = rec.get('why_it_helps', '').strip()
        timeframe = rec.get('timeframe', '').strip()
        priority = rec.get('priority', '').replace('_', ' ').title()
        
        # Build each recommendation with proper line breaks
        parts = []
        
        # Main title and description
        parts.append(f"**{idx}. {title}**")
        parts.append(f"   {description}")
        
        # Optional fields (only if they exist)
        if why_it_helps:
            parts.append(f"   **Why it helps:** {why_it_helps}")
        if timeframe:
            parts.append(f"   **When to start:** {timeframe}")
        if priority:
            parts.append(f"   **Priority:** {priority}")
        
        # Add spacing between recommendations
        formatted_lines.extend(parts)
        formatted_lines.append("")  # Empty line between recommendations
    
    # Remove the last empty line and join with newlines
    if formatted_lines and formatted_lines[-1] == "":
        formatted_lines.pop()
    
    return "\n".join(formatted_lines)
    
@api_view(['GET'])
@login_required
def get_chat_history(request):
    """Get user's previous chat sessions"""
    try:
        sessions = ChatSession.objects.filter(user=request.user).order_by('-started_at')
        serializer = ChatSessionSerializer(sessions, many=True)
        
        return Response({
            'success': True,
            'sessions': serializer.data,
            'total_sessions': sessions.count()
        })
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        return Response(
            {'error': f'Failed to get chat history: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@login_required
def get_session_detail(request, session_id):
    """Get details of a specific chat session"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        serializer = ChatSessionSerializer(session)
        
        return Response({
            'success': True,
            'session': serializer.data
        })
        
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Chat session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to get session details: {str(e)}")
        return Response(
            {'error': f'Failed to get session details: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Add this to your views.py - after the existing views
@api_view(['DELETE'])
@login_required
def delete_session(request, session_id):
    """Delete a specific chat session"""
    try:
        # Get the session belonging to the current user
        session = ChatSession.objects.get(id=session_id, user=request.user)
        session.delete()
        
        return Response({
            'success': True, 
            'message': 'Session deleted successfully'
        })
        
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Session not found or you don\'t have permission to delete it'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to delete session: {str(e)}")
        return Response(
            {'error': 'Failed to delete session'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        # Add this to your existing views.py - after the other views
@api_view(['POST'])
@login_required
def analyze_burnout_message(request):
    """Analyze free-form burnout messages with LLM"""
    try:
        user_message = request.data.get('message', '').strip()
        
        if not user_message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"🧠 Analyzing burnout message from {request.user}: {user_message[:50]}...")
        
        # Import and use your legacy offline LLM recommender for this endpoint
        import sys
        import importlib
        project_root = Path(__file__).resolve().parents[2]
        root_str = str(project_root)
        if root_str not in sys.path:
            sys.path.append(root_str)
        llm_module = importlib.import_module("ml_model.llm_recommender")
        llm_recommender = getattr(llm_module, "llm_recommender")
        
        # Get LLM recommendations
        llm_result = llm_recommender.get_recommendations(user_message)
        
        # Also get assessment from your existing model if possible
        try:
            # Try to use your existing assessment logic
            burnout_result = assessment_calculator.analyze_text(user_message)
        except:
            # Fallback to simple analysis
            text_lower = user_message.lower()
            if any(word in text_lower for word in ['exhausted', 'burned out', 'overwhelmed', 'stress', 'anxious']):
                burnout_result = {'level': 'HIGH', 'score': 0.85, 'color': '🔴'}
            elif any(word in text_lower for word in ['love', 'great', 'happy', 'energized', 'motivated']):
                burnout_result = {'level': 'LOW', 'score': 0.15, 'color': '🟢'}
            else:
                burnout_result = {'level': 'MODERATE', 'score': 0.5, 'color': '🟡'}
        
        response_data = {
            'success': True,
            'burnout_level': burnout_result['level'],
            'burnout_score': burnout_result.get('score', 0.5),
            'color': burnout_result.get('color', '🟡'),
            'llm_recommendations': llm_result['recommendations'],
            'summary': llm_result['summary'],
            'user_input': user_message,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Failed to analyze burnout message: {str(e)}")
        return Response(
            {'error': f'Analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )