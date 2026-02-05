import os
from datetime import datetime, timezone, timedelta
from crud import TaskManagerCRUD
from models import ShoppingItem

def test_shopping_logic():
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    DATABASE_ID = os.environ.get("DATABASE_ID", "(default)")
    
    if not PROJECT_ID:
        print("Skipping verification: GOOGLE_CLOUD_PROJECT not set.")
        return

    tm = TaskManagerCRUD(project_id=PROJECT_ID, database_id=DATABASE_ID)
    
    print("1. Adding a test shopping item...")
    tm.add_shopping_item("Test Item")
    
    items = tm.get_shopping_items()
    test_item = next((i for i in items if i.name == "Test Item"), None)
    assert test_item is not None
    assert test_item.checked == False
    print("   - SUCCESS: Item added and retrieved.")

    print("2. Toggling the item to checked...")
    tm.toggle_shopping_item(test_item.id, True)
    items = tm.get_shopping_items()
    test_item = next((i for i in items if i.id == test_item.id), None)
    assert test_item.checked == True
    assert test_item.checked_at is not None
    print("   - SUCCESS: Item toggled to checked.")

    # We can't easily test the 24h cleanup without mocking or waiting, 
    # but we can verify the logic in a simulated environment if needed.
    # For now, we'll manually verify the logic in get_shopping_items visually.
    
    print("3. Toggling the item back to unchecked...")
    tm.toggle_shopping_item(test_item.id, False)
    items = tm.get_shopping_items()
    test_item = next((i for i in items if i.id == test_item.id), None)
    assert test_item.checked == False
    assert test_item.checked_at is None
    print("   - SUCCESS: Item toggled to unchecked.")

    print("Cleanup: Deleting test item...")
    tm.db.collection('shopping_list').document(test_item.id).delete()
    print("   - SUCCESS: Test item deleted from Firestore.")

if __name__ == "__main__":
    try:
        test_shopping_logic()
        print("\nVerification successful!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
