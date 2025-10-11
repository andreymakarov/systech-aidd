"""Unit tests for ConversationManager"""

from bot.conversation import ConversationManager


def test_get_history_empty() -> None:
    """Пустая история для нового пользователя"""
    manager = ConversationManager()
    history = manager.get_history(user_id=123)
    assert history == []


def test_add_message() -> None:
    """Добавление одного сообщения в историю"""
    manager = ConversationManager()
    manager.add_message(user_id=123, role="user", content="Hello")
    
    history = manager.get_history(user_id=123)
    assert len(history) == 1
    assert history[0] == {"role": "user", "content": "Hello"}


def test_add_multiple_messages() -> None:
    """Добавление нескольких сообщений в историю"""
    manager = ConversationManager()
    
    manager.add_message(user_id=123, role="user", content="Hello")
    manager.add_message(user_id=123, role="assistant", content="Hi!")
    manager.add_message(user_id=123, role="user", content="How are you?")
    
    history = manager.get_history(user_id=123)
    assert len(history) == 3
    assert history[0] == {"role": "user", "content": "Hello"}
    assert history[1] == {"role": "assistant", "content": "Hi!"}
    assert history[2] == {"role": "user", "content": "How are you?"}


def test_clear_history() -> None:
    """Очистка истории диалога пользователя"""
    manager = ConversationManager()
    
    # Добавляем сообщения
    manager.add_message(user_id=123, role="user", content="Hello")
    manager.add_message(user_id=123, role="assistant", content="Hi!")
    assert len(manager.get_history(user_id=123)) == 2
    
    # Очищаем историю
    manager.clear_history(user_id=123)
    history = manager.get_history(user_id=123)
    assert history == []


def test_multiple_users() -> None:
    """Изоляция истории между разными пользователями"""
    manager = ConversationManager()
    
    # Пользователь 1
    manager.add_message(user_id=111, role="user", content="Message from user 1")
    
    # Пользователь 2
    manager.add_message(user_id=222, role="user", content="Message from user 2")
    
    # Проверяем изоляцию
    history_1 = manager.get_history(user_id=111)
    history_2 = manager.get_history(user_id=222)
    
    assert len(history_1) == 1
    assert len(history_2) == 1
    assert history_1[0]["content"] == "Message from user 1"
    assert history_2[0]["content"] == "Message from user 2"
    
    # Очищаем историю одного пользователя
    manager.clear_history(user_id=111)
    assert len(manager.get_history(user_id=111)) == 0
    assert len(manager.get_history(user_id=222)) == 1  # Второй пользователь не затронут

