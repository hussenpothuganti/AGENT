"""
Enhanced Conversation Model for ZYEON AI
Provides comprehensive conversation management with MongoDB integration
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class ConversationModel:
    """Enhanced conversation model with full CRUD operations"""
    
    def __init__(self, db_client: MongoClient):
        self.db = db_client.zyeon_ai
        self.conversations = self.db.conversations
        self.users = self.db.users
        self.sessions = self.db.sessions
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Conversation indexes
            self.conversations.create_index([("conversation_id", ASCENDING)])
            self.conversations.create_index([("user_id", ASCENDING)])
            self.conversations.create_index([("timestamp", DESCENDING)])
            self.conversations.create_index([("session_id", ASCENDING)])
            
            # User indexes
            self.users.create_index([("user_id", ASCENDING)], unique=True)
            self.users.create_index([("email", ASCENDING)], unique=True, sparse=True)
            
            # Session indexes
            self.sessions.create_index([("session_id", ASCENDING)], unique=True)
            self.sessions.create_index([("user_id", ASCENDING)])
            self.sessions.create_index([("created_at", DESCENDING)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def create_conversation(self, 
                          user_message: str, 
                          ai_response: str,
                          user_id: str = "anonymous",
                          conversation_id: Optional[str] = None,
                          session_id: Optional[str] = None,
                          message_type: str = "text",
                          metadata: Optional[Dict] = None) -> str:
        """Create a new conversation entry"""
        try:
            conversation_data = {
                "conversation_id": conversation_id or f"conv_{int(datetime.now().timestamp())}",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc),
                "user_message": user_message,
                "ai_response": ai_response,
                "message_type": message_type,  # text, voice, image, etc.
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = self.conversations.insert_one(conversation_data)
            logger.info(f"Conversation saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise
    
    def get_conversation_history(self, 
                               user_id: str = None,
                               conversation_id: str = None,
                               session_id: str = None,
                               limit: int = 50,
                               offset: int = 0) -> List[Dict]:
        """Get conversation history with filtering options"""
        try:
            query = {}
            
            if user_id:
                query["user_id"] = user_id
            if conversation_id:
                query["conversation_id"] = conversation_id
            if session_id:
                query["session_id"] = session_id
            
            conversations = list(
                self.conversations.find(query, {"_id": 0})
                .sort("timestamp", DESCENDING)
                .skip(offset)
                .limit(limit)
            )
            
            # Convert datetime objects to ISO strings for JSON serialization
            for conv in conversations:
                if "timestamp" in conv:
                    conv["timestamp"] = conv["timestamp"].isoformat()
                if "created_at" in conv:
                    conv["created_at"] = conv["created_at"].isoformat()
                if "updated_at" in conv:
                    conv["updated_at"] = conv["updated_at"].isoformat()
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def get_conversation_stats(self, user_id: str = None) -> Dict:
        """Get conversation statistics"""
        try:
            pipeline = []
            
            if user_id:
                pipeline.append({"$match": {"user_id": user_id}})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_conversations": {"$sum": 1},
                        "total_messages": {"$sum": 2},  # user + ai message
                        "voice_messages": {
                            "$sum": {"$cond": [{"$eq": ["$message_type", "voice"]}, 1, 0]}
                        },
                        "text_messages": {
                            "$sum": {"$cond": [{"$eq": ["$message_type", "text"]}, 1, 0]}
                        },
                        "first_conversation": {"$min": "$timestamp"},
                        "last_conversation": {"$max": "$timestamp"}
                    }
                }
            ])
            
            result = list(self.conversations.aggregate(pipeline))
            
            if result:
                stats = result[0]
                # Convert datetime objects to ISO strings
                if "first_conversation" in stats and stats["first_conversation"]:
                    stats["first_conversation"] = stats["first_conversation"].isoformat()
                if "last_conversation" in stats and stats["last_conversation"]:
                    stats["last_conversation"] = stats["last_conversation"].isoformat()
                return stats
            else:
                return {
                    "total_conversations": 0,
                    "total_messages": 0,
                    "voice_messages": 0,
                    "text_messages": 0,
                    "first_conversation": None,
                    "last_conversation": None
                }
                
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {}
    
    def create_user(self, user_id: str, email: str = None, name: str = None, metadata: Dict = None) -> str:
        """Create a new user"""
        try:
            user_data = {
                "user_id": user_id,
                "email": email,
                "name": name or "Anonymous User",
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_active": datetime.now(timezone.utc)
            }
            
            result = self.users.insert_one(user_data)
            logger.info(f"User created with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            user = self.users.find_one({"user_id": user_id}, {"_id": 0})
            if user:
                # Convert datetime objects to ISO strings
                for field in ["created_at", "updated_at", "last_active"]:
                    if field in user and user[field]:
                        user[field] = user[field].isoformat()
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_activity(self, user_id: str):
        """Update user's last activity timestamp"""
        try:
            self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "last_active": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
    
    def create_session(self, user_id: str, session_id: str, metadata: Dict = None) -> str:
        """Create a new session"""
        try:
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "is_active": True
            }
            
            result = self.sessions.insert_one(session_data)
            logger.info(f"Session created with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def end_session(self, session_id: str):
        """End a session"""
        try:
            self.sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "is_active": False,
                        "ended_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            logger.info(f"Session ended: {session_id}")
        except Exception as e:
            logger.error(f"Error ending session: {e}")
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Clean up conversations older than specified days"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            result = self.conversations.delete_many({"timestamp": {"$lt": cutoff_date}})
            logger.info(f"Cleaned up {result.deleted_count} old conversations")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up conversations: {e}")
            return 0

