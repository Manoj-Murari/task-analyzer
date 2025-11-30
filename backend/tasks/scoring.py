from datetime import date

def calculate_score(task_data, all_tasks_map, strategy='smart'):
    """
    Calculates the priority score for a task based on the selected strategy.
    
    Args:
        task_data (dict): Dictionary containing task fields.
        all_tasks_map (dict): Map of task ID to task data.
        strategy (str): 'smart', 'fastest', 'impact', or 'deadline'.
        
    Returns:
        tuple: (score, explanation)
    """
    score = 0
    explanations = []
    
    # --- FACTOR 1: URGENCY (Due Date) ---
    today = date.today()
    due_date = task_data.get('due_date')
    if isinstance(due_date, str):
        due_date = date.fromisoformat(due_date)
        
    days_until_due = (due_date - today).days
    
    urgency_score = 0
    if days_until_due < 0:
        urgency_score = 100 + (abs(days_until_due) * 10)
        explanations.append(f"Overdue by {abs(days_until_due)} days")
    elif days_until_due == 0:
        urgency_score = 100
        explanations.append("Due today")
    elif days_until_due <= 3:
        urgency_score = 80 - (days_until_due * 10)
        explanations.append(f"Due soon ({days_until_due} days)")
    elif days_until_due <= 7:
        urgency_score = 40
        explanations.append("Due this week")
    else:
        urgency_score = max(0, 20 - (days_until_due // 2))
    
    # Strategy Adjustment for Urgency
    if strategy == 'deadline':
        urgency_score *= 1.5
        explanations.append("(Deadline Focus x1.5)")
    
    score += urgency_score

    # --- FACTOR 2: IMPORTANCE ---
    importance = task_data.get('importance', 1)
    
    # Strategy Adjustment for Importance
    if strategy == 'impact':
        importance_multiplier = 1 + (importance / 5) # Stronger multiplier (up to 3x)
        explanations.append(f"Importance {importance} (High Impact x{importance_multiplier:.1f})")
    elif strategy == 'fastest':
        importance_multiplier = 1 # Ignore importance mostly
    else:
        importance_multiplier = 1 + (importance / 10) # Standard (up to 2x)
        explanations.append(f"Importance {importance} (x{importance_multiplier:.1f})")
        
    score *= importance_multiplier
    
    # --- FACTOR 3: EFFORT (Quick Wins) ---
    hours = task_data.get('estimated_hours', 0)
    
    if hours > 0 and hours <= 2:
        bonus = 40 if strategy == 'fastest' else 20
        score += bonus
        explanations.append(f"Quick win (< 2h) (+{bonus})")
    elif hours > 10:
        penalty = 10
        score -= penalty
        explanations.append(f"High effort (> 10h) (-{penalty})")

    # --- FACTOR 4: DEPENDENCIES ---
    task_id = task_data.get('id')
    blocking_count = 0
    if task_id is not None:
        for other_task in all_tasks_map.values():
            if task_id in other_task.get('dependencies', []):
                blocking_count += 1
    
    if blocking_count > 0:
        dependency_bonus = blocking_count * 15
        score += dependency_bonus
        explanations.append(f"Blocks {blocking_count} tasks (+{dependency_bonus})")
        
    return round(score, 2), "; ".join(explanations)

def detect_circular_dependencies(tasks):
    """
    Detects circular dependencies in a list of tasks.
    Returns a list of error messages.
    """
    errors = []
    # Build adjacency list: key depends on values
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
            # Only recurse if the neighbor is actually in our task list
            if neighbor in adj:
                if visit(neighbor):
                    return True
            
        path.remove(node)
        return False

    for task in tasks:
        if visit(task['id']):
            errors.append(f"Circular dependency detected involving task {task['id']}")
            # We break after one cycle to avoid spamming errors for the same cycle
            break 
            
    return errors