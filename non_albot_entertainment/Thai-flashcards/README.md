# Thai Flashcard Learning System

A spaced repetition flashcard application for learning to read and write Thai words.

## Features

- **Two Practice Modes:**
  - Thai → English (Reading): See Thai words, type English translations
  - English → Thai (Writing): See English words, write Thai by hand and self-evaluate
  
- **Spaced Repetition Algorithm:** Words you struggle with appear more frequently
  
- **Progress Tracking:** All your learning history is saved locally in SQLite database
  
- **Statistics:** View your overall progress and identify difficult words

## Installation & Setup

1. **Requirements:**
   - Python 3.6 or higher (no additional packages needed!)

2. **Files:**
   - `thai_flashcards.py` - Main application
   - `thai_words.json` - 100 most common Thai words
   - `thai_flashcards.db` - Database (created automatically on first run)

## How to Use

### First Time Setup

1. Run the application:
   ```bash
   python thai_flashcards.py
   ```

2. From the main menu, select option 4 to import words:
   - Press `4` and Enter
   - Press Enter again to use default file (`thai_words.json`)
   - You should see: "Successfully imported 100 new words!"

### Practice Modes

#### Mode 1: Reading Practice (Thai → English)
- Select option 1 from main menu
- You'll see a Thai word
- Type the English translation
- Press Enter to check
- The app accepts close matches (like "hi" for "hello, hi")

#### Mode 2: Writing Practice (English → Thai)
- Select option 2 from main menu
- You'll see an English word
- Write the Thai translation by hand on paper
- Press Enter when ready to check
- The app shows the correct Thai word
- You evaluate if your handwriting was correct (1 for correct, 2 for incorrect)

### View Your Progress

- Select option 3 to see:
  - Total words learned
  - Overall accuracy
  - Words that need more practice (your "problem words")

## How the Learning Algorithm Works

The app uses a weighted priority system:

1. **New words** get medium priority (shown occasionally)
2. **Words you get wrong** get high priority (shown more often)
3. **Words not seen recently** get a time-based boost
4. **Mastered words** appear occasionally to prevent forgetting

Each practice session shows 15 words selected based on these priorities.

## Adding More Words

You can easily expand beyond the initial 100 words:

1. Edit `thai_words.json` (or create a new JSON file)
2. Follow this format:
   ```json
   [
     {"thai": "สวัสดี", "english": "hello, hi"},
     {"thai": "ขอบคุณ", "english": "thank you"}
   ]
   ```
3. Import from the main menu (option 4)

## Tips for Best Results

1. **Be consistent:** Practice a little bit every day rather than long sessions once a week
2. **Be honest:** In writing mode, accurately evaluate your handwriting
3. **Review statistics:** Check which words you struggle with and focus on them
4. **Don't quit on mistakes:** Words you get wrong will keep coming back until you master them
5. **Practice both modes:** Reading and writing reinforce each other

## File Structure

```
thai_flashcards/
├── thai_flashcards.py    # Main application
├── thai_words.json        # Word database (100 words included)
└── thai_flashcards.db     # SQLite database (created automatically)
```

## Database Schema

The SQLite database contains:

- **words table:** Stores Thai-English pairs with learning statistics
- **learning_history table:** Records every practice attempt with timestamp

All data is stored locally on your computer. Nothing is sent online.

## Troubleshooting

**"No words available":**
- Make sure you've imported words using option 4

**Can't type Thai characters:**
- No problem! Use the English → Thai writing mode and write by hand

**Want to reset your progress:**
- Simply delete `thai_flashcards.db` and restart the app

## Future Expansion Ideas

Want to customize further? The code is well-commented and you can easily:
- Adjust session length (default 15 words)
- Modify the priority algorithm
- Add word categories or difficulty levels
- Export statistics to CSV
- Add example sentences

## License

Free to use and modify for personal learning!

---

Happy learning! 🇹🇭 สู้ๆ (Keep fighting/Good luck!)
