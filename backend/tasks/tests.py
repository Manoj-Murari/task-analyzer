from django.test import TestCase
from datetime import date, timedelta
from .scoring import calculate_score, detect_circular_dependencies

class ScoringTests(TestCase):
    def test_urgency_score(self):
        today = date.today()
        
        # Test 1: Due today
        task_today = {'id': 1, 'due_date': today, 'importance': 1, 'estimated_hours': 5}
        score, _ = calculate_score(task_today, {1: task_today})
        # 100 (urgency) * 1.1 (importance) = 110
        self.assertEqual(score, 110)
        
        # Test 2: Overdue
        task_overdue = {'id': 2, 'due_date': today - timedelta(days=2), 'importance': 1, 'estimated_hours': 5}
        score, _ = calculate_score(task_overdue, {2: task_overdue})
        # (100 + 20) * 1.1 = 132
        self.assertEqual(score, 132)
        
    def test_quick_win(self):
        today = date.today()
        # Due in 10 days (score 15), Importance 1 (x1.1), Quick win (+20)
        # Urgency: 20 - (10//2) = 15
        # Base: 15 * 1.1 = 16.5
        # +20 = 36.5
        task = {'id': 1, 'due_date': today + timedelta(days=10), 'importance': 1, 'estimated_hours': 1}
        score, _ = calculate_score(task, {1: task})
        self.assertEqual(score, 36.5)

    def test_dependency_boost(self):
        today = date.today()
        # Task 1 blocks Task 2
        task1 = {'id': 1, 'due_date': today + timedelta(days=10), 'importance': 1, 'estimated_hours': 5}
        task2 = {'id': 2, 'due_date': today + timedelta(days=10), 'importance': 1, 'estimated_hours': 5, 'dependencies': [1]}
        
        tasks_map = {1: task1, 2: task2}
        
        # Task 1 score:
        # Urgency: 15
        # Importance: x1.1 => 16.5
        # Dependency Bonus: 1 * 15 = +15
        # Total: 31.5
        score1, _ = calculate_score(task1, tasks_map)
        self.assertEqual(score1, 31.5)

class CircularDependencyTests(TestCase):
    def test_no_cycle(self):
        tasks = [
            {'id': 1, 'dependencies': []},
            {'id': 2, 'dependencies': [1]}
        ]
        self.assertEqual(detect_circular_dependencies(tasks), [])
        
    def test_simple_cycle(self):
        tasks = [
            {'id': 1, 'dependencies': [2]},
            {'id': 2, 'dependencies': [1]}
        ]
        errors = detect_circular_dependencies(tasks)
        self.assertTrue(len(errors) > 0)
        self.assertIn("Circular dependency detected", errors[0])
        
    def test_self_cycle(self):
        tasks = [
            {'id': 1, 'dependencies': [1]}
        ]
        errors = detect_circular_dependencies(tasks)
        self.assertTrue(len(errors) > 0)
