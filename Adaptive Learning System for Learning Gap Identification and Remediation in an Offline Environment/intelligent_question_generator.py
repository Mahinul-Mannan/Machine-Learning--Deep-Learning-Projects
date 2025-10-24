import re
import random
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import sqlite3
from datetime import datetime
import os

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class IntelligentQuestionGenerator:
    def __init__(self, db_path="intelligent_database.db"):
        # Use absolute path for database
        self.db_path = os.path.abspath(db_path)
        self.stop_words = set(stopwords.words('english'))
        
        # Bloom's Taxonomy based question frameworks
        # Bloom's Taxonomy based question frameworks
        self.blooms_frameworks = {
            "remember": [
                "Define the concept of {concept} based on the material.",
                "What are the key components of {concept}?",
                "List the main characteristics of {concept}.",
                "What is the basic definition of {concept}?",
                "Identify the fundamental elements of {concept}."
            ],
            "understand": [
                "Explain how {concept} works in your own words.",
                "What is the significance of {concept}?",
                "How would you summarize the main idea behind {concept}?",
                "What does {concept} accomplish in this system?",
                "Paraphrase the explanation of {concept}."
            ],
            "apply": [
                "How would you use {concept} to solve a real-world problem?",
                "Provide a practical example where {concept} can be applied.",
                "Demonstrate how {concept} works through a simple example.",
                "How does {concept} function in practical situations?"
            ],
            "analyze": [
                "What are the differences between {concept1} and {concept2}?",
                "Break down {concept} into its fundamental steps.",
                "What is the relationship between {concept} and other concepts?",
                "Analyze the components that make up {concept}.",
                "What patterns can you identify in how {concept} is used?"
            ]
    }
        
        self.create_database()
    
    def create_database(self):
        """Create database and tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS intelligent_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    cognitive_level TEXT NOT NULL,
                    difficulty INTEGER NOT NULL,
                    context TEXT,
                    expected_answer TEXT,
                    concepts TEXT,
                    scoring_criteria TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"Database created successfully at: {self.db_path}")
        except Exception as e:
            print(f"Error creating database: {e}")
    
    def extract_intelligent_phrases(self, text):
        """Advanced phrase extraction using NLTK"""
        print("Extracting intelligent phrases using advanced NLP...")
        
        # Tokenize sentences
        sentences = sent_tokenize(text)
        
        # Extract meaningful noun phrases
        noun_phrases = self.extract_noun_phrases(text)
        
        # Extract key concepts using frequency and importance
        key_concepts = self.extract_key_concepts(text)
        
        # Extract specific entities and terms
        specific_terms = self.extract_specific_terms(text)
        
        # Combine and filter phrases
        all_phrases = list(set(noun_phrases + key_concepts + specific_terms))
        
        meaningful_phrases = []
        for phrase in all_phrases:
            words = phrase.split()
            if len(words) >= 1 and len(phrase) > 4:
                if not all(word.lower() in self.stop_words for word in words):
                    meaningful_phrases.append(phrase)
        
        print(f"Extracted {len(meaningful_phrases)} meaningful phrases")
        return meaningful_phrases[:25], sentences
    
    def extract_noun_phrases(self, text):
        """Extract noun phrases using advanced pattern matching"""
        patterns = [
            r'\b(?:[A-Z][a-z]+\s)+[A-Z][a-z]+\b',
            r'\b(?:[A-Z][a-z]*\s){1,3}(?:system|method|technique|approach|model|process|theory|concept|principle|algorithm|framework)\b',
            r'\b(?:machine learning|deep learning|artificial intelligence|neural network|data analysis|computer vision|natural language)\b'
        ]
        
        noun_phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            noun_phrases.extend(matches)
        
        return list(set(noun_phrases))
    
    def extract_specific_terms(self, text):
        """Extract specific technical terms and entities"""
        sentences = sent_tokenize(text)
        specific_terms = []
        
        technical_indicators = ['method', 'technique', 'system', 'approach', 'model', 
                               'process', 'theory', 'concept', 'principle', 'algorithm',
                               'framework', 'structure', 'mechanism', 'technology']
        
        for sentence in sentences:
            words = word_tokenize(sentence)
            # Look for technical terms
            for i, word in enumerate(words):
                if word.lower() in technical_indicators and i > 0:
                    # Get preceding words to form the term
                    term = " ".join(words[max(0, i-2):i+1])
                    specific_terms.append(term)
        
        return list(set(specific_terms))
    
    def extract_key_concepts(self, text):
        """Extract key concepts using frequency analysis"""
        words = [word.lower() for word in word_tokenize(text) 
                if word.isalpha() and word.lower() not in self.stop_words and len(word) > 3]
        
        word_freq = Counter(words)
        
        # Extract meaningful multi-word concepts
        sentences = sent_tokenize(text)
        multi_word_concepts = []
        
        for sentence in sentences:
            words_in_sentence = [word.lower() for word in word_tokenize(sentence) 
                               if word.isalpha() and word.lower() not in self.stop_words]
            
            # Extract 2-3 word phrases
            for i in range(len(words_in_sentence) - 1):
                if len(words_in_sentence[i]) > 3 and len(words_in_sentence[i+1]) > 3:
                    phrase = f"{words_in_sentence[i]} {words_in_sentence[i+1]}"
                    if phrase in text.lower():
                        multi_word_concepts.append(phrase)
            
            for i in range(len(words_in_sentence) - 2):
                if all(len(word) > 3 for word in words_in_sentence[i:i+3]):
                    phrase = " ".join(words_in_sentence[i:i+3])
                    if phrase in text.lower():
                        multi_word_concepts.append(phrase)
        
        single_concepts = [word for word, freq in word_freq.most_common(30) if freq > 1]
        all_concepts = list(set(single_concepts + multi_word_concepts))
        
        return all_concepts[:25]
    
    def find_relevant_sentences(self, concept, sentences):
        """Find sentences relevant to a specific concept"""
        relevant = []
        for sentence in sentences:
            if concept.lower() in sentence.lower():
                relevant.append(sentence)
        return relevant
    
    def get_topic_from_context(self, sentences):
        """Extract main topic from context"""
        if not sentences:
            return "the subject"
        
        # Use first few sentences to determine topic
        context_text = " ".join(sentences[:3])
        words = [word for word in word_tokenize(context_text) 
                if word.isalpha() and word.lower() not in self.stop_words and word[0].isupper()]
        
        if words:
            return words[0]
        return "the subject"
    
    def generate_intelligent_questions(self, text, num_questions=10):
        """Generate intelligent, context-aware questions using Bloom's Taxonomy"""
        print("Generating intelligent, meaningful questions using Bloom's Taxonomy...")
        
        phrases, sentences = self.extract_intelligent_phrases(text)
        topic = self.get_topic_from_context(sentences)
        
        questions = []
        
        # Generate Bloom's taxonomy based questions
        blooms_questions = self.generate_blooms_based_questions(phrases, sentences, num_questions)
        questions.extend(blooms_questions)
        
        # Ensure we have enough questions
        if len(questions) < num_questions:
            additional = self.generate_fallback_questions(text, num_questions - len(questions))
            questions.extend(additional)
        
        # Shuffle and select
        random.shuffle(questions)
        selected_questions = questions[:num_questions]
        
        # Save to database
        self.save_questions_to_db(selected_questions)
        
        print(f"Generated {len(selected_questions)} meaningful questions across Bloom's Taxonomy levels")
        return selected_questions
    
    def generate_blooms_based_questions(self, concepts, sentences, num_questions):
        """Generate questions based on Bloom's Taxonomy"""
        questions = []
        topic = self.get_topic_from_context(sentences)
        
        if not concepts:
            return self.generate_fallback_questions(" ".join(sentences), num_questions)
        
        # Distribute questions across cognitive levels
        levels = ["remember", "understand", "apply", "analyze"]
        questions_per_level = max(1, num_questions // len(levels))
        
        for level in levels:
            level_questions = self.generate_questions_for_level(level, concepts, sentences, topic, questions_per_level)
            questions.extend(level_questions)
        
        return questions
    
    def generate_questions_for_level(self, level, concepts, sentences, topic, count):
        """Generate questions for a specific Bloom's level"""
        questions = []
        templates = self.blooms_frameworks.get(level, [])
        
        if not templates or not concepts:
            return questions
        
        for _ in range(count):
            concept = random.choice(concepts)
            template = random.choice(templates)
            
            # Handle different template placeholders
            try:
                if "{concept}" in template and "{topic}" in template:
                    question_text = template.format(concept=concept, topic=topic)
                elif "{concept1}" in template and "{concept2}" in template:
                    if len(concepts) >= 2:
                        concept1, concept2 = random.sample(concepts, 2)
                        question_text = template.format(concept1=concept1, concept2=concept2)
                    else:
                        continue
                else:
                    # For templates with only {concept} or no placeholder
                    question_text = template.format(concept=concept)
            except KeyError as e:
                print(f"KeyError in template: {template}, error: {e}")
                continue
            
            # Find relevant context
            context_sentences = self.find_relevant_sentences(concept, sentences)
            context = context_sentences[0] if context_sentences else sentences[0] if sentences else ""
            
            # Set appropriate difficulty based on cognitive level
            difficulty_map = {"remember": 2, "understand": 3, "apply": 4, "analyze": 4}
            difficulty = difficulty_map.get(level, 3)
            
            # Define scoring criteria based on cognitive level
            scoring_criteria_map = {
                "remember": ["accuracy", "completeness"],
                "understand": ["clarity", "accuracy", "depth"],
                "apply": ["relevance", "practicality", "correctness"],
                "analyze": ["depth", "logic", "comprehensiveness"]
            }
            
            questions.append({
                'question_text': question_text,
                'question_type': f'{level}_based',
                'cognitive_level': level,
                'difficulty': difficulty,
                'context': context[:200] + "..." if len(context) > 200 else context,
                'expected_answer': self.generate_expected_answer(level, concept, topic),
                'concepts': [concept],
                'scoring_criteria': scoring_criteria_map.get(level, ["completeness", "accuracy"])
            })
        
        return questions
    
    def generate_expected_answer(self, level, concept, topic):
        """Generate expected answer guidelines based on cognitive level"""
        guidelines = {
            "remember": f"Clear definition and key characteristics of {concept}.",
            "understand": f"Explanation of how {concept} works and its purpose in {topic}.",
            "apply": f"Practical example demonstrating the application of {concept}.",
            "analyze": f"Breakdown of {concept} components and their relationships."
        }
        return guidelines.get(level, f"Comprehensive response about {concept}.")
    
    def generate_fallback_questions(self, text, num_needed):
        """Generate context-aware fallback questions"""
        questions = []
        
        sentences = sent_tokenize(text)
        phrases, _ = self.extract_intelligent_phrases(text)
        topic = self.get_topic_from_context(sentences)
        
        basic_templates = [
            "What evidence or examples support the main arguments about {concept}?",
            "How is information about {concept} structured in this material?",
            "What relationships exist between different aspects of {concept}?",
            "How would you summarize the key points about {concept}?",
            "What makes {concept} relevant in today's context?"
        ]
        
        for i in range(min(num_needed, len(basic_templates))):
            if phrases:
                concept = random.choice(phrases)
                question_text = basic_templates[i].format(concept=concept)
                
                questions.append({
                    'question_text': question_text,
                    'question_type': 'comprehension',
                    'cognitive_level': 'understand',
                    'difficulty': 3,
                    'context': '',
                    'expected_answer': f'A thoughtful response based on the specific content about {concept}.',
                    'concepts': [concept],
                    'scoring_criteria': ["completeness", "accuracy", "clarity"]
                })
        
        return questions

    def save_questions_to_db(self, questions):
        """Save questions to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            for q in questions:
                c.execute('''
                    INSERT INTO intelligent_questions 
                    (question_text, question_type, cognitive_level, difficulty, context, expected_answer, concepts, scoring_criteria)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    q['question_text'],
                    q['question_type'],
                    q['cognitive_level'],
                    q['difficulty'],
                    q['context'],
                    q['expected_answer'],
                    ', '.join(q['concepts']),
                    ', '.join(q['scoring_criteria'])
                ))
            
            conn.commit()
            conn.close()
            print(f"Saved {len(questions)} questions to database")
        except Exception as e:
            print(f"Error saving to database: {e}")

    def conduct_intelligent_test(self, questions):
        """Conduct intelligent test with meaningful evaluation"""
        print(f"\n🎯 Starting Intelligent Test with {len(questions)} questions...")
        test_results = []
        
        for i, question in enumerate(questions, 1):
            print("\n" + "="*60)
            print(f"QUESTION {i}/{len(questions)}")
            print(f"Type: {question['question_type'].replace('_', ' ').title()}")
            print(f"Cognitive Level: {question['cognitive_level'].title()}")
            print(f"Difficulty: {'⭐' * question['difficulty']}")
            print(f"\n{question['question_text']}")
            
            if question.get('context'):
                print(f"\n💡 Context: {question['context'][:100]}...")
            
            user_answer = input("\n💭 Your answer: ").strip()
            
            # Simple evaluation based on answer length and content
            score = self.evaluate_simple_answer(user_answer, question)
            
            test_results.append({
                'question_number': i,
                'question_text': question['question_text'],
                'question_type': question['question_type'],
                'cognitive_level': question['cognitive_level'],
                'difficulty': question['difficulty'],
                'user_answer': user_answer,
                'score': score,
                'concepts': question['concepts']
            })
            
            # Provide meaningful feedback
            self.provide_feedback(score, question)
        
        return test_results
    
    def evaluate_simple_answer(self, user_answer, question):
        """Simple evaluation based on answer length and content"""
        if not user_answer:
            return 0.0
        
        # Score based on answer length
        word_count = len(user_answer.split())
        if word_count < 10:
            length_score = 0.3
        elif word_count < 20:
            length_score = 0.6
        else:
            length_score = 0.9
        
        # Score based on concept mention
        concept_score = 0.0
        for concept in question['concepts']:
            if concept.lower() in user_answer.lower():
                concept_score += 0.3
        
        concept_score = min(concept_score, 0.7)
        
        # Combined score
        final_score = (length_score * 0.6) + (concept_score * 0.4)
        
        return round(final_score, 2)
    
    def provide_feedback(self, score, question):
        """Provide intelligent feedback based on cognitive level"""
        cognitive_level = question.get('cognitive_level', 'understand')
        
        if score >= 0.8:
            print(f"\n✅ Excellent! Demonstrates deep {cognitive_level} level understanding.")
        elif score >= 0.6:
            print(f"\n👍 Good! Solid {cognitive_level} with room for more detail.")
        elif score >= 0.4:
            print(f"\n⚠️  Fair. Basic {cognitive_level} achieved.")
        else:
            print(f"\n❌ Needs improvement. Focus on fundamental concepts for {cognitive_level}.")
    
    def identify_weak_areas(self, test_results):
        """Identify weak areas intelligently"""
        concept_performance = {}
        level_performance = {}
        type_performance = {}
        
        for result in test_results:
            # Concept performance
            for concept in result['concepts']:
                if concept not in concept_performance:
                    concept_performance[concept] = {'total': 0, 'count': 0}
                concept_performance[concept]['total'] += result['score']
                concept_performance[concept]['count'] += 1
            
            # Cognitive level performance
            level = result['cognitive_level']
            if level not in level_performance:
                level_performance[level] = {'total': 0, 'count': 0}
            level_performance[level]['total'] += result['score']
            level_performance[level]['count'] += 1
            
            # Question type performance
            q_type = result['question_type']
            if q_type not in type_performance:
                type_performance[q_type] = {'total': 0, 'count': 0}
            type_performance[q_type]['total'] += result['score']
            type_performance[q_type]['count'] += 1
        
        # Find weak concepts
        weak_concepts = []
        for concept, perf in concept_performance.items():
            avg_score = perf['total'] / perf['count']
            if avg_score < 0.6:
                weak_concepts.append({
                    'concept': concept,
                    'average_score': avg_score,
                    'count': perf['count']
                })
        
        # Find weak cognitive levels
        weak_levels = []
        for level, perf in level_performance.items():
            avg_score = perf['total'] / perf['count']
            if avg_score < 0.6:
                weak_levels.append({
                    'cognitive_level': level,
                    'average_score': avg_score,
                    'count': perf['count']
                })
        
        # Find weak question types
        weak_types = []
        for q_type, perf in type_performance.items():
            avg_score = perf['total'] / perf['count']
            if avg_score < 0.6:
                weak_types.append({
                    'question_type': q_type,
                    'average_score': avg_score,
                    'count': perf['count']
                })
        
        weak_concepts.sort(key=lambda x: x['average_score'])
        weak_levels.sort(key=lambda x: x['average_score'])
        weak_types.sort(key=lambda x: x['average_score'])
        
        return weak_concepts, weak_levels, weak_types
    
    def generate_intelligent_report(self, student_name, test_results, questions):
        """Generate comprehensive intelligent report"""
        total_score = sum(result['score'] for result in test_results)
        average_score = total_score / len(test_results)
        percentage = average_score * 100
        
        weak_concepts, weak_levels, weak_types = self.identify_weak_areas(test_results)
        
        report_content = f"""
🤖 ENHANCED INTELLIGENT LEARNING ASSESSMENT REPORT
==================================================

Student: {student_name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Questions: {len(test_results)}

📊 PERFORMANCE SUMMARY
----------------------
Overall Score: {percentage:.1f}% ({average_score:.2f}/1.00)
Questions Attempted: {len(test_results)}

🔴 WEAK CONCEPTS IDENTIFIED
---------------------------"""
        
        if weak_concepts:
            for i, concept in enumerate(weak_concepts[:6], 1):
                report_content += f"\n{i}. {concept['concept'].title()} (Score: {concept['average_score']:.2f})"
        else:
            report_content += "\nNo significant weak concepts identified."
        
        report_content += f"""

💡 RECOMMENDATIONS
------------------"""
        
        if percentage >= 80:
            report_content += "\n🎉 Outstanding performance! Excellent critical thinking and comprehension skills."
        elif percentage >= 65:
            report_content += "\n👍 Strong performance with good analytical abilities."
        elif percentage >= 50:
            report_content += "\n⚠️  Solid understanding with room for improvement in analysis."
        else:
            report_content += "\n❌ Focus on building fundamental understanding and explanation skills."
        
        if weak_concepts:
            report_content += f"\n\n🎯 SPECIFIC FOCUS AREAS:"
            for concept in weak_concepts[:3]:
                report_content += f"\n- Review and practice: {concept['concept'].title()}"
        
        report_content += f"""

📚 LEARNING STRATEGY
--------------------
1. Review identified weak concepts thoroughly
2. Practice explaining ideas in your own words
3. Create concept maps to visualize relationships
4. Apply concepts to real-world scenarios
5. Discuss topics with others to deepen understanding

Generated by AI Intelligent Learning System
===========================================
"""
        
        filename = f"intelligent_report_{student_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\n📄 Comprehensive report generated: {filename}")
        except Exception as e:
            print(f"Error saving report: {e}")
        
        return report_content, weak_concepts, weak_levels, weak_types

def test_system():
    print("Testing Enhanced Intelligent Question Generator...")
    
    generator = IntelligentQuestionGenerator()
    
    sample_text = """
    Machine learning is a subset of artificial intelligence that enables computers to learn from data without explicit programming. 
    Deep learning uses neural networks with multiple layers to process complex patterns in data. 
    Supervised learning requires labeled datasets where the algorithm learns from input-output pairs. 
    Unsupervised learning finds hidden patterns in unlabeled data through clustering and association. 
    """
    
    questions = generator.generate_intelligent_questions(sample_text, 5)
    print(f"\nGenerated {len(questions)} meaningful questions:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. [{q['cognitive_level'].upper()}] {q['question_text']}")

if __name__ == "__main__":
    test_system()