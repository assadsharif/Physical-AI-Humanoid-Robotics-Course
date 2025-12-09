"""
Database seed script for Phase 1 test data.

Creates:
- 3 test users (student, educator, admin)
- 2 modules (ROS 2, Digital Twin) with 5 chapters each
- Test embeddings for vector search
- Sample chat messages
- Progress tracking records

Run: python scripts/seed_data.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from src.db import (
    AsyncSessionLocal,
    User,
    UserProfile,
    Module,
    Chapter,
    Embedding,
    ChapterProgress,
    ChatMessage,
)
from src.config import settings


async def seed_database():
    """Seed database with test data."""

    async with AsyncSessionLocal() as session:
        try:
            print("🌱 Starting database seeding...")

            # ============================================
            # 1. CREATE TEST USERS
            # ============================================
            print("\n📝 Creating test users...")

            user1 = User(
                id=str(uuid.uuid4()),
                email="student@example.com",
                password_hash="$2b$12$dummy_hash",  # Dummy hash - don't use in production!
                name="Ahmed Ali",
                is_active=True,
                is_admin=False,
                language_preference="en",
                theme="light",
            )

            user2 = User(
                id=str(uuid.uuid4()),
                email="educator@example.com",
                password_hash="$2b$12$dummy_hash",
                name="Dr. Sarah Khan",
                is_active=True,
                is_admin=False,
                language_preference="en",
                theme="light",
            )

            user3 = User(
                id=str(uuid.uuid4()),
                email="admin@example.com",
                password_hash="$2b$12$dummy_hash",
                name="Admin User",
                is_active=True,
                is_admin=True,
                language_preference="en",
                theme="dark",
            )

            session.add_all([user1, user2, user3])
            await session.flush()  # Flush to get IDs

            print(f"✅ Created 3 users: {user1.name}, {user2.name}, {user3.name}")

            # ============================================
            # 2. CREATE USER PROFILES
            # ============================================
            print("\n👤 Creating user profiles...")

            profile1 = UserProfile(
                id=str(uuid.uuid4()),
                user_id=user1.id,
                bio="Robotics enthusiast learning ROS 2",
                avatar_url="https://example.com/avatar1.jpg",
                organization="Tech University",
                country="Pakistan",
                email_notifications=True,
            )

            profile2 = UserProfile(
                id=str(uuid.uuid4()),
                user_id=user2.id,
                bio="Associate Professor in Robotics",
                avatar_url="https://example.com/avatar2.jpg",
                organization="Tech University",
                country="Pakistan",
                email_notifications=True,
            )

            profile3 = UserProfile(
                id=str(uuid.uuid4()),
                user_id=user3.id,
                bio="Platform administrator",
                avatar_url=None,
                organization="AI Native Textbook",
                country="Global",
                email_notifications=False,
            )

            session.add_all([profile1, profile2, profile3])
            await session.flush()

            print(f"✅ Created 3 user profiles")

            # ============================================
            # 3. CREATE MODULES
            # ============================================
            print("\n📚 Creating modules...")

            module1 = Module(
                id=str(uuid.uuid4()),
                slug="ros2",
                title="ROS 2 Fundamentals",
                description="Master the Robot Operating System 2 framework, pub/sub architecture, and core concepts.",
                order=1,
                is_published=True,
                published_at=datetime.utcnow(),
            )

            module2 = Module(
                id=str(uuid.uuid4()),
                slug="digital-twin",
                title="Digital Twin & Simulation",
                description="Learn simulation, Gazebo, and digital twin concepts for robotics.",
                order=2,
                is_published=True,
                published_at=datetime.utcnow(),
            )

            session.add_all([module1, module2])
            await session.flush()

            print(f"✅ Created 2 modules: {module1.title}, {module2.title}")

            # ============================================
            # 4. CREATE CHAPTERS
            # ============================================
            print("\n📖 Creating chapters...")

            # ROS 2 Chapters
            ros2_chapters = [
                {
                    "slug": "2.1",
                    "title": "ROS 2 Architecture Overview",
                    "description": "Understand the middleware, publisher-subscriber pattern, and node communication.",
                    "difficulty": "beginner",
                    "duration": 60,
                },
                {
                    "slug": "2.2",
                    "title": "Creating Your First Node",
                    "description": "Write, compile, and run your first ROS 2 Python node.",
                    "difficulty": "beginner",
                    "duration": 90,
                },
                {
                    "slug": "2.3",
                    "title": "Publishers and Subscribers",
                    "description": "Master pub/sub communication patterns and message passing.",
                    "difficulty": "intermediate",
                    "duration": 75,
                },
                {
                    "slug": "2.4",
                    "title": "Services and Actions",
                    "description": "Request-response and long-running task patterns in ROS 2.",
                    "difficulty": "intermediate",
                    "duration": 90,
                },
                {
                    "slug": "2.5",
                    "title": "Launch Files and Parameters",
                    "description": "Manage complex multi-node systems with launch files and dynamic parameters.",
                    "difficulty": "intermediate",
                    "duration": 60,
                },
            ]

            # Digital Twin Chapters
            dt_chapters = [
                {
                    "slug": "3.1",
                    "title": "Simulation Fundamentals",
                    "description": "Introduction to physics simulation and digital twins.",
                    "difficulty": "intermediate",
                    "duration": 75,
                },
                {
                    "slug": "3.2",
                    "title": "Gazebo Simulator Setup",
                    "description": "Install, configure, and use Gazebo for robot simulation.",
                    "difficulty": "intermediate",
                    "duration": 90,
                },
                {
                    "slug": "3.3",
                    "title": "Creating Robot Models",
                    "description": "Design URDF models and import them into simulation.",
                    "difficulty": "advanced",
                    "duration": 120,
                },
                {
                    "slug": "3.4",
                    "title": "Physics and Sensors",
                    "description": "Configure physics engines, sensors, and sensor simulation.",
                    "difficulty": "advanced",
                    "duration": 120,
                },
                {
                    "slug": "3.5",
                    "title": "Digital Twin Integration",
                    "description": "Connect real robots with their digital twins.",
                    "difficulty": "advanced",
                    "duration": 150,
                },
            ]

            chapter_list = []

            for idx, ch_data in enumerate(ros2_chapters, 1):
                chapter = Chapter(
                    id=str(uuid.uuid4()),
                    module_id=module1.id,
                    slug=ch_data["slug"],
                    title=ch_data["title"],
                    description=ch_data["description"],
                    order=idx,
                    difficulty_level=ch_data["difficulty"],
                    estimated_duration_minutes=ch_data["duration"],
                    is_published=True,
                    published_at=datetime.utcnow(),
                )
                chapter_list.append(chapter)
                session.add(chapter)

            for idx, ch_data in enumerate(dt_chapters, 1):
                chapter = Chapter(
                    id=str(uuid.uuid4()),
                    module_id=module2.id,
                    slug=ch_data["slug"],
                    title=ch_data["title"],
                    description=ch_data["description"],
                    order=idx,
                    difficulty_level=ch_data["difficulty"],
                    estimated_duration_minutes=ch_data["duration"],
                    is_published=True,
                    published_at=datetime.utcnow(),
                )
                chapter_list.append(chapter)
                session.add(chapter)

            await session.flush()
            print(f"✅ Created 10 chapters (5 per module)")

            # ============================================
            # 5. CREATE EMBEDDINGS
            # ============================================
            print("\n🧬 Creating embeddings for vector search...")

            embedding_count = 0
            for chapter in chapter_list:
                # Create 10 dummy embeddings per chapter
                sample_content = [
                    f"Introduction to {chapter.title}",
                    f"Key concepts in {chapter.title}",
                    f"Best practices for {chapter.title}",
                    f"Code examples for {chapter.title}",
                    f"Common mistakes in {chapter.title}",
                    f"Advanced topics in {chapter.title}",
                    f"Exercises for {chapter.title}",
                    f"FAQs about {chapter.title}",
                    f"Real-world applications of {chapter.title}",
                    f"Troubleshooting {chapter.title}",
                ]

                for chunk_idx, content in enumerate(sample_content):
                    embedding = Embedding(
                        id=str(uuid.uuid4()),
                        chapter_id=chapter.id,
                        content=content,
                        chunk_index=chunk_idx,
                        embedding_model="text-embedding-3-small",
                        qdrant_point_id=None,  # Will be set when synced to Qdrant
                    )
                    session.add(embedding)
                    embedding_count += 1

            await session.flush()
            print(f"✅ Created {embedding_count} embeddings (10 per chapter)")

            # ============================================
            # 6. CREATE CHAPTER PROGRESS
            # ============================================
            print("\n📊 Creating chapter progress records...")

            progress_count = 0

            # Student completed first 3 chapters
            for i, chapter in enumerate(chapter_list[:3]):
                progress = ChapterProgress(
                    id=str(uuid.uuid4()),
                    user_id=user1.id,
                    chapter_id=chapter.id,
                    status="completed",
                    progress_percentage=100,
                    time_spent_seconds=3600 + (i * 1200),  # Varying times
                    quiz_score=85 + (i * 2),
                    quiz_passed=True,
                    exercise_passed=True,
                    started_at=datetime.utcnow() - timedelta(days=10 - i),
                    completed_at=datetime.utcnow() - timedelta(days=9 - i),
                )
                session.add(progress)
                progress_count += 1

            # Student in progress on chapter 4
            progress = ChapterProgress(
                id=str(uuid.uuid4()),
                user_id=user1.id,
                chapter_id=chapter_list[3].id,
                status="in_progress",
                progress_percentage=45,
                time_spent_seconds=2700,
                quiz_score=None,
                quiz_passed=False,
                exercise_passed=False,
                started_at=datetime.utcnow() - timedelta(days=2),
            )
            session.add(progress)
            progress_count += 1

            # Educator reviewed all chapters
            for chapter in chapter_list:
                progress = ChapterProgress(
                    id=str(uuid.uuid4()),
                    user_id=user2.id,
                    chapter_id=chapter.id,
                    status="completed",
                    progress_percentage=100,
                    time_spent_seconds=5400,
                    quiz_score=98,
                    quiz_passed=True,
                    exercise_passed=True,
                    started_at=datetime.utcnow() - timedelta(days=30),
                    completed_at=datetime.utcnow() - timedelta(days=28),
                )
                session.add(progress)
                progress_count += 1

            await session.flush()
            print(f"✅ Created {progress_count} progress records")

            # ============================================
            # 7. CREATE CHAT MESSAGES
            # ============================================
            print("\n💬 Creating sample chat messages...")

            sample_queries = [
                ("What is a ROS 2 topic?", "A topic is a named bus..."),
                ("How do I create a node?", "You need to import rclpy..."),
                ("Explain the pub/sub pattern", "Publisher sends messages to subscribers..."),
                ("What's the difference between services and topics?", "Services are request-response..."),
                ("How do I debug my node?", "Use rclpy logging or print statements..."),
            ]

            chat_count = 0
            for query, response in sample_queries:
                message = ChatMessage(
                    id=str(uuid.uuid4()),
                    user_id=user1.id,
                    query=query,
                    response=response,
                    intent="explain",
                    context_chapter_id=chapter_list[0].id,
                    context_module_slug="ros2",
                    user_difficulty_level="beginner",
                    sources=f'[{{"chapter_id": "{chapter_list[0].id}", "title": "{chapter_list[0].title}"}}]',
                    user_rating=None,
                    created_at=datetime.utcnow() - timedelta(hours=5),
                )
                session.add(message)
                chat_count += 1

            await session.flush()
            print(f"✅ Created {chat_count} sample chat messages")

            # ============================================
            # COMMIT TRANSACTION
            # ============================================
            await session.commit()
            print("\n✅ Database seeding completed successfully!")
            print(f"\nSummary:")
            print(f"  • 3 users created")
            print(f"  • 2 modules created")
            print(f"  • 10 chapters created")
            print(f"  • {embedding_count} embeddings created")
            print(f"  • {progress_count} progress records created")
            print(f"  • {chat_count} chat messages created")
            print(f"\nTest Credentials:")
            print(f"  Student: student@example.com")
            print(f"  Educator: educator@example.com")
            print(f"  Admin: admin@example.com")
            print(f"\nNote: These are test accounts with dummy passwords.")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
            raise


async def main():
    """Main entry point."""
    print(f"🗄️  Database URL: {settings.DATABASE_URL}")
    print(f"Environment: {settings.ENVIRONMENT}")

    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
