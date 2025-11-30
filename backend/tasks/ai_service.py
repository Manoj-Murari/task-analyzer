import os
import google.generativeai as genai
import json

def analyze_with_gemini(tasks_data):
    """
    Uses Google Gemini API to prioritize tasks and provide insights.
    
    Args:
        tasks_data (list): List of task dictionaries.
        
    Returns:
        list: List of tasks with 'score' and 'explanation' updated by AI.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found. Falling back to standard algorithm.")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    You are an expert project manager. I have a list of tasks. 
    Please analyze them and assign a priority score (0-100) and a brief, insightful explanation for each.
    Consider urgency, importance, effort, and dependencies.
    
    Tasks:
    {json.dumps(tasks_data, default=str)}
    
    Return ONLY a valid JSON array of objects with the following structure, and NO other text:
    [
        {{
            "id": <task_id>,
            "score": <number>,
            "explanation": "<string>"
        }}
    ]
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up potential markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        ai_results = json.loads(response_text)
        
        # Merge AI results back into original tasks
        result_map = {r['id']: r for r in ai_results}
        
        merged_tasks = []
        for task in tasks_data:
            task_id = task.get('id')
            if task_id in result_map:
                ai_res = result_map[task_id]
                task['score'] = ai_res.get('score', 0)
                task['explanation'] = "✨ AI Insight: " + ai_res.get('explanation', '')
            else:
                task['score'] = 0
                task['explanation'] = "AI could not analyze this task."
            merged_tasks.append(task)
            
        return merged_tasks

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None
