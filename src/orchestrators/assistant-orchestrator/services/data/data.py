from data.chat_history_manager import ChatHistoryManager
from data.context_manager import ContextManager
from data.impl.dynamo_chat_history_manager import DynamoChatHistoryManager
from data.impl.dynamo_context_manager import DynamoContextManager
from data.impl.dynamo_ticket_manager import DynamoTicketManager
from data.ticket_manager import TicketManager


def get_chat_history_manager() -> ChatHistoryManager:
    return DynamoChatHistoryManager()


def get_ticket_manager() -> TicketManager:
    return DynamoTicketManager()


def get_context_manager() -> ContextManager:
    return DynamoContextManager()
