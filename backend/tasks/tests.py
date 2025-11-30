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
        
    def test_quick_win_strategy(self):
        today = date.today()
        # Task: Low importance, but quick (1h)
        task = {'id': 1, 'due_date': today + timedelta(days=10), 'importance': 1, 'estimated_hours': 1}
        
        # Smart Balance Strategy (Default)
        # Urgency: 15, Imp: x1.1, Bonus: +20 => (15*1.1) + 20 = 36.5
        score_smart, _ = calculate_score(task, {1: task}, strategy='smart')
        self.assertEqual(score_smart, 36.5)

        # Fastest Wins Strategy
        # Urgency: 15, Imp: x1.0 (ignored), Bonus: +40 => 15 + 40 = 55
        score_fast, _ = calculate_score(task, {1: task}, strategy='fastest')
        self.assertEqual(score_fast, 55)

    def test_circular_dependency(self):
        tasks = [
            {'id': 1, 'dependencies': [2]},
            {'id': 2, 'dependencies': [1]}
        ]
        errors = detect_circular_dependencies(tasks)
        self.assertTrue(len(errors) > 0)
        self.assertIn("Circular dependency", errors[0])