from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskInputSerializer
from .scoring import calculate_score, detect_circular_dependencies
from .models import Task

class AnalyzeTasksView(APIView):
    def post(self, request):
        """
        Analyzes a list of tasks.
        """
        serializer = TaskInputSerializer(data=request.data, many=True)
        if serializer.is_valid():
            tasks_data = serializer.validated_data
            
            # 1. Handle Missing IDs (Assign temp ones for calculation)
            for i, task in enumerate(tasks_data):
                if 'id' not in task:
                    task['id'] = i + 1000 
            
            # 2. Check for circular dependencies
            cycles = detect_circular_dependencies(tasks_data)
            if cycles:
                return Response({'error': 'Circular dependencies detected', 'details': cycles}, status=status.HTTP_400_BAD_REQUEST)

            # 3. Calculate scores
            use_ai = request.query_params.get('use_ai') == 'true'
            strategy = request.query_params.get('strategy', 'smart') # Default to smart
            
            results = None
            
            if use_ai:
                from .ai_service import analyze_with_gemini
                results = analyze_with_gemini(tasks_data)
                
            # Fallback to standard algorithm
            if not results:
                tasks_map = {t['id']: t for t in tasks_data}
                results = []
                for task in tasks_data:
                    score, explanation = calculate_score(task, tasks_map, strategy=strategy)
                    task_result = task.copy()
                    task_result['score'] = score
                    task_result['explanation'] = explanation
                    results.append(task_result)
            
            # 4. Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # 5. Persist to DB for "Suggest" feature compatibility
            # Wipe old data to keep state clean for this demo
            Task.objects.all().delete()
            
            id_map = {} 
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
                
            # Set dependencies
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
        Returns top 3 tasks based on current DB state using Smart Balance.
        """
        tasks = Task.objects.all()
        
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
            # Always use 'smart' strategy for general suggestions
            score, explanation = calculate_score(task, tasks_map, strategy='smart')
            task['score'] = score
            task['explanation'] = explanation
            results.append(task)
            
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return Response(results[:3])