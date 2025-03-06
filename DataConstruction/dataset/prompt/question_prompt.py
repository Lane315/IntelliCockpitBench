import pandas as pd
def make_example(df: pd.DataFrame, col):
      if col=="Description":
        questions = df[df['label2'].isna() | (df['label2'].str.strip() == '')]['english'].tolist()
      else:
        questions = df[df['label2'] == col]['english'].tolist()
      return "e.g.: " + " ".join([f"{idx+1}. {value}" for idx, value in enumerate(questions)])

def create_english_question_prompt(df:pd.DataFrame):
    prompt = f"""
You are a driver operating a vehicle. Based on the content of images captured by the onboard cameras, generate 'questions' and their 'perspectives' from the **question perspective**, **question requirement**, and **question classification**. Please ensure:

**Usage Scenario and Goal**:
The goal is to generate a variety of questions for vehicle multimodal scenarios that align with human habits and cover diverse perspectives. Avoid meaningless or illogical questions. The questions must specifically require the use of multimodal models (combining visual and other data) and should not be solvable by language models alone or language models paired with tools like maps, weather applications, or navigation systems. Additionally, avoid using terms such as "in the image" or "in the background," as these are not typical questions asked by drivers.

1. **Clarity**: The questions must be specific and relate directly to perceivable information in the image. For instance, if asking "What is the license plate number of the car in the left foreground?", the image must include the vehicle in the left foreground and its license plate, with answers being accurate in accordance with the image content.
2. **Consistency with Classification**: The questions must strictly correspond to the primary and secondary tags listed in the 'question classification system' below, avoiding cross-category queries.
3. **Diverse Perspectives**: For each primary tag, attempt to formulate questions using one of the following **question perspectives**. Note that these are perspectives, not classification tags:
4. **Human Alignment**: Ensure questions reflect real-world in-car scenarios and are consistent with human questioning habits.
5. **Conciseness**: Ensure questions and explanations are short and easy to process for quick comprehension during real-time operations.
6. **Relevance to Multimodal Capabilities** : Since the questions target the construction of vehicle multimodal capabilities, avoid questions that can be resolved without such capabilities, such as asking for the current precise location (solvable via maps) or current weather conditions (solvable via weather apps).
7. **Random Selection**: Randomly select three aspects from the ‘question classification system’, and generate one question for each aspect, resulting in a total of three questions.
---

**Question Perspectives**

   - **Why** 
   - **What** 
   - **Where** 
   - **When** 
   - **Who/Which** 
   - **How** 
   - **How much/How many** 
   - **How feel** 
   - **Can/Have** 
   - **Is/Do/Others**

---
**Question Classification System** :

1. Description:{make_example(df,'Description')}
2. Recognition:
   - **Vehicle Model Recognition**: {make_example(df,'Vehicle Model Recognition')}
   - **Information Extraction**: {make_example(df,'Information Extraction')}
   - **Object Recognition**: {make_example(df,'Object Recognition')}
   - **Emotion Recognition**: {make_example(df,'Emotion Recognition')}
   - **Human Activity Recognition**: {make_example(df,'Human Activity Recognition')}
3. World Knowledge Q&A:
   - **Traffic Laws and Regulations**: {make_example(df,'Traffic Laws and Regulations')}
   - **Geospatial Environmental Information**: {make_example(df,'Geospatial Environmental Information')}
   - **Socio-cultural Knowledge**: {make_example(df,'Socio-cultural Knowledge')}
   - **General Knowledge**: {make_example(df,'General Knowledge')}
4. Reasoning:
   - **Quantitative Statistics**: {make_example(df,'Quantitative Statistics')}
   - **Distance Measurement**: {make_example(df,'Distance Measurement')}
   - **Angle Measurement**: {make_example(df,'Angle Measurement')}
   - **Area and Volume**: {make_example(df,'Area and Volume')}
   - **Probabilistic Reasoning/Intent Recognition**: {make_example(df,'Probabilistic Reasoning/Intent Recognition')}
   - **Driving Decisions**: {make_example(df,'Driving Decisions')}
5. Others:
   - **Creation**: {make_example(df,'Creation')}
   - **Translation**: {make_example(df,'Translation')}
   - **Others**: {make_example(df,'Others')}
---

**Question Requirements**

(a) Relevance
- Definition: Is the question relevant to the given image?
(b) Answerability
- Definition: Can the question be clearly answered?
(c) Innovativeness
- Definition: Is the question novel and not easily repetitive?
(d) Authenticity
- Definition: Is the question typical of an in-car scenario, consistent with human preferences?
(e) Simplicity
- Definition: Is the question concise, avoiding unnecessary complexity?

---

Output Format:
'''
[
{{"Question":"Generated Question 1","Perspective":"Question Perspective 1"}},
......
{{"Question":"Generated Question n","Perspective":"Question Perspective n"}},
]
'''

Begin generating questions, ensuring diverse perspectives, and output only in the specified 'Output Format' without any extra text!!!
"""
    return prompt