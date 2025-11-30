from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskInputSerializer, TaskSerializer
from .scoring import calculate_score, detect_circular_dependencies
from .models import Task
import datetime

class AnalyzeTasksView(APIView):
    def post(self, request):
        """
        Analyzes a list of tasks.
        Input: List of task objects.
        Output: List of tasks with 'score' and 'explanation', sorted by score desc.
        """
        serializer = TaskInputSerializer(data=request.data, many=True)
        if serializer.is_valid():
            tasks_data = serializer.validated_data
            
            # 1. Check for circular dependencies
            # We need to ensure IDs are present for dependency checking.
            # If input doesn't have IDs, we might need to assign temp ones or assume index based?
            # The prompt implies "Input: list of tasks".
            # Let's assume the input JSON includes IDs if they reference dependencies by ID.
            # If not, we can't link them.
            
            # Assign temporary IDs if missing (for internal logic)
            for i, task in enumerate(tasks_data):
                if 'id' not in task:
                    task['id'] = i + 1000 # Temp ID
            
            cycles = detect_circular_dependencies(tasks_data)
            if cycles:
                return Response({'error': 'Circular dependencies detected', 'details': cycles}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Calculate scores
            use_ai = request.query_params.get('use_ai') == 'true'
            results = None
            
            if use_ai:
                from .ai_service import analyze_with_gemini
                results = analyze_with_gemini(tasks_data)
                
            # Fallback to standard algorithm if AI not requested or failed
            if not results:
                # Create a map for easy lookup
                tasks_map = {t['id']: t for t in tasks_data}
                
                results = []
                for task in tasks_data:
                    score, explanation = calculate_score(task, tasks_map)
                    task_result = task.copy()
                    task_result['score'] = score
                    task_result['explanation'] = explanation
                    results.append(task_result)
            
            # 3. Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # 4. Save to DB?
            # The prompt says "Input: list of tasks", "Output: sorted tasks".
            # It also has a "Suggest" endpoint which implies persistence.
            # I will wipe existing tasks and save these new ones to keep it simple and consistent with "Bulk Input".
            Task.objects.all().delete()
            
            # We need to save them carefully because of ManyToMany dependencies.
            # First pass: Create Task objects without dependencies
            id_map = {} # Input ID -> Real DB ID
            created_tasks = []
            
            for task_data in tasks_data:
                t = Task.objects.create(
                    title=task_data['title'],
                    due_date=task_data['due_date'],
                    estimated_hours=task_data['estimated_hours'],
                    importance=task_data['importance']
                )
                id_map[task_data['id']] = t.id
                created_tasks.append((t, task_data.get('dependencies', [])))
                
            # Second pass: Set dependencies
            for t, deps in created_tasks:
                real_dep_ids = []
                for dep_id in deps:
                    if dep_id in id_map:
                        real_dep_ids.append(id_map[dep_id])
                if real_dep_ids:
                    t.dependencies.set(real_dep_ids)
            
            return Response(results)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SuggestTasksView(APIView):
    def get(self, request):
        """
        Returns top 3 tasks based on current DB state.
        """
        tasks = Task.objects.all()
        # We need to re-calculate scores because time passes (urgency changes)
        # and we don't store scores in DB (computed field).
        
        # Serialize DB tasks to dicts for our scoring function
        tasks_data = []
        for t in tasks:
            tasks_data.append({
                'id': t.id,
                'title': t.title,
                'due_date': t.due_date,
                'estimated_hours': t.estimated_hours,
                'importance': t.importance,
                'dependencies': [d.id for d in t.dependencies.all()]
            })
            
        tasks_map = {t['id']: t for t in tasks_data}
        results = []
        for task in tasks_data:
            score, explanation = calculate_score(task, tasks_map)
            task['score'] = score
            task['explanation'] = explanation
            results.append(task)
            
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return Response(results[:3])
