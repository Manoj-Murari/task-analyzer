from datetime import date

def calculate_score(task_data, all_tasks_map):
    """
    Calculates the priority score for a task.
    
    Args:
        task_data (dict): Dictionary containing task fields.
        all_tasks_map (dict): Map of task ID (or temporary ID) to task data.
        
    Returns:
        tuple: (score, explanation)
    """
    score = 0
    explanations = []
    
    # 1. Urgency (Due Date)
    today = date.today()
    due_date = task_data.get('due_date')
    if isinstance(due_date, str):
        due_date = date.fromisoformat(due_date)
        
    days_until_due = (due_date - today).days
    
    if days_until_due < 0:
        urgency_score = 100 + (abs(days_until_due) * 10)
        explanations.append(f"Overdue by {abs(days_until_due)} days (+{urgency_score})")
    elif days_until_due == 0:
        urgency_score = 100
        explanations.append("Due today (+100)")
    elif days_until_due <= 3:
        urgency_score = 80 - (days_until_due * 10)
        explanations.append(f"Due soon ({days_until_due} days) (+{urgency_score})")
    elif days_until_due <= 7:
        urgency_score = 40
        explanations.append("Due this week (+40)")
    else:
        urgency_score = max(0, 20 - (days_until_due // 2))
        explanations.append(f"Due in {days_until_due} days (+{urgency_score})")
        
    score += urgency_score
    
    # 2. Importance
    importance = task_data.get('importance', 1)
    importance_multiplier = 1 + (importance / 10)
    score *= importance_multiplier
    explanations.append(f"Importance {importance} (x{importance_multiplier:.1f})")
    
    # 3. Effort (Quick Wins)
    hours = task_data.get('estimated_hours', 0)
    if hours > 0 and hours <= 2:
        score += 20
        explanations.append("Quick win (< 2h) (+20)")
    elif hours > 10:
        score -= 10
        explanations.append("High effort (> 10h) (-10)")
        
    # 4. Dependencies (Blocking others)
    # We need to know how many tasks depend on THIS task.
    # In the input `all_tasks_map`, we can check who lists this task ID in their `dependencies`.
    task_id = task_data.get('id')
    blocking_count = 0
    if task_id is not None:
        for other_task in all_tasks_map.values():
            if task_id in other_task.get('dependencies', []):
                blocking_count += 1
    
    if blocking_count > 0:
        dependency_bonus = blocking_count * 15
        score += dependency_bonus
        explanations.append(f"Blocks {blocking_count} other tasks (+{dependency_bonus})")
        
    return round(score, 2), "; ".join(explanations)

def detect_circular_dependencies(tasks):
    """
    Detects circular dependencies in a list of tasks.
    Returns a list of error messages.
    """
    errors = []
    adj = {t['id']: t.get('dependencies', []) for t in tasks}
    visited = set()
    path = set()
    
    def visit(node):
        if node in path:
            return True # Cycle detected
        if node in visited:
            return False
        
        visited.add(node)
        path.add(node)
        
        for neighbor in adj.get(node, []):
            if neighbor in adj: # Only check if neighbor exists in current set
                if visit(neighbor):
                    return True
            
        path.remove(node)
        return False

    for task in tasks:
        if visit(task['id']):
            errors.append(f"Circular dependency detected involving task {task['id']}")
            # Clear visited/path to find other cycles? 
            # Simple DFS finds one cycle per component usually.
            # We just return generic error for now or specific one.
            break 
            
    return errors
