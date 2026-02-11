from google.cloud import firestore
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from models import Task, DailyStat, ShoppingItem
from logic import calculate_priority

class TaskManagerCRUD:
    def __init__(self, project_id: Optional[str], database_id: str):
        self.db = firestore.Client(project=project_id, database=database_id)

    def get_all_tasks(self) -> List[Task]:
        tasks = []
        docs = self.db.collection('tasks').stream()
        for doc in docs:
            data = doc.to_dict()
            if 'difficulty' not in data:
                self.db.collection('tasks').document(doc.id).update({'difficulty': 1})
                data['difficulty'] = 1

            created_at = data.get('created_at')
            h = data.get('half_life', 7.0)
            p = calculate_priority(created_at, h) if isinstance(created_at, datetime) else 0.0
            
            tasks.append(Task(
                id=doc.id,
                name=data.get('name', 'Unnamed Task'),
                half_life=h,
                difficulty=data.get('difficulty', 1),
                is_recurrent=data.get('is_recurrent', False),
                created_at=created_at if isinstance(created_at, datetime) else datetime.now(timezone.utc),
                priority=p,
                hashtag=data.get('hashtag')
            ))
        
        tasks.sort(key=lambda x: x.priority, reverse=True)
        return tasks

    def add_task(self, name: str, half_life: float, difficulty: int, is_recurrent: bool, hashtag: Optional[str] = None):
        self.db.collection('tasks').add({
            'name': name,
            'half_life': half_life,
            'difficulty': difficulty,
            'is_recurrent': is_recurrent,
            'created_at': datetime.now(timezone.utc),
            'hashtag': hashtag
        })

    def update_task(self, task_id: str, name: str, half_life: float, difficulty: int, is_recurrent: bool, hashtag: Optional[str] = None):
        self.db.collection('tasks').document(task_id).update({
            'name': name,
            'half_life': half_life,
            'difficulty': difficulty,
            'is_recurrent': is_recurrent,
            'hashtag': hashtag
        })

    def complete_task(self, task_id: str):
        doc_ref = self.db.collection('tasks').document(task_id)
        doc = doc_ref.get()
        if not doc.exists: return False
            
        data = doc.to_dict()
        difficulty = data.get('difficulty', 1)
        now = datetime.now(timezone.utc)
        
        today_str = now.strftime('%Y-%m-%d')
        stats_ref = self.db.collection('daily_stats').document(today_str)
        stats_ref.set({'total_stars': firestore.Increment(difficulty)}, merge=True)
        
        self.db.collection('history').add({
            'name': data.get('name'),
            'difficulty': difficulty,
            'completed_at': now,
        })
        
        if data.get('is_recurrent'):
            doc_ref.update({'created_at': now})
        else:
            doc_ref.delete()
        return True

    def delete_task(self, task_id: str):
        self.db.collection('tasks').document(task_id).delete()

    def get_7_day_stats(self) -> List[DailyStat]:
        stats = []
        today = datetime.now(timezone.utc).date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            doc = self.db.collection('daily_stats').document(day_str).get()
            total = doc.to_dict().get('total_stars', 0) if doc.exists else 0
            total = doc.to_dict().get('total_stars', 0) if doc.exists else 0
            stats.append(DailyStat(date=day_str, total=total, day_name=day.strftime('%a')))
        return stats

    def get_shopping_items(self) -> List[ShoppingItem]:
        items = []
        now = datetime.now(timezone.utc)
        docs = self.db.collection('shopping_list').stream()
        for doc in docs:
            data = doc.to_dict()
            checked = data.get('checked', False)
            checked_at = data.get('checked_at')
            
            # Cleanup logic: delete if checked more than 24 hours ago
            if checked and isinstance(checked_at, datetime):
                if now - checked_at > timedelta(hours=24):
                    self.db.collection('shopping_list').document(doc.id).delete()
                    continue

            items.append(ShoppingItem(
                id=doc.id,
                name=data.get('name', 'Unnamed Item'),
                checked=checked,
                checked_at=checked_at
            ))
        return items

    def add_shopping_item(self, name: str):
        self.db.collection('shopping_list').add({
            'name': name,
            'checked': False,
            'checked_at': None
        })

    def toggle_shopping_item(self, item_id: str, checked: bool):
        update_data = {'checked': checked}
        if checked:
            update_data['checked_at'] = datetime.now(timezone.utc)
        else:
            update_data['checked_at'] = None
        self.db.collection('shopping_list').document(item_id).update(update_data)
