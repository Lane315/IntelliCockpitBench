def create_english_answer_prompt(question):
   prompt=f"""
You are an in-car intelligent agent. Based on the content of images captured by the onboard camera and the given question, generate matching 'primary tags' and 'secondary tags' from the **Question Classification System**, and provide the 'answer' to the question along with the 'reason' for the answer. Ensure the following:

1. **Clarity**: Descriptions must be clear and concise.
2. **Consistency**: The generated primary and secondary tags must strictly correspond to the relevant categories in the classification system without cross-category questions.
3. **Conciseness**: Ensure questions and explanations are short and easy to process for quick comprehension during real-time operations.
4. **Relevance**: If the question is unclear or does not require the capabilities of the in-car multimodal model (i.e., it can be answered solely by the language model or by using tools like 'weather software', 'maps' for precise location, 'navigation', etc.), please directly generate "Sorry, I can't answer" in the 'Answer' field of the **Output Format**.
5. **Context Relevance**: If the question contains phrases such as 'in the picture', 'in the background', etc., which are not typical of questions a driver would ask while driving, please directly generate "Sorry, I can't answer" in the 'Answer' field of the **Output Format**.

---
**Question**

{question}

---

**Question Classification System**

1. Description

2. Recognition:
   - **Vehicle Model Recognition**: e.g., What is the vehicle model in the far left foreground?
   - **Information Extraction**: e.g., What is the content of the yellow billboard on the top right?
   - **Object Recognition**: e.g., What is on the ground on the left?
   - **Emotion Recognition**: e.g., Is that person on the road crying? Why is that man laughing?
   - **Human Activity Recognition**: e.g., What is that person doing? Why is he crawling on the road?

3. World Knowledge Q&A:
   - **Traffic Laws and Regulations**: e.g., What is the meaning of the sign ahead? Can I turn left at this intersection?
   - **Geospatial Environmental Information**: e.g., Where is this place? Is this a commercial or residential area? What building is in front? What is the current weather?
   - **Socio-cultural Knowledge**: e.g., How is this left-turn signal represented in other countries?
   - **General Knowledge**: e.g., Is the building on the street a restaurant or a hotel?

4. Reasoning:
   - **Quantitative Statistics**: e.g., How many black cars are in the left foreground lane? How many lanes are there on the road ahead? How many floors does the white building on the right have?
   - **Distance Measurement**: e.g., How far is the bus stop from me? How far is the man in black from the mall? How far is the car from the crosswalk?
   - **Angle Measurement**: e.g., What is the approximate distance between the black car ahead and the pedestrian?
   - **Area and Volume**: e.g., What is the ground area of the object on the right ahead?
   - **Probabilistic Reasoning/Intent Recognition**: e.g., What is that person standing in the middle of the road trying to do? Is there an accident ahead? Why is this car signaling a left turn?
   - **Driving Decisions**: e.g., Based on the sign, which lane should be chosen to head to a specific address? Please evaluate the road conditions ahead; how should I operate to avoid danger in the situation ahead? How to get to a specific address?

5. Others:
   - **Creation**: e.g., Please write a poem based on the road conditions.
   - **Translation**: e.g., Please translate the content of the advertisement ahead into English.
   - **Others**: Questions not included in the above categories

---

Output Format:
```
[
  {{"Primary Tag": "Primary Tag of the Question", "Secondary Tag": "Secondary Tag of the Question", "Answer": "Answer to the Question"}}
]
```

Please begin generating and output only in the specified 'Output Format' without any extra text.
```
"""
   return prompt

def get_translate_question_prompt(question):
   prompt=f"""
    Please translate the following question into Chinese without changing its meaning. Please note the following requirements:
    1. The question should be relevant to an in-car scenario.
    2. The question should conform to the habits of human drivers.
    3. The sentence should be fluent and meet human preferences.
    Please only output the translation, no additional content!!!!!.

    Question:
    {question}
"""
   return prompt

def get_translate_answer_prompt(answer):
   prompt=f"""
   Please translate the following answer into Chinese without changing its meaning. Please note the following requirements:
   1. The answer should be related to the in-car scenario.
   2. The answer should conform to the answering habits of in-car intelligent systems.
   3. The sentences should be fluent and align with human preferences.
   Please only output the translated content without adding any extra content!!!!! 

   Answer:
   {answer}
"""
   return prompt

def get_translate_question_answer_prompt(question,answer):
   prompt=f"""
You are an excellent translator,I have created a set of questions and answers related to in-car scenarios. Please translate them into Chinese according to the following guidelines, ensuring the original meaning is retained while paying particular attention to the following points:

1. The translated content should correspond to the actual usage in in-car scenarios.
2. Ensure the correct use of terminology and proper nouns.
3. The translated sentences should be grammatically correct and naturally fluent.
4. Prioritize making the translation meet the language requirements of the user (if mentioned in the question).
5. Considering user experience, ensure the language is concise and easy to understand.
6. Comply with the cultural and linguistic habits of different regions.
7. Avoid ambiguity and ensure operational instructions are clear.
8. The translation should be as conversational as possible.
—
**Question**
{question}
_
**Answer**
{answer}
—
**Output Format**
[{{"question": "Chinese translation of the question", "answer": "Chinese translation of the answer"}}]
__
Please start generating, and note that you only need to generate content that conforms to the output format, without any additional information!

"""
   return prompt