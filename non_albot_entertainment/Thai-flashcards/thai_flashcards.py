#!/usr/bin/env python3
"""
Thai Flashcard Learning System
A spaced repetition flashcard app for learning Thai words
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys


class ThaiFlashcards:
    def __init__(self, db_path="thai_flashcards.db"):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Words table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thai TEXT NOT NULL UNIQUE,
                english TEXT NOT NULL,
                times_shown INTEGER DEFAULT 0,
                times_correct INTEGER DEFAULT 0,
                times_incorrect INTEGER DEFAULT 0,
                last_shown TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Learning history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                was_correct BOOLEAN NOT NULL,
                mode TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_id) REFERENCES words (id)
            )
        """)
        
        self.conn.commit()
    
    def import_words_from_json(self, json_path):
        """Import words from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            words_data = json.load(f)
        
        cursor = self.conn.cursor()
        imported = 0
        
        for word in words_data:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO words (thai, english)
                    VALUES (?, ?)
                """, (word['thai'], word['english']))
                if cursor.rowcount > 0:
                    imported += 1
            except Exception as e:
                print(f"Error importing word {word}: {e}")
        
        self.conn.commit()
        return imported
    
    def calculate_word_priority(self, word):
        """Calculate priority score for word selection (higher = more likely to show)"""
        times_shown = word['times_shown']
        times_correct = word['times_correct']
        times_incorrect = word['times_incorrect']
        last_shown = word['last_shown']
        
        # New words get medium priority
        if times_shown == 0:
            return 50
        
        # Calculate error rate
        total_attempts = times_correct + times_incorrect
        if total_attempts == 0:
            error_rate = 0
        else:
            error_rate = times_incorrect / total_attempts
        
        # Base priority on error rate (0-100)
        priority = error_rate * 100
        
        # Boost priority for words not seen recently
        if last_shown:
            last_shown_date = datetime.fromisoformat(last_shown)
            days_since = (datetime.now() - last_shown_date).days
            priority += min(days_since * 5, 50)  # Up to 50 bonus points
        else:
            priority += 30  # Never seen before gets boost
        
        # Cap priority at reasonable max
        return min(priority, 150)
    
    def select_words_for_session(self, count=15):
        """Select words for practice session using weighted random selection"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM words")
        all_words = cursor.fetchall()
        
        if len(all_words) == 0:
            return []
        
        if len(all_words) <= count:
            return all_words
        
        # Calculate priorities
        word_priorities = []
        for word in all_words:
            priority = self.calculate_word_priority(word)
            word_priorities.append((word, priority))
        
        # Weighted random selection
        selected = []
        for _ in range(count):
            if not word_priorities:
                break
            
            total_priority = sum(p for _, p in word_priorities)
            rand_val = random.uniform(0, total_priority)
            
            cumulative = 0
            for i, (word, priority) in enumerate(word_priorities):
                cumulative += priority
                if rand_val <= cumulative:
                    selected.append(word)
                    word_priorities.pop(i)
                    break
        
        return selected
    
    def record_answer(self, word_id, was_correct, mode):
        """Record answer and update word statistics"""
        cursor = self.conn.cursor()
        
        # Update word statistics
        if was_correct:
            cursor.execute("""
                UPDATE words 
                SET times_shown = times_shown + 1,
                    times_correct = times_correct + 1,
                    last_shown = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), word_id))
        else:
            cursor.execute("""
                UPDATE words 
                SET times_shown = times_shown + 1,
                    times_incorrect = times_incorrect + 1,
                    last_shown = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), word_id))
        
        # Record in history
        cursor.execute("""
            INSERT INTO learning_history (word_id, was_correct, mode)
            VALUES (?, ?, ?)
        """, (word_id, was_correct, mode))
        
        self.conn.commit()
    
    def fuzzy_match(self, answer, correct):
        """Simple fuzzy matching for user answers"""
        answer = answer.strip().lower()
        correct = correct.strip().lower()
        
        # Exact match
        if answer == correct:
            return True
        
        # Check if answer is in comma-separated alternatives
        correct_options = [opt.strip() for opt in correct.split(',')]
        if answer in correct_options:
            return True
        
        # Check if any option is in answer (for partial credit)
        for opt in correct_options:
            if opt and opt in answer:
                return True
        
        return False
    
    def mode_thai_to_english(self):
        """Practice mode: Thai word shown, user types English"""
        print("\n" + "="*50)
        print("MODE: Thai → English (Reading Practice)")
        print("="*50)
        print("Read the Thai word and type the English translation.")
        print("Type 'quit' to return to main menu.\n")
        
        words = self.select_words_for_session()
        if not words:
            print("No words available. Please import words first.")
            return
        
        correct_count = 0
        total_count = len(words)
        
        for i, word in enumerate(words, 1):
            print(f"\nWord {i}/{total_count}")
            print(f"Thai: {word['thai']}")
            print("-" * 30)
            
            answer = input("English: ").strip()
            
            if answer.lower() == 'quit':
                print("\nReturning to main menu...")
                break
            
            is_correct = self.fuzzy_match(answer, word['english'])
            
            if is_correct:
                print("✓ Correct!")
                correct_count += 1
                self.record_answer(word['id'], True, 'thai_to_english')
            else:
                print(f"✗ Incorrect. The answer is: {word['english']}")
                self.record_answer(word['id'], False, 'thai_to_english')
        
        # Session summary
        if total_count > 0:
            accuracy = (correct_count / total_count) * 100
            print("\n" + "="*50)
            print("SESSION COMPLETE")
            print("="*50)
            print(f"Correct: {correct_count}/{total_count} ({accuracy:.1f}%)")
            print("="*50)
    
    def mode_english_to_thai(self):
        """Practice mode: English word shown, user writes Thai"""
        print("\n" + "="*50)
        print("MODE: English → Thai (Writing Practice)")
        print("="*50)
        print("Write the Thai translation by hand, then press Enter to check.")
        print("Type 'quit' to return to main menu.\n")
        
        words = self.select_words_for_session()
        if not words:
            print("No words available. Please import words first.")
            return
        
        correct_count = 0
        total_count = len(words)
        
        for i, word in enumerate(words, 1):
            print(f"\nWord {i}/{total_count}")
            print(f"English: {word['english']}")
            print("-" * 30)
            
            input("Press Enter when you're ready to check your answer...")
            
            print(f"\nCorrect Thai: {word['thai']}")
            print("\nWas your handwritten answer correct?")
            print("1. Yes (Correct)")
            print("2. No (Incorrect)")
            print("3. Skip this word")
            
            while True:
                choice = input("\nYour evaluation (1/2/3): ").strip()
                
                if choice == '1':
                    print("✓ Marked as correct!")
                    correct_count += 1
                    self.record_answer(word['id'], True, 'english_to_thai')
                    break
                elif choice == '2':
                    print("✗ Marked as incorrect. Keep practicing!")
                    self.record_answer(word['id'], False, 'english_to_thai')
                    break
                elif choice == '3':
                    print("Skipped.")
                    break
                elif choice.lower() == 'quit':
                    print("\nReturning to main menu...")
                    return
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
        
        # Session summary
        if total_count > 0:
            accuracy = (correct_count / total_count) * 100
            print("\n" + "="*50)
            print("SESSION COMPLETE")
            print("="*50)
            print(f"Correct: {correct_count}/{total_count} ({accuracy:.1f}%)")
            print("="*50)
    
    def show_statistics(self):
        """Display learning statistics"""
        cursor = self.conn.cursor()
        
        # Overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_words,
                SUM(times_shown) as total_reviews,
                SUM(times_correct) as total_correct,
                SUM(times_incorrect) as total_incorrect
            FROM words
        """)
        stats = cursor.fetchone()
        
        # Find difficult words (leeches)
        cursor.execute("""
            SELECT thai, english, times_shown, times_correct, times_incorrect,
                   CAST(times_incorrect AS FLOAT) / (times_correct + times_incorrect) as error_rate
            FROM words
            WHERE times_shown >= 3 AND (times_correct + times_incorrect) > 0
            ORDER BY error_rate DESC
            LIMIT 10
        """)
        difficult_words = cursor.fetchall()
        
        # Display statistics
        print("\n" + "="*50)
        print("LEARNING STATISTICS")
        print("="*50)
        print(f"Total words in database: {stats['total_words']}")
        print(f"Total reviews completed: {stats['total_reviews']}")
        
        if stats['total_correct'] or stats['total_incorrect']:
            total = stats['total_correct'] + stats['total_incorrect']
            accuracy = (stats['total_correct'] / total) * 100
            print(f"Overall accuracy: {accuracy:.1f}%")
            print(f"  Correct: {stats['total_correct']}")
            print(f"  Incorrect: {stats['total_incorrect']}")
        
        if difficult_words:
            print("\n" + "-"*50)
            print("WORDS THAT NEED MORE PRACTICE:")
            print("-"*50)
            for i, word in enumerate(difficult_words, 1):
                error_rate = word['error_rate'] * 100
                print(f"{i}. {word['thai']} ({word['english']})")
                print(f"   Shown {word['times_shown']} times | "
                      f"Error rate: {error_rate:.1f}%")
        
        print("="*50)
    
    def main_menu(self):
        """Display main menu and handle user input"""
        while True:
            print("\n" + "="*50)
            print("THAI FLASHCARD LEARNING SYSTEM")
            print("="*50)
            print("1. Practice Reading (Thai → English)")
            print("2. Practice Writing (English → Thai)")
            print("3. View Statistics")
            print("4. Import Words from JSON")
            print("5. Exit")
            print("="*50)
            
            choice = input("\nSelect an option (1-5): ").strip()
            
            if choice == '1':
                self.mode_thai_to_english()
            elif choice == '2':
                self.mode_english_to_thai()
            elif choice == '3':
                self.show_statistics()
            elif choice == '4':
                json_path = input("Enter path to JSON file (default: thai_words.json): ").strip()
                if not json_path:
                    json_path = "thai_words.json"
                
                if Path(json_path).exists():
                    count = self.import_words_from_json(json_path)
                    print(f"\n✓ Successfully imported {count} new words!")
                else:
                    print(f"\n✗ File not found: {json_path}")
            elif choice == '5':
                print("\nGoodbye! Keep practicing! 🇹🇭")
                break
            else:
                print("\n✗ Invalid option. Please select 1-5.")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main entry point"""
    app = ThaiFlashcards()
    
    try:
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye! Keep practicing! 🇹🇭")
    finally:
        app.close()


if __name__ == "__main__":
    main()
