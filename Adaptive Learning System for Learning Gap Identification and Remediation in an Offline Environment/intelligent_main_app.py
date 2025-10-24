import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import traceback
import datetime
from advanced_data_processor import AdvancedDataProcessor
from intelligent_question_generator import IntelligentQuestionGenerator

class IntelligentLearningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Intelligent Learning System")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f8ff')
        
        self.student_name = tk.StringVar()
        self.file_path = tk.StringVar()
        self.question_generator = IntelligentQuestionGenerator()
        self.data_processor = AdvancedDataProcessor()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = tk.Label(main_frame, text="🤖 AI Intelligent Learning System", 
                               font=("Arial", 22, "bold"), fg="#2c3e50", bg='#f0f8ff')
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        subtitle_label = tk.Label(main_frame, 
                                 text="Upload any study material and get AI-powered, comprehension-based questions!",
                                 font=("Arial", 12), fg="#3498db", bg='#f0f8ff')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Student Info
        tk.Label(main_frame, text="Student Name:", font=("Arial", 12, "bold"), 
                bg='#f0f8ff').grid(row=2, column=0, sticky=tk.W, pady=15)
        name_entry = ttk.Entry(main_frame, textvariable=self.student_name, 
                              width=30, font=("Arial", 12))
        name_entry.grid(row=2, column=1, pady=15, padx=10, sticky=tk.W)
        
        # File Upload
        tk.Label(main_frame, text="Upload Study Material:", font=("Arial", 12, "bold"),
                bg='#f0f8ff').grid(row=3, column=0, sticky=tk.W, pady=15)
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path, 
                              width=30, font=("Arial", 12))
        file_entry.grid(row=3, column=1, pady=15, padx=10, sticky=tk.W)
        
        ttk.Button(main_frame, text="📁 Browse Files", 
                  command=self.browse_file, width=15).grid(row=3, column=2, pady=15)
        
        # Supported formats
        formats_label = tk.Label(main_frame, 
                                text="Supported: PDF, DOCX, TXT files (any subject/topic)",
                                font=("Arial", 10), fg="#27ae60", bg='#f0f8ff')
        formats_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Process Button
        self.process_btn = ttk.Button(main_frame, 
                                    text="🧠 Analyze & Generate Intelligent Questions", 
                                    command=self.process_material,
                                    width=35)
        self.process_btn.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Results Frame
        self.results_frame = tk.LabelFrame(main_frame, text="Analysis Results", 
                                          padx=15, pady=15, font=("Arial", 11, "bold"),
                                          bg='#f0f8ff', fg="#2c3e50")
        self.results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Test Button
        self.test_button = ttk.Button(main_frame, 
                                     text="🎯 Start 10-Question Intelligent Test", 
                                     command=self.start_intelligent_test, 
                                     state=tk.DISABLED, width=28)
        self.test_button.grid(row=7, column=0, columnspan=3, pady=15)
        
        # Status Label
        self.status_label = tk.Label(main_frame, text="Ready to analyze your study material...", 
                                     font=("Arial", 10), fg="#27ae60", bg='#f0f8ff')
        self.status_label.grid(row=8, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Study Material",
            filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx"), 
                      ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            file_size = os.path.getsize(filename) / 1024  # Size in KB
            self.status_label.config(
                text=f"✅ Selected: {os.path.basename(filename)} ({file_size:.1f} KB)", 
                fg="#27ae60"
            )
    
    def process_material(self):
        if not self.student_name.get().strip():
            messagebox.showerror("Error", "Please enter your name")
            return
        
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a study material file")
            return
        
        self.status_label.config(text="📖 Reading and analyzing your material with AI...", fg="#e67e22")
        self.progress.start()
        self.process_btn.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            # First validate file
            is_valid, validation_msg = self.data_processor.validate_file(self.file_path.get())
            if not is_valid:
                messagebox.showerror("Error", validation_msg)
                return
            
            # Process file
            print(f"Processing file: {self.file_path.get()}")  # Debug
            text = self.data_processor.extract_text_from_file(self.file_path.get())
            print(f"Extracted text length: {len(text) if text else 0}")  # Debug
            
            if not text or len(text.strip()) < 50:  # Reduced minimum text requirement
                messagebox.showerror("Error", 
                    "Could not read sufficient text from the file. The file might be empty, corrupted, or in an unsupported format.")
                return
            
            # Preprocess text
            processed_text = self.data_processor.preprocess_text(text)
            print(f"Processed text length: {len(processed_text)}")  # Debug
            
            self.status_label.config(text="🤔 Generating intelligent questions using advanced NLP...", fg="#3498db")
            self.root.update()
            
            # Generate intelligent questions
            self.generated_questions = self.question_generator.generate_intelligent_questions(processed_text, 10)
            print(f"Generated {len(self.generated_questions)} questions")  # Debug
            
            self.display_analysis_results()
            self.test_button.config(state=tk.NORMAL)
            
            self.status_label.config(
                text="🎉 Ready! 10 intelligent questions generated. Click 'Start Test' to begin.", 
                fg="#27ae60"
            )
            messagebox.showinfo("Success", 
                            "AI Analysis Complete!\n\nGenerated 10 comprehension-based questions from your material using advanced NLP techniques.\n\nClick 'Start Intelligent Test' to begin!")
            
        except Exception as e:
            self.status_label.config(text="❌ Processing failed", fg="#e74c3c")
            # Detailed error message with traceback
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"Processing failed: {str(e)}\n\nError type: {type(e).__name__}"
            print(f"Full error traceback:\n{error_details}")  # This will print full traceback to console
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.process_btn.config(state=tk.NORMAL)
    
    def display_analysis_results(self):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Display cognitive levels breakdown
        cognitive_levels = {}
        question_types = {}
        for q in self.generated_questions:
            level = q['cognitive_level']
            q_type = q['question_type']
            
            if level not in cognitive_levels:
                cognitive_levels[level] = 0
            cognitive_levels[level] += 1
            
            if q_type not in question_types:
                question_types[q_type] = 0
            question_types[q_type] += 1
        
        tk.Label(self.results_frame, text="📊 Enhanced Question Analysis:", 
                font=("Arial", 12, "bold"), bg='#f0f8ff', fg="#2c3e50"
                ).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        # Show cognitive levels distribution
        level_text = "Cognitive Levels: "
        level_list = []
        for level, count in cognitive_levels.items():
            level_name = level.title()
            level_list.append(f"{level_name} ({count})")
        
        level_text += " | ".join(level_list)
        
        tk.Label(self.results_frame, text=level_text, font=("Arial", 10), 
                wraplength=800, justify=tk.LEFT, bg='#f0f8ff'
                ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Show question types
        type_text = "Question Types: "
        type_list = []
        for q_type, count in question_types.items():
            type_name = q_type.replace('_', ' ').title()
            type_list.append(f"{type_name} ({count})")
        
        type_text += " | ".join(type_list)
        
        tk.Label(self.results_frame, text=type_text, font=("Arial", 10), 
                wraplength=800, justify=tk.LEFT, bg='#f0f8ff'
                ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Show sample questions with cognitive levels
        tk.Label(self.results_frame, text="Sample Questions:", 
                font=("Arial", 11, "bold"), bg='#f0f8ff', fg="#2c3e50"
                ).grid(row=3, column=0, sticky=tk.W, pady=10)
        
        for i, question in enumerate(self.generated_questions[:3], 1):
            q_text = f"Q{i}: {question['question_text']}"
            if len(q_text) > 100:
                q_text = q_text[:97] + "..."
            
            q_level = question['cognitive_level'].title()
            q_type = question['question_type'].replace('_', ' ').title()
            difficulty = "⭐" * question['difficulty']
            
            question_label = tk.Label(self.results_frame, 
                                    text=f"{q_text}\n   Level: {q_level} | Type: {q_type} | Difficulty: {difficulty}", 
                                    font=("Arial", 9), 
                                    wraplength=800, justify=tk.LEFT, fg="#2980b9",
                                    bg='#f0f8ff')
            question_label.grid(row=3+i, column=0, sticky=tk.W, pady=2)
        
        tk.Label(self.results_frame, 
                text=f"📝 Total Enhanced Questions: {len(self.generated_questions)} (Bloom's Taxonomy Based)", 
                font=("Arial", 11, "bold"), fg="#e67e22", bg='#f0f8ff'
                ).grid(row=7, column=0, sticky=tk.W, pady=10)
    
    def start_intelligent_test(self):
        self.status_label.config(text="🎯 Starting intelligent test... Provide thoughtful answers!", fg="#9b59b6")
        self.root.update()
        
        try:
            test_results = self.question_generator.conduct_intelligent_test(self.generated_questions)
            
            # Updated to handle 4 return values from generate_intelligent_report
            report, weak_concepts, weak_levels, weak_types = self.question_generator.generate_intelligent_report(
                self.student_name.get(), test_results, self.generated_questions)
            
            self.display_enhanced_analysis(weak_concepts, weak_levels, weak_types)
            
            self.status_label.config(text="✅ Intelligent test completed! Comprehensive report generated.", fg="#27ae60")
            messagebox.showinfo("Test Completed", 
                            "Intelligent Test Finished!\n\nYou completed 10 comprehension-based questions.\n\nDetailed analysis with weak areas identification has been generated.")
            
        except Exception as e:
            self.status_label.config(text="❌ Test failed", fg="#e74c3c")
            messagebox.showerror("Error", f"Test failed: {str(e)}")
    
    def display_enhanced_analysis(self, weak_concepts, weak_levels, weak_types):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        current_row = 0
        
        # Display analysis header
        tk.Label(self.results_frame, text="📈 Enhanced Intelligent Analysis Results:", 
                 font=("Arial", 13, "bold"), fg="#2c3e50", bg='#f0f8ff'
                 ).grid(row=current_row, column=0, sticky=tk.W, pady=10)
        current_row += 1
        
        # Display weak concepts
        if weak_concepts:
            tk.Label(self.results_frame, text="🔴 Concepts Needing Improvement:", 
                     font=("Arial", 11, "bold"), fg="#e74c3c", bg='#f0f8ff'
                     ).grid(row=current_row, column=0, sticky=tk.W, pady=10)
            current_row += 1
            
            for i, concept in enumerate(weak_concepts[:6], 1):
                concept_text = f"{i}. {concept['concept'].title()} (Understanding Score: {concept['average_score']:.2f}/1.00)"
                tk.Label(self.results_frame, text=concept_text, font=("Arial", 9), 
                         fg="#c0392b", wraplength=800, justify=tk.LEFT, bg='#f0f8ff'
                         ).grid(row=current_row, column=0, sticky=tk.W, pady=2)
                current_row += 1
        
        # Display weak cognitive levels
        if weak_levels:
            tk.Label(self.results_frame, text="🟠 Weak Cognitive Levels:", 
                     font=("Arial", 11, "bold"), fg="#e67e22", bg='#f0f8ff'
                     ).grid(row=current_row, column=0, sticky=tk.W, pady=10)
            current_row += 1
            
            for i, level in enumerate(weak_levels, 1):
                level_name = level['cognitive_level'].title()
                level_text = f"{i}. {level_name} (Performance Score: {level['average_score']:.2f}/1.00)"
                tk.Label(self.results_frame, text=level_text, font=("Arial", 9), 
                         fg="#d35400", wraplength=800, justify=tk.LEFT, bg='#f0f8ff'
                         ).grid(row=current_row, column=0, sticky=tk.W, pady=2)
                current_row += 1
        
        # Display weak question types
        if weak_types:
            tk.Label(self.results_frame, text="🟡 Question Types Needing Practice:", 
                     font=("Arial", 11, "bold"), fg="#f39c12", bg='#f0f8ff'
                     ).grid(row=current_row, column=0, sticky=tk.W, pady=10)
            current_row += 1
            
            for i, q_type in enumerate(weak_types, 1):
                type_name = q_type['question_type'].replace('_', ' ').title()
                type_text = f"{i}. {type_name} (Performance Score: {q_type['average_score']:.2f}/1.00)"
                tk.Label(self.results_frame, text=type_text, font=("Arial", 9), 
                         fg="#e67e22", wraplength=800, justify=tk.LEFT, bg='#f0f8ff'
                         ).grid(row=current_row, column=0, sticky=tk.W, pady=2)
                current_row += 1
        
        if not weak_concepts and not weak_levels and not weak_types:
            tk.Label(self.results_frame, text="🎉 Excellent! No significant weak areas identified.", 
                     font=("Arial", 11, "bold"), fg="#27ae60", bg='#f0f8ff'
                     ).grid(row=current_row, column=0, sticky=tk.W, pady=10)
            current_row += 1
        
        # Recommendations
        tk.Label(self.results_frame, text="💡 Personalized Learning Recommendations:", 
                 font=("Arial", 11, "bold"), fg="#27ae60", bg='#f0f8ff'
                 ).grid(row=current_row, column=0, sticky=tk.W, pady=10)
        current_row += 1
        
        recommendations = [
            "🎯 Focus on understanding concepts rather than memorization",
            "💭 Practice explaining concepts in your own words",
            "🗺️ Create concept maps to visualize relationships",
            "🌍 Apply concepts to real-world scenarios",
            "📚 Review fundamental principles regularly",
            "🤔 Ask 'why' and 'how' questions to develop critical thinking",
            "🔍 Analyze relationships between different concepts",
            "📊 Practice different types of questions regularly"
        ]
        
        for i, rec in enumerate(recommendations):
            tk.Label(self.results_frame, text=rec, font=("Arial", 9), 
                     fg="#16a085", wraplength=800, justify=tk.LEFT, bg='#f0f8ff'
                     ).grid(row=current_row, column=0, sticky=tk.W, pady=1)
            current_row += 1
        
        # Cognitive level specific strategies
        if weak_levels:
            tk.Label(self.results_frame, text="🧠 Cognitive Level Improvement Strategies:", 
                     font=("Arial", 11, "bold"), fg="#8e44ad", bg='#f0f8ff'
                     ).grid(row=current_row, column=0, sticky=tk.W, pady=10)
            current_row += 1
            
            strategies = {
                'remember': "• Create flashcards and practice definitions\n• Use mnemonic devices for memorization",
                'understand': "• Explain concepts to others in simple terms\n• Create summaries in your own words",
                'apply': "• Work on practical examples and case studies\n• Solve real-world problems using concepts",
                'analyze': "• Break down complex topics into components\n• Compare and contrast different concepts",
                'evaluate': "• Practice critical analysis and justification\n• Assess strengths and limitations of ideas"
            }
            
            for level in weak_levels:
                level_name = level['cognitive_level']
                if level_name in strategies:
                    strategy_text = f"📌 {level_name.title()}:\n{strategies[level_name]}"
                    tk.Label(self.results_frame, text=strategy_text, font=("Arial", 9), 
                             fg="#9b59b6", wraplength=800, justify=tk.LEFT, bg='#f0f8ff'
                             ).grid(row=current_row, column=0, sticky=tk.W, pady=5)
                    current_row += 1

def main():
    root = tk.Tk()
    app = IntelligentLearningApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()